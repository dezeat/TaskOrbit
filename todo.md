# Project Roadmap & TODOs

This file tracks implementation tasks and their status. Sections are ordered by development flow: Setup → MVP → Core Features → Advanced Features.

---

## 1. Completed Milestones

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
    - [x] Implement "Active" vs "Accomplished" Tabs

### Core Feature: Tasks (CRUD)
- [x] Create and Delete tasks
    - [x] Templates load and display tasks
    - [x] Display user's tasks at session start (page refresh)
    - [x] Add task popup for input
    - [x] Delete button with hover UI, triggers DB delete and list refresh
    - [x] Dynamic search using HTMX partials
- [x] Edit tasks
    - [x] Make task content editable in popup
    - [x] Update task and refresh list (debounce/delay considered)

---

## 2. Immediate Priorities (Testing & CI)

- [x] Unit testing (priority)
    - [x] Config tests
    - [x] Database tests
    - [x] CRUD tests
    - [x] Add GitHub Actions pipeline to run tests

- [ ] Containerize for deployment
    - [ ] Create `Dockerfile` for platform-agnostic image
    - [ ] Verify network/port configuration for localhost
    - [ ] Ensure Flask serves HTML correctly inside container

---

## 3. Feature Roadmap (In Implementation Order)


### Phase 2: Task Metadata Enhancements
*Quick wins to make the app useful immediately.*

- [ ] **Priorities**
    - [ ] Add `priority` column to Task (Enum: HIGH, MEDIUM, LOW)
    - [ ] Update UI: Add color-coded badges (Red/Orange/Green) or icons
    - [ ] Update "Add/Edit Task" popup with Priority dropdown

- [ ] **Due Dates & "Due Soon"**
    - [ ] Add `due_date` column to Task (DateTime)
    - [ ] Update UI: Show date next to task; highlight if overdue (red) or today (orange)
    - [ ] Create backend filter for "Due Soon" (next 24-48 hours)

- [ ] **Tags (Labels)**
    - [ ] Create `Tag` model (`id`, `name`, `color`)
    - [ ] Create `TaskTag` association table (Many-to-Many)
    - [ ] UI: Allow creating/selecting tags in Task Popup
    - [ ] UI: Display pill-shaped tags on Task card

### Phase 3: User Authentication (Auth)
*Securing the application.*

- [ ] **Design data model**
    - [ ] Update `User` table (via Alembic): Add `email`, `is_active`, `last_login_ts`
    - [ ] Add `passlib[bcrypt]` for secure password hashing
    - [ ] Add `Flask-Login` for session management

- [x] **Implement backend endpoints**
    - [x] Create endpoints: `/login`, `/register`, `/logout`
    - [x] Create auth decorator to handle "Unauthorized" requests (Return HTTP 401 for API, Redirect for browser)
    - [ ] **HTMX Handling:** Middleware to trigger client-side redirect (`HX-Redirect`) on session expiry

- [x] **UI integration**
    - [x] Create Login/Register HTML templates
    - [x] Update "Add Task" and "Edit" to verify user session before action
    - [x] Add "Log Out" button in the header

### Phase 4: Advanced Search & Filtering
*Leveraging the metadata created in Phase 2.*

- [ ] **Refine Search**
    - [ ] Update `search_tasks` in CRUD to support multiple parameters (not just text string)
    - [ ] Enable searching by Tag (e.g., "tag:work")

- [ ] **Filter UI Implementation**
    - [ ] Add Filter Controls to the Dashboard (Dropdown or Sidebar)
        - [ ] Filter by: Priority (High/Med/Low)
        - [ ] Filter by: Due Date (Overdue, Today, This Week)
        - [ ] Filter by: Tags
    - [ ] Connect filters to HTMX task list reload (`hx-include` parameters)

### Phase 5: Support Multiple Task Lists
*Adding organizational hierarchy.*

- [ ] **Design schema and relationships**
    - [ ] Add `TaskList` table (name, owner_id)
    - [ ] Migration: Add `tasklist_id` FK to `Task` table
    - [ ] UI: Add Sidebar or Dropdown to switch current Task List

### Phase 6: Production Hardening

- [ ] **Pluginable DB Backends**
    - [ ] Define interface for DB backends
    - [ ] Document developer workflow for switching between SQLite (Dev) and Postgres (Prod)