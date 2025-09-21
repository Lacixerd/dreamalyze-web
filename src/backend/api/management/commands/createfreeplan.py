from typing import Any
from django.core.management.base import BaseCommand
from api.models import ProductPlan

class Command(BaseCommand):
    help = "Renew credits on users' signup day each month"

    def handle(self, *args, **options):
        ProductPlan.objects.create(plan='Free', plan_description="Blank Desc", lemon_id="blanck id", price=0, max_credit_amount=1)

        self.stdout.write(self.style.SUCCESS("Default free plan created"))