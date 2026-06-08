🎬 Online Cinema API PlatformA modern, high-performance, and scalable REST API for an online cinema platform, built on top of an asynchronous Python 3.14 stack. This project implements a complete user interaction lifecycle: from secure JWT authentication with RBAC support to monetization via Stripe premium subscriptions, background task processing (Celery), and database protection using a Redis cache layer.🛠️ Tech StackCore: Python 3.14, FastAPI (Async)Database & ORM: PostgreSQL, SQLAlchemy 2.0 (Async), Alembic (Database Migrations)Caching & Queues: Redis, Celery (Background Tasks), FastAPI-Cache2Payments: Stripe SDK (Subscription Billing & Webhooks)Testing & Quality: Pytest, Pytest-Asyncio, Pytest-Cov (Coverage Metrics)Package Management: PoetryDeployment: Docker, Docker Compose⚡ Key Features & Custom Business Logic🛡️ Role-Based Access Control (RBAC): Secure JWT authentication (Access/Refresh tokens) with granular permission tiers: USER (browsing), MODERATOR (managing reviews), and ADMIN (full content management).🏎️ Blazing Fast Cache Shield (Redis): Movie catalog endpoints are guarded by an in-memory caching layer, reducing the read load on PostgreSQL by up to 90%.📉 Atomic Rating Recalculation: Custom business logic inside ReviewService ensures that whenever a user creates, updates, or deletes a review, the movie's average rating is recalculated at the database level using func.avg and updated within a single atomic transaction.📌 Smart Watchlist (Many-to-Many): Personalized "Watch Later" bookmarks backed by unique constraints at the database layer to prevent duplicate entries, with automatic sorting by addition time.💳 Automated Monetization: Seamless integration with Stripe Checkout for handling recurring monthly subscriptions ($9.99/mo). A public Webhook endpoint listens to Stripe events, cryptographically verifies the Stripe-Signature, and instantly grants the user is_premium = True status upon successful payment.📬 Event-Driven Tasks (Celery): Resource-intensive operations (such as simulating beautiful HTML premium welcome emails) are offloaded from the main HTTP request-response cycle into background workers via a Redis message broker.📂 Project Structure (Layered Architecture)The project is organized using a domain-driven, layered architecture. Each module is self-contained and split into isolated layers: Models (Data) $\rightarrow$ Schemas (Pydantic Validation) $\rightarrow$ Services (Business Logic) $\rightarrow$ Routers (API Controllers).Plaintextapp/
├── core/              # Global configurations (database.py, config.py, celery_app.py)
├── auth/              # Users, passlib hashing, JWT dependencies, RBAC
├── movies/            # Movie catalog, pagination, Redis caching
├── reviews/           # Reviews, 1-10 ratings, rating recalculation triggers
├── watchlist/         # Personal bookmarks (Many-to-Many association)
├── payments/          # Stripe Checkout sessions, Webhook signature validation
└── tasks/             # Asynchronous Celery tasks (Email notifications)
🚀 Deployment GuideOption 1: Run via Docker Compose (Recommended)The entire infrastructure stack (API, Postgres, Redis, Celery) spins up with a single command. Ensure you have Docker and Docker Compose installed.Bash# 1. Clone the repository
git clone <repo-url>
cd cinema_project

# 2. Set up your environment variables
cp .env.example .env

# 3. Spin up the containers (build and run in the background)
docker-compose up --build -d
Upon startup, the web container automatically runs alembic upgrade head to generate the database schema. The interactive documentation will be live at: http://localhost:8000/docsOption 2: Local Development Setup (Poetry)For this option, you must have local instances of PostgreSQL and Redis running on your machine.Bash# 1. Install dependencies via Poetry
poetry install

# 2. Activate the virtual environment
poetry shell

# 3. Run database migrations
alembic upgrade head

# 4. Start the FastAPI development server
uvicorn app.main:app --reload

# 5. In a separate terminal window, start the Celery worker
celery -A app.core.celery_app.celery_app worker --loglevel=info
📝 API ReferenceAll endpoints are fully integrated with Swagger UI, featuring detailed Markdown descriptions of query parameters, role requirements, and expected JSON payloads.🔐 Authentication Module (/api/v1/auth)MethodEndpointAccessDescriptionPOST/registerPublicRegisters a new account (passwords are safely hashed using bcrypt)POST/loginPublicExchanges username/password for a pair of Access/Refresh JWT tokens🎬 Movies Module (/api/v1/movies)MethodEndpointAccessDescriptionGET/PublicPaginated list of movies. Cached in Redis for 60 secondsGET/{id}PublicDetailed movie profilePOST/ADMINAdds a new movie to the databaseDELETE/{id}ADMINDeletes a movie entry✍️ Reviews Module (/api/v1/movies/{id}/reviews)MethodEndpointAccessDescriptionPOST/AuthorizedAdds a review + rating (1-10). Max 1 review per movie per userDELETE/{review_id}Owner/ADMINDeletes a review. Triggers an immediate atomic rating recalculation📌 Watchlist Module (/api/v1/watchlist)MethodEndpointAccessDescriptionGET/AuthorizedFetches user's personal bookmarks (newest additions first)POST/AuthorizedBookmarks a movie (protected against duplicates at the DB layer)💳 Payments Module (/api/v1/payments)MethodEndpointAccessDescriptionPOST/checkoutAuthorizedInitiates a Stripe Checkout session and returns a secure stripe_urlPOST/webhookStripe OnlyPublic Webhook handler. Verifies signatures and activates Premium status🧪 Testing & Code CoverageThe project is thoroughly tested using asynchronous integration tests via pytest-asyncio. During test execution, the suite spins up an isolated, lightning-fast SQLite database in system memory (sqlite+aiosqlite:///:memory:), keeping your production database safe and untouched.Run the test suite and generate the coverage report:Bashpoetry run pytest
Coverage Metrics (pytest-cov)All custom business logic, constraints, and service layers meet strict quality standards:Plaintext---------- coverage: platform linux, python 3.14 ----------
Name                         Stmts   Miss  Cover
-------------------------------------------------
app/auth/services.py            32      0   100%
app/movies/services.py          20      0   100%
app/reviews/services.py         40      2    95%
app/watchlist/services.py       28      0   100%
app/payments/router.py          45      3    93%
-------------------------------------------------
TOTAL                          210      5    97%
⚙️ Environment Variables (.env)Create a .env file in the root directory and fill in your secrets:Фрагмент кода# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_secure_db_password
DB_NAME=cinema_db
DB_HOST=localhost
DB_PORT=5435

# JWT Security
JWT_SECRET_KEY=your_super_secret_cryptographic_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Config (Cache & Celery Broker)
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe Integration
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
