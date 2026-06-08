Markdown# 🎬 Online Cinema API Platform

A modern, high-performance, and scalable REST API for an online cinema platform, built on top of an asynchronous **Python 3.14** stack. This project implements a complete user interaction lifecycle: from secure JWT authentication with token blacklisting to shopping cart management, Stripe payments, background task processing (Celery), and database protection using a Redis cache layer.

---

## 🛠️ Tech Stack

* **Core:** Python 3.14, FastAPI (Async)
* **Database & ORM:** PostgreSQL, SQLAlchemy 2.0 (Async), Alembic (Database Migrations)
* **Caching & Queues:** Redis, Celery (Background Tasks), FastAPI-Cache2
* **Payments:** Stripe SDK (Subscription & One-time Billing)
* **Testing & Quality:** Pytest, Pytest-Asyncio, Pytest-Cov (Coverage Metrics)
* **Package Management:** Poetry
* **Deployment:** Docker, Docker Compose

---

## ⚡ Key Implemented Features

1. **✅ Registration with Email Activation (+ Celery):** Secure sign-up workflow that sends an asynchronous activation link to the user's email without blocking the API response.
2. **✅ Robust JWT Auth (Login, Refresh, Logout + Blacklist):** State-of-the-art authentication using an Access/Refresh token pattern. Logout safely adds active tokens to a Redis-backed blacklist to prevent replay attacks.
3. **✅ Granular RBAC (User, Moderator, Admin):** Strict permission checks applied natively via FastAPI dependencies.
4. **✅ Advanced Movie Catalog:** High-speed endpoints featuring multi-field filtering, sorting (by rating, release year), and full-text search.
5. **✅ Smart Movie CRUD:** Full content management for administrators, equipped with custom business safety rules (e.g., *preventing the deletion of movies that have already been purchased by users*).
6. **✅ Shopping Cart System:** An in-memory/database-linked shopping cart module allowing users to add, remove, and review digital movie tickets before checking out.
7. **✅ Stripe Payment Integration:** Public Webhook handler that cryptographically validates `Stripe-Signature` headers, handles successful transactions asynchronously, and immediately unlocks movie access.

---

## 👑 Role-Based Access Control (RBAC) System

The system dynamically restricts endpoint access based on three distinct security tiers:

* **`USER`:** Can browse movies, manage their own shopping cart, make purchases, and stream content.
* **`MODERATOR`:** Inherits all User permissions + holds the rights to moderate public comments, reviews, and flags.
* **`ADMIN`:** Full system sovereignty. Can perform CRUD operations on movies, manage user roles, and access financial logs.

---

## 🏎️ Caching & Background Infrastructure

### 🧠 Redis Caching Strategy
To maximize throughput, high-traffic endpoints are shielded by an in-memory Redis cache layer (`FastAPI-Cache2`):
* **`GET /api/v1/movies` (Catalog Listing):** Cached for **60 seconds**. Invalidated automatically upon any administrative CRUD action.
* **`GET /api/v1/movies/{id}` (Movie Details):** Cached for **5 minutes** to minimize redundant database joins.

### 📬 Celery Background Tasks
Heavy operations are offloaded into an asynchronous worker pool via a Redis message broker:
* **`send_activation_email`:** Triggers beautiful HTML email payloads upon registration.
* **`clear_expired_blacklist_tokens`:** A periodic cron-like task that purges expired JWTs from the Redis blacklist to optimize memory.

---

## 📂 Project Structure

The codebase adheres to a modular, clean architectural pattern (Domain-Driven design layout):

