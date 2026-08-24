# PetCare

PetCare is a small appointment-booking system with a FastAPI backend and an Expo client. The API manages users, clinics, pets, appointments, and cached availability slots.

## Requirements

- Python 3.11 or newer
- Node.js and npm
- A database supported by the SQLAlchemy URL in `DATABASE_URL`
- Redis, because the availability-slot service requires `REDIS_URL`

## Run the API

From `api/`, create a virtual environment and install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `api/.env` with the database and Redis connection details:

```dotenv
DATABASE_URL=postgresql+psycopg://petcare:petcare@localhost:5432/petcare
REDIS_URL=redis://localhost:6379/0
TEST_DATABASE_URL=postgresql+psycopg://petcare:petcare@localhost:5432/petcare_test
APP_ENV=dev
```

Apply the schema and load the sample users, clinics, pets, and appointments:

```powershell
alembic upgrade head
python -m scripts.seed
```

Start the development server:

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. FastAPI's interactive documentation is at `/docs`; `/health` checks database connectivity.

## Run the client

From `client/`:

```powershell
npm install
npm start
```

Use the Expo CLI to open the app on a device or emulator. For a web build, run `npm run web`. The client reads `EXPO_PUBLIC_API_URL`; set it to a reachable API address when `localhost` is not the development machine from the device's perspective.

## Tests

The API tests use a separate database configured by `TEST_DATABASE_URL` and recreate its tables for the test session:

```powershell
cd api
pytest
```

The client tests use Jest and the Expo preset:

```powershell
cd client
npm test
```

## API overview

Authenticated requests identify the user with an `X-User-Id` header. The current implementation exposes these main operations:

- `GET /health` and `GET /me`
- `GET|POST /pets`, `GET|PATCH /pets/{pet_id}`
- `GET|POST /appointments`, `GET|PATCH /appointments/{appointment_id}`
- `PATCH /appointments/{appointment_id}/status`
- `GET /clinics/{clinic_id}/available-slots?on_date=YYYY-MM-DD`
- `GET /clinics/{clinic_id}/appointments` for that clinic's owner

Pagination is available on list endpoints with `limit` and `offset` query parameters.

## Design decisions

- FastAPI routers keep HTTP concerns separate from service functions, where authorization and booking rules are enforced.
- SQLAlchemy models and Alembic migrations keep the database schema explicit and reproducible.
- Availability slots are cached and invalidated when an appointment is booked, edited, or has its status changed.
- Appointment status changes use an explicit transition table: scheduled appointments may become completed or cancelled, while terminal states cannot transition again.
- Booking checks for overlapping scheduled appointments for the same pet and returns a conflict instead of creating a second appointment.
- Error responses use stable error codes so clients can distinguish authorization, not-found, conflict, and validation failures.

## Ownership rule

Ownership is resource-specific; it is deliberately not a blanket `current_user.id` filter:

- **Clinics:** clinic listings and available slots are readable without ownership, because a pet owner must be able to discover a clinic before booking. Clinic schedules are readable only by the clinic owner, and clinic writes are owner-only.
- **Pets:** list, read, create, and update operations are scoped to the authenticated pet owner.
- **Appointments:** appointment list, read, update, status changes, and booking are scoped to the pet owner. A user can book only for a pet they own, but can book at a clinic they do not own.

The current authentication mechanism is intentionally simple: `X-User-Id` is looked up directly in the users table. Missing, malformed, or unknown IDs return `401 Unauthorized`.

## Known limitations

- Authentication is a development identity mechanism, not production authentication. There are no passwords, tokens, sessions, or role-based access controls beyond ownership checks.
- Clinic create/update/delete endpoints are not currently exposed, and there is no general clinic-list endpoint in the API.
- The slot availability check uses a check-then-act flow. Concurrent bookings can still double-book a pet until a database-level exclusion or equivalent locking constraint is added.
- The seed script is idempotent for its sample records, but it is intended for development data rather than production provisioning.
- Redis availability is required by configuration, and there is no documented fallback when Redis is unavailable.
- The Expo client currently covers available-slot loading and selection; it is not yet a complete login, clinic browsing, pet management, or appointment-management application.