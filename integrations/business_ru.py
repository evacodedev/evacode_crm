"""Business.Ru integration — stub for local MVP.

TODO: real API client, credentials from env, retries, idempotency key,
owner = sell-manager mapping.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    ok: bool
    status: str
    message: str


class BusinessRuClient(Protocol):
    def push_order(self, order) -> SyncResult: ...


class StubBusinessRuClient:
    """No live credentials — records that sync was stubbed."""

    def push_order(self, order) -> SyncResult:
        logger.info(
            "Business.Ru stub: would push order #%s (client=%s, total=%s)",
            order.pk,
            order.client_name,
            order.total_amount,
        )
        return SyncResult(
            ok=True,
            status="stubbed",
            message=(
                "MVP stub: заказ сохранён в CRM. Выгрузка в Business.Ru "
                "не выполнялась (нет live credentials). TODO: реализовать API."
            ),
        )


def get_business_ru_client() -> BusinessRuClient:
    # Future: switch on BUSINESS_RU_API_URL / keys
    return StubBusinessRuClient()
