from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Brand, Sneaker, SneakerSize
from .serializers import (
    BrandSerializer,
    SneakerDetailSerializer,
    SneakerListSerializer,
    SneakerSizeSerializer,
)


def error_response(
    message,
    error_type="Bad Request",
    status_code=status.HTTP_400_BAD_REQUEST,
    details=None,
):
    return Response(
        {"error": error_type, "message": message, "details": details},
        status=status_code,
    )


class BrandListCreateView(APIView):
    def get(self, request):
        brands = Brand.objects.all().order_by("name")
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(
            message="Помилка валідації даних бренду",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )


class BrandDetailView(APIView):
    def get_object(self, pk):
        try:
            return Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return None

    def get(self, request, pk):
        brand = self.get_object(pk)
        if not brand:
            return error_response(
                message=f"Бренд з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = BrandSerializer(brand)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        brand = self.get_object(pk)
        if not brand:
            return error_response(
                message=f"Бренд з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = BrandSerializer(brand, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return error_response(
            message="Помилка оновлення бренду",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )

    def delete(self, request, pk):
        brand = self.get_object(pk)
        if not brand:
            return error_response(
                message=f"Бренд з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            brand.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            count = brand.sneakers.count()
            return error_response(
                message=f"Неможливо видалити бренд '{brand.name}', оскільки за ним закріплено {count} моделей кросівок",
                error_type="Conflict",
                status_code=status.HTTP_409_CONFLICT,
            )


class SneakerListCreateView(APIView):
    def get(self, request):
        queryset = (
            Sneaker.objects.all().select_related("brand").prefetch_related("sizes")
        )

        brand_param = request.query_params.get("brand")
        search_param = request.query_params.get("search")
        category_param = request.query_params.get("category")
        gender_param = request.query_params.get("gender")
        size_param = request.query_params.get("size")

        if brand_param:
            if brand_param.isdigit():
                queryset = queryset.filter(brand_id=int(brand_param))
            else:
                queryset = queryset.filter(brand__name__iexact=brand_param)

        if search_param:
            queryset = queryset.filter(name__icontains=search_param)

        if category_param:
            queryset = queryset.filter(category__iexact=category_param)

        if gender_param:
            queryset = queryset.filter(gender__iexact=gender_param)

        if size_param:
            try:
                float_size = float(size_param)
                queryset = queryset.filter(sizes__size=float_size).distinct()
            except ValueError:
                pass

        sort_param = request.query_params.get("sort")
        if sort_param == "price_asc":
            queryset = queryset.order_by("price")
        elif sort_param == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort_param == "newest":
            queryset = queryset.order_by("-created_at")

        serializer = SneakerListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SneakerDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(
            message="Помилка створення товару",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )


class SneakerDetailView(APIView):
    def get_object(self, pk):
        try:
            return (
                Sneaker.objects.select_related("brand")
                .prefetch_related("sizes")
                .get(pk=pk)
            )
        except Sneaker.DoesNotExist:
            return None

    def get(self, request, pk):
        sneaker = self.get_object(pk)
        if not sneaker:
            return error_response(
                message=f"Кросівки з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = SneakerDetailSerializer(sneaker)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        sneaker = self.get_object(pk)
        if not sneaker:
            return error_response(
                message=f"Кросівки з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = SneakerDetailSerializer(sneaker, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return error_response(
            message="Помилка оновлення даних товару",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )

    def delete(self, request, pk):
        sneaker = self.get_object(pk)
        if not sneaker:
            return error_response(
                message=f"Кросівки з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        sneaker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SneakerSizeListCreateView(APIView):
    def get(self, request):
        sneaker_id = request.query_params.get("sneaker")
        queryset = SneakerSize.objects.all()
        if sneaker_id:
            queryset = queryset.filter(sneaker_id=sneaker_id)
        serializer = SneakerSizeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SneakerSizeSerializer(data=request.data)
        if serializer.is_valid():
            sneaker = serializer.validated_data["sneaker"]
            size = serializer.validated_data["size"]
            if SneakerSize.objects.filter(sneaker=sneaker, size=size).exists():
                return error_response(
                    message=f"Розмір {size} для моделі '{sneaker.name}' вже додано в базу",
                    error_type="Conflict",
                    status_code=status.HTTP_409_CONFLICT,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(
            message="Помилка додавання розміру",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )


class SneakerSizeDetailView(APIView):
    def get_object(self, pk):
        try:
            return SneakerSize.objects.get(pk=pk)
        except SneakerSize.DoesNotExist:
            return None

    def put(self, request, pk):
        size_obj = self.get_object(pk)
        if not size_obj:
            return error_response(
                message=f"Розмір з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = SneakerSizeSerializer(size_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return error_response(
            message="Помилка оновлення розміру",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )

    def delete(self, request, pk):
        size_obj = self.get_object(pk)
        if not size_obj:
            return error_response(
                message=f"Розмір з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        size_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
