from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        max_length=128,
        error_messages={
            "required": "Пароль є обов'язковим полем",
            "min_length": "Пароль має містити щонайменше 8 символів",
            "max_length": "Пароль не може перевищувати 128 символів",
        },
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "Підтвердження пароля є обов'язковим полем",
        },
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        error_messages={
            "required": "Email є обов'язковим полем",
            "invalid": "Введіть коректну адресу електронної пошти",
        },
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        error_messages={
            "required": "Ім'я користувача є обов'язковим полем",
            "max_length": "Ім'я користувача не може бути довшим за 150 символів",
        },
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        default="",
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        default="",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Користувач із таким ім'ям уже існує")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Користувач із таким email уже зареєстрований")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Паролі не збігаються"}
            )

        user_temp = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            first_name=attrs.get("first_name", ""),
            last_name=attrs.get("last_name", ""),
        )
        password_validation.validate_password(attrs.get("password"), user=user_temp)

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_staff"]
