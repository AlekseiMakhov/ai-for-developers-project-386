# CLAUDE.md — Slot Booking Service

## Overview

A time-slot booking service similar to cal.com. Users can create availability schedules, share booking links, and allow others to book appointments. The system supports multiple service types, time zones, and calendar integrations.

---

## Monorepo Structure

```
/
├── apps/
│   ├── api/                  # FastAPI backend
│   └── web/                  # Vue 3 frontend
├── packages/
│   └── contract/             # TypeSpec API contract + generated types
├── docker/
│   ├── api.Dockerfile
│   ├── web.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
└── CLAUDE.md
```

---

## Tech Stack

### API Contract
- **TypeSpec** — API contract definition
- Generated: OpenAPI 3.1 spec + Python/TypeScript types

### Backend (`apps/api`)
- **FastAPI** — web framework
- **PostgreSQL** — primary database
- **SQLAlchemy** (async) — ORM
- **Alembic** — database migrations
- **asyncpg** — async PostgreSQL driver
- **Pydantic v2** — request/response validation
- **pytest + pytest-asyncio** — unit and integration tests
- **httpx** — async test client

### Frontend (`apps/web`)
- **Vue 3** + **TypeScript** + **Vite**
- **shadcn-vue** — UI component library (built on Radix Vue + Tailwind)
- **Tailwind CSS v3** — utility-first styling
- **@schedule-x/vue** — calendar/schedule component
- **Pinia** — state management
- **Vue Router** — routing
- **VeeValidate + Zod** — form validation
- **Playwright** — e2e tests

### Infrastructure
- **Docker** + **Docker Compose** — containerization
- **GitHub Actions** — CI/CD
- **Nginx** — reverse proxy / static frontend serving

---

## API Contract (TypeSpec)

Location: `packages/contract/`

### File Structure
```
packages/contract/
├── main.tsp
├── models/
│   ├── user.tsp
│   ├── schedule.tsp
│   ├── slot.tsp
│   └── booking.tsp
├── routes/
│   ├── auth.tsp
│   ├── schedules.tsp
│   ├── slots.tsp
│   └── bookings.tsp
├── tspconfig.yaml
└── generated/
    ├── openapi.yaml
    └── types/
        ├── index.py      # Python models (Pydantic)
        └── index.ts      # TypeScript types
```

### Core Models

**User**
- `id: uuid`
- `email: string`
- `name: string`
- `timezone: string`
- `slug: string` — unique public booking URL
- `createdAt: datetime`

**Schedule**
- `id: uuid`
- `userId: uuid`
- `name: string`
- `description?: string`
- `duration: integer` — in minutes (e.g. 30, 60)
- `bufferBefore: integer` — buffer time before slot
- `bufferAfter: integer` — buffer time after slot
- `availability: WeeklyAvailability` — working hours per day of week
- `timezone: string`
- `isActive: boolean`

**WeeklyAvailability**
- `monday?: TimeRange[]`
- `tuesday?: TimeRange[]`
- ...
- `sunday?: TimeRange[]`

**TimeRange**
- `start: string` — "09:00"
- `end: string` — "17:00"

**Slot**
- `id: uuid`
- `scheduleId: uuid`
- `startAt: datetime`
- `endAt: datetime`
- `status: "available" | "booked" | "blocked"`

**Booking**
- `id: uuid`
- `scheduleId: uuid`
- `slotId: uuid`
- `guestName: string`
- `guestEmail: string`
- `guestNote?: string`
- `status: "pending" | "confirmed" | "cancelled"`
- `confirmationToken: string`
- `cancelToken: string`
- `createdAt: datetime`

### API Endpoints

```
# Auth
POST   /auth/register
POST   /auth/login
POST   /auth/logout
GET    /auth/me

# Schedules (authenticated)
GET    /schedules
POST   /schedules
GET    /schedules/{id}
PUT    /schedules/{id}
DELETE /schedules/{id}

# Public booking flow (no auth)
GET    /public/{slug}                         # Host profile + active schedules
GET    /public/{slug}/schedules/{scheduleId}/slots?date=YYYY-MM-DD  # Available slots
POST   /public/{slug}/schedules/{scheduleId}/bookings               # Create booking

# Booking management
GET    /bookings                              # Host: list all bookings
GET    /bookings/{id}
PATCH  /bookings/{id}/confirm
PATCH  /bookings/{id}/cancel
GET    /bookings/confirm/{token}              # Guest confirms booking
GET    /bookings/cancel/{cancelToken}         # Guest cancels booking
```

---

## Backend (`apps/api`)

