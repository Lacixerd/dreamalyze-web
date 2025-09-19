from django.core.management.base import BaseCommand
from api.models import UserCredits

class Command(BaseCommand):
    help = "Renew credits on users' signup day each month"

    def handle(self, *args, **options):
        for credit in UserCredits.objects.filter(deleted_at__isnull=True):
            if credit.should_renew_today():
                credit.renew()
        self.stdout.write(self.style.SUCCESS("Credits renewed for today"))