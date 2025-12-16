## Project TODOs

This file tracks implementation tasks and their status. Sections are ordered roughly by development flow: setup → MVP → polish → next features.

### Dev Environment

- [x] DevContainers configured and working (Fedora / WSL2)
    - [x] Make devcontainer platform-agnostic
    - [x] Setup dependencies with `poetry`
    - [x] Setup `make` and create `Makefile`

### Proof of Concept (POC)

- [x] Basic Flask POC
    - [x] Return a basic HTML page with Flask
    - [x] Draft first interface
    - [x] Render basic task text

### Modular OOP DB MVP

- [x] SQLAlchemy configuration and validation
    - [x] Create config from file/dict
    - [x] Validate config inputs
- [x] SQLAlchemy initialization script
- [x] Use `pydantic` dataclasses for domain models
- [x] SQLAlchemy ORM models implemented
- [x] Application-specific CRUD helpers
- [x] Populate DB with seed/test data

### Application / Frontend

- [x] Frontend conceptualization and routes
    - [x] Map routes to DB interactions
    - [x] Use server-side templates
    - [x] Use CRUD helpers to display/manage tasks

### Core Feature: Tasks (Create / Read / Update / Delete)

- [x] Create and Delete tasks
    - [x] Templates load and display tasks
    - [x] Display user's tasks at session start (page refresh)
    - [x] Add task popup for input
    - [x] Delete button with hover UI, triggers DB delete and list refresh
    - [x] Dynamic search using HTMX partials

- [x] Edit tasks
    - [x] Make task content editable in popup
    - [x] Update task and refresh list (debounce/delay considered)

### Testing & CI

- [ ] Unit testing (priority)
    - [ ] Config tests
    - [ ] Database tests
    - [ ] CRUD tests
    - [ ] Add GitHub Actions pipeline to run tests

### Packaging / Deployment

- [ ] Containerize for deployment
    - [ ] Create `Dockerfile` for platform-agnostic image
    - [ ] Verify network/port configuration for localhost
    - [ ] Ensure Flask serves HTML correctly inside container

### Next Features — Detailed Tasks

These are the next major features and the step-by-step tasks to get them implemented. Work on them in the order listed, but individual steps can be parallelized when safe.

#### 1) User Authentication (Auth)

- Design data model
    - [ ] Add `User` fields: `id`, `name`, `hashed_password`, `email?`, `is_active`, `created_at`, `last_login_ts`
    - [ ] Decide password hashing library (e.g. `bcrypt` or `passlib`) and add to project deps
    - [ ] Document auth flows: register, login, logout, password reset (optional)

- Implement backend endpoints and logic
    - [ ] Create endpoints: `/register`, `/login`, `/logout`, `/me` (GET current user)
    - [ ] Add helper functions in `app/utils/auth.py` for hashing and verifying passwords
    - [ ] Wire user CRUD into `app/utils/db/crud.py` (create user, fetch user by name/email)

- Session & security
    - [ ] Choose session strategy (Flask server-side sessions vs signed cookies)
    - [ ] Add secure session handling (use `SECRET_KEY`, session timeout, regeneration on login)
    - [ ] Implement simple CSRF protections for form posts (Flask built-ins or tokens)
    - [ ] Rate-limit login attempts (basic in-memory or note for production)

- UI integration & forms
    - [ ] Add templates for login/register forms (use HTMX to progressively enhance)
    - [ ] Update `app/app.py` to check auth for protected routes and set `session['uid']` appropriately
    - [ ] Add logout button and user menu in the UI partials

- Tests & docs
    - [ ] Add unit tests for auth helpers and endpoints (`tests/test_auth.py`)
    - [ ] Document how to create dev users and seed credentials in `README.md`

#### 2) Support Multiple Task Lists (Modularize Task Functionality)

- Design schema and relationships
    - [ ] Add `TaskList` table/model: `id`, `name`, `owner_id` (FK to `User`), `is_shared`, `created_at`
    - [ ] Update `Task` to include `tasklist_id` FK and optional `position`/`metadata`
    - [ ] Decide sharing model (private per user vs shareable lists) and permissions

