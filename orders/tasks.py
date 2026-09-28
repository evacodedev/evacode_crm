from celery import shared_task
from django.db import transaction

from integrations.business_ru import get_business_ru_client

from .models import Order


@shared_task(name="orders.push_order_to_business_ru")
def push_order_to_business_ru(order_id: int) -> str:
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return f"order {order_id} missing"

    client = get_business_ru_client()
    result = client.push_order(order)

    with transaction.atomic():
        order.business_ru_sync_status = (
            Order.SyncStatus.STUBBED if result.ok else Order.SyncStatus.FAILED
        )
        order.business_ru_sync_message = result.message
        order.save(
            update_fields=[
                "business_ru_sync_status",
                "business_ru_sync_message",
                "updated_at",
            ]
        )
    return result.status
