from django.contrib import admin

from foodgram_backend.constants import MIN_RECIPE_ADMIN
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    min_num = MIN_RECIPE_ADMIN


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'name', 'tags__name')
    inlines = [
        RecipeIngredientsInline,
    ]

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = ' Добавлений рецепта в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredients)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
