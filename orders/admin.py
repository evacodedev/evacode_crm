from django.contrib import admin

from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    readonly_fields = ("product_name", "product_sku", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_name",
        "status",
        "total_amount",
        "business_ru_sync_status",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "business_ru_sync_status")
    inlines = [OrderLineInline]


admin.site.register(OrderLine)
