                       # Updated Roadmap for Telegram Bot Carpooling Project

This roadmap outlines the development of a Telegram bot for carpooling volleyball players, running as a Python daemon in a Docker container, using Python 3.12, `python-telegram-bot` (v21.x), SQLite via SQLAlchemy, Sentry for tracing, and supporting role switching between passenger and driver. The roadmap is updated to align with the modular structure defined previously.

---

## Phase 1: Setup and Configuration

**Objective**: Establish the development environment and project structure.

- **Task 1.1: Project Structure Setup**

    - Create the project directory structure as defined:
      ```
      carpool_bot/
      ├── Dockerfile
      ├── .env
      ├── requirements.txt
      ├── alembic.ini
      ├── alembic/migrations/
      ├── src/
      │   ├── __init__.py
      │   ├── main.py
      │   ├── config/
      │   ├── database/
      │   ├── models/
      │   ├── handlers/
      │   ├── services/
      │   ├── utils/
      │   └── tests/
      ├── logs/
      ```
    - Initialize Git repository and add `.gitignore` for `.env`, `logs/`, and `*.db`.

- **Task 1.2: Docker Configuration**

    - Write `Dockerfile` using `python:3.12-slim` as the base image.
    - Install dependencies from `requirements.txt`:
        - `python-telegram-bot==21.*`
        - `SQLAlchemy==2.*`
        - `sentry-sdk==2.*`
        - `python-dotenv==1.*`
        - `alembic==1.*`
        - `pytest==8.*`
    - Configure non-root user and set entry point to `python src/main.py`.
    - Ensure SQLite database file (`carpool.db`) and `logs/` are mountable as volumes.

- **Task 1.3: Environment and Configuration**

    - Create `src/config/config.py` to load environment variables from `.env`:
        - `TELEGRAM_TOKEN`: Telegram bot token.
        - `DATABASE_URL`: SQLite path (e.g., `sqlite:///carpool.db`).
        - `SENTRY_DSN`: Sentry tracing configuration.
        - `LOG_LEVEL`: Logging level (e.g., `DEBUG`, `INFO`).
    - Implement `setup_sentry()` and `setup_logging()` in `config.py` for Sentry initialization and logging to `logs/`.

- **Task 1.4: Database Setup**

    - Implement `src/database/db.py` to initialize SQLAlchemy engine and session factory for SQLite.
    - Define models in `src/models/models.py`:
        - `User`: `id`, `name`, `telegram_id`, `role` (driver/passenger).
        - `Trip`: `id`, `driver_id`, `status`.
        - `PickupPoint`: `id`, `trip_id`, `address`, `time`.
        - `Participant`: `trip_id`, `passenger_id`, `pickup_point_id`.
        - `TripTemplate`: `id`, `driver_id`, `name`, `pickup_points` (JSON), `seats`.
    - Configure Alembic in `alembic.ini` and `src/database/migrations.py` for schema migrations.

---

## Phase 2: Core Bot Functionality

**Objective**: Implement essential bot features for user management, trips, and role switching.

- **Task 2.1: Main Bot Initialization**

    - Implement `src/main.py` to:
        - Load configuration from `src/config/config.py`.
        - Initialize Sentry via `config.setup_sentry()`.
        - Set up Telegram bot with `python-telegram-bot`.
        - Register handlers from `src/handlers/`.
        - Start polling mode for development (webhooks for production).
    - Ensure daemon behavior with proper signal handling.

- **Task 2.2: User Management**

    - Implement `src/services/user.py` for:
        - `register_user(telegram_id, name)`: Create/update user in `Users`.
        - `switch_role(user_id, new_role)`: Toggle between driver/passenger.
        - `get_user(telegram_id)`: Retrieve user data.
    - Add handlers in `src/handlers/commands.py`:
        - `/start`: Register user and prompt for role.
        - `/switch_role`: Toggle role with confirmation.
    - Log user operations to Sentry for tracing.

