# Job Board Portal 💼

A comprehensive Django job board application connecting employers with job seekers, featuring real-time job alerts, notifications, and a modern responsive interface.

## ✨ Features

### 👤 For Job Seekers
- **Browse & Search Jobs** - Advanced filtering by location, keywords, salary
- **Apply with Resume** - Upload PDF resumes and cover letters
- **Job Alerts** - Get notified when jobs match your criteria
- **Application Tracking** - Monitor application status and history
- **Real-time Notifications** - In-app notifications for job matches

### 🏢 For Employers
- **Company Profiles** - Showcase your company with logos and descriptions
- **Job Management** - Post, edit, and manage job listings
- **Application Review** - View applications and update candidate status
- **Dashboard** - Track job performance and application metrics

### 🔧 Technical Features
- **Role-based Authentication** - Separate interfaces for employers and job seekers
- **Responsive Design** - Works seamlessly on desktop and mobile
- **File Upload Security** - Secure handling of resumes and company logos
- **Real-time Alerts** - Automatic job matching and notification system
- **Admin Panel** - Comprehensive Django admin interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd JobBoardPortal
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🎯 Sample Data

The project includes CS-focused sample data:

**Companies:** TechFlow Solutions, DataMind Analytics, CloudNine Systems, CyberShield Security, QuantumCode Labs, GreenTech Innovations

**Job Types:** Full Stack Developer, Data Scientist, DevOps Engineer, Cybersecurity Analyst, Research Software Engineer, IoT Developer, Frontend/Backend Developer, Mobile Developer, Product Manager

**Login Credentials:**
- Admin: `admin` / `admin123`
- Employers: `employer_1` to `employer_6` / `employer123`
- Job Seekers: `alex_dev`, `sarah_data`, etc. / `jobseeker123`

## 🏗️ Project Structure

```
JobBoardPortal/
├── manage.py                   # Django management
├── requirements.txt            # Dependencies
├── JobBoardPortal/            # Main project
│   ├── settings.py            # Configuration
│   ├── urls.py                # Main URL routing
│   ├── accounts/              # User authentication
│   ├── jobs/                  # Job management
│   ├── companies/             # Company profiles
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS, images
├── media/                     # User uploads
└── db.sqlite3                 # Database
```

## 🔧 Configuration

### Environment Variables (Production)
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
EMAIL_HOST=your-email-host
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

### Key Settings
- **File Limits:** Resumes 5MB (PDF), Logos 2MB (images)
- **Session Timeout:** 2 weeks
- **Security:** CSRF protection, secure file validation
- **Email:** Job alert notifications (configurable)

## 🌐 API Endpoints

### Authentication
| Method | URL | Description | Auth Required |
|--------|-----|-------------|---------------|
| GET/POST | `/accounts/login/` | User login | No |
| POST | `/accounts/logout/` | User logout | Yes |
| GET/POST | `/accounts/register/employer/` | Employer registration | No |
| GET/POST | `/accounts/register/jobseeker/` | Job seeker registration | No |
| GET/POST | `/accounts/profile/` | Profile management | Yes |

### Job Management
| Method | URL | Description | Auth Required | Role |
|--------|-----|-------------|---------------|------|
| GET | `/jobs/` | List all jobs | No | - |
| GET | `/jobs/<id>/` | Job details | No | - |
| GET/POST | `/jobs/create/` | Create job | Yes | Employer |
| GET/POST | `/jobs/<id>/edit/` | Edit job | Yes | Job Owner |
| POST | `/jobs/<id>/delete/` | Delete job | Yes | Job Owner |

### Application Management
| Method | URL | Description | Auth Required | Role |
|--------|-----|-------------|---------------|------|
| GET/POST | `/jobs/<id>/apply/` | Apply for job | Yes | Job Seeker |
| GET | `/jobs/applications/` | My applications | Yes | Job Seeker |
| GET | `/jobs/employer/applications/` | Manage applications | Yes | Employer |
| POST | `/jobs/applications/<id>/update-status/` | Update status | Yes | Job Owner |
| GET | `/jobs/applications/<id>/detail/` | Application details | Yes | Owner/Job Owner |

### Job Alerts & Notifications
| Method | URL | Description | Auth Required | Role |
|--------|-----|-------------|---------------|------|
| GET | `/jobs/alerts/` | List job alerts | Yes | Job Seeker |
| POST | `/jobs/alerts/create/` | Create alert | Yes | Job Seeker |
| POST | `/jobs/alerts/<id>/delete/` | Delete alert | Yes | Alert Owner |
| GET | `/jobs/notifications/` | View notifications | Yes | Job Seeker |
| GET | `/jobs/notifications/<id>/read/` | Mark as read | Yes | Notification Owner |

### Company Management
| Method | URL | Description | Auth Required | Role |
|--------|-----|-------------|---------------|------|
| GET/POST | `/companies/profile/` | Company profile | Yes | Employer |
| GET | `/companies/<id>/` | Company details | No | - |

## 🔗 URL Patterns

### Main Routes
| URL | Description |
|-----|-------------|
| `/` | Home (redirects to `/jobs/`) |
| `/admin/` | Django admin interface |
| `/accounts/` | User authentication |
| `/jobs/` | Job management |
| `/companies/` | Company profiles |

### Template Usage Examples
```html
<a href="{% url 'jobs:job_detail' job.pk %}">View Job</a>
<a href="{% url 'accounts:profile' %}">My Profile</a>
<a href="{% url 'companies:profile' %}">Company Profile</a>
```

### View Redirects
```python
from django.shortcuts import redirect
return redirect('jobs:job_list')
return redirect('jobs:job_detail', pk=job.id)
```

## 📝 API Examples

### Apply for Job
```http
POST /jobs/123/apply/
Content-Type: multipart/form-data

resume: [PDF file]
cover_letter: "I am interested in this position..."
```

### Create Job Alert
```http
POST /jobs/alerts/create/
Content-Type: application/x-www-form-urlencoded

keyword=python+developer&location=san+francisco
```

### Search Jobs
```http
GET /jobs/?keyword=data+scientist&location=remote&page=1
```

## 📊 Status Codes
- **200**: Success
- **302**: Redirect (successful form submission)
- **400**: Bad request/validation errors
- **403**: Access denied
- **404**: Not found
- **500**: Server error

## 🛡️ Security Features

- CSRF protection on all forms
- Role-based access control
- Secure file upload validation
- User input sanitization
- SQL injection prevention
- Session-based authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


**Built with Django 4.2 + Bootstrap 5 + Python 3.13**