# RECLAIM — Campus Lost & Found Intelligence System

A small, working DBMS mini-project built with **Python, Flask, and SQLite**. It helps a campus community report lost/found items, search reports, submit claims, review claims, and record successful returns.

## Features
- Create LOST and FOUND reports
- Search by title, location, or description; filter by status
- Relational `users`, `items`, and `claims` tables
- Submit a claim with identifying proof
- Approve/reject claims; approved claims update item status
- Mark claimed items as returned
- Dashboard counters for total, lost, found, and returned items
- Primary keys, foreign keys, `UNIQUE`, `NOT NULL`, and `CHECK` constraints

## Run locally
1. Install Python 3.9 or newer.
2. Open a terminal in this folder.
3. Run:
   ```bash
   python -m pip install -r requirements.txt
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.

The SQLite database `reclaim.db` is created automatically on first run and seeded with two demo reports. Delete `reclaim.db` if you want to reset the demo database.

## GitHub upload
Create a new empty repository on GitHub, then run these commands in this folder:
```bash
git init
git add .
git commit -m "Build RECLAIM campus lost and found DBMS project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/reclaim-campus-lost-found.git
git push -u origin main
```
Replace the remote URL with your repository's actual URL. Add that URL to your report only after the push succeeds.

## DBMS concepts demonstrated
- Entity relationships and relational schema
- One user can report many items
- One item can have multiple claims
- Joins between users/items/claims
- Aggregate queries for dashboard statistics
- Data integrity through constraints
- Transactional writes through SQLite connection context managers
- State transitions: LOST/FOUND → CLAIMED → RETURNED

## Limitations / future scope
This is a classroom prototype. Claim-review buttons are intentionally simplified and do not implement login or authorization. A production deployment should add authentication, role-based permissions, privacy controls, CSRF protection, and stronger validation.
