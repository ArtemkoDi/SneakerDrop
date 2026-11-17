from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import Sneaker


@pytest.mark.django_db
def test_get_sneakers_list_public_success(api_client, sneaker, sneaker_size):
    # Arrange
    url = reverse("sneaker-list-create")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Air Force 1"
    assert response.data[0]["brand"] == "Nike"
    assert response.data[0]["sizes"] == [42.5]


@pytest.mark.django_db
def test_filter_and_sort_sneakers_success(api_client, brand, sneaker, sneaker_size):
    # Arrange
    Sneaker.objects.create(
        brand=brand,
        name="Pegasus 40",
        price=Decimal("5100.00"),
        category="Running",
        gender="men",
    )
    url = reverse("sneaker-list-create")

    # Act
    filtered_response = api_client.get(
        url,
        {
            "brand": "Nike",
            "search": "Pegasus",
            "category": "Running",
            "gender": "men",
            "sort": "price_desc",
        },
    )
    size_response = api_client.get(url, {"size": "42.5"})
    invalid_size_response = api_client.get(
        url, {"brand": str(brand.id), "size": "invalid", "sort": "price_asc"}
    )

    # Assert
    assert filtered_response.status_code == status.HTTP_200_OK
    assert len(filtered_response.data) == 1
    assert filtered_response.data[0]["name"] == "Pegasus 40"
    assert len(size_response.data) == 1
    assert size_response.data[0]["name"] == "Air Force 1"
    assert len(invalid_size_response.data) == 2
    assert invalid_size_response.data[0]["name"] == "Air Force 1"


@pytest.mark.django_db
def test_get_sneaker_detail_success(api_client, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == sneaker.pk
    assert response.data["name"] == "Air Force 1"


@pytest.mark.django_db
def test_get_nonexistent_sneaker_returns_404(api_client):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": 99999})

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_sneaker_admin_success(admin_client, brand):
    # Arrange
    url = reverse("sneaker-list-create")
    initial_count = Sneaker.objects.count()
    payload = {
        "name": "Dunk Low",
        "brand_id": brand.id,
        "description": "Retro basketball shoe",
        "price": "4800.00",
        "category": "Lifestyle",
        "gender": "unisex",
    }

    # Act
    response = admin_client.post(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert Sneaker.objects.count() == initial_count + 1
    assert Sneaker.objects.filter(name="Dunk Low").exists()


@pytest.mark.django_db
def test_create_sneaker_unauthenticated_returns_401(api_client, brand):
    # Arrange
    url = reverse("sneaker-list-create")
    payload = {
        "name": "Dunk Low",
        "brand_id": brand.id,
        "price": "4800.00",
        "category": "Lifestyle",
    }

    # Act
    response = api_client.post(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_sneaker_regular_user_returns_403(user_client, brand):
    # Arrange
    url = reverse("sneaker-list-create")
    payload = {
        "name": "Dunk Low",
        "brand_id": brand.id,
        "price": "4800.00",
        "category": "Lifestyle",
    }

    # Act
    response = user_client.post(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_sneaker_invalid_data_returns_400(admin_client, brand):
    # Arrange
    url = reverse("sneaker-list-create")
    payload = {
        "name": "",
        "brand_id": brand.id,
        "price": "-100.00",
        "category": "Lifestyle",
    }

    # Act
    response = admin_client.post(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "details" in response.data


@pytest.mark.django_db
def test_update_sneaker_admin_success(admin_client, brand, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})
    payload = {
        "name": "Air Force 1 '07",
        "brand_id": brand.id,
        "description": "Updated description",
        "price": "4600.00",
        "category": "Lifestyle",
        "gender": "unisex",
    }

    # Act
    response = admin_client.put(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    sneaker.refresh_from_db()
    assert sneaker.name == "Air Force 1 '07"
    assert sneaker.price == Decimal("4600.00")


@pytest.mark.django_db
def test_update_sneaker_unauthenticated_returns_401(api_client, brand, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})
    payload = {
        "name": "Updated",
        "brand_id": brand.id,
        "price": "4600.00",
        "category": "Lifestyle",
    }

    # Act
    response = api_client.put(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_sneaker_regular_user_returns_403(user_client, brand, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})
    payload = {
        "name": "Hacked",
        "brand_id": brand.id,
        "price": "10.00",
        "category": "Lifestyle",
    }

    # Act
    response = user_client.put(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_sneaker_invalid_data_returns_400(admin_client, brand, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})
    payload = {
        "name": "Air Force 1",
        "brand_id": brand.id,
        "price": "0.00",
        "category": "Lifestyle",
    }

    # Act
    response = admin_client.put(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_nonexistent_sneaker_returns_404(admin_client, brand):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": 99999})
    payload = {
        "name": "Ghost",
        "brand_id": brand.id,
        "price": "3000.00",
        "category": "Lifestyle",
    }

    # Act
    response = admin_client.put(url, data=payload, format="json")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_sneaker_admin_success(admin_client, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})

    # Act
    response = admin_client.delete(url)

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Sneaker.objects.filter(pk=sneaker.pk).exists()


@pytest.mark.django_db
def test_delete_sneaker_unauthenticated_returns_401(api_client, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})

    # Act
    response = api_client.delete(url)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_sneaker_regular_user_returns_403(user_client, sneaker):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": sneaker.pk})

    # Act
    response = user_client.delete(url)

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_nonexistent_sneaker_returns_404(admin_client):
    # Arrange
    url = reverse("sneaker-detail", kwargs={"pk": 99999})

    # Act
    response = admin_client.delete(url)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
