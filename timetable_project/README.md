# School Timetable Manager

A production-ready Django web application for managing school timetables.
Built with Django, plain HTML/CSS/JavaScript (no frontend framework required).

## Features

- **Dashboard** — at-a-glance stats and recent timetables
- **Subjects** — manage subjects with colour coding and periods-per-week
- **Teachers** — assign subjects, available days, max periods per day
- **Classrooms** — track rooms with type and capacity
- **School Classes** — manage classes with optional class teacher
- **Periods** — define the daily schedule including breaks and lunch
- **Timetables**
  - Auto-generation with conflict-free constraint satisfaction (Fisher-Yates + backtracking)
  - Manual entry editing (click any cell)
  - Publish / Unpublish
  - Clone to a different year or term
  - Conflict detection
  - Print / PDF export via browser print

---

## Quick Start (SQLite – zero config)

```bash
# 1. Clone / unzip the project
cd timetable_project

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install Django
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate --settings=settings

# 5. Create demo data + superuser (admin / admin)
python manage.py setup_demo --settings=settings

# 6. Start the server
python manage.py runserver --settings=settings
```

Open **http://127.0.0.1:8000** — log in with `admin` / `admin`.

---

## PostgreSQL Setup

Edit `settings.py` and replace the `DATABASES` block:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timetable_db',
        'USER': 'postgres',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Install the driver:

```bash
pip install psycopg2-binary
```

Then run `python manage.py migrate --settings=settings` as normal.

---

## Integrating into an Existing Django Project

1. Copy the `timetable/` app folder into your project.
2. Add `'timetable'` to `INSTALLED_APPS`.
3. Include the URLs:
   ```python
   # your_project/urls.py
   path('timetable/', include('timetable.urls')),
   ```
4. Run `python manage.py migrate`.
5. The app uses Django's built-in auth — if your project already has
   auth configured, it will work seamlessly.

---

## Project Structure

```
timetable_project/
├── settings.py                 # Django settings
├── urls.py                     # Root URL config
├── wsgi.py
├── requirements.txt
└── timetable/
    ├── models.py               # Subject, Teacher, Classroom, SchoolClass,
    │                           #   Period, Timetable, TimetableEntry
    ├── views.py                # All views (HTML pages + JSON API endpoints)
    ├── urls.py                 # URL patterns
    ├── admin.py                # Django admin registration
    ├── services/
    │   └── generator.py        # Timetable generation engine
    ├── templatetags/
    │   └── dict_extras.py      # {{ dict|get_item:key }} template filter
    ├── management/commands/
    │   └── setup_demo.py       # python manage.py setup_demo
    ├── static/timetable/
    │   ├── css/style.css       # Dark-theme stylesheet
    │   └── js/app.js           # Shared JS (API, modals, toasts)
    └── templates/timetable/
        ├── base.html           # Sidebar layout
        ├── login.html
        ├── dashboard.html
        ├── subjects.html
        ├── teachers.html
        ├── classrooms.html
        ├── classes.html
        ├── periods.html
        ├── timetables.html
        └── timetable_view.html # Grid viewer + inline editor
```

---

## Generation Algorithm

The engine (`timetable/services/generator.py`) uses a **greedy randomised
constraint-satisfaction** approach:

1. Loads all subjects, teachers, classrooms, and teaching periods.
2. Checks feasibility (total required periods ≤ available slots).
3. Builds a shuffled queue of subject assignments (subject × periods_per_week).
4. For each assignment, iterates shuffled slots to find one where:
   - The slot is not already used by this class.
   - An eligible teacher (has the subject, is available that day, not over max) is free.
   - A classroom is free at that slot.
5. Marks occupied slots and bulk-inserts all entries in a single transaction.
6. Returns a `GenerationOutcome` with counts and any conflict records.

---

## API Endpoints (JSON)

All endpoints require login (`@login_required`).

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/subjects/` | List subjects |
| POST | `/api/subjects/create/` | Create subject |
| PUT | `/api/subjects/<id>/update/` | Update subject |
| DELETE | `/api/subjects/<id>/delete/` | Delete subject |
| GET | `/api/teachers/` | List teachers |
| POST | `/api/teachers/create/` | Create teacher |
| GET | `/api/teachers/<id>/schedule/` | Teacher's schedule |
| GET | `/api/classrooms/` | List classrooms |
| GET | `/api/classes/` | List school classes |
| GET | `/api/periods/` | List periods |
| POST | `/api/timetables/create/` | Create timetable |
| POST | `/api/timetables/<id>/generate/` | Auto-generate entries |
| POST | `/api/timetables/<id>/publish/` | Publish timetable |
| POST | `/api/timetables/<id>/unpublish/` | Unpublish timetable |
| POST | `/api/timetables/<id>/clone/` | Clone timetable |
| GET | `/api/timetables/<id>/conflicts/` | Detect conflicts |
| GET | `/api/timetables/<id>/entries/` | List entries for timetable |
| POST | `/api/entries/create/` | Add entry (with conflict check) |
| PUT | `/api/entries/<id>/update/` | Update entry |
| DELETE | `/api/entries/<id>/delete/` | Delete entry |

---

## Production Checklist

- Set `DEBUG = False` in `settings.py`
- Set `SECRET_KEY` from an environment variable
- Configure `ALLOWED_HOSTS`
- Run `python manage.py collectstatic`
- Serve static files via nginx / WhiteNoise
- Use PostgreSQL instead of SQLite
- Set up a process manager (gunicorn + systemd or Docker)
