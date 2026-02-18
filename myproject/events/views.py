import json
from decimal import Decimal

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from accounts.decorators import admin_required
from .forms import EventForm, BookingForm, ReviewForm, ContactForm
from .models import Category, Event, Booking, Payment, Review, FAQ


# ─── Home ─────────────────────────────────────────────────────────────────────

def home(request):
    featured_events = Event.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    return render(request, "events/home.html", {
        "featured_events": featured_events,
        "categories": categories,
    })


# ─── Event Browsing ──────────────────────────────────────────────────────────

def event_list(request):
    events = Event.objects.filter(is_active=True)

    query = request.GET.get("q")
    if query:
        events = events.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )

    category = request.GET.get("category")
    if category:
        events = events.filter(category__slug=category)

    location = request.GET.get("location")
    if location:
        events = events.filter(location__icontains=location)

    date = request.GET.get("date")
    if date:
        events = events.filter(date=date)

    price_range = request.GET.get("price_range")
    if price_range:
        if price_range == "0-1000":
            events = events.filter(price__lte=1000)
        elif price_range == "1000-5000":
            events = events.filter(price__gte=1000, price__lte=5000)
        elif price_range == "5000-10000":
            events = events.filter(price__gte=5000, price__lte=10000)
        elif price_range == "10000+":
            events = events.filter(price__gte=10000)

    return render(request, "events/event_list.html", {
        "events": events,
        "categories": Category.objects.all(),
    })


def events_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    events = Event.objects.filter(category=category, is_active=True)
    return render(request, "events/event_list.html", {
        "events": events,
        "categories": Category.objects.all(),
        "current_category": category,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    reviews = event.reviews.select_related("user").all()
    can_review = False
    if request.user.is_authenticated:
        has_booking = Booking.objects.filter(
            user=request.user, event=event, status="confirmed"
        ).exists()
        has_reviewed = Review.objects.filter(
            user=request.user, event=event
        ).exists()
        can_review = has_booking and not has_reviewed
    return render(request, "events/event_detail.html", {
        "event": event,
        "reviews": reviews,
        "can_review": can_review,
    })


# ─── Event CRUD (Admin) ─────────────────────────────────────────────────────

@admin_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect("events:event_detail", slug=event.slug)
    else:
        form = EventForm()
    return render(request, "events/event_create.html", {"form": form})


@admin_required
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect("events:event_detail", slug=event.slug)
    else:
        form = EventForm(instance=event)
    return render(request, "events/event_edit.html", {"form": form, "event": event})


@admin_required
def event_delete(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect("events:event_list")
    return render(request, "events/event_delete_confirm.html", {"event": event})


# ─── Booking ─────────────────────────────────────────────────────────────────

@login_required
def booking_create(request, slug):
    event = get_object_or_404(Event, slug=slug, is_active=True)

    if event.is_past:
        messages.error(request, "This event has already passed.")
        return redirect("events:event_detail", slug=slug)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            guests = form.cleaned_data["number_of_guests"]
            if guests > event.available_slots:
                messages.error(
                    request,
                    f"Only {event.available_slots} slots available."
                )
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.event = event
                booking.total_amount = event.price * guests
                booking.save()
                messages.success(request, "Booking created! Please proceed to payment.")
                return redirect("events:payment_checkout", booking_id=booking.pk)
    else:
        form = BookingForm()
    return render(request, "events/booking_form.html", {
        "form": form,
        "event": event,
    })


@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related("event", "payment")
    return render(request, "events/booking_history.html", {"bookings": bookings})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, "events/booking_confirmation.html", {"booking": booking})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == "pending":
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "This booking cannot be cancelled.")
    return redirect("events:booking_history")


# ─── Payment ─────────────────────────────────────────────────────────────────

def _razorpay_configured():
    """Check if real Razorpay keys are set (not placeholders)."""
    return (
        settings.RAZORPAY_KEY_ID
        and settings.RAZORPAY_KEY_SECRET
        and "XXXX" not in settings.RAZORPAY_KEY_ID
        and "XXXX" not in settings.RAZORPAY_KEY_SECRET
    )


@login_required
def payment_checkout(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status != "pending":
        messages.error(request, "This booking cannot be paid for.")
        return redirect("events:booking_history")

    # Demo mode: confirm booking directly if Razorpay not configured
    if not _razorpay_configured():
        payment, _ = Payment.objects.get_or_create(
            booking=booking,
            defaults={"amount": booking.total_amount},
        )
        payment.razorpay_payment_id = "demo_payment"
        payment.status = "success"
        payment.save()
        booking.status = "confirmed"
        booking.save()
        _send_booking_confirmation(booking)
        messages.success(request, "Booking confirmed! (Demo mode - Razorpay not configured)")
        return redirect("events:payment_success", booking_id=booking.pk)

    # Real Razorpay flow
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_in_paise = int(booking.total_amount * 100)

    razorpay_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1",
    })

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={"amount": booking.total_amount},
    )
    payment.razorpay_order_id = razorpay_order["id"]
    payment.save()

    return render(request, "events/payment_checkout.html", {
        "booking": booking,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount_in_paise,
        "currency": "INR",
    })


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            "razorpay_order_id": request.POST.get("razorpay_order_id"),
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_signature": request.POST.get("razorpay_signature"),
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(
                razorpay_order_id=params_dict["razorpay_order_id"]
            )
            payment.razorpay_payment_id = params_dict["razorpay_payment_id"]
            payment.razorpay_signature = params_dict["razorpay_signature"]
            payment.status = "success"
            payment.save()

            payment.booking.status = "confirmed"
            payment.booking.save()

            # Send confirmation emails
            _send_booking_confirmation(payment.booking)

            return redirect("events:payment_success", booking_id=payment.booking.pk)
        except Exception:
            if params_dict["razorpay_order_id"]:
                try:
                    payment = Payment.objects.get(
                        razorpay_order_id=params_dict["razorpay_order_id"]
                    )
                    payment.status = "failed"
                    payment.save()
                    return redirect("events:payment_failure", booking_id=payment.booking.pk)
                except Payment.DoesNotExist:
                    pass
    return redirect("events:home")


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, "events/payment_success.html", {"booking": booking})