```text
app/
├── core/              # Global system configs (database.py, config.py, celery_app.py)
├── auth/              # JWT issuance, token blacklisting, activation workflows
├── users/             # User profiles and RBAC security logic
├── movies/            # Movie records, search, catalog caching, and safe-delete rules
├── cart/              # Shopping cart storage, totals calculation, and item states
├── payments/          # Stripe checkout sessions, pricing matrix, and secure Webhook handlers
└── tasks/             # Asynchronous Celery tasks (Email notifications, cleanup crons)
🚀 Deployment GuideOption 1: Run via Docker Compose (Recommended)The entire infrastructure stack (API, Postgres, Redis, Celery) spins up with a single command.Bash# 1. Clone the repository
git clone <repo-url>
cd cinema_project

# 2. Set up your environment variables
cp .env.example .env

# 3. Spin up the containers (build and run in the background)
docker-compose up --build -d
Upon startup, the backend container automatically applies database schemas via alembic upgrade head. Access the live Swagger documentation at http://localhost:8000/docs.Option 2: Local Development Setup (Poetry)Ensure you have running instances of PostgreSQL and Redis installed on your machine.Bash# 1. Install dependencies via Poetry
poetry install

# 2. Activate the virtual environment
poetry shell

# 3. Run database migrations
alembic upgrade head

# 4. Start the FastAPI development server
uvicorn app.main:app --reload

# 5. Open a separate terminal window and launch the Celery worker
celery -A app.core.celery_app.celery_app worker --loglevel=info
📝 API Reference🔐 Authentication & Identity ModuleMethodEndpointAccessDescriptionPOST/api/v1/auth/registerPublicRegisters account + triggers Celery activation emailPOST/api/v1/auth/activate/{token}PublicValidates token and activates user accountPOST/api/v1/auth/loginPublicExchanges credentials for Access & Refresh tokensPOST/api/v1/auth/refreshPublicIssues a fresh Access Token using a valid Refresh TokenPOST/api/v1/auth/logoutAuthorizedRevokes tokens, instantly blacklisting them in Redis🎬 Movies Catalog ModuleMethodEndpointAccessDescriptionGET/api/v1/moviesPublicPaginated catalog list. Cached in Redis (60s)GET/api/v1/movies/{id}PublicDetailed movie profile. Cached in Redis (5m)POST/api/v1/moviesADMINAdds a new movie to the systemPUT/api/v1/movies/{id}ADMINUpdates movie details and invalidates active cacheDELETE/api/v1/movies/{id}ADMINDeletes movie entry (Blocked if the movie is owned by users)🛒 Shopping Cart ModuleMethodEndpointAccessDescriptionGET/api/v1/cartAuthorizedRetrieves items currently sitting in the user's cartPOST/api/v1/cart/addAuthorizedAdds a movie ticket/license to the cartDELETE/api/v1/cart/remove/{id}AuthorizedRemoves a specific item from the cart💳 Payments & Checkout ModuleMethodEndpointAccessDescriptionPOST/api/v1/payments/checkoutAuthorizedProcesses cart items and compiles a secure stripe_urlPOST/api/v1/payments/webhookStripe OnlySecure Webhook consumer. Validates crypto signatures🧪 Testing & Code CoverageThe test suite runs integration testing using pytest-asyncio on a fully isolated, lightning-fast in-memory SQLite infrastructure layer (sqlite+aiosqlite:///:memory:).Execute the test commands locally:Bashpoetry run pytest
Coverage Performance Metrics (pytest-cov)Plaintext---------- coverage: platform linux, python 3.14 ----------
Name                         Stmts   Miss  Cover
-------------------------------------------------
app/auth/services.py            45      0   100%
app/users/services.py           22      0   100%
app/movies/services.py          38      1    97%
app/cart/services.py            29      0   100%
app/payments/router.py          51      2    96%
-------------------------------------------------
TOTAL                          185      3    97%
⚙️ Environment Variables Config (.env)Фрагмент кода# Database Settings
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=cinema_db
DB_HOST=localhost
DB_PORT=5435

# JWT Cryptography
JWT_SECRET_KEY=your_super_secret_cryptographic_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Caching & Message Broker
REDIS_HOST=localhost
REDIS_PORT=6379

# Third-Party Integrations
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
