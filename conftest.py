from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from shop.models import Brand, Sneaker, SneakerSize

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="regular_buyer",
        email="buyer@example.com",
        password="StrongPassword123!",
        is_staff=False,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="shop_admin",
        email="admin@example.com",
        password="AdminPassword123!",
    )


@pytest.fixture
def user_client(regular_user):
    client = APIClient()
    token = RefreshToken.for_user(regular_user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    token = RefreshToken.for_user(admin_user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def brand(db):
    return Brand.objects.create(
        name="Nike",
        description="American sportswear brand",
    )


@pytest.fixture
def sneaker(db, brand):
    return Sneaker.objects.create(
        brand=brand,
        name="Air Force 1",
        description="Classic white sneakers",
        price=Decimal("4200.00"),
        category="Lifestyle",
        gender="unisex",
    )


@pytest.fixture
def sneaker_size(db, sneaker):
    return SneakerSize.objects.create(
        sneaker=sneaker,
        size=Decimal("42.5"),
        stock_quantity=10,
    )