@login_required
def payment_failure(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, "events/payment_failure.html", {"booking": booking})


# ─── Reviews ─────────────────────────────────────────────────────────────────

@login_required
def add_review(request, slug):
    event = get_object_or_404(Event, slug=slug)

    has_booking = Booking.objects.filter(
        user=request.user, event=event, status="confirmed"
    ).exists()
    if not has_booking:
        messages.error(request, "You can only review events you have attended.")
        return redirect("events:event_detail", slug=slug)

    if Review.objects.filter(user=request.user, event=event).exists():
        messages.error(request, "You have already reviewed this event.")
        return redirect("events:event_detail", slug=slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.event = event
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect("events:event_detail", slug=slug)
    else:
        form = ReviewForm()
    return render(request, "events/review_form.html", {"form": form, "event": event})


# ─── Admin Dashboard ─────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status="success").aggregate(
        total=Sum("amount")
    )["total"] or 0
    recent_bookings = (
        Booking.objects.select_related("user", "event")
        .order_by("-created_at")[:10]
    )

    monthly_revenue_qs = list(
        Payment.objects.filter(status="success")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )[-6:]
    # Serialize for Chart.js (datetime/Decimal not JSON-safe)
    monthly_revenue = json.dumps([
        {"month": item["month"].strftime("%Y-%m-%d"), "total": float(item["total"])}
        for item in monthly_revenue_qs
    ])

    category_counts_qs = list(
        Event.objects.values("category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    category_counts = json.dumps([
        {"category__name": item["category__name"] or "Uncategorized", "count": item["count"]}
        for item in category_counts_qs
    ])

    return render(request, "events/admin_dashboard.html", {
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "recent_bookings": recent_bookings,
        "monthly_revenue": monthly_revenue,
        "category_counts": category_counts,
    })


# ─── Contact & Support ──────────────────────────────────────────────────────

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect("events:contact_success")
    else:
        form = ContactForm()
    return render(request, "events/contact.html", {"form": form})


def contact_success(request):
    return render(request, "events/contact_success.html")


def faq(request):
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, "events/faq.html", {"faqs": faqs})


def about(request):
    return render(request, "events/about.html")


# ─── Email Helpers ───────────────────────────────────────────────────────────

def _send_booking_confirmation(booking):
    send_mail(
        subject=f"Booking Confirmed - {booking.event.title}",
        message=(
            f"Hi {booking.user.first_name},\n\n"
            f"Your booking for '{booking.event.title}' has been confirmed!\n\n"
            f"Booking Details:\n"
            f"- Event: {booking.event.title}\n"
            f"- Date: {booking.booking_date}\n"
            f"- Guests: {booking.number_of_guests}\n"
            f"- Total Amount: Rs.{booking.total_amount}\n\n"
            f"Thank you for using EventManager!"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.user.email],
    )
