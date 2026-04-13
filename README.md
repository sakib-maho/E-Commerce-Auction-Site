# E-Commerce Auction Site

<!-- BrandCloud:readme-standard -->
[![Maintained](https://img.shields.io/badge/Maintained-yes-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Showcase](https://img.shields.io/badge/Portfolio-Showcase-blue.svg)](#)

_Part of the `sakib-maho` project showcase series with consistent documentation and quality standards._

A complete Django web application for auction-style e-commerce listings.

This project now includes authentication, listing creation, bidding, comments, watchlist management, and category browsing.

## Features

- User registration and login/logout
- Create auction listings with title, description, image URL, and category
- Place bids with validation (must be higher than current price)
- Comment on listings
- Add or remove listings from personal watchlist
- Close auction as the listing owner
- Browse listings by categories
- Basic admin panel for managing auction data

## Tech Stack

- Python 3
- Django 5
- SQLite (default for local development)
- Bootstrap 5

## Project Structure

```text
.
├── manage.py
├── requirements.txt
├── commerce/              # Django project settings and root urls
└── auctions/              # App (models, views, routes, templates, static)
```

## Quick Start

```bash
git clone https://github.com/sakib-maho/E-Commerce-Auction-Site.git
cd E-Commerce-Auction-Site
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Main Routes

- `/` - active listings
- `/listing/create` - create new listing
- `/listing/<id>` - listing details and bidding
- `/watchlist` - current user watchlist
- `/categories` - category list
- `/admin/` - Django admin

## Notes

- This project uses SQLite for local development out of the box.
- `db.sqlite3` is ignored by git.
- For production deployment, set secure Django settings and a production database.

## License

MIT License - see [LICENSE](LICENSE).
