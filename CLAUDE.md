# CLAUDE.md — Slot Booking Service

## Overview

A time-slot booking service similar to cal.com. Users can create availability schedules, share booking links, and allow others to book appointments. The system supports multiple service types, time zones, and calendar integrations.

There are two roles: **host** (authenticated calendar owner) and **guests** (book without an account). A default host account **John Doe** is seeded on first run so the system is usable immediately without manual registration.

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
- **tanstack/useQuery** — for queries
- **Vue Router** — routing
- **VeeValidate + Zod** — form validation
- **vue-i18n** — internationalization (ru + en)
- **@vueuse/core** — `useInjectionState` for shared state composition
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
- `availability: WeeklyAvailability` — working hours per day of week; defaults to Mon–Fri 09:00–18:00
- `timezone: string`
- `isActive: boolean`

**WeeklyAvailability**
- `monday?: TimeRange[]`
- `tuesday?: TimeRange[]`
- ...
- `sunday?: TimeRange[]`

**TimeRange**
- `start: string` — "09:00"
- `end: string` — "18:00"

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
│   │   └── email.py           # Cancellation emails (no confirmation email)
│   └── utils/
│       ├── timezone.py
│       └── tokens.py
├── alembic/
│   ├── env.py
│   └── versions/
├── scripts/
│   └── seed.py                # Seeds default John Doe user on first run
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

**Default user (John Doe):**
- Seeded via `scripts/seed.py` on first run (or via startup event if DB is empty)
- Credentials configurable via env: `DEFAULT_USER_EMAIL`, `DEFAULT_USER_PASSWORD`, `DEFAULT_USER_NAME`, `DEFAULT_USER_SLUG`
- Default: email `john@example.com`, password `changeme`, name `John Doe`, slug `john`

**Default schedule availability:**
- When a new schedule is created without specifying `availability`, it defaults to Mon–Fri, 09:00–18:00
- Buffer before/after defaults to 0

**Slot generation:**
- On schedule create/update, generate available slots for the next **14 days** (not configurable at runtime)
- Respect `bufferBefore` / `bufferAfter` between slots
- Regenerate slots when availability settings change
- Block slots that overlap with existing confirmed bookings

**Booking flow:**
1. Guest fetches available slots for a date
2. Guest submits booking (name, email, note)
3. **Conflict rule:** before creating, check that no confirmed booking across **any schedule of the same host** overlaps the requested time window. Return 409 if conflict.
4. System creates booking with status `pending`
5. On success, the API returns full booking details — frontend shows them immediately on the confirmation page (no email link needed)
6. Host can confirm (`pending` → `confirmed`) or cancel from the dashboard
7. Guest can cancel via cancel link → status `cancelled`, slot freed

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/booking
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
DEFAULT_USER_EMAIL=john@example.com
DEFAULT_USER_PASSWORD=changeme
DEFAULT_USER_NAME=John Doe
DEFAULT_USER_SLUG=john
```

### Testing Strategy
- **Unit tests**: services (slot generation, availability logic, conflict detection)
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
│   │   │   └── LoginView.vue           # Login only (no register in public UI)
│   │   ├── dashboard/
│   │   │   ├── DashboardView.vue       # Overview + upcoming bookings
│   │   │   ├── SchedulesView.vue       # List of schedules
│   │   │   ├── ScheduleEditView.vue    # Create/edit schedule + availability
│   │   │   └── BookingsView.vue        # All bookings with calendar view
│   │   └── public/
│   │       ├── PublicProfileView.vue   # Guest: pick schedule
│   │       ├── SlotPickerView.vue      # Guest: pick date/time slot
│   │       ├── BookingFormView.vue     # Guest: enter details
│   │       └── BookingConfirmView.vue  # Guest: shows full booking info on success (no "go home" button)
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
- Uses shadcn `Calendar` (date picker) limited to today + 13 days (14-day window)

### Key UI Pages

**Dashboard / BookingsView**: @schedule-x calendar + shadcn sidebar filters + shadcn Dialog for details

**ScheduleEditView**: shadcn Form + VeeValidate + Zod for schedule settings; custom `AvailabilityEditor` component for weekly time ranges using shadcn inputs. Default availability pre-filled as Mon–Fri 09:00–18:00.

**Public SlotPickerView**: Two-column layout — left: shadcn Calendar for date selection (capped to 14 days from today), right: time slot grid built with shadcn Buttons + Tailwind.

**Public BookingConfirmView**: Displays full booking details (schedule name, date/time, guest name, email, note, status) after successful booking creation. No "go to home" button — guest sees all info inline.

### Playwright E2E Tests
```
e2e/
├── auth.spec.ts              # Login, logout (uses default John Doe account)
├── schedule.spec.ts          # Create schedule, set availability
└── booking-flow.spec.ts      # Full flow: visit public page → pick slot → fill form → confirm page with booking details
```

Test strategy:
- Use default John Doe account (`john@example.com` / `changeme`) — no registration step needed
- Assert UI state at each step
- Verify conflict rule: book a slot on schedule A, attempt overlapping slot on schedule B → expect 409
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
  deploy-web:
    - Deploys frontend to Vercel via Vercel CLI (vercel deploy --prod --yes)
    - Requires secrets: VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
```

