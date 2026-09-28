from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from catalog.models import Product

from .models import Order, OrderLine
from .tasks import push_order_to_business_ru


class OrderLineInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price",
            "line_total",
        )


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, read_only=True)
    line_items = OrderLineInputSerializer(many=True, write_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "client_name",
            "client_phone",
            "client_email",
            "client_note",
            "delivery_country",
            "delivery_city",
            "delivery_street",
            "delivery_postal",
            "total_amount",
            "business_ru_sync_status",
            "business_ru_sync_message",
            "created_by_username",
            "lines",
            "line_items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "status",
            "total_amount",
            "business_ru_sync_status",
            "business_ru_sync_message",
            "created_at",
            "updated_at",
        )

    def validate_line_items(self, value):
        if not value:
            raise serializers.ValidationError("Добавьте хотя бы одну позицию.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        line_items = validated_data.pop("line_items")
        user = self.context["request"].user
        order = Order.objects.create(
            created_by=user,
            status=Order.Status.SUBMITTED,
            **validated_data,
        )
        total = Decimal("0.00")
        product_ids = [item["product_id"] for item in line_items]
        products = {
            p.id: p
            for p in Product.objects.filter(id__in=product_ids, is_active=True)
        }
        for item in line_items:
            product = products.get(item["product_id"])
            if not product:
                raise serializers.ValidationError(
                    {"line_items": f"Товар id={item['product_id']} не найден или неактивен."}
                )
            qty = item["quantity"]
            unit = product.price
            line_total = unit * qty
            OrderLine.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                quantity=qty,
                unit_price=unit,
                line_total=line_total,
            )
            total += line_total
        order.total_amount = total
        order.save(update_fields=["total_amount", "updated_at"])
        # Prefer Celery; fall back to sync stub if broker unavailable
        try:
            push_order_to_business_ru.delay(order.id)
        except Exception:
            push_order_to_business_ru(order.id)
        order.refresh_from_db()
        return order
