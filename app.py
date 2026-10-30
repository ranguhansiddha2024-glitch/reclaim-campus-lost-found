import os
from flask import Flask, request, redirect, url_for, flash, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-for-production"
DB_PATH = Path(__file__).with_name("reclaim.db")

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student','staff'))
);
CREATE TABLE IF NOT EXISTS items (
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
CREATE TABLE IF NOT EXISTS claims (
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
"""

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RECLAIM | Campus Recovery</title>
<style>
:root{--navy:#14213d;--teal:#18a999;--paper:#f5f7fb;--ink:#172033;--muted:#657087}
*{box-sizing:border-box}body{margin:0;background:var(--paper);font:15px/1.5 Inter,Segoe UI,Arial,sans-serif;color:var(--ink)}
header{background:linear-gradient(120deg,#14213d,#23395d);color:white;padding:28px max(5vw,20px)}
.brand{font-size:28px;font-weight:900;letter-spacing:2px}.brand span{color:#55e0ce}
header p{color:#d7e2f0;margin:4px 0 0}.wrap{max-width:1120px;margin:24px auto;padding:0 18px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stat,.panel,.item{background:white;border:1px solid #e5eaf2;border-radius:15px;padding:18px;box-shadow:0 5px 18px #17203308}
.stat small{color:var(--muted)}.num{font-size:29px;font-weight:800;margin-top:4px}
.layout{display:grid;grid-template-columns:340px 1fr;gap:18px;margin-top:18px}.panel h2{margin:0 0 12px;font-size:19px}
label{display:block;font-size:13px;font-weight:700;margin:11px 0 5px}input,select,textarea{width:100%;padding:10px 11px;border:1px solid #d5dce7;border-radius:9px;font:inherit;background:white}
textarea{min-height:74px;resize:vertical}button,.btn{border:0;border-radius:9px;background:var(--teal);color:#062a2a;font-weight:800;padding:11px 14px;cursor:pointer;text-decoration:none;display:inline-block}
button:hover,.btn:hover{filter:brightness(.95)}.full{width:100%;margin-top:14px}.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.toolbar input{flex:1;min-width:140px}.toolbar select{width:auto}
.items{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.item h3{margin:8px 0 3px}.item p{margin:5px 0;color:var(--muted)}.pill{display:inline-block;border-radius:30px;padding:3px 9px;background:#e2f7f3;color:#087e71;font-size:11px;font-weight:900;letter-spacing:.5px}.pill.LOST{background:#fff0d8;color:#8c5700}.pill.CLAIMED{background:#eee7ff;color:#5e39a5}.pill.RETURNED{background:#e8edf5;color:#4b5870}
.claimbox{background:#f5f7fb;border-radius:10px;padding:12px;margin-top:12px}.claimbox input{margin-bottom:8px}.notice{padding:11px 14px;background:#e2f7f3;border-radius:9px;margin-bottom:12px}.empty{padding:30px;text-align:center;color:var(--muted);background:white;border-radius:12px}
footer{text-align:center;color:var(--muted);padding:24px;font-size:12px}
@media(max-width:800px){.layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.items{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><div class="brand">RE<span>CLAIM</span></div><p>Lost something? Found something? Help it find its way home.</p></header>
<main class="wrap">
{% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}<div class="notice">{{m}}</div>{% endfor %}{% endif %}{% endwith %}
<section class="stats">
<div class="stat"><small>All reports</small><div class="num">{{stats.total}}</div></div>
<div class="stat"><small>Lost items</small><div class="num">{{stats.lost}}</div></div>
<div class="stat"><small>Found items</small><div class="num">{{stats.found}}</div></div>
<div class="stat"><small>Returned</small><div class="num">{{stats.returned}}</div></div>
</section>
<section class="layout">
<div class="panel">
<h2>＋ Report an item</h2>
<form method="post" action="{{url_for('add_item')}}">
<label>Your name</label><input name="name" required maxlength="80" placeholder="e.g. Aanya Rao">
<label>College email</label><input name="email" type="email" required maxlength="120" placeholder="you@college.edu">
<label>Report type</label><select name="status"><option>LOST</option><option>FOUND</option></select>
<label>Item name</label><input name="title" required maxlength="100" placeholder="e.g. Black calculator">
<label>Category</label><select name="category"><option>Electronics</option><option>ID / Cards</option><option>Books / Stationery</option><option>Wallet / Keys</option><option>Clothing</option><option>Other</option></select>
<label>Location</label><input name="location" required maxlength="120" placeholder="e.g. Library, second floor">
<label>Description</label><textarea name="description" required maxlength="500" placeholder="Colour, brand, identifying details…"></textarea>
<button class="full" type="submit">Publish report</button>
</form>
</div>
<div class="panel">
<h2>Campus item board</h2>
<form class="toolbar" method="get">
<input name="q" value="{{q}}" placeholder="Search title, location, description">
<select name="status"><option value="">All statuses</option>{% for s in ['LOST','FOUND','CLAIMED','RETURNED'] %}<option value="{{s}}" {% if status==s %}selected{% endif %}>{{s}}</option>{% endfor %}</select>
<button type="submit">Filter</button><a class="btn" href="{{url_for('index')}}">Reset</a>
</form>
{% if items %}
<div class="items">
{% for item in items %}
<article class="item">
<span class="pill {{item.item_status}}">{{item.item_status}}</span>
<h3>{{item.title}}</h3><p><b>{{item.category}}</b> · {{item.location}}</p>
<p>{{item.description}}</p><p>Reported by {{item.full_name}} · {{item.created_at}}</p>
{% if item.item_status in ['FOUND','LOST'] %}
<form class="claimbox" method="post" action="{{url_for('claim_item', item_id=item.item_id)}}">
<strong>Submit a claim</strong>
<input name="name" required placeholder="Your full name">
<input name="email" type="email" required placeholder="Your college email">
<input name="proof" required maxlength="300" placeholder="Describe identifying proof">
<button type="submit">Submit claim</button>
</form>
{% endif %}
{% if item.claims %}
<div class="claimbox"><strong>Claims</strong>
{% for c in item.claims %}
<p>{{c.full_name}}: {{c.proof}} — <b>{{c.claim_status}}</b></p>
{% if c.claim_status == 'PENDING' %}
<form method="post" action="{{url_for('review_claim', claim_id=c.claim_id)}}" style="display:inline">
<button name="decision" value="APPROVED">Approve</button>
<button name="decision" value="REJECTED" style="background:#f4d9d9;color:#782626">Reject</button>
</form>
{% endif %}
{% endfor %}
</div>
{% endif %}
{% if item.item_status == 'CLAIMED' %}
<form method="post" action="{{url_for('mark_returned', item_id=item.item_id)}}"><button class="full">Mark as returned</button></form>
{% endif %}
</article>
{% endfor %}
</div>
{% else %}<div class="empty">No reports match this search yet. Add the first one!</div>{% endif %}
</div>
</section>
</main><footer>RECLAIM · DBMS Mini Project · Flask + SQLite · Built for safer campus recovery</footer>
</body></html>
"""

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
        count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            con.execute("INSERT INTO users(full_name,email,role) VALUES(?,?,?)", ("Demo Student","demo@college.edu","student"))
            uid = con.execute("SELECT user_id FROM users WHERE email=?", ("demo@college.edu",)).fetchone()[0]
            con.execute("INSERT INTO items(title,category,description,location,item_status,reporter_id) VALUES(?,?,?,?,?,?)",
                         ("Scientific Calculator","Books / Stationery","Grey calculator with a small sticker on the back.","Central Library","FOUND",uid))
            con.execute("INSERT INTO items(title,category,description,location,item_status,reporter_id) VALUES(?,?,?,?,?,?)",
                         ("Black Wireless Earbuds","Electronics","Small black case, brand logo on lid.","Cafeteria","LOST",uid))

@app.route("/")
def index():
    init_db()
    q = request.args.get("q","").strip()
    status = request.args.get("status","").strip()
    with connect() as con:
        stats = {
            "total": con.execute("SELECT COUNT(*) FROM items").fetchone()[0],
            "lost": con.execute("SELECT COUNT(*) FROM items WHERE item_status='LOST'").fetchone()[0],
            "found": con.execute("SELECT COUNT(*) FROM items WHERE item_status='FOUND'").fetchone()[0],
            "returned": con.execute("SELECT COUNT(*) FROM items WHERE item_status='RETURNED'").fetchone()[0],
        }
        sql = """SELECT i.*, u.full_name FROM items i JOIN users u ON u.user_id=i.reporter_id WHERE
                 (lower(i.title) LIKE lower(?) OR lower(i.location) LIKE lower(?) OR lower(i.description) LIKE lower(?))"""
        args = [f"%{q}%",f"%{q}%",f"%{q}%"]
        if status:
            sql += " AND i.item_status=?"
            args.append(status)
        sql += " ORDER BY i.created_at DESC, i.item_id DESC"
        rows = con.execute(sql,args).fetchall()
        items = []
        for r in rows:
            d = dict(r)
            d["claims"] = [dict(c) for c in con.execute(
                """SELECT cl.*, u.full_name FROM claims cl JOIN users u ON u.user_id=cl.claimant_id
                   WHERE cl.item_id=? ORDER BY cl.created_at DESC""", (r["item_id"],)).fetchall()]
            items.append(d)
    return render_template_string(PAGE, stats=stats, items=items, q=q, status=status)

@app.route("/add", methods=["POST"])
def add_item():
    try:
        with connect() as con:
            con.execute("INSERT OR IGNORE INTO users(full_name,email) VALUES(?,?)",
                        (request.form["name"].strip(), request.form["email"].strip().lower()))
            user = con.execute("SELECT user_id,full_name FROM users WHERE email=?",
                               (request.form["email"].strip().lower(),)).fetchone()
            con.execute("""INSERT INTO items(title,category,description,location,item_status,reporter_id)
                           VALUES(?,?,?,?,?,?)""",
                        (request.form["title"].strip(), request.form["category"],
                         request.form["description"].strip(), request.form["location"].strip(),
                         request.form["status"], user["user_id"]))
        flash("Report published successfully.")
    except sqlite3.IntegrityError:
        flash("Could not publish this report. Check the submitted details.")
    return redirect(url_for("index"))

@app.route("/claim/<int:item_id>", methods=["POST"])
def claim_item(item_id):
    try:
        with connect() as con:
            con.execute("INSERT OR IGNORE INTO users(full_name,email) VALUES(?,?)",
                        (request.form["name"].strip(),request.form["email"].strip().lower()))
            user = con.execute("SELECT user_id FROM users WHERE email=?",
                               (request.form["email"].strip().lower(),)).fetchone()
            item = con.execute("SELECT item_status FROM items WHERE item_id=?", (item_id,)).fetchone()
            if not item or item["item_status"] not in ("LOST","FOUND"):
                flash("Claims can only be submitted for active LOST or FOUND reports.")
            else:
                con.execute("INSERT INTO claims(item_id,claimant_id,proof) VALUES(?,?,?)",
                            (item_id,user["user_id"],request.form["proof"].strip()))
                flash("Claim submitted. The report owner can review it below.")
    except sqlite3.IntegrityError:
        flash("You have already submitted a claim for this item, or the details are invalid.")
    return redirect(url_for("index"))

@app.route("/review/<int:claim_id>", methods=["POST"])
def review_claim(claim_id):
    decision = request.form.get("decision")
    if decision not in ("APPROVED","REJECTED"):
        flash("Invalid claim decision.")
        return redirect(url_for("index"))
    with connect() as con:
        claim = con.execute("SELECT item_id,claim_status FROM claims WHERE claim_id=?", (claim_id,)).fetchone()
        if not claim or claim["claim_status"] != "PENDING":
            flash("This claim has already been reviewed.")
        else:
            con.execute("UPDATE claims SET claim_status=? WHERE claim_id=?", (decision,claim_id))
            if decision == "APPROVED":
                con.execute("UPDATE items SET item_status='CLAIMED' WHERE item_id=?", (claim["item_id"],))
                con.execute("""UPDATE claims SET claim_status='REJECTED'
                               WHERE item_id=? AND claim_id<>? AND claim_status='PENDING'""",
                            (claim["item_id"],claim_id))
            flash("Claim review saved.")
    return redirect(url_for("index"))

@app.route("/returned/<int:item_id>", methods=["POST"])
def mark_returned(item_id):
    with connect() as con:
        con.execute("UPDATE items SET item_status='RETURNED' WHERE item_id=? AND item_status='CLAIMED'", (item_id,))
    flash("Item marked as returned.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    print("RECLAIM is running at http://127.0.0.1:5000")
    app.run(debug=True)