> Railway deploys automatically via GitHub integration (Railway → service → Settings → Source → connect repo → branch: main). No token or CD step needed.

### GitHub Secrets required

| Secret | Where to get |
|---|---|
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens → Create Token |
| `VERCEL_ORG_ID` | Run `npx vercel link` in `apps/web/` → read from `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | Run `npx vercel link` in `apps/web/` → read from `.vercel/project.json` |

---

## Development Workflow

### Getting started
```bash
# Start all services
docker-compose up

# Run DB migrations
docker-compose exec api alembic upgrade head

# Seed default John Doe user + sample schedules
docker-compose exec api python scripts/seed.py
```

### Running tests
```bash
# Backend
cd apps/api && pytest

# Frontend unit
cd apps/web && npm run test

# E2E — from host (requires Playwright installed locally)
cd apps/web && npx playwright test

# E2E — inside Docker (recommended, no local Playwright needed)
# The web container uses mcr.microsoft.com/playwright base image with Chromium pre-installed.
# API calls from fixtures go directly to the api service; browser calls go via Vite proxy (/api → api:8000).
docker compose exec -e API_URL=http://api:8000 web npx playwright test

# E2E — run a single spec inside Docker
docker compose exec -e API_URL=http://api:8000 web npx playwright test e2e/schedule.spec.ts
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
seed:        docker-compose exec api python scripts/seed.py
test-api:    docker-compose exec api pytest
test-web:    cd apps/web && npm run test
test-e2e:    cd apps/web && npx playwright test
lint:        cd apps/api && ruff check . && cd ../web && npm run lint
```

---

## Development Phases

The project is built **vertically by feature** — each phase delivers a fully working slice (backend + frontend) and is merged to `main` before the next begins.

### Git workflow per phase
```
git checkout main && git pull origin main
git checkout -b dev/phase-N
# ... implement ...
git add <files> && git commit -m "feat: ..."
git push origin dev/phase-N
# open PR → merge → repeat
```

### Phase 0 — Infrastructure ✅ (merged)
Branch: `dev/create-backend-init`
- Docker Compose (db + api + web)
- FastAPI skeleton, SQLAlchemy async setup, Alembic
- Vue 3 + Vite + Tailwind + shadcn-vue scaffold
- TypeSpec contract fully defined

### Phase 1 — Auth ✅ (merged)
Branch: `dev/phase-1`
- Backend: User model, JWT auth (register / login / logout / me), bcrypt password hashing, tests
- Frontend: Login view (VeeValidate + Zod), auth Pinia store, router navigation guard
- Seed script: `scripts/seed.py` creates default John Doe user (`john@example.com` / `changeme` / slug `john`)

### Phase 2 — Schedules ✅ (merged)
Branch: `dev/phase-2`
- Backend: Schedule + Slot models, CRUD routes, slot generation service (`regenerate_slots`), migration
- Default availability pre-filled: Mon–Fri 09:00–18:00 when `availability` is not provided
- Slot generation window: **14 days** from today
- Frontend: schedules Pinia store, `ScheduleCard` + `ScheduleForm` components, `AppLayout` with nav, dashboard routing
- UI: indigo primary color, globally increased font/icon sizes for better readability on mobile

### Phase 3 — Public Booking Flow ✅ (merged)
Branch: `dev/phase-3`
- Backend: public routes (`GET /public/{slug}`, slots by date, `POST bookings`), Booking model + service
- **Conflict rule implemented:** booking creation checks for overlapping confirmed bookings across all schedules of the same host. Returns 409 on conflict.
- Booking created with status `pending`; API returns full booking object in response
- Frontend: `PublicProfileView`, `SlotPickerView`, `BookingFormView`; `BookingConfirmView` shows full booking details (no "go home" button)
- Public router layout; slot calendar capped to 14-day window

### Phase 4 — Bookings Dashboard ✅ (merged)
Branch: `dev/phase-4`
- Backend: booking management routes (list, confirm, cancel, token-based guest cancel)
- Frontend: `BookingsView` with `@schedule-x/vue` calendar, `BookingCard`, `BookingDialog`, status badges
- E2E: Playwright spec `booking-dashboard.spec.ts` — list bookings, confirm/cancel actions, calendar view

### Phase 5 — CI/CD ✅ (merged)
Branch: `dev/phase-5`
- GitHub Actions: CI (lint + tests + e2e) and CD (Vercel deploy via CLI)
- Production `docker-compose.prod.yml` with Nginx reverse proxy
- Railway deploys automatically via GitHub integration (no CD step needed)

### Phase 5.5 — i18n ✅ (merged)
Branch: `dev/i18n`
- `vue-i18n` added; supported locales: **ru** (default) + **en**
- Translation files: `src/locales/ru.json`, `src/locales/en.json`
- Playwright config set to `ru-RU` locale for consistent e2e tests

### Phase 6 — Mobile UI Polish ✅ (merged)
Branch: `dev/phase-6-ui-mobile`
- Favicon: custom SVG calendar icon (`public/favicon.svg`), blue `#2563EB` background
- Font: Plus Jakarta Sans via Google Fonts, applied globally
- `viewport-fit=cover` + `env(safe-area-inset-*)` for iPhone notch/home bar
- `AppLayout.vue`: bottom navigation bar on mobile (Dashboard / Schedules / Bookings), hidden sidebar on small screens
- `PublicLayout.vue`: mobile-friendly header
- `BookingsView.vue`: sticky header with filters on mobile
- Locales (`ru.json` / `en.json`): bottom nav labels added

