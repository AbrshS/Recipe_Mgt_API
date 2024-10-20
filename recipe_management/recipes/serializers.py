from rest_framework import serializers
from .models import Recipe
from .models import Review

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'  # Expose all fields for simplicity
        read_only_fields = ['user', 'created_at', 'updated_at']
          # User, timestamps should not be manually modified 
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['user', 'rating', 'comment', 'created_at']