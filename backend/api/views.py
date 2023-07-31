from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Sum


from .pagination import CustomPagination
from .serializers import (
    ChangePasswordSerializer,
    CustomUserSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    RecipeCreateSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer
)
from .permissions import AdminOrReadOnly, IsAuthorOrReadOnly
from users.models import CustomUser, FollowUser
#from tag.models import Tag
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from shoppingcart.models import ShoppingCart
from favorite.models import Favorite


class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
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
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(subscriber__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)

        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Подписка на самого себя запрещена'
                }, status=status.HTTP_400_BAD_REQUEST)
            if FollowUser.objects.filter(user=user, author=author).exists():
                return Response({
                    'errors': 'Вы уже подписаны на данного пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            follow = FollowUser.objects.create(user=user, author=author)
            serializer = SubscriptionsSerializer(follow, context={
                'request': request
            })
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            the_subscribe = get_object_or_404(FollowUser,
                                              user=user,
                                              author=author)
            the_subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

#    queryset = Tag.objects.all()
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


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.prefetch_related('author', 'ingredients', 'tags')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = self.get_object()

        if request.method == "POST":
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(recipe.favorite, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        deleted = get_object_or_404(Favorite, user=request.user, recipe=recipe)
        deleted.delete()
        return Response(
            {"message": "Рецепт успешно удален из избранного"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        deleted = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        )
        deleted.delete()
        return Response(
            {"message": "Рецепт успешно удален из списка покупок"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_recipes = Recipe.objects.filter(shoppingcart__user=user)
        ingredients = (
            RecipeIngredients.objects.filter(recipe__in=shopping_cart_recipes)
            .values('ingredient__name', 'ingredient__measurement')
            .annotate(amount=Sum('amount'))
        )
        result = ''
        for i in ingredients:
            result += (
                f' Name : {i["ingredient__name"]}\n'
                f' Amount : {i["amount"]}\n'
                f' Measurement: {i["ingredient__measurement"]}\n'
            )
        headers = {
            'Content-Disposition': 'attachment; filename=shopping_cart.txt'
        }
        return HttpResponse(
            result, content_type='text/plain; charset=UTF-8', headers=headers
        )
