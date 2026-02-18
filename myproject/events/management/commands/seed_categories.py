from django.core.management.base import BaseCommand
from events.models import Category


class Command(BaseCommand):
    help = "Seed the database with initial event categories"

    def handle(self, *args, **options):
        categories = [
            {"name": "Wedding", "slug": "wedding", "description": "Wedding ceremonies and receptions", "icon": "bi-heart"},
            {"name": "Birthday", "slug": "birthday", "description": "Birthday celebrations and parties", "icon": "bi-cake2"},
            {"name": "Corporate Meeting", "slug": "corporate-meeting", "description": "Business meetings and conferences", "icon": "bi-briefcase"},
            {"name": "Festival", "slug": "festival", "description": "Cultural and seasonal festivals", "icon": "bi-stars"},
            {"name": "Private Party", "slug": "private-party", "description": "Private gatherings and parties", "icon": "bi-music-note-beamed"},
        ]
        for cat_data in categories:
            Category.objects.get_or_create(slug=cat_data["slug"], defaults=cat_data)
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(categories)} categories"))
