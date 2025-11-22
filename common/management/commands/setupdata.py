import os
import sys
from secrets import token_urlsafe

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Migrate and populate data base with initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbosity',
            type=int,
            default=1,
            help='Verbosity level; 0=minimal, 1=normal, 2=verbose, 3=very verbose',
        )
        parser.add_argument(
            '--skip-fixtures',
            action='store_true',
            help='Skip loading fixtures (useful if they hang)',
        )

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        skip_fixtures = options.get('skip_fixtures', False)
        
        self.stdout.write(self.style.SUCCESS('Starting setupdata...'))
        
        # Step 1: Migrations
        if not settings.TESTING:
            self.stdout.write(self.style.WARNING('Step 1/3: Running migrations...'))
            try:
                call_command('migrate', verbosity=verbosity)
                self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Migration error: {e}'))
                if verbosity >= 2:
                    import traceback
                    self.stdout.write(traceback.format_exc())
                sys.exit(1)

        # Step 2: Load fixtures
        if not skip_fixtures:
            self.stdout.write(self.style.WARNING('Step 2/3: Loading fixtures...'))
            fixtures = [
                'country.json',
                'currency.json',
                'groups.json',
                'resolution.json',
                'department.json',
                'deal_stage.json',
                'projectstage.json',
                'taskstage.json',
                'client_type.json',
                'closing_reason.json',
                'industry.json',
                'lead_source.json',
                'publicemaildomain.json',
                'help_en.json',
                'sites.json',
                'reminders.json',
                'massmailsettings.json',
            ]
            
            for i, fixture in enumerate(fixtures, 1):
                self.stdout.write(f'  Loading {i}/{len(fixtures)}: {fixture}...', ending='')
                try:
                    call_command('loaddata', fixture, verbosity=verbosity)
                    self.stdout.write(self.style.SUCCESS(' ✓'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f' ✗ Error: {e}'))
                    if verbosity >= 2:
                        import traceback
                        self.stdout.write(traceback.format_exc())
                    # Continue with other fixtures
            self.stdout.write(self.style.SUCCESS('✓ Fixtures loading completed'))
        else:
            self.stdout.write(self.style.WARNING('Skipping fixtures (--skip-fixtures)'))

        # Step 3: Create superuser
        if not settings.TESTING:
            self.stdout.write(self.style.WARNING('Step 3/3: Creating superuser...'))
            try:
                pas = token_urlsafe(6)
                os.environ.setdefault('DJANGO_SUPERUSER_PASSWORD', pas)
                os.environ.setdefault('DJANGO_SUPERUSER_USERNAME', 'IamSUPER')
                os.environ.setdefault('DJANGO_SUPERUSER_EMAIL', 'super@example.com')
                call_command('createsuperuser', '--noinput', verbosity=verbosity)
                self.stdout.write(self.style.SUCCESS('✓ Superuser created'))
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nSUPERUSER Credentials:\n"
                        f" USERNAME: IamSUPER\n"
                        f" PASSWORD: {pas}\n"
                        f" EMAIL: super@example.com\n"
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Superuser creation error: {e}'))
                if verbosity >= 2:
                    import traceback
                    self.stdout.write(traceback.format_exc())
                # Don't exit - superuser might already exist
        
        self.stdout.write(self.style.SUCCESS('\n✅ Setup complete!'))
