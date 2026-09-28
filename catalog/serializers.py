from rest_framework import serializers

from .models import Category, ConsultantGroup, ConsultantGroupItem, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "sort_order")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "category",
            "category_name",
            "price",
            "is_active",
            "description",
        )


class ConsultantGroupItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
        required=False,
    )

    class Meta:
        model = ConsultantGroupItem
        fields = ("id", "product", "product_id", "sort_order")


class ConsultantGroupSerializer(serializers.ModelSerializer):
    items = ConsultantGroupItemSerializer(many=True, read_only=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = ConsultantGroup
        fields = ("id", "name", "sort_order", "items", "product_ids", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")

    def create(self, validated_data):
        product_ids = validated_data.pop("product_ids", [])
        group = ConsultantGroup.objects.create(
            owner=self.context["request"].user,
            **validated_data,
        )
        self._replace_products(group, product_ids)
        return group

    def update(self, instance, validated_data):
        product_ids = validated_data.pop("product_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if product_ids is not None:
            self._replace_products(instance, product_ids)
        return instance

    def _replace_products(self, group: ConsultantGroup, product_ids: list[int]) -> None:
        group.items.all().delete()
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        by_id = {p.id: p for p in products}
        for idx, pid in enumerate(product_ids):
            product = by_id.get(pid)
            if product:
                ConsultantGroupItem.objects.create(
                    group=group,
                    product=product,
                    sort_order=idx,
                )
