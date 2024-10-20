import stat
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import RecipeSerializer, ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Recipe, Review
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Restrict recipes to the ones created by the authenticated user
        return Recipe.objects.filter(user=self.request.user)

# Pagination
class RecipePagination(PageNumberPagination):
    page_size = 10

# Search by Category
class RecipeByCategoryView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        category_name = self.kwargs['category_name']
        return Recipe.objects.filter(category__iexact=category_name)

# Search by Ingredient
class RecipeByIngredientView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        ingredient_name = self.kwargs['ingredient_name']
        return Recipe.objects.filter(ingredients__icontains=ingredient_name)

# Search by Title
class RecipeSearchView(generics.ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        title = self.request.query_params.get('title', None)
        if title:
            # Debugging print
            print("Searching for title:", title)
            queryset = Recipe.objects.filter(title__icontains=title)
            print("Matching recipes:", queryset)
            if queryset.exists(): 
                 # Check if any match exists
                return queryset
        return Recipe.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"detail": "Recipe not found."}, status=404)
        return super().list(request, *args, **kwargs)


# Filter by Preparation and Cooking Time
class RecipeFilterView(generics.ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        preparation_time = self.request.query_params.get('preparation_time', None)
        cooking_time = self.request.query_params.get('cooking_time', None)

        if preparation_time is not None:
            queryset = queryset.filter(preparation_time=preparation_time)
        
        if cooking_time is not None:
            queryset = queryset.filter(cooking_time=cooking_time)

        return queryset
    
class AddToFavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({"detail": "Recipe not found."}, status=stat.HTTP_404_NOT_FOUND)

        # Ensure favorite_recipes exists on user
        if not hasattr(request.user, 'favorite_recipes'):
            return Response({"detail": "User model does not have a 'favorite_recipes' attribute."}, status=status.HTTP_400_BAD_REQUEST)

        # Add recipe to user's favorites
        request.user.favorite_recipes.add(recipe)
        return Response({"message": "Recipe added to favorites"}, status=stat.HTTP_201_CREATED)


class AddFavoriteRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        try:
            # Fetch the recipe by ID
            recipe = Recipe.objects.get(id=recipe_id)
            
            # Check if the recipe is already in the user's favorites
            if request.user.favorite_recipes.filter(id=recipe_id).exists():
                return Response({"message": "Recipe already in favorites"}, status=status.HTTP_400_BAD_REQUEST)

            # Add the recipe to the user's favorites
            request.user.favorite_recipes.add(recipe)
            return Response({"message": "Recipe added to favorites"}, status=status.HTTP_201_CREATED)

        except Recipe.DoesNotExist:
            return Response({"message": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)
        
class RecipeReviewListView(APIView):
    def get(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            reviews = recipe.reviews.all()  # Fetch all reviews related to the recipe

            # Serialize the reviews
            review_data = []
            for review in reviews:
                review_data.append({
                    'user': review.user.username,  # You can include more details about the user if needed
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at
                })

            return Response(review_data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({"message": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

class FavoriteRecipesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorite_recipes = request.user.favorite_recipes.all()
        serializer = RecipeSerializer(favorite_recipes, many=True)
        return Response(serializer.data) 
    
class RecipeReviewView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs['recipe_id']
        serializer.save(recipe_id=recipe_id, user=self.request.user) 

class FavoriteRecipesListView(generics.ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return self.request.user.favorites.all()