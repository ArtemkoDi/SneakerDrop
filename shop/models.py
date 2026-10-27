from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Sneaker(models.Model):
    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("unisex", "Unisex"),
    ]


    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="sneakers")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="unisex")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class SneakerSize(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE, related_name="sizes")
    size = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(10.0), MaxValueValidator(48.0)]
    )
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("sneaker", "size")

    def __str__(self):
        return f"{self.sneaker.name} - {self.size}"
