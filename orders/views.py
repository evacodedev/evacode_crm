from rest_framework import mixins, viewsets

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(created_by=self.request.user)
            .prefetch_related("lines")
            .all()
        )
