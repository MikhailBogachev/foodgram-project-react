from django.contrib import admin

from .models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredients,
    FavoriteRecipe,
    ShoppingCart
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'hex_code', 'slug')
    list_editable = ('name', 'hex_code', 'slug')
    empty_value_display = '-пусто-'

class IngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 2
# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = (
#         'name', 'cooking_time', 'text', 
#         'tags', 'image', 'author'
#     )
#     list_editable = (
#         'name', 'cooking_time', 'text', 'tags',
#         'image', 'author'
#     )
#     readonly_fields = ('in_favorites',)
#     list_filter = ('name', 'author', 'tags')
#     empty_value_display = '-пусто-'

#     @admin.display(description='В избранном')
#     def in_favorites(self, obj):
#         return obj.favorite_recipe.count()
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    fields = (
        (
            "name",
            "cooking_time",
        ),
        (
            "author",
            "tags",
        ),
        ("text",),
        ("image",),
    )
    raw_id_fields = ("author",)
    search_fields = (
        "name",
        "author__username",
        "tags__name",
    )
    list_filter = ("name", "author__username", "tags__name")

    inlines = (IngredientInline,)
    save_on_top = True

@admin.register(RecipeIngredients)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')