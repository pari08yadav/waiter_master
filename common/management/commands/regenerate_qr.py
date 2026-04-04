from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from common.model_helpers import attach_qr
from common.models import Table


class Command(BaseCommand):
    help = "Regenerate QR codes for all tables"

    def handle(self, *args, **kwargs):
        tables = Table.objects.all()
        for table in tables:
            qr_bytes = attach_qr(table.uid).getvalue()
            file_name = f"QR_{table.uid}.png"
            table.qr_code.delete(save=False)
            table.qr_code.save(file_name, ContentFile(qr_bytes), save=True)
            self.stdout.write(f"Regenerated QR for table {table.number} ({table.uid})")
        self.stdout.write(self.style.SUCCESS(f"Done. {tables.count()} QR(s) regenerated."))
