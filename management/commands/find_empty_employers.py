from django.core.management.base import BaseCommand
from jobs.models import Company

class Command(BaseCommand):
    help = 'Find Company instances without an associated employer and report the result.'

    help = 'Find Company instances without an associated employer'

    def handle(self, *args, **kwargs):
        empty_employers = Company.objects.filter(employer__isnull=True)
        self.stdout.write(self.style.SUCCESS(f'Found {empty_employers.count()} Company instances without an employer.'))

        self.stdout.write(self.style.SUCCESS('Command executed successfully.'))

        if empty_employers.exists():
            self.stdout.write(self.style.WARNING('Found Company instances without an employer:'))
            for company in empty_employers:
                self.stdout.write(f' - {company.name} (ID: {company.id})')
        else:
            self.stdout.write(self.style.SUCCESS('No Company instances without an employer found.'))
