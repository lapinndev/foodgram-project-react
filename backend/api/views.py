from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Sum
from django_filters.rest_framework import DjangoFilterBackend


from .pagination import CustomPagination
from .serializers import (
    ChangePasswordSerializer,
    CustomUserSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    ShortRecipeSerializer
)
from .filters import RecipesFilterSet, IngredientFilter
from .permissions import AdminOrReadOnly, IsAuthorOrReadOnly
from users.models import CustomUser, FollowUser
from tag.models import Tag
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from shoppingcart.models import ShoppingCart
from favorite.models import Favorite


class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get'],
        pagination_class=None,
        permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Пароль успешно изменен!'},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)

        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            FollowUser.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                FollowUser, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    search_fields = ('^name',)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    search_fields = ('^name',)
    pagination_class = None
    filter_backends = (IngredientFilter, )


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilterSet
    filter_backends = (DjangoFilterBackend, )
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnly]
    add_serializer = ShortRecipeSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):

        if request.method == 'POST':
            return self.add_or_remove(Favorite, request.user, pk, add=True)
        else:
            return self.add_or_remove(Favorite, request.user, pk, add=False)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):

        if request.method == 'POST':
            return self.add_or_remove(ShoppingCart, request.user,
                                      pk, add=True)

        else:
            return self.add_or_remove(ShoppingCart, request.user,
                                      pk, add=False)

    def add_or_remove(self, model, user, pk, add=False):
        if add:
            if model.objects.filter(user=user, recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
        else:
            obj = model.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
            else:
                return Response({'errors': 'Рецепт уже удален!'},
                                status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED
                        if add else status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = self.get_shopping_cart_ingredients(user)
        result = self.format_ingredients_as_text(ingredients)

        headers = {
            'Content-Disposition': 'attachment; filename=shopping_cart.txt'
        }
        return HttpResponse(
            result, content_type='text/plain; charset=UTF-8', headers=headers
        )

    def get_shopping_cart_ingredients(self, user):
        shopping_cart_recipes = Recipe.objects.filter(shoppingcart__user=user)
        ingredients = (
            RecipeIngredients.objects.filter(recipe__in=shopping_cart_recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
        return ingredients

    def format_ingredients_as_text(self, ingredients):
        result = ''
        for i in ingredients:
            result += (
                f' {i["ingredient__name"]}-'
                f' {i["amount"]}-'
                f' {i["ingredient__measurement_unit"]}\n'
            )
        return result
