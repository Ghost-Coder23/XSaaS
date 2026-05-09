# EduCore — Multi-Tenant School Management SaaS

A complete school management system built for Zimbabwe, designed to work well on low bandwidth.

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
| **Attendance** | Daily marking, bulk entry |
| **Results** | Mark entry, grading, approval workflow |
| **Report Cards** | PDF generation with school branding |
| **Fees** | Fee structures, invoices, payment recording |
| **Analytics** | Role-specific dashboards (headmaster/admin/teacher/parent/student) |
| **Notifications** | In-app notifications, announcements, SMS stub |
| **Parent Portal** | View results, attendance, fee balance, QR-based self-registration |
| **Student Portal** | View own results and attendance |
| **QR Registration** | Token-based secure QR codes for parent self-onboarding |
| **Superadmin** | Platform-level school management |

---

## User Roles

- **Super Admin** — Django superuser, manages the platform
- **Headmaster** — Full school access, approves results, sees analytics
- **School Admin** — Manages students, fees, users
- **Teacher** — Marks attendance, enters results
- **Parent** — Read-only: child's results, attendance, fees
- **Student** — Read-only: own results and attendance

---

## Parent-Child Linking & QR Registration

EduCore uses an explicit parent-to-student link table and a secure QR-based self-registration system.

### Parent-Student Links
- Model: `academics.ParentStudentLink` (`parent` -> `student`, scoped to `school`)
- Parent self-registration creates a link to the selected child and auto-links siblings in the same school.

### Secure QR Registration
Schools can now generate unique QR codes for parent onboarding:
- **Token-based Security**: Each school has a unique `registration_token` embedded in the QR link.
- **Admin Control**: Headmasters can enable/disable self-registration or regenerate tokens (invalidating old QR codes) from School Settings.
- **On-the-fly Generation**: QR codes are generated dynamically using the `qrcode` library.

To set up:
```bash
pip install "qrcode[pil]"
python manage.py migrate schools
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

## File Structure

```
educore_project/
├── accounts/          # Auth, user profiles
├── schools/           # Multi-tenant, school branding
├── academics/         # Students, classes, subjects
├── results/           # Marks, grades, report cards
├── reports/           # PDF generation
├── attendance/        # Daily attendance
├── fees/              # Fee management + payments
├── notifications/     # In-app notifications + SMS stub
├── analytics/         # Role-based dashboards
├── superadmin/        # Platform management
├── middleware/        # Tenant detection
├── static/            # CSS, JS, and image assets
├── templates/         # All HTML templates
└── manage.py
```
So no i added the offline functionality and now the users can browse ove tye site wit or withourt internetc cinnection
