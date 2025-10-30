"""
Management command to set up admin permissions for different user roles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from admin import setup_employer_permissions


class Command(BaseCommand):
    help = 'Set up admin permissions for employer and job seeker roles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all groups and permissions before setting up',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing groups and permissions...')
            Group.objects.filter(name__in=['Employers', 'JobSeekers']).delete()
        
        self.stdout.write('Setting up employer permissions...')
        setup_employer_permissions()
        
        # Set up job seeker group (limited permissions)
        jobseeker_group, created = Group.objects.get_or_create(name='JobSeekers')
        
        if created:
            self.stdout.write('Created JobSeekers group')
            
            # Job seekers can only view and manage their own job alerts
            permissions_to_add = [
                ('jobs', 'jobalert', 'view_jobalert'),
                ('jobs', 'jobalert', 'add_jobalert'),
                ('jobs', 'jobalert', 'change_jobalert'),
                ('jobs', 'jobalert', 'delete_jobalert'),
                
                # Job seekers can view their own applications
                ('jobs', 'application', 'view_application'),
            ]
            
            for app_label, model, codename in permissions_to_add:
                try:
                    content_type = ContentType.objects.get(app_label=app_label, model=model)
                    permission = Permission.objects.get(content_type=content_type, codename=codename)
                    jobseeker_group.permissions.add(permission)
                    self.stdout.write(f'Added permission: {codename}')
                except (ContentType.DoesNotExist, Permission.DoesNotExist):
                    self.stdout.write(
                        self.style.WARNING(f'Permission {codename} not found, skipping...')
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up admin permissions for all user roles')
        )