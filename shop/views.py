import logging

from django.db import DatabaseError
from django.db.models import ProtectedError
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Brand, Sneaker, SneakerSize
from .permissions import IsAdminOrReadOnly
from .serializers import (
    BrandSerializer,
    SneakerDetailSerializer,
    SneakerListSerializer,
    SneakerSizeSerializer,
)

logger = logging.getLogger(__name__)


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
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(tags=["Brands"], responses={200: BrandSerializer(many=True)})
    def get(self, request):
        brands = Brand.objects.all().order_by("name")
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Brands"],
        request=BrandSerializer,
        responses={
            201: BrandSerializer,
            400: OpenApiResponse(description="Помилка валідації"),
        },
    )
    def post(self, request):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            brand = serializer.save()
            logger.info(
                "Admin id=%s created brand id=%s (%s)",
                request.user.id,
                brand.id,
                brand.name,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(
            "Brand validation failed for user id=%s: %s",
            request.user.id,
            serializer.errors,
        )
        return error_response(
            message="Помилка валідації даних бренду",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )


class BrandDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return None

    @extend_schema(
        tags=["Brands"],
        responses={200: BrandSerializer, 404: OpenApiResponse()},
    )
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

    @extend_schema(
        tags=["Brands"],
        request=BrandSerializer,
        responses={
            200: BrandSerializer,
            400: OpenApiResponse(),
            404: OpenApiResponse(),
        },
    )
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
            logger.info("Admin id=%s updated brand id=%s", request.user.id, pk)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return error_response(
            message="Помилка оновлення бренду",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )

    @extend_schema(
        tags=["Brands"],
        responses={
            204: OpenApiResponse(),
            404: OpenApiResponse(),
            409: OpenApiResponse(),
        },
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
            logger.info("Admin id=%s deleted brand id=%s", request.user.id, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            count = brand.sneakers.count()
            logger.warning(
                "Cannot delete brand id=%s: %s sneakers attached", pk, count
            )
            return error_response(
                message=(
                    f"Неможливо видалити бренд '{brand.name}', "
                    f"оскільки за ним закріплено {count} моделей кросівок"
                ),
                error_type="Conflict",
                status_code=status.HTTP_409_CONFLICT,
            )


class SneakerListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        tags=["Sneakers"],
        summary="Отримати список кросівок",
        description="Публічний ендпоінт для перегляду, фільтрації та сортування каталогу кросівок.",
        parameters=[
            OpenApiParameter("brand", str, description="ID або назва бренду (напр. Nike)"),
            OpenApiParameter("search", str, description="Пошук за назвою моделі"),
            OpenApiParameter("category", str, description="Категорія взуття"),
            OpenApiParameter(
                "gender",
                str,
                enum=["men", "women", "unisex"],
                description="Стать",
            ),
            OpenApiParameter("size", float, description="Наявний розмір (напр. 42.5)"),
            OpenApiParameter(
                "sort",
                str,
                enum=["price_asc", "price_desc", "newest"],
                description="Сортування результатів",
            ),
        ],
        responses={200: SneakerListSerializer(many=True)},
    )
    def get(self, request):
        logger.debug(
            "Fetching sneaker catalog with query_params=%s",
            request.query_params.dict(),
        )
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
                logger.warning("Invalid size filter value ignored: %s", size_param)

        sort_param = request.query_params.get("sort")
        if sort_param == "price_asc":
            queryset = queryset.order_by("price")
        elif sort_param == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort_param == "newest":
            queryset = queryset.order_by("-created_at")

        serializer = SneakerListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Sneakers"],
        summary="Створити нову модель кросівок",
        description="Доступно лише користувачам із правами адміністратора (is_staff=True).",
        request=SneakerDetailSerializer,
        responses={
            201: SneakerDetailSerializer,
            400: OpenApiResponse(description="Помилка валідації вхідних даних"),
            401: OpenApiResponse(description="Відсутній або недійсний JWT-токен"),
            403: OpenApiResponse(description="Недостатньо прав доступу (не адмін)"),
        },
        examples=[
            OpenApiExample(
                "Приклад створення кросівок",
                value={
                    "name": "Air Max 90",
                    "brand_id": 1,
                    "description": "Класичні повсякденні кросівки",
                    "price": "4500.00",
                    "category": "Lifestyle",
                    "gender": "unisex",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = SneakerDetailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sneaker = serializer.save()
            except DatabaseError:
                logger.exception(
                    "Database error while creating sneaker by user id=%s",
                    request.user.id,
                )
                return error_response(
                    message="Внутрішня помилка збереження товару",
                    error_type="Database Error",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            logger.info(
                "Admin id=%s created sneaker id=%s (%s)",
                request.user.id,
                sneaker.id,
                sneaker.name,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(
            "Sneaker creation validation failed for user id=%s: %s",
            request.user.id,
            serializer.errors,
        )
        return error_response(
            message="Помилка створення товару",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )


class SneakerDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return (
                Sneaker.objects.select_related("brand")
                .prefetch_related("sizes")
                .get(pk=pk)
            )
        except Sneaker.DoesNotExist:
            return None

    @extend_schema(
        tags=["Sneakers"],
        summary="Отримати детальну інформацію про кросівки",
        responses={
            200: SneakerDetailSerializer,
            404: OpenApiResponse(description="Кросівки не знайдено"),
        },
    )
    def get(self, request, pk):
        sneaker = self.get_object(pk)
        if not sneaker:
            logger.warning("Sneaker id=%s not found on GET", pk)
            return error_response(
                message=f"Кросівки з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = SneakerDetailSerializer(sneaker)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Sneakers"],
        summary="Оновити модель кросівок",
        description="Повне оновлення даних моделі кросівок (лише для адміністратора).",
        request=SneakerDetailSerializer,
        responses={
            200: SneakerDetailSerializer,
            400: OpenApiResponse(description="Помилка валідації"),
            401: OpenApiResponse(description="Необхідна автентифікація"),
            403: OpenApiResponse(description="Доступ заборонено"),
            404: OpenApiResponse(description="Кросівки не знайдено"),
        },
    )
    def put(self, request, pk):
        sneaker = self.get_object(pk)
        if not sneaker:
            logger.warning(
                "Sneaker id=%s not found on PUT by user id=%s", pk, request.user.id
            )
            return error_response(
                message=f"Кросівки з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = SneakerDetailSerializer(sneaker, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except DatabaseError:
                logger.exception(
                    "Database error while updating sneaker id=%s by user id=%s",
                    pk,
                    request.user.id,
                )
                return error_response(
                    message="Внутрішня помилка оновлення товару",
                    error_type="Database Error",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            logger.info("Admin id=%s updated sneaker id=%s", request.user.id, pk)
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(
            "Sneaker id=%s update validation failed for user id=%s: %s",
            pk,
            request.user.id,
            serializer.errors,
        )
        return error_response(
            message="Помилка оновлення даних товару",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )

    @extend_schema(
        tags=["Sneakers"],
        summary="Видалити модель кросівок",
        description="Видалення моделі кросівок із каталогу (лише для адміністратора).",
        responses={
            204: OpenApiResponse(description="Успішно видалено"),
            401: OpenApiResponse(description="Необхідна автентифікація"),
            403: OpenApiResponse(description="Доступ заборонено"),
            404: OpenApiResponse(description="Кросівки не знайдено"),
        },
    )
    def delete(self, request, pk):
        sneaker = self.get_object(pk)
        if not sneaker:
            logger.warning(
                "Sneaker id=%s not found on DELETE by user id=%s", pk, request.user.id
            )
            return error_response(
                message=f"Кросівки з id={pk} не знайдено",
                error_type="Not Found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            sneaker.delete()
        except DatabaseError:
            logger.exception(
                "Database error while deleting sneaker id=%s by user id=%s",
                pk,
                request.user.id,
            )
            return error_response(
                message="Внутрішня помилка видалення товару",
                error_type="Database Error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        logger.info("Admin id=%s deleted sneaker id=%s", request.user.id, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SneakerSizeListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(tags=["Sizes"], responses={200: SneakerSizeSerializer(many=True)})
    def get(self, request):
        sneaker_id = request.query_params.get("sneaker")
        queryset = SneakerSize.objects.all()
        if sneaker_id:
            queryset = queryset.filter(sneaker_id=sneaker_id)
        serializer = SneakerSizeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Sizes"],
        request=SneakerSizeSerializer,
        responses={
            201: SneakerSizeSerializer,
            400: OpenApiResponse(),
            409: OpenApiResponse(),
        },
    )
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
            logger.info(
                "Admin id=%s added size %s to sneaker id=%s",
                request.user.id,
                size,
                sneaker.id,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(
            message="Помилка додавання розміру",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )


class SneakerSizeDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return SneakerSize.objects.get(pk=pk)
        except SneakerSize.DoesNotExist:
            return None

    @extend_schema(
        tags=["Sizes"],
        request=SneakerSizeSerializer,
        responses={
            200: SneakerSizeSerializer,
            400: OpenApiResponse(),
            404: OpenApiResponse(),
        },
    )
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
            logger.info("Admin id=%s updated size id=%s", request.user.id, pk)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return error_response(
            message="Помилка оновлення розміру",
            error_type="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors,
        )

    @extend_schema(
        tags=["Sizes"],
        responses={204: OpenApiResponse(), 404: OpenApiResponse()},
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
        logger.info("Admin id=%s deleted size id=%s", request.user.id, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