- Implement `TaskList` model and migrations
    - [ ] Create ORM model `TaskList` in `app/utils/db/models.py`
    - [ ] Add helper CRUD functions: create_list, fetch_lists_for_user, add_task_to_list
    - [ ] Add database migration notes / simple migration script for SQLite (manual SQL)

- Refactor tasks and routes to be modular
    - [ ] Update existing task routes to accept `list_id` and default to a 'default' list
    - [ ] Factor task-related logic into a `tasks` module (controllers + services) so different list backends can be plugged
    - [ ] Ensure HTMX partials accept `current_list` and render accordingly

- Templates & UI changes
    - [ ] Add UI to select/switch lists, create and manage lists
    - [ ] Update task-add/edit popup to include `list` selection

- Tests & migration
    - [ ] Add tests for list creation, task-list association and list-permissions
    - [ ] Provide a small migration guide for devs to update existing DB files

#### 3) DB: Pluginable backends & developer-friendly DB handling

- Document user and developer interaction flow
    - [ ] Write docs describing runtime DB selection, where to put configs, and how `db_factory` works
    - [ ] Document how devs can test with SQLite locally and with Postgres in CI

- Refactor DB factory for plugins
    - [ ] Define a minimal plugin interface (class or protocol) for DB backends: `engine()`, `session()`, `setup()`
    - [ ] Make `db_factory` load backend classes from a registry or entry-point-like mapping

- Define and implement a plugin interface
    - [ ] Create `app/utils/db/plugins.py` describing the interface and helper registration functions
    - [ ] Update `SQLiteDB` & `PostgresDB` to conform to the interface

- Implement example Postgres plugin (dev/test)
    - [ ] Add example Postgres config YAML and instructions in `README.md`
    - [ ] Implement connection validation and optional fast-fail messages if driver missing

- Update configuration docs & developer guide
    - [ ] Improve `app/utils/db/default_db_config.yaml` examples and document `echo` option and env overrides
    - [ ] Add a `DEVELOPER.md` (or expand `README.md`) explaining how to add a new DB plugin

- Tests & validation for plugins
    - [ ] Add tests that assert `db_factory` returns expected backend for sample configs
    - [ ] Add CI step to smoke-test with SQLite and, if available, Postgres (optional)

### How to proceed (recommended order)

1. Implement Auth data model + password helpers + seeder update (so devs can create admin user).
2. Add auth endpoints and update UI to allow login/register flows.
3. Design and add `TaskList` model + refactor Task model.
4. Modularize task handling code and update templates for lists.
5. Refactor `db_factory` into plugin-friendly structure and add documentation.
6. Add tests and CI steps for auth, lists and DB-plugin resolution.

### Notes & priorities

- Keep changes small and testable — prefer incremental PRs per feature (auth, lists, db-plugin).
- Prioritize secure handling for auth (do not commit plain-text passwords in seeds for production — keep only for local dev).
- Aim to keep HTMX partials stable: refactor server-side views to accept `list_id` without heavy template rewrites.

## Next Features — Detailed Tasks

These are the next major features and the step-by-step tasks to get them implemented. Work on them in the order listed, but individual steps can be parallelized when safe.

### 1) User Authentication (Auth)

- Design data model
    - [ ] Add `User` fields: `id`, `name`, `hashed_password`, `email?`, `is_active`, `created_at`, `last_login_ts`
    - [ ] Decide password hashing library (e.g. `bcrypt` or `passlib`) and add to project deps
    - [ ] Document auth flows: register, login, logout, password reset (optional)

- Implement backend endpoints and logic
    - [ ] Create endpoints: `/register`, `/login`, `/logout`, `/me` (GET current user)
    - [ ] Add helper functions in `app/utils/auth.py` for hashing and verifying passwords
    - [ ] Wire user CRUD into `app/utils/db/crud.py` (create user, fetch user by name/email)

