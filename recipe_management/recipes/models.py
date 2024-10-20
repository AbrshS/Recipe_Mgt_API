from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('Dessert', 'Dessert'),
        ('Main Course', 'Main Course'),
        ('Appetizer', 'Appetizer'),
        ('Breakfast', 'Breakfast'),
        ('Beverage', 'Beverage'),
        ('Vegetarian', 'Vegetarian'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    preparation_time = models.PositiveIntegerField(help_text='Time in minutes')
    cooking_time = models.PositiveIntegerField(help_text='Time in minutes')
    servings = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favorited_by = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()  # Rating from 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.recipe.title}"
