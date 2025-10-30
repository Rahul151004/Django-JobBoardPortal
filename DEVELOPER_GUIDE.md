# Job Board Portal - Developer Guide for Viva

## 🎯 Project Overview

**What is this project?**
A Django web application that connects job seekers with employers. Think of it like LinkedIn Jobs or Indeed, but built from scratch.

**Key Concept:** Two types of users with different needs:
- **Job Seekers:** Browse jobs, apply, get notifications
- **Employers:** Post jobs, review applications, manage company

## 🏗️ Django Architecture Explained

### What is Django?
Django is a Python web framework that follows the **MVT (Model-View-Template)** pattern:
- **Model:** Database structure (what data we store)
- **View:** Business logic (what happens when user clicks something)
- **Template:** HTML presentation (what user sees)

### Project Structure
```
JobBoardPortal/                 # Main project folder
├── manage.py                   # Django's command-line utility
├── JobBoardPortal/            # Project configuration
│   ├── settings.py            # All project settings
│   ├── urls.py                # Main URL routing
│   ├── accounts/              # User management app
│   ├── jobs/                  # Job management app
│   ├── companies/             # Company management app
│   └── templates/             # Shared HTML templates
```

## 📱 Django Apps Explained

### What are Django Apps?
Apps are like modules - each handles a specific functionality.
Think of them as different departments in a company.
### 
1. Accounts App (`JobBoardPortal/accounts/`)
**Purpose:** Handles user registration, login, profiles

