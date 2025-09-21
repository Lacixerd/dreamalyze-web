from django.core.management.base import BaseCommand
from api.models import Subscription

class Command(BaseCommand):
    help = "Updates subscription status."

    def handle(self, *args, **options):
        pass
        # self.stdout.write(self.style.SUCCESS("Credits renewed for today"))