from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import Product


class Command(BaseCommand):
    help = "Désactive les boosts expirés (boost_expires_at passé)."

    def handle(self, *args, **options):
        now = timezone.now()
        updated = Product.objects.filter(
            is_boosted=True,
            boost_expires_at__lte=now,
        ).update(is_boosted=False, boost_expires_at=None)

        self.stdout.write(
            self.style.SUCCESS(f"{updated} boost(s) expiré(s) désactivé(s).")
        )
