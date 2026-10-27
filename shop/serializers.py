from rest_framework import serializers

from .models import Brand, Sneaker, SneakerSize


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "description"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Назва бренду не може бути порожньою")
        return value


class SneakerSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SneakerSize
        fields = ["id", "sneaker", "size", "stock_quantity"]

    def validate_size(self, value):
        if value < 10 or value > 60:
            raise serializers.ValidationError("Розмір має бути від 10 до 48")
        if (value * 10) % 5 != 0:
            raise serializers.ValidationError("Розмір має закінчуватися на .0 або .5 (наприклад: 43.0, 43.5).")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Кількість на складі не може бути меншою за 0"
            )
        return value


class SneakerListSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Sneaker
        fields = ["id", "name", "brand", "price", "category", "gender"]


class SneakerDetailSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source="brand", write_only=True
    )
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = Sneaker
        fields = [
            "id",
            "name",
            "brand",
            "brand_id",
            "description",
            "price",
            "category",
            "gender",
            "sizes",
            "created_at",
        ]

    def get_sizes(self, obj):
        return [float(item.size) for item in obj.sizes.all()]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Ціна товару має бути більшою за 0")
        return value
