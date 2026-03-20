# HRMS Lite (Django + DRF)

This is a Django REST Framework version of the HRMS Lite API (employees, attendance, reporting) with consistent response envelopes:

* Success: `{ "success": true, "data": ... }` (and `{ "success": true, "count": N, "data": [...] }` for lists)
* Error: `{ "success": false, "error": ... }`

## Run locally

1. Create/activate a virtual environment (already created in this workspace as `venv`).
2. Install deps: `venv\\Scripts\\pip install -r requirements.txt`
3. (Optional) Configure PostgreSQL:
   * copy `.env.example` to `.env`
   * set `DATABASE_URL`
4. Migrate: `venv\\Scripts\\python manage.py migrate`
5. Start server: `venv\\Scripts\\python manage.py runserver 0.0.0.0:8000`

## Endpoints

* `GET /health`
* `GET /` (API overview)
* `GET /docs/` (Swagger UI)

API (base: `/api/`):
* `employees`: CRUD via `/api/employees` and `/api/employees/{id}`
* `attendance`: CRUD via `/api/attendance` and `/api/attendance/{id}`
* `reports`:
  * `GET /api/reports/attendance-summary?department=...`
  * `GET /api/reports/attendance-by-range?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

