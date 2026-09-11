from django.core.management.base import BaseCommand
from jobs.models import Company

class Command(BaseCommand):
    help = 'Remove Company instances without an associated employer'

    def handle(self, *args, **kwargs):
        empty_employers = Company.objects.filter(employer__isnull=True)
        count = empty_employers.count()
        
        if count > 0:
            empty_employers.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully removed {count} Company instances without an employer.'))
        else:
            self.stdout.write(self.style.SUCCESS('No Company instances without an employer found to remove.'))