### File Structure
```
apps/api/
├── app/
│   ├── main.py
│   ├── config.py              # Settings via pydantic-settings
│   ├── database.py            # Async SQLAlchemy engine + session
│   ├── dependencies.py        # FastAPI deps (get_db, get_current_user)
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── schedule.py
│   │   ├── slot.py
│   │   └── booking.py
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── schedule.py
│   │   ├── slot.py
│   │   └── booking.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── schedules.py
│   │   ├── slots.py
│   │   ├── bookings.py
│   │   └── public.py
│   ├── services/
│   │   ├── auth.py            # JWT, password hashing
│   │   ├── schedule.py        # Availability computation
│   │   ├── slot.py            # Slot generation logic
│   │   ├── booking.py         # Booking lifecycle
│   │   └── email.py           # Confirmation/cancellation emails
│   └── utils/
│       ├── timezone.py
│       └── tokens.py
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py            # Fixtures: test DB, async client
│   ├── test_auth.py
│   ├── test_schedules.py
│   ├── test_slots.py
│   ├── test_bookings.py
│   └── test_public.py
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

### Key Business Logic

**Slot generation:**
- On schedule create/update, generate available slots for the next N days (configurable, default 60)
- Respect `bufferBefore` / `bufferAfter` between slots
- Regenerate slots when availability settings change
- Block slots that overlap with existing confirmed bookings

**Booking flow:**
1. Guest fetches available slots for a date
2. Guest submits booking (name, email, note)
3. System creates booking with status `pending`, sends confirmation email to guest
4. Guest clicks confirmation link → status → `confirmed`, host notified
5. Either party can cancel → status → `cancelled`, other party notified

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/booking
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
FRONTEND_URL=http://localhost:5173
```

### Testing Strategy
- **Unit tests**: services (slot generation, availability logic)
- **Integration tests**: API endpoints via `httpx.AsyncClient` with test database
- Use `pytest-asyncio` with `asyncio_mode = "auto"`
- Separate test database, rolled back after each test via transactions
- Run: `pytest --cov=app tests/`

---

## Frontend (`apps/web`)

### File Structure
```
apps/web/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts
│   ├── stores/                # Pinia stores
│   │   ├── auth.ts
│   │   ├── schedule.ts
│   │   └── booking.ts
│   ├── api/                   # API client (fetch/axios wrappers)
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── schedules.ts
│   │   └── bookings.ts
│   ├── types/                 # TypeScript types (from contract)
│   │   └── index.ts
│   ├── views/
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   ├── dashboard/
│   │   │   ├── DashboardView.vue       # Overview + upcoming bookings
│   │   │   ├── SchedulesView.vue       # List of schedules
│   │   │   ├── ScheduleEditView.vue    # Create/edit schedule + availability
│   │   │   └── BookingsView.vue        # All bookings with calendar view
│   │   └── public/
│   │       ├── PublicProfileView.vue   # Guest: pick schedule
│   │       ├── SlotPickerView.vue      # Guest: pick date/time slot
│   │       ├── BookingFormView.vue     # Guest: enter details
│   │       └── BookingConfirmView.vue  # Guest: confirmation page
│   ├── components/
│   │   ├── ui/                # shadcn-vue components (auto-generated)
│   │   ├── schedule/
│   │   │   ├── ScheduleCalendar.vue    # @schedule-x/vue wrapper
│   │   │   ├── AvailabilityEditor.vue  # Weekly hours editor
│   │   │   └── SlotPicker.vue          # Public slot selection grid
│   │   ├── booking/
│   │   │   ├── BookingCard.vue
│   │   │   ├── BookingDialog.vue       # shadcn Dialog with booking details
│   │   │   └── BookingStatusBadge.vue
│   │   └── layout/
│   │       ├── AppLayout.vue
│   │       ├── DashboardSidebar.vue
│   │       └── PublicLayout.vue
│   └── lib/
│       └── utils.ts           # shadcn cn() utility
├── e2e/                       # Playwright tests
│   ├── auth.spec.ts
│   ├── schedule.spec.ts
│   ├── booking-flow.spec.ts   # Full public booking flow
│   └── fixtures/
│       └── index.ts
├── playwright.config.ts
├── tailwind.config.ts
├── components.json            # shadcn-vue config
├── vite.config.ts
└── package.json
```

### Calendar Integration (@schedule-x/vue)

`ScheduleCalendar.vue` wraps `@schedule-x/vue` for the **host dashboard** (BookingsView):
- Shows confirmed bookings in week/month view
- Uses shadcn `Dialog` on event click to show booking details
- Booking colors reflect status: confirmed=green, pending=yellow, cancelled=grey

