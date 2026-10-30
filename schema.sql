PRAGMA foreign_keys = ON;

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student','staff'))
);

CREATE TABLE items (
  item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  location TEXT NOT NULL,
  item_status TEXT NOT NULL CHECK(item_status IN ('LOST','FOUND','CLAIMED','RETURNED')),
  reporter_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(reporter_id) REFERENCES users(user_id)
);

CREATE TABLE claims (
  claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER NOT NULL,
  claimant_id INTEGER NOT NULL,
  proof TEXT NOT NULL,
  claim_status TEXT NOT NULL DEFAULT 'PENDING'
    CHECK(claim_status IN ('PENDING','APPROVED','REJECTED')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(item_id) REFERENCES items(item_id) ON DELETE CASCADE,
  FOREIGN KEY(claimant_id) REFERENCES users(user_id),
  UNIQUE(item_id, claimant_id)
);

-- Dashboard aggregate examples
SELECT COUNT(*) AS total_reports FROM items;
SELECT item_status, COUNT(*) AS count_by_status
FROM items GROUP BY item_status;

-- JOIN example
SELECT i.title, i.item_status, u.full_name, u.email
FROM items i
JOIN users u ON u.user_id = i.reporter_id
ORDER BY i.created_at DESC;
