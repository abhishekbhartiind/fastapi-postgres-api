# 🐘 PostgreSQL Deep Dive: Joins, Indexes, Query Plans & Migrations

This guide covers PostgreSQL database concepts implemented in this service, including relational design, index optimization, query planning analysis, and Alembic migrations.

---

## 1. Relational Modeling & Schema Design

Our schema implements a **One-to-Many (1:N)** relationship between `users` and `tasks`:
- One user can have many tasks.
- Each task belongs to exactly one user (`owner_id` Foreign Key).

### DDL Schema
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority VARCHAR(50) NOT NULL DEFAULT 'medium',
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Why `ON DELETE CASCADE`?
When a user is deleted, all their associated tasks are automatically purged by the database engine within the same transaction, avoiding orphaned records and manual deletion queries.

---

## 2. PostgreSQL Indexes Deep Dive

An index is an auxiliary data structure that allows the query engine to locate rows without scanning the entire table (`Seq Scan`).

### A. Single Column B-Tree Indexes
```sql
CREATE UNIQUE INDEX ix_users_email ON users(email);
CREATE INDEX ix_tasks_title ON tasks(title);
CREATE INDEX ix_tasks_owner_id ON tasks(owner_id);
```
- **B-Tree (Balanced Tree)** is PostgreSQL's default index type.
- Lookup complexity: **$O(\log N)$** instead of $O(N)$ table scans.
- `ix_tasks_owner_id`: Essential for fast foreign key lookups and JOIN operations. Without this index, joining tasks with users on large tables results in slow sequential scans.

### B. Composite (Multi-Column) Indexes
```sql
CREATE INDEX idx_tasks_owner_status ON tasks(owner_id, status);
```
- **Use Case**: Filtering a specific user's tasks by status:
  ```sql
  SELECT * FROM tasks WHERE owner_id = 42 AND status = 'pending';
  ```
- **The Leftmost Prefix Rule**:
  - `idx_tasks_owner_status (owner_id, status)` can accelerate queries on:
    1. `WHERE owner_id = 42 AND status = 'pending'` (Uses both columns)
    2. `WHERE owner_id = 42` (Uses leftmost column)
  - It CANNOT accelerate `WHERE status = 'pending'` alone because B-Tree sorting starts with the first column (`owner_id`).

---

## 3. SQL Joins in Action

In `app/repositories/task_repository.py`:
```python
# SQLAlchemy Eager Loading with joinedload:
stmt = select(Task).options(joinedload(Task.owner)).where(Task.id == task_id)
```

### What SQL does this generate?
```sql
SELECT 
    tasks.id AS tasks_id,
    tasks.title AS tasks_title,
    tasks.description AS tasks_description,
    tasks.status AS tasks_status,
    tasks.priority AS tasks_priority,
    tasks.owner_id AS tasks_owner_id,
    tasks.created_at AS tasks_created_at,
    tasks.updated_at AS tasks_updated_at,
    users.id AS users_id,
    users.email AS users_email,
    users.full_name AS users_full_name,
    users.is_active AS users_is_active,
    users.is_superuser AS users_is_superuser
FROM tasks
LEFT OUTER JOIN users ON users.id = tasks.owner_id
WHERE tasks.id = $1;
```

### Solving the N+1 Query Problem:
- **Without Eager Loading (Lazy)**: Fetching 50 tasks, then accessing `task.owner` for each fires **51 individual database queries** (1 + 50).
- **With `joinedload` (Eager Join)**: Fetches all data in **1 single query** via `LEFT OUTER JOIN`.

---

## 4. Query Plans with `EXPLAIN (ANALYZE, BUFFERS)`

To inspect how PostgreSQL executes a query:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM tasks WHERE owner_id = 1 AND status = 'pending';
```

### Sample Output Explained:
```text
Bitmap Heap Scan on tasks  (cost=4.30..15.20 rows=8 width=248) (actual time=0.042..0.055 rows=8 loops=1)
  Recheck Cond: ((owner_id = 1) AND (status = 'pending'::character varying))
  Buffers: shared hit=3
  ->  Bitmap Index Scan on idx_tasks_owner_status  (cost=0.00..4.30 rows=8 width=0) (actual time=0.021..0.022 rows=8 loops=1)
        Index Cond: ((owner_id = 1) AND (status = 'pending'::character varying))
        Buffers: shared hit=1
Planning Time: 0.125 ms
Execution Time: 0.082 ms
```

### Breakdown:
1. **`Bitmap Index Scan on idx_tasks_owner_status`**:
   - The query planner consults the composite index to find memory block pointers for matching rows.
2. **`Bitmap Heap Scan on tasks`**:
   - Reads the actual data pages from disk/cache matching those pointers.
3. **`Buffers: shared hit=3`**:
   - All 3 memory pages were served directly from PostgreSQL's shared buffer pool (RAM), 0 disk I/O reads!
4. **Scan Types Comparison**:
   - `Seq Scan`: Scans entire table row-by-row (used when table is tiny or query returns >20% of all rows).
   - `Index Scan`: Traverses B-tree directly to the data page (ideal for high-cardinality unique lookups).
   - `Bitmap Index Scan`: Collects bitmapped pages from index before fetching (ideal for multiple matches).

---

## 5. Database Migrations with Alembic

Alembic manages schema version control across development, CI, and production.

### Key Commands:
```bash
# 1. Check current migration state
alembic current

# 2. Generate a new revision from model changes
alembic revision --autogenerate -m "add_category_to_tasks"

# 3. Apply all pending migrations to database
alembic upgrade head

# 4. Rollback the last migration
alembic downgrade -1

# 5. View migration history
alembic history --verbose
```

### Safe Migration Best Practices:
1. Always review autogenerated migration files before committing.
2. For large tables in production, avoid long table locks:
   - Create indexes concurrently: `CREATE INDEX CONCURRENTLY`.
   - Add nullable columns with defaults in multi-step migrations.
