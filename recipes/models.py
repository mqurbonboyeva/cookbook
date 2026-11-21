from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator, MaxValueValidator, MinValueValidator,
)
from django.db import models


def validate_image_size(image):
    if image.size > 3 * 1024 * 1024:
        raise ValidationError("Rasm 3 MB dan katta bo'lmasligi kerak.")


class Category(models.Model):
    name = models.CharField('Nomi', max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.CharField('Ikonka', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Oson'
        MEDIUM = 'medium', "O'rtacha"
        HARD = 'hard', 'Qiyin'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Muallif')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name='recipes', verbose_name='Kategoriya')
    title = models.CharField('Taom nomi', max_length=120)
    image = models.ImageField(
        'Rasm', upload_to='recipes/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size,
        ])
    description = models.TextField('Qisqacha tavsif', max_length=500)
    prep_time = models.PositiveIntegerField(
        'Tayyorlash vaqti (daqiqa)',
        validators=[MinValueValidator(1), MaxValueValidator(1440)])
    servings = models.PositiveIntegerField(
        'Necha kishilik',
        validators=[MinValueValidator(1), MaxValueValidator(50)])
    difficulty = models.CharField(
        'Murakkablik', max_length=10, choices=Difficulty.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Retsept'
        verbose_name_plural = 'Retseptlar'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField('Nomi', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Masalliq'
        verbose_name_plural = 'Masalliqlar'

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    class Unit(models.TextChoices):
        G = 'g', 'g'
        KG = 'kg', 'kg'
        ML = 'ml', 'ml'
        L = 'l', 'l'
        PIECE = 'dona', 'dona'
        TBSP = 'osh qoshiq', 'osh qoshiq'
        TSP = 'choy qoshiq', 'choy qoshiq'
        GLASS = 'stakan', 'stakan'

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name='recipe_ingredients')
    quantity = models.DecimalField(
        'Miqdori', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    unit = models.CharField('Birlik', max_length=20, choices=Unit.choices)

    class Meta:
        verbose_name = 'Retsept masalliği'
        verbose_name_plural = 'Retsept masalliqlari'

    def __str__(self):
        return f'{self.ingredient} — {self.quantity} {self.unit}'


class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField('Tartib raqami')
    text = models.TextField('Matn')

    class Meta:
        ordering = ['order']
        verbose_name = 'Bosqich'
        verbose_name_plural = 'Bosqichlar'

    def __str__(self):
        return f'{self.recipe} — {self.order}-bosqich'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Sevimli'
        verbose_name_plural = 'Sevimlilar'

    def __str__(self):
        return f'{self.user} ♥ {self.recipe}'