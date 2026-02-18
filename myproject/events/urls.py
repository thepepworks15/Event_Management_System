from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.event_list, name="event_list"),
    path("events/category/<slug:slug>/", views.events_by_category, name="events_by_category"),
    path("events/create/new/", views.event_create, name="event_create"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("events/<slug:slug>/edit/", views.event_edit, name="event_edit"),
    path("events/<slug:slug>/delete/", views.event_delete, name="event_delete"),
    path("events/<slug:slug>/book/", views.booking_create, name="booking_create"),
    path("events/<slug:slug>/review/", views.add_review, name="add_review"),
    path("bookings/", views.booking_history, name="booking_history"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
    path("payment/<int:booking_id>/checkout/", views.payment_checkout, name="payment_checkout"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
    path("payment/success/<int:booking_id>/", views.payment_success, name="payment_success"),
    path("payment/failure/<int:booking_id>/", views.payment_failure, name="payment_failure"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("contact/", views.contact, name="contact"),
    path("contact/success/", views.contact_success, name="contact_success"),
    path("faq/", views.faq, name="faq"),
    path("about/", views.about, name="about"),
]