**Key Files:**
- `models.py` - UserProfile model (extends Django's User)
- `views.py` - Registration, login, profile management
- `forms.py` - Registration and profile forms
- `mixins.py` - Role-based access control (employer vs jobseeker)

**What it does:**
- User registration with role selection (employer/jobseeker)
- Login/logout functionality
- Profile management
- Role-based permissions

### 2. Jobs App (`JobBoardPortal/jobs/`)
**Purpose:** Core job functionality - listings, applications, alerts

**Key Files:**
- `models.py` - Job, Application, JobAlert, JobAlertNotification models
- `views.py` - Job CRUD, application handling, alerts
- `forms.py` - Job posting, application, alert forms
- `signals.py` - Automatic job alert notifications

**What it does:**
- Job posting (employers)
- Job browsing and searching
- Job applications (jobseekers)
- Job alerts and notifications
- Application status management

### 3. Companies App (`JobBoardPortal/companies/`)
**Purpose:** Company profile management

**Key Files:**
- `models.py` - Company model
- `views.py` - Company profile CRUD
- `forms.py` - Company profile form

**What it does:**
- Company profile creation/editing
- Company logo upload
- Public company pages## 🗄️ D
atabase Models Explained

### User Management
```python
# Built-in Django User model (username, email, password)
User (Django built-in)
  ↓
UserProfile (our extension)
  - user_type: 'employer' or 'jobseeker'
  - phone: contact number
```

### Core Business Models
```python
Company
  - user: ForeignKey to User (one employer = one company)
  - name, description, website, logo, location

Job
  - company: ForeignKey to Company
  - title, description, requirements, location, salary, deadline

Application
  - job: ForeignKey to Job
  - applicant: ForeignKey to User
  - resume: PDF file
  - cover_letter: text
  - status: applied/under_review/shortlisted/rejected

JobAlert
  - user: ForeignKey to User
  - keyword: what to search for
  - location: where to search

JobAlertNotification
  - user: ForeignKey to User
  - job: ForeignKey to Job
  - job_alert: ForeignKey to JobAlert
  - message: notification text
  - is_read: boolean
```

### Key Relationships
- One User → One UserProfile (OneToOne)
- One Employer → One Company (OneToOne)
- One Company → Many Jobs (OneToMany)
- One Job → Many Applications (OneToMany)
- One User → Many JobAlerts (OneToMany)
- One User → Many Applications (OneToMany)## 
🎭 Views Explained (The Business Logic)

### Types of Views Used

**1. Function-Based Views (FBV)**
```python
def apply_for_job(request, pk):
    # Simple function that handles job application
    job = get_object_or_404(Job, pk=pk)
    # ... logic here
```

**2. Class-Based Views (CBV)**
```python
class JobListView(ListView):
    # Django's built-in view for listing objects
    model = Job
    template_name = 'jobs/job_list.html'
```

### Key Views by App

**Accounts Views:**
- `register_choice` - Choose employer or jobseeker
- `employer_register` - Employer registration form
- `jobseeker_register` - Jobseeker registration form
- `CustomLoginView` - User login
- `profile_view` - Profile management

**Jobs Views:**
- `JobListView` - Display all jobs (with search)
- `JobDetailView` - Show single job details
- `JobCreateView` - Create new job (employers only)
- `apply_for_job` - Handle job applications
- `ApplicationListView` - Show user's applications
- `NotificationListView` - Show job alert notifications

**Companies Views:**
- `CompanyProfileView` - Manage company profile

### Access Control (Mixins)
```python
EmployerRequiredMixin - Only employers can access
JobSeekerRequiredMixin - Only jobseekers can access
LoginRequiredMixin - Must be logged in
```## 🎨 Templat
es Explained (The User Interface)

### Template Hierarchy
```
templates/
├── base.html                   # Main layout (navbar, footer)
├── home.html                   # Homepage
├── accounts/
│   ├── login.html             # Login form
│   ├── register_choice.html   # Choose user type
│   └── profile.html           # User profile
├── jobs/
│   ├── job_list.html          # Browse jobs
│   ├── job_detail.html        # Job details
│   ├── job_form.html          # Create/edit job
│   ├── apply_job.html         # Job application form
│   └── notifications.html     # Job alert notifications
└── companies/
    └── profile.html           # Company profile form
```

### Template Inheritance
```html
<!-- base.html - The master template -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Job Board{% endblock %}</title>
    <!-- Bootstrap CSS, favicon -->
</head>
<body>
    <nav><!-- Navigation bar --></nav>
    
    {% block content %}
    <!-- Child templates fill this -->
    {% endblock %}
    
    <footer><!-- Footer --></footer>
    <!-- Bootstrap JS -->
</body>
</html>

<!-- job_list.html - Extends base -->
{% extends 'base.html' %}
{% block title %}Jobs - Job Board{% endblock %}
{% block content %}
    <!-- Job listing content here -->
{% endblock %}
```

### Key Template Features
- **Bootstrap 5** for responsive design
- **Font Awesome** for icons
- **Django template tags** for dynamic content
- **CSRF protection** on all forms
- **Role-based content** (different menus for employers/jobseekers)## 🔧 Form
s Explained (User Input Handling)

### Django Forms Purpose
Forms handle user input, validation, and security.

### Key Forms by App

**Accounts Forms:**
```python
EmployerRegistrationForm - Employer signup
JobSeekerRegistrationForm - Jobseeker signup
UserProfileForm - Profile editing
```

**Jobs Forms:**
```python
JobForm - Create/edit job postings
ApplicationForm - Job application with resume upload
JobAlertForm - Create job alerts
JobSearchForm - Search jobs by keyword/location
```

**Companies Forms:**
```python
CompanyProfileForm - Company profile with logo upload
```

### Form Features
- **File Upload Validation:** PDF for resumes, images for logos
- **Security:** CSRF tokens, input sanitization
- **User Experience:** Bootstrap styling, error messages
- **Custom Validation:** Business rules (e.g., only employers can post jobs)

## 🔐 Security Features

### Authentication & Authorization
- **Session-based authentication** (Django built-in)
- **Role-based access control** (employer vs jobseeker)
- **Permission decorators** (@employer_required, @jobseeker_required)
- **Mixins for class-based views** (EmployerRequiredMixin)

### Data Security
- **CSRF protection** on all forms
- **File upload validation** (type, size limits)
- **SQL injection prevention** (Django ORM)
- **XSS protection** (template auto-escaping)
- **Input sanitization** in forms## ⚡
 Advanced Features

### 1. Job Alert System (Real-time Notifications)
**How it works:**
1. Jobseeker creates alert with keywords and location
2. When employer posts new job, Django signal triggers
3. System checks if job matches any alerts
4. Creates notification for matching users
5. User sees notification in their dashboard

**Technical Implementation:**
```python
# signals.py
@receiver(post_save, sender=Job)
def check_job_alerts(sender, instance, created, **kwargs):
    if created:  # Only for new jobs
        # Find matching alerts
        # Create notifications
        # Optional: Send emails
```

### 2. File Upload System
**Resume Upload:**
- Only PDF files allowed
- 5MB size limit
- Stored in `JobBoardPortal/media/resumes/`
- Secure filename handling

**Company Logo Upload:**
- Image files (JPG, PNG, GIF, BMP)
- 2MB size limit
- Stored in `JobBoardPortal/media/logos/`
- Automatic SVG logo generation for companies

### 3. Search & Filtering
**Job Search Features:**
- Keyword search (title, description)
- Location filtering
- Pagination (10 jobs per page)
- Active jobs only (deadline not passed)

### 4. Application Status Tracking
**Workflow:**
1. Jobseeker applies → Status: "Applied"
2. Employer reviews → Status: "Under Review"
3. Employer decides → Status: "Shortlisted" or "Rejected"

### 5. Context Processors
**Custom context processors add data to all templates:**
- `user_navigation` - User type and display name
- `last_visited_job` - Remember last viewed job
- `unread_notifications_count` - Notification badge count## 🛠️ Co
nfiguration Files

### settings.py (The Brain of the Project)
**Key Settings Explained:**

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Using SQLite for development
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files (CSS, JS, Images)
STATIC_URL = '/static/'  # URL prefix for static files
STATICFILES_DIRS = [BASE_DIR / 'JobBoardPortal' / 'static']  # Source files

# Media Files (User Uploads)
MEDIA_URL = '/media/'  # URL prefix for uploaded files
MEDIA_ROOT = BASE_DIR / 'JobBoardPortal' / 'media'  # Storage location

# File Upload Limits
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB for resumes
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',      # Admin interface
    'django.contrib.auth',       # User authentication
    'django.contrib.messages',   # Flash messages
    'JobBoardPortal.accounts',   # Our custom apps
    'JobBoardPortal.jobs',
    'JobBoardPortal.companies',
]
```

### urls.py (URL Routing)
**How URLs work:**
```python
# Main urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/jobs/')),  # Home → Jobs
    path('accounts/', include('accounts.urls')),    # /accounts/login/, etc.
    path('jobs/', include('jobs.urls')),           # /jobs/, /jobs/create/, etc.
    path('companies/', include('companies.urls')), # /companies/profile/, etc.
]

