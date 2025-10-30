from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from JobBoardPortal.accounts.models import UserProfile
from JobBoardPortal.companies.models import Company
from JobBoardPortal.jobs.models import Job, Application, JobAlert


class Command(BaseCommand):
    help = 'Generate sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=20,
            help='Number of jobs to create (default: 20)'
        )
        parser.add_argument(
            '--applications',
            type=int,
            default=50,
            help='Number of applications to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing sample data...')
            self.clear_sample_data()

        self.stdout.write('Generating sample data...')
        
        # Create users and profiles
        employers, job_seekers = self.create_users(options['users'])
        self.stdout.write(f'Created {len(employers)} employers and {len(job_seekers)} job seekers')
        
        # Create companies for employers
        companies = self.create_companies(employers)
        self.stdout.write(f'Created {len(companies)} companies')
        
        # Create jobs
        jobs = self.create_jobs(companies, options['jobs'])
        self.stdout.write(f'Created {len(jobs)} jobs')
        
        # Create applications
        applications = self.create_applications(job_seekers, jobs, options['applications'])
        self.stdout.write(f'Created {len(applications)} applications')
        
        # Create job alerts
        alerts = self.create_job_alerts(job_seekers)
        self.stdout.write(f'Created {len(alerts)} job alerts')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sample data:\n'
                f'  - {len(employers + job_seekers)} users\n'
                f'  - {len(companies)} companies\n'
                f'  - {len(jobs)} jobs\n'
                f'  - {len(applications)} applications\n'
                f'  - {len(alerts)} job alerts'
            )
        )

    def clear_sample_data(self):
        """Clear existing sample data (excluding superusers)"""
        # Delete applications first (foreign key constraints)
        Application.objects.filter(applicant__userprofile__isnull=False).delete()
        
        # Delete job alerts
        JobAlert.objects.filter(user__userprofile__isnull=False).delete()
        
        # Delete jobs
        Job.objects.filter(company__user__userprofile__isnull=False).delete()
        
        # Delete companies
        Company.objects.filter(user__userprofile__isnull=False).delete()
        
        # Delete user profiles and users (except superusers)
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, count):
        """Create sample users with profiles"""
        employers = []
        job_seekers = []
        
        # Sample data
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ', 
                    'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'San Jose, CA']
        
        for i in range(count):
            # Alternate between employers and job seekers
            user_type = 'employer' if i % 3 == 0 else 'jobseeker'
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i}"
            email = f"{username}@example.com"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Update the automatically created profile
            profile = user.userprofile
            profile.user_type = user_type
            profile.phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            profile.location = random.choice(locations)
            profile.save()
            
            if user_type == 'employer':
                employers.append(user)
            else:
                job_seekers.append(user)
        
        return employers, job_seekers

    def create_companies(self, employers):
        """Create sample companies for employers"""
        companies = []
        
        company_names = [
            'TechCorp Solutions', 'Global Innovations Inc', 'Digital Dynamics LLC', 
            'Future Systems Ltd', 'Smart Technologies', 'NextGen Software',
            'Innovative Designs Co', 'Advanced Analytics Inc', 'Creative Solutions LLC',
            'Modern Enterprises', 'Elite Consulting Group', 'Premier Services Inc'
        ]
        
        company_descriptions = [
            'Leading technology company specializing in innovative software solutions.',
            'Global consulting firm providing strategic business solutions.',
            'Creative agency focused on digital marketing and design.',
            'Software development company building cutting-edge applications.',
            'Data analytics firm helping businesses make informed decisions.',
            'Full-service technology consultancy with expertise in cloud solutions.'
        ]
        
        for employer in employers:
            company = Company.objects.create(
                user=employer,
                name=random.choice(company_names) + f" {random.randint(1, 100)}",
                description=random.choice(company_descriptions),
                website=f"https://www.{employer.username}company.com",
                location=employer.userprofile.location
            )
            companies.append(company)
        
        return companies

    def create_jobs(self, companies, count):
        """Create sample job postings"""
        jobs = []
        
        job_titles = [
            'Software Engineer', 'Senior Developer', 'Product Manager', 'Data Scientist',
            'UX Designer', 'Marketing Manager', 'Sales Representative', 'Business Analyst',
            'DevOps Engineer', 'Quality Assurance Engineer', 'Project Manager',
            'Frontend Developer', 'Backend Developer', 'Full Stack Developer'
        ]
        
        job_descriptions = [
            'We are looking for a talented professional to join our growing team. The ideal candidate will have strong technical skills and a passion for innovation.',
            'Join our dynamic team and work on exciting projects that make a real impact. We offer competitive compensation and excellent benefits.',
            'Seeking an experienced professional to lead key initiatives and drive business growth. Great opportunity for career advancement.',
            'Looking for a creative problem-solver to help us build the next generation of products. Remote work options available.'
        ]
        
        requirements = [
            'Bachelor\'s degree in relevant field\n3+ years of experience\nStrong communication skills\nTeam player',
            'Master\'s degree preferred\n5+ years of experience\nLeadership experience\nProblem-solving skills',
            'Relevant certifications\n2+ years of experience\nAttention to detail\nCustomer-focused',
            'Technical degree\n1+ years of experience\nEager to learn\nCollaborative mindset'
        ]
        
        for i in range(count):
            company = random.choice(companies)
            
            # Create deadline between 1-90 days from now
            deadline = timezone.now().date() + timedelta(days=random.randint(1, 90))
            
            job = Job.objects.create(
                company=company,
                title=random.choice(job_titles),
                description=random.choice(job_descriptions),
                requirements=random.choice(requirements),
                location=company.location,
                salary=random.randint(40000, 150000),
                deadline=deadline
            )
            jobs.append(job)
        
        return jobs

    def create_applications(self, job_seekers, jobs, count):
        """Create sample job applications"""
        applications = []
        
        cover_letters = [
            'I am very interested in this position and believe my skills would be a great fit for your team.',
            'With my experience and passion for the industry, I am confident I can contribute to your company\'s success.',
            'I am excited about the opportunity to work with your innovative team and help drive your mission forward.',
            'My background aligns well with your requirements, and I am eager to discuss how I can add value to your organization.'
        ]
        
        statuses = ['applied', 'under_review', 'shortlisted', 'rejected']
        
        # Track applications to prevent duplicates
        applied_combinations = set()
        
        for i in range(count):
            # Ensure no duplicate applications
            attempts = 0
            while attempts < 50:  # Prevent infinite loop
                job_seeker = random.choice(job_seekers)
                job = random.choice(jobs)
                combination = (job_seeker.id, job.id)
                
                if combination not in applied_combinations:
                    applied_combinations.add(combination)
                    break
                attempts += 1
            else:
                continue  # Skip if we can't find a unique combination
            
            # Random application date within the last 30 days
            applied_date = timezone.now() - timedelta(days=random.randint(0, 30))
            
            application = Application.objects.create(
                job=job,
                applicant=job_seeker,
                resume='resumes/sample_resume.pdf',  # Placeholder path
                cover_letter=random.choice(cover_letters),
                status=random.choice(statuses),
                applied_date=applied_date
            )
            applications.append(application)
        
        return applications

    def create_job_alerts(self, job_seekers):
        """Create sample job alerts for job seekers"""
        alerts = []
        
        keywords = [
            'python', 'javascript', 'react', 'django', 'software engineer',
            'data scientist', 'product manager', 'designer', 'marketing',
            'sales', 'remote', 'full-time', 'part-time', 'internship'
        ]
        
        locations = [
            'New York', 'San Francisco', 'Los Angeles', 'Chicago', 'Boston',
            'Seattle', 'Austin', 'Denver', 'Remote', 'Anywhere'
        ]
        
        # Create 1-3 alerts per job seeker
        for job_seeker in job_seekers:
            num_alerts = random.randint(1, 3)
            
            for _ in range(num_alerts):
                alert = JobAlert.objects.create(
                    user=job_seeker,
                    keyword=random.choice(keywords),
                    location=random.choice(locations)
                )
                alerts.append(alert)
        
        return alerts