from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token

from catalog.models import Category, ConsultantGroup, ConsultantGroupItem, Product


class Command(BaseCommand):
    help = "Seed demo sales user, products, and one consultant group panel"

    @transaction.atomic
    def handle(self, *args, **options):
        password = settings.DEMO_SALES_PASSWORD
        user, created = User.objects.get_or_create(
            username="sales",
            defaults={
                "first_name": "Анна",
                "last_name": "Консультант",
                "email": "sales@evacode.local",
            },
        )
        user.set_password(password)
        user.save()
        Token.objects.get_or_create(user=user)

        cats = {}
        for slug, name, order in [
            ("skincare", "Уход за кожей", 1),
            ("makeup", "Макияж", 2),
            ("sets", "Наборы", 3),
        ]:
            cats[slug], _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "sort_order": order},
            )

        products_spec = [
            ("EV-001", "Тонер с центеллой 200 мл", "skincare", "890.00"),
            ("EV-002", "Сыворотка ниацинамид 30 мл", "skincare", "1450.00"),
            ("EV-003", "Крем SPF50+", "skincare", "1200.00"),
            ("EV-004", "Тинт для губ Rose", "makeup", "650.00"),
            ("EV-005", "Кушон светлый", "makeup", "2100.00"),
            ("EV-006", "Набор миниатюр ухода", "sets", "3200.00"),
            ("EV-007", "Маска тканевая (5 шт)", "skincare", "780.00"),
            ("EV-008", "Очищающая пенка", "skincare", "540.00"),
        ]
        products = []
        for sku, name, cat_slug, price in products_spec:
            p, _ = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": cats[cat_slug],
                    "price": Decimal(price),
                    "is_active": True,
                    "description": f"Демо-товар {name}",
                },
            )
            products.append(p)

        group, _ = ConsultantGroup.objects.get_or_create(
            owner=user,
            name="Частые позиции",
            defaults={"sort_order": 1},
        )
        group.items.all().delete()
        for idx, product in enumerate(products[:4]):
            ConsultantGroupItem.objects.create(
                group=group,
                product=product,
                sort_order=idx,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed OK. User sales / {password} "
                f"({'created' if created else 'updated'}); "
                f"{len(products)} products; group «{group.name}»."
            )
        )
