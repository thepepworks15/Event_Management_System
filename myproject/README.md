# EventManager - Event Management System

A full-featured Event Management System built with Django 5.2.9, MySQL, and Bootstrap 5.

## Features

### 1. User Authentication
- User registration with email verification
- Login / Logout
- Forgot password (email-based reset)
- Profile page (edit profile, change password, profile picture)

### 2. Event Management
- Browse and search events
- Filter by category, location, date, and price range
- Admin: Create, edit, delete events
- Event image uploads

### 3. Event Categories
- Wedding
- Birthday
- Corporate Meeting
- Festival
- Private Party

### 4. Event Booking System
- Book events with date and guest selection
- Booking confirmation page
- Booking history
- Cancel pending bookings

### 5. Payment Integration
- Razorpay payment gateway
- Online payment (cards, UPI, net banking)
- Payment success/failure handling
- Transaction ID storage
- Demo mode when Razorpay keys not configured

### 6. Admin Dashboard
- Total users, bookings, and revenue stats
- Monthly revenue bar chart (Chart.js)
- Category distribution pie chart
- Recent bookings table

### 7. Reviews & Ratings
- 1-5 star ratings for attended events
- User comments/reviews
- Average rating display on event pages

### 8. Notifications
- Booking confirmation email
- Payment confirmation email
- Email verification on registration

### 9. Contact & Support
- Contact form
- FAQ section (accordion style)
- About page

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Backend language |
| Django 5.2.9 | Web framework |
| MySQL | Database |
| Bootstrap 5 | Frontend CSS framework |
| Bootstrap Icons | Icon library |
| Razorpay | Payment gateway |
| Chart.js | Dashboard charts |
| django-crispy-forms | Form rendering |
| Pillow | Image handling |

## Project Structure

```
myproject/
├── manage.py
├── myproject/              # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/               # Authentication & Profiles
│   ├── models.py           # UserProfile model
│   ├── views.py            # Auth views (register, login, profile, etc.)
│   ├── forms.py            # Registration, login, profile forms
│   ├── urls.py
│   ├── decorators.py       # admin_required decorator
│   ├── admin.py
│   └── templates/accounts/ # 11 templates
├── events/                 # Events, Bookings, Payments, Reviews
│   ├── models.py           # Category, Event, Booking, Payment, Review, FAQ, ContactMessage
│   ├── views.py            # 20+ views
│   ├── forms.py            # Event, booking, review, contact forms
│   ├── urls.py             # 21 URL patterns
│   ├── admin.py            # Admin registration for all models
│   ├── context_processors.py
│   ├── management/commands/seed_categories.py
│   └── templates/events/   # 18 templates
├── templates/              # Project-level templates
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   └── messages.html
├── static/                 # Static files
│   ├── css/style.css
│   └── js/main.js
└── media/                  # User uploads (events/, profiles/)
```

## Database Schema

| Table | Description |
|-------|-------------|
| auth_user | Django built-in user (username, email, password, is_staff) |
| accounts_userprofile | Extended profile (phone, address, picture, email_verified) |
| events_category | Event categories (Wedding, Birthday, etc.) |
| events_event | Events (title, description, location, date, price, capacity) |
| events_booking | Bookings (user, event, guests, amount, status) |
| events_payment | Payments (Razorpay IDs, amount, status) |
| events_review | Reviews (user, event, rating 1-5, comment) |
| events_contactmessage | Contact form submissions |
| events_faq | Frequently asked questions |

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

## URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/events/` | Browse all events |
| `/events/category/<slug>/` | Events by category |
| `/events/<slug>/` | Event detail page |
| `/events/create/new/` | Create event (admin) |
| `/bookings/` | Booking history |
| `/dashboard/` | Admin dashboard |
| `/accounts/register/` | User registration |
| `/accounts/login/` | User login |
| `/accounts/profile/` | User profile |
| `/contact/` | Contact form |
| `/faq/` | FAQ page |
| `/about/` | About page |
| `/admin/` | Django admin panel |