# jobs/urls.py
urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),           # /jobs/
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'), # /jobs/123/
    path('create/', JobCreateView.as_view(), name='job_create'),   # /jobs/create/
]
```#
# 🔄 Request-Response Flow

### Example: User Applies for a Job

1. **User clicks "Apply" button**
   - URL: `/jobs/123/apply/`
   - Method: GET (show form)

2. **Django URL routing**
   - `urls.py` matches pattern `<int:pk>/apply/`
   - Calls `apply_for_job` view with `pk=123`

3. **View processing**
   ```python
   def apply_for_job(request, pk):
       job = get_object_or_404(Job, pk=pk)  # Get job from database
       
       if request.method == 'GET':
           form = ApplicationForm()  # Empty form
           return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})
   ```

4. **Template rendering**
   - `apply_job.html` extends `base.html`
   - Shows job details and application form
   - Form includes file upload for resume

5. **User submits form**
   - URL: same `/jobs/123/apply/`
   - Method: POST (with form data)

6. **View processes submission**
   ```python
   if request.method == 'POST':
       form = ApplicationForm(request.POST, request.FILES)
       if form.is_valid():
           application = form.save(commit=False)
           application.job = job
           application.applicant = request.user
           application.save()
           return redirect('jobs:job_detail', pk=pk)
   ```

7. **Database update**
   - New Application record created
   - Resume file saved to media folder

8. **Redirect to success page**
   - User sees job detail page with success message

## 🎨 Frontend Technologies

### Bootstrap 5
- **Responsive grid system** for mobile-friendly design
- **Components:** Cards, forms, buttons, navigation
- **Utilities:** Spacing, colors, typography

### Font Awesome
- **Icons:** User, briefcase, bell, search, etc.
- **Usage:** `<i class="fas fa-user"></i>`

### Custom CSS
- **Location:** `JobBoardPortal/static/css/custom.css`
- **Purpose:** Project-specific styling
- **Features:** Job card hover effects, custom colors##
 🗃️ Database Design Decisions

### Why These Models?
**User & UserProfile separation:**
- Django's User model handles authentication
- UserProfile extends it with role (employer/jobseeker)
- Allows different user types with same login system

**Company-Job relationship:**
- One company can post many jobs
- Jobs belong to companies, not directly to users
- Allows company branding and information

**Application model:**
- Links users to jobs they applied for
- Tracks application status
- Stores resume and cover letter
- Prevents duplicate applications (unique_together)

**Job Alert system:**
- Stores user preferences for job matching
- Separate notification model for tracking
- Allows multiple alerts per user

### Database Constraints
```python
# Prevent duplicate applications
class Application(models.Model):
    class Meta:
        unique_together = ['job', 'applicant']

