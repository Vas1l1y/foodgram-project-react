from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Tag",
        help_text="Enter a tag",
    )
    color = models.CharField(
        blank=True,
        null=True,
        max_length=7,
        verbose_name="color",
        help_text="Enter a color",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Tag URL",
        help_text="Enter the tag URL",
    )

    class Meta:
        ordering = ("name", "slug")
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Ingredient",
        help_text="Enter a ingredient",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Ingredient",
        help_text="Enter a ingredient",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tag = models.ManyToManyField(
        Tag,
        # null=True,
        related_name='tags',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    is_favorite = models.BooleanField(
        verbose_name='В избранном',
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В корзине',
        default=False
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Recipe',
        help_text='Enter a recipe',
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipes/',
        blank=True
    )
    text = models.TextField(
        verbose_name='Text recipe',
        help_text='Добавьте рецепт',
    )
    cooking_time = models.TimeField(
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):
        return self.name
