# Week 03 — Self-Check

## 1. Why do your tasks survive a server restart this week, when last week they did not?

In Week 03, tasks are stored in a PostgreSQL database instead of a Python dictionary in the server's memory. The database stores the data on disk using the `pgdata` volume, so the tasks remain available even after restarting the server. In the previous week, the tasks were stored in memory and were lost when the server process stopped.

## 2. What is a migration, and why not create tables by hand in `psql` like in Step 2?

A migration is a script that records changes to the database structure and is stored in version control. Using Alembic allows developers to apply the same database changes consistently across different environments. Creating tables manually in `psql` does not record these changes in the project, which can cause differences between developers' databases.

## 3. `project_id` is a nullable foreign key. What do "nullable" and "foreign key" each mean for a task?

Nullable means that a task can exist without being assigned to a project, so its `project_id` can be `NULL`. A foreign key ensures that if a task is assigned to a project, its `project_id` must match the ID of an existing project in the `projects` table. This maintains data consistency and prevents references to projects that do not exist.

## 4. Why does the test fixture delete tasks before projects?

The test fixture deletes tasks before projects because tasks may reference projects through a foreign key. If a project is deleted while tasks still reference it, the database may reject the operation because it would violate the foreign key constraint. Deleting tasks first avoids this problem and allows the tests to start with clean tables.

## 5. What does `db.commit()` do, and what happens to your `INSERT` if you forget it?

The `db.commit()` method commits the current transaction and saves its changes to the database. If it is omitted, the `INSERT` may not be committed and can be rolled back when the database session closes. As a result, the new record may not be saved permanently.