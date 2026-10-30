# RECLAIM — Campus Lost & Found Intelligence System
## DBMS Mini Project Report

**Student Name:** ____________________  
**Registration Number:** ____________________  
**Course:** Database Management Systems  
**Project Type:** Web-based relational database application

## 1. Abstract
RECLAIM is a campus-focused lost-and-found application designed to make recovery of misplaced belongings more organized and traceable. Users can report lost or found items, search reports, submit a claim with identifying proof, and track a claim through review and return. The application uses Flask for the web interface and SQLite as the relational database. It demonstrates database design, relationships, constraints, joins, aggregate queries, and controlled status updates.

## 2. Problem Statement
Lost-property handling on campus is often informal and scattered across messages, noticeboards, and word of mouth. A person who finds an item may not know its owner, while the owner may not know where to ask. RECLAIM centralizes reports and records the claim/recovery process.

## 3. Objectives
- Provide a single searchable place for lost and found reports.
- Store reports and user details consistently in relational tables.
- Allow claim submission with identifying proof.
- Record claim decisions and successful returns.
- Demonstrate core DBMS concepts in a working application.

## 4. Proposed System
The user submits a report containing item name, category, description, location, report type, and contact identity. Another user searches the board and submits a claim with proof. A claim can be approved or rejected. Approval changes the item's status to CLAIMED; after handover, the item can be marked RETURNED.

## 5. Technology Stack
- Front end: HTML and CSS rendered through Flask templates
- Back end: Python / Flask
- Database: SQLite
- Interface: Browser-based local web application

## 6. Database Design
### Entities
**Users:** Stores user identity and unique email.  
**Items:** Stores item details and links each report to its reporter.  
**Claims:** Stores claims, identifying proof, and review status; each claim links an item and claimant.

### Relationships
- One user can report many items (Users 1:M Items).
- One item can receive multiple claims (Items 1:M Claims).
- One user can submit multiple claims (Users 1:M Claims).

### Relational Schema
- `Users(user_id PK, full_name, email UNIQUE, role)`
- `Items(item_id PK, title, category, description, location, item_status, reporter_id FK, created_at)`
- `Claims(claim_id PK, item_id FK, claimant_id FK, proof, claim_status, created_at, UNIQUE(item_id, claimant_id))`

### Integrity Constraints
Primary keys uniquely identify rows. Foreign keys connect related records. Email is unique. Required fields use NOT NULL. CHECK constraints restrict valid roles and item/claim statuses. A uniqueness constraint prevents the same user from submitting duplicate claims for the same item.

## 7. DBMS Operations Demonstrated
1. **INSERT:** Create users, reports, and claims.
2. **SELECT and WHERE:** Search by title/location/description and filter by status.
3. **JOIN:** Combine item reports with reporter information and claims with claimant information.
4. **Aggregate functions:** Count all reports and reports by status for dashboard statistics.
5. **UPDATE:** Review claims and update item state after approval or return.
6. **Constraints:** Maintain data consistency through unique, foreign-key, and check constraints.

## 8. Test Cases
| Test | Action | Expected Result |
|---|---|---|
| 1 | Open the home page for the first time | Demo reports and dashboard counts appear |
| 2 | Add a LOST report with valid details | Report appears on the board |
| 3 | Search for an item title or location | Matching reports are displayed |
| 4 | Filter by FOUND | Only found reports are displayed |
| 5 | Submit a claim for an active report | Claim appears with PENDING status |
| 6 | Approve a pending claim | Claim becomes APPROVED and item becomes CLAIMED |
| 7 | Mark a claimed item as returned | Item status becomes RETURNED |
| 8 | Submit a duplicate claim from the same email | Duplicate is prevented by database constraint |

## 9. How to Execute
Install dependencies using `python -m pip install -r requirements.txt`, then run `python app.py`. Open `http://127.0.0.1:5000` in a browser. The database file is generated automatically.

## 10. Conclusion
RECLAIM shows how a relational database can solve a practical campus problem through connected tables, integrity constraints, SQL retrieval, and controlled status changes. The design is small enough for a mini project while providing clear opportunities for future enhancement.

## 11. Future Enhancements
Authentication and role-based access, image uploads, email notifications, automatic similarity suggestions, administrator verification, and deployment to a hosted server.

## Repository Link
Paste the actual GitHub repository URL here after uploading and verifying the project: **[Add your GitHub URL]**

## Evidence / Screenshots
After running the app, capture screenshots of (1) dashboard and demo items, (2) adding a report, (3) submitting a claim, and (4) approved/returned status. Insert genuine screenshots from your running implementation before submission.
