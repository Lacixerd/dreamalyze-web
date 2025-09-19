from typing import Any
from django.core.management.base import BaseCommand
from api.models import UserPlan

class Command(BaseCommand):
    help = "Renew credits on users' signup day each month"

    def handle(self, *args, **options):
        UserPlan.objects.create(plan='Free', max_credit_amount=1)

        self.stdout.write(self.style.SUCCESS("Default free plan created"))