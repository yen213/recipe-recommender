from django.urls import path

from .views import RecipesView, TagsView, IngredientsView

urlpatterns = [
    path('ingredients/', IngredientsView.as_view(), name='ingredients'),
    path('tags/', TagsView.as_view(), name='tags'),
    path('recipes/', RecipesView.as_view(), name='recipes-list'),
    path('recipes/ingredients/', RecipesView.as_view(action="recipes-ingredients"), name='recipes-ingredients'),
    path('recipes/tags/', RecipesView.as_view(action="recipes-tags"), name='recipes-tags'),
    path('recipes/ingredients-and-tags/', RecipesView.as_view(action="recipes-ingredients-and-tags"), name='recipes-ingredients-and-tags'),
]