- **Task 2.3: Trip Creation**

    - Implement `src/services/trip.py` for:
        - `create_trip(driver_id, seats, pickup_points)`: Create trip and pickup points.
        - `get_trip(trip_id)`: Retrieve trip details.
    - Add conversation handler in `src/handlers/conversations.py` for trip creation:
        - Prompt for seats and pickup points (address, time).
        - Offer templates via inline buttons (callback: `select_template_<id>`).
    - Implement template selection in `src/services/template.py`:
        - `get_templates(driver_id)`: List driver’s templates.
        - `apply_template(template_id)`: Populate trip data.
    - Use `src/utils/validation.py` for input validation (e.g., time format, seat count).
    - Trace trip creation with Sentry.

- **Task 2.4: Passenger Trip Joining**

    - Implement `src/services/trip.py` for:
        - `join_trip(trip_id, passenger_id, pickup_id)`: Add passenger to trip.
    - Add callback handler in `src/handlers/callbacks.py`:
        - `join_trip_<trip_id>_<pickup_id>`: Process passenger join request.
    - Use `src/utils/telegram.py` to generate inline keyboards for pickup points.
    - Validate seat availability with SQLAlchemy queries.
    - Log join attempts to Sentry.

---

## Phase 3: Advanced Features

**Objective**: Add trip editing, notifications, and template management.

- **Task 3.1: Trip Editing and Cancellation**

    - Extend `src/services/trip.py` with:
        - `edit_trip(trip_id, updates)`: Update trip details.
        - `cancel_trip(trip_id)`: Mark trip as canceled.
    - Add conversation handler in `src/handlers/conversations.py` for editing:
        - Prompt for changes (seats, pickup points).
        - Confirm edits via callback (`confirm_edit_<trip_id>`).
    - Implement cancellation command in `src/handlers/commands.py`.
    - Trace edits and cancellations with Sentry.

- **Task 3.2: Notification System**

    - Implement `src/services/notification.py` for:
        - `notify_participants(trip_id, message)`: Send messages to trip participants.
        - `notify_trip_update(trip_id, changes)`: Notify about changes.
    - Use SQLAlchemy in `notification.py` to query `Participants`.
    - Integrate with `src/utils/telegram.py` for message sending.
    - Log notification delivery to Sentry.

- **Task 3.3: Template Management**

    - Extend `src/services/template.py` with:
        - `save_template(driver_id, trip_id, name)`: Save trip as template.
        - `delete_template(template_id)`: Remove template.
    - Add handlers in `src/handlers/conversations.py` and `src/handlers/callbacks.py`:
        - Conversation for template creation.
        - Callback for saving templates (`save_template_<trip_id>`).
        - Command `/list_templates` to display templates.
    - Trace template operations with Sentry.

---

## Phase 4: Testing and Deployment

**Objective**: Validate functionality and deploy the bot.

- **Task 4.1: Testing**

    - Implement tests in `src/tests/`:
        - `test_user.py`: User registration and role switching.
        - `test_trip.py`: Trip creation, editing, and joining.
        - `test_template.py`: Template creation and application.
        - `test_notification.py`: Notification delivery.
    - Use `pytest` with SQLAlchemy for test database setup.
    - Monitor test runs with Sentry for error detection.

- **Task 4.2: Deployment**

    - Build and push Docker image to a registry (e.g., Docker Hub).
    - Deploy container to production (e.g., AWS ECS or VPS).
    - Configure Docker volumes for `carpool.db` and `logs/`.
    - Set up Sentry to monitor production errors and performance.
    - Run Alembic migrations to initialize production database.

- **Task 4.3: Maintenance**

    - Monitor Sentry dashboards for errors and performance issues.
    - Update dependencies (`python-telegram-bot`, `SQLAlchemy`, etc.) regularly.
    - Apply Alembic migrations for schema changes.
    - Incorporate user feedback to enhance features.

---

## Additional Considerations

- **Concurrency**: Use SQLAlchemy transactions to manage concurrent updates.
- **Security**: Protect `.env` and restrict SQLite file access; validate all user inputs.
- **Scalability**: Optimize SQLAlchemy queries with indexes on `telegram_id` and `trip_id`.
- **Error Handling**: Implement try-catch blocks with Sentry logging in all modules.
- **Role Switching**: Ensure seamless role transitions, restricting driver actions to users with "driver" role.

This roadmap integrates the modular structure, ensuring the bot is developed efficiently with Python 3.12, SQLite via SQLAlchemy, Sentry tracing, and robust role-switching functionality.
