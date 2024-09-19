from rest_framework import serializers
from .models import Recipe, Tag, Ingredient

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag_name']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'ingredient_name']

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, source='tags.all')
    ingredients = IngredientSerializer(many=True, source='ingredients.all')

    class Meta:
        model = Recipe
        fields = '__all__'
