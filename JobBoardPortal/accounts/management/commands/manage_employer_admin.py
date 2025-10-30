"""
Management command to grant or revoke admin access for employer users
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from admin import grant_employer_admin_access, revoke_employer_admin_access


class Command(BaseCommand):
    help = 'Grant or revoke admin access for employer users'
    
    def add_arguments(self, parser):
        parser.add_argument('action', choices=['grant', 'revoke'], help='Action to perform')
        parser.add_argument('username', help='Username of the employer')
        parser.add_argument(
            '--all-employers',
            action='store_true',
            help='Apply action to all employers (ignores username)',
        )
    
    def handle(self, *args, **options):
        action = options['action']
        username = options['username']
        all_employers = options['all_employers']
        
        if all_employers:
            # Apply to all employers
            employers = User.objects.filter(userprofile__user_type='employer')
            
            if not employers.exists():
                self.stdout.write(self.style.WARNING('No employers found in the system'))
                return
            
            success_count = 0
            for employer in employers:
                if action == 'grant':
                    if grant_employer_admin_access(employer):
                        success_count += 1
                        self.stdout.write(f'Granted admin access to {employer.username}')
                else:  # revoke
                    if revoke_employer_admin_access(employer):
                        success_count += 1
                        self.stdout.write(f'Revoked admin access from {employer.username}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully {action}ed admin access for {success_count} employers')
            )
        
        else:
            # Apply to specific user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')
            
            if not hasattr(user, 'userprofile') or user.userprofile.user_type != 'employer':
                raise CommandError(f'User "{username}" is not an employer')
            
            if action == 'grant':
                if grant_employer_admin_access(user):
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully granted admin access to {username}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to grant admin access to {username}')
                    )
            else:  # revoke
                if revoke_employer_admin_access(user):
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully revoked admin access from {username}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to revoke admin access from {username}')
                    )