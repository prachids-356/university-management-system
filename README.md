# University Management System (Django Monolith)

End-to-end monolithic university management application with modules for users, academics, enrollment, exams, finance, and notifications.

## Features

- Role-based authentication (Admin, Faculty, Student)
- Admissions and faculty onboarding
- Course creation, assignment, prerequisites, and capacity
- Student enrollment with validations
- Attendance marking and grading
- Exam schedule and result entry
- Fee invoice generation and payment status tracking
- Internal JSON APIs for courses, enrollments, and invoices
- Seed data command for quick setup

## Architecture

- `users` – auth, roles, profiles, dashboard/reports
- `academics` – courses and prerequisites
- `enrollment` – enrollments, attendance, grading workflow
- `exams` – exams and results
- `finance` – fee invoices and payment tracking
- `notifications_app` – user notifications
- `services` – domain validation/business rules
- `domain` – decoupled core entities

## Real Database Setup (PostgreSQL)

1. Start PostgreSQL with Docker:
   ```bash
   docker compose up -d
   ```
2. Configure environment from `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Export env vars (or load `.env` in your shell), then:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_data
   python manage.py runserver
   ```

> For local lightweight runs, set `DB_ENGINE=sqlite`.

## Default Seeded Accounts

- Admin: `admin / admin123`
- Faculty: `faculty1 / fac123`
- Student: `student1 / stud123`

## Backup

Create SQLite backups (when using SQLite):
```bash
python manage.py backup_db
```

## Tests and CI

Run tests:
```bash
python manage.py test
```

GitHub Actions workflow is available at `.github/workflows/ci.yml`.
