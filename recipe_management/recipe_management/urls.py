from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import RegisterView  # Assuming you've created this view
from recipes.views import RecipeReviewView, RecipeByCategoryView, RecipeByIngredientView, RecipeReviewListView, RecipeSearchView, RecipeFilterView, AddFavoriteRecipeView, FavoriteRecipesListView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),  # User registration
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT login
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT token refresh
    
    # Recipe management endpoints
    path('api/', include('recipes.urls')),  # Include the recipes app's URLs
    
    # Search and filter endpoints
    path('api/recipes/category/<str:category_name>/', RecipeByCategoryView.as_view(), name='recipe-by-category'),
    path('api/recipes/ingredient/<str:ingredient_name>/', RecipeByIngredientView.as_view(), name='recipe-by-ingredient'),
    path('api/recipes/search/', RecipeSearchView.as_view(), name='recipe-search'),
    path('api/recipes/filter/', RecipeFilterView.as_view(), name='recipe-filter'),
    
    
    # path('api/<int:recipe_id>/reviews/', RecipeReviewView.as_view(), name='recipe-reviews'),
      path('api/recipes/<int:recipe_id>/reviews/', RecipeReviewView.as_view(), name='recipe-reviews'),
    
    path('api/recipes/<int:recipe_id>/reviews/', RecipeReviewListView.as_view(), name='recipe-reviews'),
    # Add DRF session login for testing
    path('api-auth/', include('rest_framework.urls')),
]   