# EcoReminder System Architecture & Data Flow

EcoReminder is a full-stack Smart Dustbin Alert & Waste Management System built on Python Flask, SQLite/MySQL, and modern frontend web standards (Bootstrap 5, Chart.js, Leaflet.js).

## System Overview

```
+-----------------------------------------------------------------------+
|                             USER ROLES                                |
|   +-------------------+   +--------------------+   +--------------+   |
|   |  Citizen User     |   | Sanitation Officer |   | City Admin   |   |
|   +---------+---------+   +---------+----------+   +------+-------+   |
+-------------|-----------------------|---------------------|-----------+
              |                       |                     |
              v                       v                     v
+-----------------------------------------------------------------------+
|                         FLASK CONTROLLERS                             |
|  /register, /login,      /collector/dashboard  /admin/dashboard       |
|  /report, /citizen/dash  /collector/update     /admin/assign          |
+-------------------------------------+---------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------+
|                           DATABASE ENGINE                             |
|    Users Table | Collectors Table | Admins Table | Complaints Table   |
+-----------------------------------------------------------------------+
```

## Database Schema (ERD)

### `users`
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT)
- `email` (TEXT UNIQUE)
- `password` (BLOB)
- `created_at` (DATETIME)

### `collectors`
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT)
- `email` (TEXT UNIQUE)
- `password` (BLOB)
- `phone` (TEXT)
- `created_at` (DATETIME)

### `admins`
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `password` (BLOB)
- `created_at` (DATETIME)

### `complaints`
- `complaint_id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FK -> users.id)
- `location` (TEXT)
- `latitude` (REAL)
- `longitude` (REAL)
- `description` (TEXT)
- `image` (TEXT)
- `status` (TEXT: Pending, In Progress, Collected)
- `assigned_collector` (INTEGER FK -> collectors.id)
- `proof_image` (TEXT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)
