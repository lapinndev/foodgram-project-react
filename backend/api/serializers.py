import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from users.models import CustomUser, FollowUser
from tag.models import Tag
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from favorite.models import Favorite
from shoppingcart.models import ShoppingCart


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        user = request.user
        return FollowUser.objects.filter(user=user, author=obj).exists()


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        old_password = value
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError(
                {'old_password': 'Неправильный пароль.'}
            )
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        try:
            validate_password(new_password)
        except Exception as e:
            raise serializers.ValidationError(
                {'new_password': list(e)})
        return data

    def update(self, instance, validated_data):
        if (validated_data['old_password']
                == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class SubscriptionsSerializer(CustomUserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count',)
        read_only_fields = ('email', 'username', 'last_name', 'first_name',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes,
                                      many=True,
                                      read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement = serializers.ReadOnlyField(
        source='ingredient.measurement'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'amount', 'measurement')
        read_only_fields = ('name', 'measurement')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.ingredient.id
        return data


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientRecipeSerializer(
        source='recipeingredients', many=True
    )
    is_favorited = SerializerMethodField(read_only=True)
    in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'tags',
            'text',
            'image',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user_id=user.id,
                                           recipe=obj).exists()
        return False

    def get_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user_id=user.id,
                                               recipe=obj).exists()
        return False


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        required=False,
        allow_null=True
    )
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeCreateSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'tags',
            'author',
            'text',
            'image',
            'ingredients',
            'cooking_time',
        )

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError({'tags': 'Нужно добавить тег!'})
        tags = []
        for i in tags:
            if i['id'] in tags:
                raise ValidationError(
                    {'tags': 'Тег уже есть в списке'}
                )
            tags.append(i)
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Нужно добавить ингредиент!'}
            )
        ingredients = []
        for i in ingredients:
            if i in ingredients:
                raise ValidationError(
                    {'ingredients': 'Ингредиенты не могут повторяться'}
                )
            ingredients.append(i)
            if int(i['amount']) < 1:
                raise ValidationError(
                    {
                        'amount': (
                            'Количество ингредиентов не может быть меньше 1'
                        )
                    }
                )
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise ValidationError(
                {
                    'cooking_time': (
                        'Время приготовления рецепта не может меньше 1'
                    )
                }
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        name = validated_data.get('name')
        if Recipe.objects.filter(name=name).exists():
            raise ValidationError({'name': 'Название рецепта уже существует'})
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)

        name = validated_data.get('name')
        if Recipe.objects.filter(name=name).exists():
            raise ValidationError({'name': 'Название рецепта уже существует'})

        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient['amount']
                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient.get('id'),
                    defaults={'amount': amount},
                )
        return super().update(instance, validated_data)


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'
