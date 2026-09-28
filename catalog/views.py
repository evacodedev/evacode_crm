from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, ConsultantGroup, Product
from .serializers import (
    CategorySerializer,
    ConsultantGroupSerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category")
        category = self.request.query_params.get("category")
        q = self.request.query_params.get("q")
        if category:
            qs = qs.filter(category_id=category)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        return qs


class ConsultantGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultantGroupSerializer
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        return (
            ConsultantGroup.objects.filter(owner=self.request.user)
            .prefetch_related("items__product__category")
            .all()
        )

    @action(detail=True, methods=["put"], url_path="products")
    def set_products(self, request, pk=None):
        group = self.get_object()
        product_ids = request.data.get("product_ids", [])
        if not isinstance(product_ids, list):
            return Response({"detail": "product_ids должен быть списком."}, status=400)
        serializer = self.get_serializer(
            group,
            data={"product_ids": product_ids},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
