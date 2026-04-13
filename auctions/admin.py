from django.contrib import admin

from .models import Bid, Category, Comment, Listing


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "current_price", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("title", "description")


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "bidder", "amount", "created_at")
    list_filter = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "author", "created_at")
    list_filter = ("created_at",)
