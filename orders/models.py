from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SUBMITTED = "submitted", "Оформлен"

    class SyncStatus(models.TextChoices):
        PENDING = "pending", "Ожидает"
        STUBBED = "stubbed", "Stub (не в Business.Ru)"
        FAILED = "failed", "Ошибка"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Консультант",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )

    client_name = models.CharField("ФИО клиента", max_length=255)
    client_phone = models.CharField("Телефон", max_length=64)
    client_email = models.EmailField("Email", blank=True)
    client_note = models.TextField("Комментарий", blank=True)

    delivery_country = models.CharField("Страна", max_length=100, default="Россия")
    delivery_city = models.CharField("Город", max_length=100)
    delivery_street = models.CharField("Адрес (улица, дом, кв.)", max_length=255)
    delivery_postal = models.CharField("Индекс", max_length=32, blank=True)

    total_amount = models.DecimalField(
        "Сумма",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    business_ru_sync_status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING,
    )
    business_ru_sync_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return f"#{self.pk} {self.client_name} ({self.status})"

    def recalculate_total(self) -> None:
        total = sum((line.line_total for line in self.lines.all()), Decimal("0.00"))
        self.total_amount = total
        self.save(update_fields=["total_amount", "updated_at"])


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="order_lines",
    )
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self) -> str:
        return f"{self.product_sku} × {self.quantity}"
