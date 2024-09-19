from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

import json
import math

from .models import Recipe, Ingredient, Tag, RecipeIngredient, RecipeTag
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer

# Page size for each paginated result
PAGE_SIZE = 100

# Helper method to build the response object of a successful HTTP request
def buildResponseObj(data, msg):
    return {
        "status": "success",
        "code": 200,
        "message": msg,
        "data": data.get("results"),
        "meta": {
            "total": data.get("count"),
            "pages": math.ceil(data.get("count") / PAGE_SIZE),
        },
        "links": {
            "next": data.get("next"),
            "previous": data.get("previous")
            },
    }

# Helper method to build the response object of a successful HTTP request
# Method used for response objects which don't need meta data information
def buildSimpleResponseObj(data, msg):
    return {
        "status": "success",
        "code": 200,
        "message": msg,
        "data": data,
    }

# Helper method to build response object of an unsuccessful HTTP request     
def buildErrorResponseObj(code, msg):
    return {
            "status": "error",
            "code": code,
            "message": msg
    }

@method_decorator(csrf_exempt, name='dispatch')
class IngredientsView(View):
    # Returns all Ingredients from the DB
    def getAllIngredients(request):
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        
        return serializer.data
    
    # Get request returning all ingredients for all recipes
    def get(self, request):
        try:
            response = buildSimpleResponseObj(self.getAllIngredients(), 
                                            "Successfully retrieved all ingredients")
            
            return JsonResponse(response, status=200)
        
        except Exception as e:
            return JsonResponse(buildErrorResponseObj(500, str(e)), status=500)

@method_decorator(csrf_exempt, name='dispatch')
class TagsView(View):
    # Returns all Tags from the DB
    def getAllTags(request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        
        return serializer.data
    
    # Get request returning all tags for all recipes
    def get(self, request):
        try:
            response = buildSimpleResponseObj(self.getAllTags(), 
                                            "Successfully retrieved all tags")
            
            return JsonResponse(response, status=200)
        
        except Exception as e:
            return JsonResponse(buildErrorResponseObj(500, str(e)), status=500)

@method_decorator(csrf_exempt, name='dispatch') 
class RecipesView(View):
    action = None
    
    # Route post requests to appropriate methods based on action
    def post(self, request, *args, **kwargs):
        if self.action == 'recipes-ingredients':
            return self.postRecipesIngredients(request)
        elif self.action == 'recipes-tags':
            return self.postRecipesTags(request)
        elif self.action == 'recipes-ingredients-and-tags':
            return self.postRecipesIngredientsAndTags(request)
    
        return JsonResponse(buildErrorResponseObj(400, "Invalid action"), status=500)
            
    # Returns paginated result of all Recipes from the DB
    def getPaginatedRecipes(self, request, recipes):
        # Initialize the DRF paginator
        paginator = PageNumberPagination()
        paginator.page_size = PAGE_SIZE  
        
        # Wrap the WSGI request in a DRF Request object
        drf_request = Request(request)
        
        paginated_recipes = paginator.paginate_queryset(recipes, drf_request, view=self)
        serializer = RecipeSerializer(paginated_recipes, many=True)
        
        return paginator.get_paginated_response(serializer.data).data

    # Get request returning all recipes with pagination
    def get(self, request):
        try:
            recipes = Recipe.objects.all()
            data = self.getPaginatedRecipes(request, recipes)
            response = buildResponseObj(data, "Successfully retrieved recipes")
            
            return JsonResponse(response, status=200)
        
        except Exception as e:
            return JsonResponse(buildErrorResponseObj(500, str(e)), status=500)

    # Post request returning all recipes containing at least all the request body ingredients
    # Recipes can however contain other ingredients. Response is paginated
    def postRecipesIngredients(self, request):
        try:
            # Parse the request body to get the list of ingredients
            body = json.loads(request.body)
            ingredient_names = body.get('ingredients', [])
            
            ingredients = Ingredient.objects.filter(ingredient_name__in=ingredient_names)
            recipes = Recipe.objects.all().order_by('id')
            
            for ingredient in ingredients:
                recipes = recipes.filter(ingredients=ingredient)
            
            data = self.getPaginatedRecipes(request, recipes)
            
            return JsonResponse(buildResponseObj(
                                    data, 
                                    "Successfully retrieved recipes containing the ingredients"), 
                                status=200)
        
        except json.JSONDecodeError as e:
            return JsonResponse(buildErrorResponseObj(400, e.msg), status=400)
        
        except Exception as e:
            return JsonResponse(buildErrorResponseObj(500, str(e)), status=500)

    # Post request returning all recipes containing at least all the request body tags
    # Recipes can however contain other tags. Response is paginated
    def postRecipesTags(self, request):
        try:
            # Parse the request body to get the list of tags
            body = json.loads(request.body)
            tag_names = body.get('tags', [])
            
            tags = Tag.objects.filter(tag_name__in=tag_names)
            recipes = Recipe.objects.all().order_by('id')
            
            for tag in tags:
                recipes = recipes.filter(tags=tag)
            
            data = self.getPaginatedRecipes(request, recipes)
            
            return JsonResponse(buildResponseObj(
                                    data, 
                                    "Successfully retrieved recipes containing the tags"), 
                                status=200)
            
        except json.JSONDecodeError as e:
            return JsonResponse(buildErrorResponseObj(400, e.msg), status=400)
        
        except Exception as e:
            return JsonResponse(buildErrorResponseObj(500, str(e)), status=500)

    # Post request returning all recipes containing at least all the request body tags and ingredients
    # Recipes can however contain other tags and ingredients. Response is paginated
    def postRecipesIngredientsAndTags(self, request):
        try:
            # Parse the request body to get the list of tags and ingredients
            body = json.loads(request.body)
            tag_names = body.get('tags', [])
            ingredient_names = body.get('ingredients', [])
            
            tags = Tag.objects.filter(tag_name__in=tag_names)
            ingredients = Ingredient.objects.filter(ingredient_name__in=ingredient_names)
            recipes = Recipe.objects.all().order_by('id')
            
            for tag in tags:
                recipes = recipes.filter(tags=tag)
                
            for ingredient in ingredients:
                recipes = recipes.filter(ingredients=ingredient)
            
            data = self.getPaginatedRecipes(request, recipes)
            
            return JsonResponse(buildResponseObj(
                                    data, 
                                    "Successfully retrieved recipes containing the tags and ingredients"), 
                                status=200)
            
        except json.JSONDecodeError as e:
            return JsonResponse(buildErrorResponseObj(400, e.msg), status=400)
        
        except Exception as e:
            return JsonResponse(buildErrorResponseObj(500, str(e)), status=500)