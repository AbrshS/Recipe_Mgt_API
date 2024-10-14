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
    pagination_class = RecipePagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title = self.request.query_params.get('title', None)
        if title:
            return Recipe.objects.filter(title__icontains=title)
        return Recipe.objects.all()

# Filter by Preparation and Cooking Time
class RecipeFilterView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        prep_time = self.request.query_params.get('prep_time', None)
        cook_time = self.request.query_params.get('cook_time', None)
        queryset = Recipe.objects.all()
        if prep_time:
            queryset = queryset.filter(prep_time__lte=prep_time)
        if cook_time:
            queryset = queryset.filter(cook_time__lte=cook_time)
        return queryset
    
class AddToFavoritesView(APIView):
    def post(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        request.user.favorites.add(recipe)
        return Response({"message": "Recipe added to favorites"}, status=status.HTTP_200_OK)

class AddFavoriteRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        if request.user.favorite_recipes.filter(id=recipe_id).exists():
            return Response({"message": "Already in favorites"}, status=status.HTTP_400_BAD_REQUEST)
        request.user.favorite_recipes.add(recipe)
        return Response({"message": "Recipe added to favorites"}, status=status.HTTP_201_CREATED)


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