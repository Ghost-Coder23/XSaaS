# EduCore — Multi-Tenant School Management SaaS

A complete school management system built for Zimbabwe, designed to work on low bandwidth and offline.

---

## Quick Start (Local Dev)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create platform superadmin
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

Visit: http://localhost:8000

---

## Multi-Tenant Local Testing

Access a specific school using the `?school=` query param:

```
http://localhost:8000/?school=demo
http://localhost:8000/analytics/dashboard/?school=greenwood
```

Or use subdomain routing in production: `greenwood.educore.com`

---

## Modules Included

| Module | Description |
|--------|-------------|
| **Students** | Registration, admissions, profiles, IDs |
| **Academics** | Classes, subjects, academic years, terms |
| **Attendance** | Daily marking, bulk entry, offline sync |
| **Results** | Mark entry, grading, approval workflow |
| **Report Cards** | PDF generation with school branding |
| **Fees** | Fee structures, invoices, payment recording |
| **Analytics** | Role-specific dashboards (headmaster/admin/teacher/parent/student) |
| **Notifications** | In-app notifications, announcements, SMS stub |
| **Parent Portal** | View results, attendance, fee balance |
| **Student Portal** | View own results and attendance |
| **Superadmin** | Platform-level school management |
| **PWA** | Installable, works offline |

---

## User Roles

- **Super Admin** — Django superuser, manages the platform
- **Headmaster** — Full school access, approves results, sees analytics
- **School Admin** — Manages students, fees, users
- **Teacher** — Marks attendance, enters results
- **Parent** — Read-only: child's results, attendance, fees
- **Student** — Read-only: own results and attendance

---

## Parent-Child Linking (Many Children Per Parent)

EduCore now uses an explicit parent-to-student link table so one parent account can be linked to multiple children safely.

- New model: `academics.ParentStudentLink` (`parent` -> `student`, scoped to `school`)
- Unique constraint prevents duplicate links for the same parent/student pair
- Parent self-registration now creates a link to the selected child and auto-links same-email sibling records in that school
- Parent dashboard reads linked children from `ParentStudentLink` (not only email matching)
- A migration backfills links from existing `Student.parent_email` data for already-created parent accounts

After pulling changes, run:

```bash
python manage.py migrate
```

---

## Switch to PostgreSQL

Edit `settings.py`, uncomment the PostgreSQL section and set your credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educore',
        'USER': 'postgres',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Then run: `python manage.py migrate`

---

## Production (Contabo VPS)

1. Install Nginx + Gunicorn + PostgreSQL on Ubuntu 24
2. Configure Nginx with wildcard subdomain: `*.educore.com`
3. Get wildcard SSL cert via Certbot
4. Set `DEBUG=False` in `.env`
5. Run `python manage.py collectstatic`

---

## SMS Integration

SMS is stubbed in `notifications/utils.py`. To activate real SMS:

1. Register at Africa's Talking (africastalking.com)
2. Get API key
3. Replace the `send_sms()` function body in `notifications/utils.py`

---

## Payment Integration

Each school configures their own payment gateway at:
`/fees/payment-config/`

Supported: Paynow, EcoCash, OneMoney, Bank Transfer (Zimswitch), Cash

---

## PWA

The app installs to home screen on Android/iOS. Service worker caches pages for offline use. Attendance marked offline syncs automatically when connection is restored.

---

## File Structure

```
educore_project/
├── accounts/          # Auth, user profiles
├── schools/           # Multi-tenant, school branding
├── academics/         # Students, classes, subjects
├── results/           # Marks, grades, report cards
├── reports/           # PDF generation
├── attendance/        # Daily attendance + offline sync
├── fees/              # Fee management + payments
├── notifications/     # In-app notifications + SMS stub
├── analytics/         # Role-based dashboards
├── superadmin/        # Platform management
├── middleware/        # Tenant detection
├── static/            # CSS, JS, PWA icons, service worker
├── templates/         # All HTML templates
└── manage.py
```