`SlotPicker.vue` for the **public booking flow** — custom component (not schedule-x):
- Shows a grid of available time slots for the selected date
- Uses shadcn `Button` for each slot
- Uses shadcn `Calendar` (date picker) to select the date

### Key UI Pages

**Dashboard / BookingsView**: @schedule-x calendar + shadcn sidebar filters + shadcn Dialog for details

**ScheduleEditView**: shadcn Form + VeeValidate + Zod for schedule settings; custom `AvailabilityEditor` component for weekly time ranges using shadcn inputs

**Public SlotPickerView**: Two-column layout — left: shadcn Calendar for date selection, right: time slot grid built with shadcn Buttons + Tailwind

### Playwright E2E Tests
```
e2e/
├── auth.spec.ts              # Register, login, logout
├── schedule.spec.ts          # Create schedule, set availability
└── booking-flow.spec.ts      # Full flow: visit public page → pick slot → fill form → confirm
```

Test strategy:
- Use `page.goto()` with a seeded test user
- Assert UI state at each step
- Test cancellation flow (follow cancel link)
- Run against dev server: `playwright test --project=chromium`

---

## Docker Setup

### docker-compose.yml (development)
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: booking
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build:
      context: ./apps/api
      dockerfile: ../../docker/api.Dockerfile
    volumes:
      - ./apps/api:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/booking
    ports:
      - "8000:8000"
    depends_on:
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  web:
    build:
      context: ./apps/web
      dockerfile: ../../docker/web.Dockerfile
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    command: npm run dev

volumes:
  pgdata:
```

### docker-compose.prod.yml (production)
- Multi-stage builds for both api and web
- Nginx serves built Vue frontend + proxies `/api` to FastAPI
- No volume mounts, env vars via secrets

---

## CI/CD (GitHub Actions)

### `.github/workflows/ci.yml`
Triggers: push to any branch, pull_request to main

```
Jobs:
  contract:
    - Install TypeSpec
    - Compile TypeSpec → OpenAPI
    - Assert generated files are up to date

  api:
    - Set up Python 3.12
    - Install dependencies
    - Run ruff (lint) + mypy (types)
    - Spin up PostgreSQL service container
    - Run pytest with coverage
    - Upload coverage report

  web:
    - Set up Node 20
    - Install dependencies
    - Run vue-tsc (type check)
    - Run eslint
    - Run vitest (unit tests)
    - Build production bundle

  e2e:
    - Build and start docker-compose (api + db + web)
    - Wait for services to be healthy
    - Run Playwright tests
    - Upload test artifacts on failure
```

### `.github/workflows/cd.yml`
Triggers: push to main (after CI passes)

```
Jobs:
  deploy:
    - Build Docker images (api + web)
    - Push to container registry (GHCR or Docker Hub)
    - SSH to server and run docker-compose pull + up
```

---

## Development Workflow

### Getting started
```bash
# Start all services
docker-compose up

# Run DB migrations
docker-compose exec api alembic upgrade head

# Seed test data (optional)
docker-compose exec api python scripts/seed.py
```

### Running tests
```bash
# Backend
cd apps/api && pytest

# Frontend unit
cd apps/web && npm run test

# E2E
cd apps/web && npx playwright test
```

### Generating types from TypeSpec
```bash
cd packages/contract
npx tsp compile .
# Outputs: generated/openapi.yaml, generated/types/index.ts
```

---

## Makefile (convenience)

```makefile
up:          docker-compose up -d
down:        docker-compose down
migrate:     docker-compose exec api alembic upgrade head
test-api:    docker-compose exec api pytest
test-web:    cd apps/web && npm run test
test-e2e:    cd apps/web && npx playwright test
lint:        cd apps/api && ruff check . && cd ../web && npm run lint
```

---

## Notes for Claude

- **UI mockups**: When provided, use them as the source of truth for layout, component placement, and user flow. Implement pixel-accurate layouts using Tailwind utilities.
- **API contract first**: Always update TypeSpec definitions before implementing backend routes or frontend API calls. Regenerate types after any contract change.
- **shadcn-vue**: Components are copied into `src/components/ui/` via CLI (`npx shadcn-vue@latest add <component>`). Do not edit generated files directly — extend via wrapper components.
- **@schedule-x/vue**: Use only for the host dashboard calendar view. The public slot-picking UI is a custom grid component built with Tailwind + shadcn Buttons for better UX control.
- **Timezones**: Always store datetimes in UTC in the database. Convert to the host's timezone for display and to the guest's local timezone during the public booking flow.
- **Testing**: Every new endpoint must have at least one integration test. Every new Vue page must have at least one Playwright spec covering the happy path.