- Session & security
    - [ ] Choose session strategy (Flask server-side sessions vs signed cookies)
    - [ ] Add secure session handling (use `SECRET_KEY`, session timeout, regeneration on login)
    - [ ] Implement simple CSRF protections for form posts (Flask built-ins or tokens)
    - [ ] Rate-limit login attempts (basic in-memory or note for production)

- UI integration & forms
    - [ ] Add templates for login/register forms (use HTMX to progressively enhance)
    - [ ] Update `app/app.py` to check auth for protected routes and set `session['uid']` appropriately
    - [ ] Add logout button and user menu in the UI partials

- Tests & docs
    - [ ] Add unit tests for auth helpers and endpoints (`tests/test_auth.py`)
    - [ ] Document how to create dev users and seed credentials in `README.md`

### 2) Support Multiple Task Lists (Modularize Task Functionality)

- Design schema and relationships
    - [ ] Add `TaskList` table/model: `id`, `name`, `owner_id` (FK to `User`), `is_shared`, `created_at`
    - [ ] Update `Task` to include `tasklist_id` FK and optional `position`/`metadata`
    - [ ] Decide sharing model (private per user vs shareable lists) and permissions

- Implement `TaskList` model and migrations
    - [ ] Create ORM model `TaskList` in `app/utils/db/models.py`
    - [ ] Add helper CRUD functions: create_list, fetch_lists_for_user, add_task_to_list
    - [ ] Add database migration notes / simple migration script for SQLite (manual SQL)

- Refactor tasks and routes to be modular
    - [ ] Update existing task routes to accept `list_id` and default to a 'default' list
    - [ ] Factor task-related logic into a `tasks` module (controllers + services) so different list backends can be plugged
    - [ ] Ensure HTMX partials accept `current_list` and render accordingly

- Templates & UI changes
    - [ ] Add UI to select/switch lists, create and manage lists
    - [ ] Update task-add/edit popup to include `list` selection

- Tests & migration
    - [ ] Add tests for list creation, task-list association and list-permissions
    - [ ] Provide a small migration guide for devs to update existing DB files

### 3) DB: Pluginable backends & developer-friendly DB handling

- Document user and developer interaction flow
    - [ ] Write docs describing runtime DB selection, where to put configs, and how `db_factory` works
    - [ ] Document how devs can test with SQLite locally and with Postgres in CI

- Refactor DB factory for plugins
    - [ ] Define a minimal plugin interface (class or protocol) for DB backends: `engine()`, `session()`, `setup()`
    - [ ] Make `db_factory` load backend classes from a registry or entry-point-like mapping

- Define and implement a plugin interface
    - [ ] Create `app/utils/db/plugins.py` describing the interface and helper registration functions
    - [ ] Update `SQLiteDB` & `PostgresDB` to conform to the interface

- Implement example Postgres plugin (dev/test)
    - [ ] Add example Postgres config YAML and instructions in `README.md`
    - [ ] Implement connection validation and optional fast-fail messages if driver missing

- Update configuration docs & developer guide
    - [ ] Improve `app/utils/db/default_db_config.yaml` examples and document `echo` option and env overrides
    - [ ] Add a `DEVELOPER.md` (or expand `README.md`) explaining how to add a new DB plugin

- Tests & validation for plugins
    - [ ] Add tests that assert `db_factory` returns expected backend for sample configs
    - [ ] Add CI step to smoke-test with SQLite and, if available, Postgres (optional)

### How to proceed (recommended order)

1. Implement Auth data model + password helpers + seeder update (so devs can create admin user).
2. Add auth endpoints and update UI to allow login/register flows.
3. Design and add `TaskList` model + refactor Task model.
4. Modularize task handling code and update templates for lists.
5. Refactor `db_factory` into plugin-friendly structure and add documentation.
6. Add tests and CI steps for auth, lists and DB-plugin resolution.

### Notes & priorities

- Keep changes small and testable — prefer incremental PRs per feature (auth, lists, db-plugin).
- Prioritize secure handling for auth (do not commit plain-text passwords in seeds for production — keep only for local dev).
- Aim to keep HTMX partials stable: refactor server-side views to accept `list_id` without heavy template rewrites.

