from django.contrib import admin
from .models import Category, Event, Booking, Payment, Review, ContactMessage, FAQ


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "location", "date", "price", "capacity", "is_active"]
    list_filter = ["category", "is_active", "date"]
    search_fields = ["title", "location"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "event", "number_of_guests", "total_amount", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__username", "event__title"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "booking", "amount", "status", "razorpay_payment_id", "created_at"]
    list_filter = ["status"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "event", "rating", "created_at"]
    list_filter = ["rating"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "is_read", "created_at"]
    list_filter = ["is_read"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_filter = ["is_active"]
    list_editable = ["order", "is_active"]
