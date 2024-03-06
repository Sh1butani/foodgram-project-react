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

from foodgram_backend.constants import FILE_NAME
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
    SubscribeCreateSerializer,
    SubscribeSerializer,
    TagSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
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
        author = get_object_or_404(User, id=user_id)
        serializer = SubscribeCreateSerializer(
            data={'user': request.user.id, 'author': user_id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        deleted_subscribe, _ = Subscribe.objects.filter(
            user=request.user, author=user
        ).delete()
        if not deleted_subscribe:
            return Response(
                {'errors': 'Такой подписки не существует!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Просмотр подписок."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(subscribing__user=self.request.user)


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
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Добавление и удаление рецепта в избранное."""
        serializer = FavoriteSerializer(
            data={'user': request.user.pk, 'recipe': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        deleted_favorites, _ = Favorites.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted_favorites:
            return Response(
                {'errors': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецепта в список покупок."""
        serializer = ShoppingCartSerializer(
            data={'user': request.user.pk, 'recipe': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        deleted_shopping_list, _ = (
            ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        ).delete()
        if not deleted_shopping_list:
            return Response(
                {'errors': 'Рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
