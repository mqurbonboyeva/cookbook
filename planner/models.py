from django.conf import settings
from django.db import models

from recipes.models import Recipe


class MealPlan(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast', 'Nonushta'
        LUNCH = 'lunch', 'Tushlik'
        DINNER = 'dinner', 'Kechki ovqat'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='meal_plans')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='meal_plans')
    date = models.DateField('Sana')
    meal_type = models.CharField(
        'Ovqatlanish vaqti', max_length=10, choices=MealType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date', 'meal_type'], name='unique_meal_slot'),
        ]
        ordering = ['date', 'meal_type']
        verbose_name = 'Ovqatlanish rejasi'
        verbose_name_plural = 'Ovqatlanish rejalari'

    def __str__(self):
        return f'{self.user} — {self.date} {self.meal_type}'


class ShoppingItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='shopping_items')
    name = models.CharField('Mahsulot', max_length=100)
    quantity = models.DecimalField('Miqdori', max_digits=10, decimal_places=2)
    unit = models.CharField('Birlik', max_length=20)
    is_bought = models.BooleanField('Sotib olindi', default=False)
    is_manual = models.BooleanField("Qo'lda qo'shilgan", default=False)
    week_start = models.DateField('Hafta boshi')

    class Meta:
        ordering = ['is_bought', 'name']
        verbose_name = 'Xarid elementi'
        verbose_name_plural = 'Xaridlar ro‘yxati'

    def __str__(self):
        return f'{self.name} — {self.quantity} {self.unit}'