# Ensure only employers have companies
class Company(models.Model):
    user = models.ForeignKey(
        User, 
        limit_choices_to={'userprofile__user_type': 'employer'}
    )
```

## 🚀 Deployment Considerations

### Development vs Production
**Development (Current):**
- SQLite database (single file)
- Django dev server (`runserver`)
- Debug mode enabled
- Media files served by Django

**Production (Future):**
- PostgreSQL database
- Web server (Nginx + Gunicorn)
- Debug mode disabled
- Static/media files served by web server
- Environment variables for secrets#
# 🎯 Common Viva Questions & Answers

### Q: Why did you choose Django?
**A:** Django is a "batteries-included" framework that provides:
- Built-in admin interface for data management
- Robust authentication system
- ORM for database operations
- Security features (CSRF, XSS protection)
- Rapid development with less code

### Q: Explain the MVC/MVT pattern in your project
**A:** Django uses MVT (Model-View-Template):
- **Model:** Database structure (User, Job, Application models)
- **View:** Business logic (JobListView, apply_for_job function)
- **Template:** Presentation layer (HTML files with Django template language)

### Q: How do you handle different user types?
**A:** Role-based access control:
- UserProfile model with user_type field ('employer'/'jobseeker')
- Custom mixins (EmployerRequiredMixin, JobSeekerRequiredMixin)
- Different templates and menus based on user type
- Permission decorators on views

### Q: How does the job alert system work?
**A:** Event-driven notifications:
1. User creates JobAlert with keywords/location
2. Django signals detect new Job creation
3. System matches job against all alerts
4. Creates JobAlertNotification for matches
5. User sees notifications in dashboard

### Q: What security measures did you implement?
**A:** Multiple layers:
- CSRF tokens on all forms
- File upload validation (type, size)
- Role-based access control
- SQL injection prevention (Django ORM)
- Input sanitization in forms
- Session-based authentication

### Q: How do you handle file uploads?
**A:** Secure file handling:
- Separate upload directories (resumes/, logos/)
- File type validation (PDF for resumes, images for logos)
- Size limits (5MB resumes, 2MB logos)
- Secure filename generation
- Storage outside web root

### Q: Explain your database relationships
**A:** Key relationships:
- User ↔ UserProfile (OneToOne)
- User ↔ Company (OneToOne, employers only)
- Company ↔ Job (OneToMany)
- Job ↔ Application (OneToMany)
- User ↔ Application (OneToMany)
- User ↔ JobAlert (OneToMany)## 🔍 
Code Examples for Viva

### 1. Model Example
```python
class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    
    @property
    def is_active(self):
        return self.deadline > timezone.now().date()
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
```

### 2. View Example
```python
class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['has_applied'] = Application.objects.filter(
                job=self.object,
                applicant=self.request.user
            ).exists()
        return context
```

### 3. Form Example
```python
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if not resume.name.endswith('.pdf'):
                raise ValidationError('Resume must be a PDF file.')
            if resume.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('File size must be less than 5MB.')
        return resume
```

### 4. Template Example
```html
{% extends 'base.html' %}
{% block content %}
<div class="container">
    <h2>{{ job.title }}</h2>
    <p><strong>Company:</strong> {{ job.company.name }}</p>
    <p><strong>Salary:</strong> ${{ job.salary|floatformat:0 }}</p>
    
    {% if user.is_authenticated and user.userprofile.user_type == 'jobseeker' %}
        {% if has_applied %}
            <div class="alert alert-success">You have already applied!</div>
        {% else %}
            <a href="{% url 'jobs:apply_job' job.pk %}" class="btn btn-primary">
                Apply Now
            </a>
        {% endif %}
    {% endif %}
</div>
{% endblock %}
```

## 🎓 Final Tips for Viva

### Be Ready to Explain:
1. **Why you made specific design decisions**
2. **How data flows through the application**
3. **Security considerations you implemented**
4. **How you would scale the application**
5. **What improvements you would make**

### Demonstrate Understanding:
- Walk through a complete user journey
- Explain the database schema
- Show how templates inherit from base.html
- Discuss the role-based access control
- Explain the job alert notification system

### Common Follow-up Questions:
- "How would you add email notifications?"
- "How would you implement job categories?"
- "How would you handle multiple resume formats?"
- "How would you add a messaging system?"
- "How would you optimize for mobile users?"

