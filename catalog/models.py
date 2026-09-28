from django.db import models


class Category(models.Model):
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField(unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    sku = models.CharField("Артикул", max_length=64, unique=True)
    name = models.CharField("Название", max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Категория",
    )
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    is_active = models.BooleanField("Активен", default=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return f"{self.sku} — {self.name}"


class ConsultantGroup(models.Model):
    """Персональная группа товаров консультанта (своя панель)."""

    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="consultant_groups",
        verbose_name="Консультант",
    )
    name = models.CharField("Название группы", max_length=200)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Группа консультанта"
        verbose_name_plural = "Группы консультанта"

    def __str__(self) -> str:
        return f"{self.owner.username}: {self.name}"


class ConsultantGroupItem(models.Model):
    group = models.ForeignKey(
        ConsultantGroup,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="group_items",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        unique_together = ("group", "product")
        verbose_name = "Товар в группе"
        verbose_name_plural = "Товары в группе"

    def __str__(self) -> str:
        return f"{self.group.name} → {self.product.sku}"
