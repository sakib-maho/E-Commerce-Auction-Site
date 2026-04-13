from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .models import Bid, Category, Comment, Listing


def index(request):
    listings = Listing.objects.filter(is_active=True).select_related("category", "seller")
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        return render(request, "auctions/login.html", {"message": "Invalid username or password."})

    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})
        login(request, user)
        return redirect("index")

    return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    categories = Category.objects.all().order_by("name")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image_url = request.POST.get("image_url", "").strip()
        category_name = request.POST.get("category", "").strip()

        try:
            starting_bid = Decimal(request.POST.get("starting_bid", "0"))
        except (InvalidOperation, TypeError):
            messages.error(request, "Starting bid must be a valid number.")
            return render(request, "auctions/create_listing.html", {"categories": categories})

        if not title:
            messages.error(request, "Title is required.")
            return render(request, "auctions/create_listing.html", {"categories": categories})
        if starting_bid <= 0:
            messages.error(request, "Starting bid must be greater than zero.")
            return render(request, "auctions/create_listing.html", {"categories": categories})

        category = None
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)

        listing = Listing.objects.create(
            seller=request.user,
            title=title,
            description=description,
            image_url=image_url,
            starting_bid=starting_bid,
            current_price=starting_bid,
            category=category,
        )
        messages.success(request, "Listing created successfully.")
        return redirect("listing_detail", listing_id=listing.id)

    return render(request, "auctions/create_listing.html", {"categories": categories})


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing.objects.select_related("seller", "category"), pk=listing_id)
    bids = listing.bids.select_related("bidder")
    comments = listing.comments.select_related("author")
    highest_bid = bids.first()

    is_watching = False
    if request.user.is_authenticated:
        is_watching = listing.watchers.filter(id=request.user.id).exists()

    context = {
        "listing": listing,
        "highest_bid": highest_bid,
        "comments": comments,
        "is_watching": is_watching,
    }
    return render(request, "auctions/listing_detail.html", context)


@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if not listing.is_active:
        messages.error(request, "This listing is closed.")
        return redirect("listing_detail", listing_id=listing.id)

    try:
        amount = Decimal(request.POST.get("amount", "0"))
    except (InvalidOperation, TypeError):
        messages.error(request, "Bid amount is invalid.")
        return redirect("listing_detail", listing_id=listing.id)

    if amount <= listing.current_price:
        messages.error(request, "Bid must be higher than current price.")
        return redirect("listing_detail", listing_id=listing.id)

    Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
    listing.current_price = amount
    listing.save(update_fields=["current_price", "updated_at"])
    messages.success(request, "Bid placed successfully.")
    return redirect("listing_detail", listing_id=listing.id)


@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    body = request.POST.get("body", "").strip()
    if body:
        Comment.objects.create(listing=listing, author=request.user, body=body)
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Comment cannot be empty.")
    return redirect("listing_detail", listing_id=listing.id)


@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.watchers.filter(id=request.user.id).exists():
        listing.watchers.remove(request.user)
        messages.info(request, "Removed from watchlist.")
    else:
        listing.watchers.add(request.user)
        messages.success(request, "Added to watchlist.")
    return redirect("listing_detail", listing_id=listing.id)


@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.seller != request.user:
        messages.error(request, "Only the seller can close this listing.")
        return redirect("listing_detail", listing_id=listing.id)

    listing.is_active = False
    listing.save(update_fields=["is_active", "updated_at"])
    messages.success(request, "Listing closed.")
    return redirect("listing_detail", listing_id=listing.id)


@login_required
def watchlist(request):
    listings = request.user.watched_listings.filter(is_active=True).select_related("category", "seller")
    return render(request, "auctions/watchlist.html", {"listings": listings})


def categories(request):
    all_categories = Category.objects.all().order_by("name")
    return render(request, "auctions/categories.html", {"categories": all_categories})


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = category.listings.filter(is_active=True).select_related("seller")
    return render(
        request,
        "auctions/category_listings.html",
        {"category": category, "listings": listings},
    )
