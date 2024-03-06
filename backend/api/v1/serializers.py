from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend.constants import MIN_COOKING_TIME
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and Subscribe.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


class RecipeSimpleSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов без ингридиентов
    для отображения в подписках, списках покупок и в избранном."""
    name = serializers.CharField()
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    """Сериализатор для подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                try:
                    recipes = recipes[:int(recipes_limit)]
                except (TypeError, ValueError):
                    pass
        return RecipeSimpleSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""
    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author',),
                message='Вы уже подписаны на данного пользователя!'
            ),
        ]

    def validate(self, value):
        if value['author'] == value['user']:
            raise serializers.ValidationError(
                {'errors': 'Вы не можете подписаться на самого себя!'}
            )
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance.author, context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""
    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, value):
        if Favorites.objects.filter(
            user=value['user'], recipe=value['recipe']
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в избранное!'}
            )
        return value

    def to_representation(self, instance):
        return FavoriteAndShoppingCartResponseSerializer(instance).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, value):
        if ShoppingCart.objects.filter(
            user=value['user'], recipe=value['recipe']
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в список покупок!'}
            )
        return value

    def to_representation(self, instance):
        return FavoriteAndShoppingCartResponseSerializer(instance).data


class FavoriteAndShoppingCartResponseSerializer(serializers.Serializer):
    """Сериализатор для выдачи данных для избранного и списка покупок."""

    def to_representation(self, instance):
        return RecipeSimpleSerializer(instance.recipe).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredients."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'tags', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and Favorites.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredients_list = [
            RecipeIngredients(
                recipe=recipe, ingredient=ingredient['id'], amount=amount
            )
            for ingredient in ingredients
            for amount in [ingredient['amount']]
        ]
        RecipeIngredients.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        RecipeIngredients.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance).data

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Обязательное поле!'}
            )
        ingredients_id = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты должны быть уникальными!'}
            )

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Обязательное поле!'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги должны быть уникальными!'}
            )

        return attrs

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                {'image': 'Обязательное поле!'}
            )
        return value