### Phase 7 — PWA ✅ (merged)
Branch: `dev/phase-7-pwa`
- `vite-plugin-pwa` — service worker (Workbox, `autoUpdate`), web app manifest injected at build time
- Icons generated from `favicon.svg` via `@vite-pwa/assets-generator`: 64, 192, 512 px PNG + maskable 512 + Apple touch 180
- Workbox caching: `CacheFirst` for Google Fonts, `NetworkFirst` for `/api/*`
- `index.html`: `apple-touch-icon`, `theme-color`, `apple-mobile-web-app-*` meta tags
- `PwaInstallPrompt.vue` — 3-mode smart banner:
  - **Android/Desktop**: native `beforeinstallprompt` → кнопка «Установить»
  - **iOS Safari**: инструкция «Поделиться → На экран "Домой"»
  - **iOS Chrome/Firefox**: подсказка «Откройте в Safari»
  - Не показывается если уже установлено (`standalone`) или закрыто в сессии
- `npm run generate-pwa-assets` — скрипт для регенерации иконок
- CI/CD: Node.js 20 → 24

### Phase 8 — Google OAuth Integration
Branch: `dev/phase-8-google-oauth`
- Backend: Google OAuth2 flow — `GET /auth/google` (redirect to Google consent screen), `GET /auth/google/callback` (exchange code for token, upsert user, issue JWT)
- Use `authlib` or `httpx` to exchange authorization code; store `google_id` on User model (new migration)
- If user with given email already exists — link Google account; if new — auto-register
- Frontend: «Войти через Google» button on `LoginView.vue`; redirect to `/auth/google` on click
- After successful OAuth callback, backend redirects to frontend with JWT in query param (or sets cookie); auth store picks it up and navigates to dashboard
- E2E: mock Google OAuth in tests (intercept `/auth/google/callback` or use a test credential)
- Required env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

---

## Notes for Claude

- **Default user:** A seed script (`scripts/seed.py`) must create the John Doe default account on first run. E2E tests use this account — do not require manual registration.
- **Auth kept:** JWT auth and logout are fully functional. Registration page may exist but is not linked from the public UI — hosts register via `/auth/register` directly if needed.
- **Default availability:** When creating a schedule without specifying `availability`, default to Mon–Fri 09:00–18:00. The `AvailabilityEditor` in the frontend should pre-fill this default.
- **14-day slot window:** `slot_generation_days = 14` in config. The guest calendar must be capped to today + 13 days.
- **Cross-schedule conflict check:** When creating a booking, verify that no confirmed booking across **any schedule belonging to the same host** overlaps the requested time window (start_at / end_at of the chosen slot). Return 409 on conflict. This applies even if the conflicting booking is on a different schedule/event type.
- **Booking flow — no email confirmation:** Booking is created as `pending`. The API returns the full booking object. The frontend `BookingConfirmView` renders the booking details directly. Do not send a confirmation email or require a guest to click any link. The host confirms from the dashboard.
- **BookingConfirmView:** Show schedule name, date, time, guest name, email, note, and status. No "go to home" / "back to main" button.
- **UI mockups**: When provided, use them as the source of truth for layout, component placement, and user flow. Implement pixel-accurate layouts using Tailwind utilities.
- **API contract first**: Always update TypeSpec definitions before implementing backend routes or frontend API calls. Regenerate types after any contract change.
- **shadcn-vue**: Components are copied into `src/components/ui/` via CLI (`npx shadcn-vue@latest add <component>`). Do not edit generated files directly — extend via wrapper components.
- **@schedule-x/vue**: Use only for the host dashboard calendar view. The public slot-picking UI is a custom grid component built with Tailwind + shadcn Buttons for better UX control.
- **Timezones**: Always store datetimes in UTC in the database. Convert to the host's timezone for display and to the guest's local timezone during the public booking flow.
- **Testing**: Every new endpoint must have at least one integration test. Every new Vue page must have at least one Playwright spec covering the happy path.
