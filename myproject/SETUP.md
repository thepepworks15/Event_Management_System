# Setup & Execution Steps

## Prerequisites

- Python 3.10 or higher
- MySQL Server
- pip (Python package manager)

## Step 1: Clone / Navigate to Project

```bash
cd "D:\Event Management system"
```

## Step 2: Create Virtual Environment (if not already created)

```bash
python -m venv ems
```

## Step 3: Activate Virtual Environment

**Windows (Command Prompt):**
```bash
ems\Scripts\activate
```

**Windows (PowerShell):**
```bash
ems\Scripts\Activate.ps1
```

**Windows (Git Bash):**
```bash
source ems/Scripts/activate
```

## Step 4: Install Dependencies

```bash
pip install django==5.2.9 mysqlclient django-crispy-forms crispy-bootstrap5 razorpay Pillow
```

## Step 5: Create MySQL Database

Open MySQL and run:
```sql
CREATE DATABASE event_management_db;
```

## Step 6: Configure Database Password

Open `myproject/myproject/settings.py` and update line 66:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "event_management_db",
        "USER": "root",
        "PASSWORD": "your-mysql-password",  # <-- Update this
        "HOST": "localhost",
        "PORT": "3306",
    }
}
```

## Step 7: Run Migrations

```bash
cd myproject
python manage.py makemigrations accounts events
python manage.py migrate
```

## Step 8: Seed Categories

```bash
python manage.py seed_categories
```

Output: `Successfully seeded 5 categories`

## Step 9: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

## Step 10: Run Development Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000/**

## Optional Configuration

### Enable Gmail SMTP (for real emails)

In `myproject/settings.py`, comment out the console backend and uncomment the Gmail block:

```python
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"
DEFAULT_FROM_EMAIL = "your-email@gmail.com"
```

**To get a Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate a new password for "Mail"

### Enable Razorpay Payments

In `myproject/settings.py`, replace the placeholder keys:

```python
RAZORPAY_KEY_ID = "rzp_test_YOUR_KEY_ID"
RAZORPAY_KEY_SECRET = "YOUR_KEY_SECRET"
```

**To get Razorpay Test Keys:**
1. Sign up at https://dashboard.razorpay.com/signup
2. Go to Settings > API Keys > Generate Test Key
3. Copy Key ID and Key Secret

Without real Razorpay keys, the system runs in **demo mode** (bookings are confirmed directly without payment).

## Quick Test Guide

### As a Regular User:
1. Register at `/accounts/register/`
2. Login at `/accounts/login/`
3. Browse events at `/events/`
4. Use filters (category, location, date, price)
5. Click "Book Now" on any event
6. Fill booking form (date, guests)
7. Complete payment (demo mode auto-confirms)
8. View booking history at `/bookings/`
9. Leave a review on attended events

### As an Admin:
1. Login with admin credentials
2. Visit Dashboard at `/dashboard/`
3. Create events at `/events/create/new/`
4. Edit/delete events from event detail pages
5. Manage all data at `/admin/`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `mysqlclient` install fails | Try: `pip install mysqlclient` from https://www.lfd.uci.edu/~gohlke/pythonlibs/ |
| MySQL access denied | Check password in `settings.py` matches your MySQL root password |
| Static files not loading | Run `python manage.py collectstatic` |
| Media uploads not showing | Ensure `media/` directory exists with `events/` and `profiles/` subdirectories |
| Email not working | Check terminal output (console backend) or verify Gmail app password |
| Payment error | Ensure Razorpay keys are valid, or use demo mode (placeholder keys) |
