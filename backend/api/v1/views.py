from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from io import BytesIO

from foodgram_backend.settings import FILE_NAME
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    RecipeSimpleSerializer,
    SubscribeCreateSerializer,
    SubscribeSerializer,
    TagSerializer,
)


pdfmetrics.registerFont(TTFont('PFDFont', 'pfd.ttf'))


class UserViewSet(BaseUserViewSet):
    """Вьюсет кастомного пользователя, унаследованный от djoser."""
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()


class SubscribeViewSet(views.APIView):
    """Cоздание и удаление подписки."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        serializer = SubscribeCreateSerializer(
            data={'user': request.user.id, 'author': user_id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author_id=user_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscribe = get_object_or_404(
            Subscribe, user=request.user, author=user_id
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Просмотр подписок."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Добавление и удаление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = Favorites.objects.filter(
            user=request.user, recipe=recipe
        )
        if request.method == 'POST':
            if favorites.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSimpleSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not favorites.exists():
                return Response(
                    {'errors': 'Рецепта нет в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorites.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_list = (
            ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        )
        if request.method == 'POST':
            if shopping_list.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSimpleSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not shopping_list.exists():
                return Response(
                    {'errors': 'Рецепта нет в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart_pdf(self, request):
        """Скачивает список покупок в формате pdf."""
        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
        ).annotate(amount_sum=Sum('amount'))
        shopping_list = [
            {
                'name': ingredient['ingredient__name'],
                'measurement_unit': ingredient['ingredient__measurement_unit'],
                'amount': ingredient['amount_sum']
            } for ingredient in ingredients
        ]
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont('PFDFont', 12)
        y = 750
        for idx, ingredient in enumerate(shopping_list, start=1):
            line = (
                f"{idx}. {ingredient['name']} "
                f"({ingredient['measurement_unit']}) - {ingredient['amount']}"
            )
            p.drawString(100, y, line)
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={FILE_NAME}'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
