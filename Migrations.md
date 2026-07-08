# Database Migrations — Alembic Workflow

This project uses **Alembic** to manage database schema changes. `Base.metadata.create_all()`
is no longer used — the database schema is now version-controlled, just like code.

---

## Current state

- Local test DB and production RDS are both stamped at revision: `f4b37b30c8a4`
  ("create users and images tables")
- `app/main.py` no longer creates tables on startup — it assumes migrations have
  already been applied.

---

## Workflow for any FUTURE schema change (e.g. adding a column)

### 1. Start a new branch
```bash
git checkout main
git pull
git checkout -b feature/your-change-name
```

### 2. Edit the model
Make your change in `app/models.py` (e.g. add a new `Column(...)`).

### 3. Make sure the local test database is running
```bash
docker-compose -f docker-compose.test.yml up -d
```

### 4. Point local `.env` at the test database (temporarily)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/image_metadata_test_db
```
(Keep your real RDS URL saved somewhere so you can restore it after.)

### 5. Generate the migration
```bash
alembic revision --autogenerate -m "short description of the change"
```

### 6. Review the generated file in `alembic/versions/`
Autogenerate is very good, but not perfect — always read the `upgrade()` and
`downgrade()` functions before trusting them. Check for:
- Correct column types / nullability
- No accidental drops of unrelated columns/tables
- Renames are sometimes detected as "drop + add" — fix manually if so

### 7. Apply it locally and test
```bash
alembic upgrade head
uvicorn app.main:app --reload
```
Test the affected endpoints manually (or add/update pytest tests).

### 8. Restore your real `.env` (back to RDS) before committing
Don't commit `.env` either way — it's gitignored — but make sure you don't
accidentally leave your local dev pointed at the test DB long-term.

### 9. Commit and push
```bash
git add app/models.py alembic/versions/<new_file>.py
git commit -m "Add <column/table> via migration"
git push -u origin feature/your-change-name
```

### 10. Open a Pull Request into `main`
GitHub Actions will automatically run the `test` job on the PR.
Wait for it to pass before merging.

### 11. Merge the PR
This triggers `deploy`, which SSHes into EC2, pulls the new code, and
rebuilds the container. The container will start successfully, but the
**database schema on RDS is NOT updated yet** — the app code and the
database schema are applied in two separate steps.

### 12. SSH into EC2 and apply the migration to real RDS
```bash
ssh -i "C:\Users\Harsha Barlanka\Downloads\image-metadata-key.pem" ubuntu@43.204.77.197
cd Full-Stack-Backend
docker compose exec api alembic upgrade head
```

### 13. Verify
```bash
docker compose exec api alembic current
```
Should show your new revision as `(head)`. Then test the live app via
`http://43.204.77.197:8000/docs`.

---

## Special case: fixing a database that's out of sync with Alembic

If a database already has tables that match a migration's `upgrade()` exactly,
but has no `alembic_version` table (e.g. it was originally created via
`create_all()`, like this project's RDS was), use:

```bash
docker compose exec api alembic stamp head
```

This records "this database is at revision X" WITHOUT running any SQL —
use only when you've manually verified the actual schema already matches.
Do NOT use this to skip a migration that hasn't actually been applied.

---

## Useful commands reference

| Command | What it does |
|---|---|
| `alembic current` | Shows which revision the connected database is at |
| `alembic history` | Shows the full chain of migrations, in order |
| `alembic upgrade head` | Applies all pending migrations |
| `alembic downgrade -1` | Reverts the most recent migration |
| `alembic revision --autogenerate -m "msg"` | Generates a new migration from model changes |
| `alembic stamp head` | Marks current revision without running SQL (see above) |