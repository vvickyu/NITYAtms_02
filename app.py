"""
Nitya VFX Studio — Production Management System
Streamlit + SQLite | Works on Streamlit Cloud
"""

import streamlit as st
import sqlite3, os, datetime, hashlib, pandas as pd
from pathlib import Path

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Nitya VFX Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = Path(__file__).parent / "nitya_vfx.db"

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&display=swap');

/* Global */
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0A0C10; color: #E8EAF0; }
.block-container { padding: 1rem 2rem 2rem; max-width: 100%; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Cards */
.nx-card {
    background: #161A22; border: 1px solid #1F2430;
    border-radius: 14px; padding: 20px; margin-bottom: 14px;
}
.nx-card-blue { border-left: 3px solid #00D4FF; }
.nx-card-green { border-left: 3px solid #00E5A0; }
.nx-card-yellow { border-left: 3px solid #FFD60A; }
.nx-card-red { border-left: 3px solid #FF4444; }
.nx-card-purple { border-left: 3px solid #A855F7; }
.nx-card-orange { border-left: 3px solid #FF9F43; }

/* Stat boxes */
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; }
.stat-box {
    background: #161A22; border: 1px solid #1F2430;
    border-radius: 12px; padding: 16px 20px;
    flex: 1; min-width: 140px;
}
.stat-label { font-size: 10px; font-weight: 700; color: #5A6278;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; }
.stat-value { font-size: 22px; font-weight: 800; }
.c-blue { color: #00D4FF; } .c-green { color: #00E5A0; }
.c-yellow { color: #FFD60A; } .c-red { color: #FF4444; }
.c-purple { color: #A855F7; } .c-orange { color: #FF9F43; }
.c-muted { color: #5A6278; }

/* Badges */
.badge {
    display: inline-block; font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 20px; margin: 1px;
}
.badge-blue { background: rgba(0,212,255,0.1); color:#00D4FF; border:1px solid rgba(0,212,255,0.3); }
.badge-green { background: rgba(0,229,160,0.1); color:#00E5A0; border:1px solid rgba(0,229,160,0.3); }
.badge-yellow { background: rgba(255,214,10,0.1); color:#FFD60A; border:1px solid rgba(255,214,10,0.3); }
.badge-red { background: rgba(255,68,68,0.1); color:#FF4444; border:1px solid rgba(255,68,68,0.3); }
.badge-purple { background: rgba(168,85,247,0.1); color:#A855F7; border:1px solid rgba(168,85,247,0.3); }
.badge-muted { background: rgba(90,98,120,0.15); color:#5A6278; border:1px solid rgba(90,98,120,0.3); }

/* Nav */
.nx-nav {
    background: rgba(10,12,16,0.95); border-bottom: 1px solid #1F2430;
    padding: 12px 24px; display: flex; align-items: center;
    margin: -1rem -2rem 1.5rem; gap: 12px;
}
.nx-logo { font-size: 18px; font-weight: 800; color: #E8EAF0; }
.nx-logo span { color: #00D4FF; }
.nx-pill {
    font-size: 11px; font-weight: 700; padding: 4px 12px;
    border-radius: 20px; background: #161A22; border: 1px solid;
}
.nx-pill-admin { color:#00D4FF; border-color:#00D4FF; }
.nx-pill-coord { color:#FF9F43; border-color:#FF9F43; }
.nx-pill-artist { color:#00E5A0; border-color:#00E5A0; }

/* Section title */
.sec-title {
    font-size: 11px; font-weight: 700; color: #5A6278;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 12px;
}

/* Tables */
.nx-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.nx-table th {
    font-size: 10px; font-weight: 700; color: #5A6278;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 8px 12px; border-bottom: 1px solid #1F2430; text-align: left;
}
.nx-table td { padding: 10px 12px; border-bottom: 1px solid #1F2430; }
.nx-table tr:hover td { background: rgba(255,255,255,0.02); }

/* Progress bar */
.prog-bar-bg {
    background: #1F2430; border-radius: 4px; height: 6px;
    overflow: hidden; margin-top: 4px;
}
.prog-bar-fill { height: 100%; border-radius: 4px; background: #00D4FF; }

/* Correction card */
.correction-card {
    background: #111318; border: 1px solid rgba(255,68,68,0.25);
    border-left: 3px solid #FF4444; border-radius: 10px;
    padding: 12px 14px; margin-bottom: 8px;
}
.file-card {
    background: #111318; border: 1px solid #1F2430;
    border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        client TEXT, start_date TEXT, deadline TEXT,
        budget REAL DEFAULT 0, desc TEXT, status TEXT DEFAULT 'Active');

    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        role TEXT, rate REAL DEFAULT 0, password TEXT NOT NULL,
        rate_from TEXT);

    CREATE TABLE IF NOT EXISTS artist_shots (
        artist_id INTEGER, shot_id INTEGER,
        PRIMARY KEY(artist_id, shot_id));

    CREATE TABLE IF NOT EXISTS shots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER,
        name TEXT NOT NULL, task TEXT, frames INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Not Started', est_hours REAL DEFAULT 0,
        outsourced INTEGER DEFAULT 0);

    CREATE TABLE IF NOT EXISTS outsource (
        id INTEGER PRIMARY KEY AUTOINCREMENT, shot_id INTEGER,
        vendor TEXT, cost REAL DEFAULT 0, delivery_date TEXT,
        status TEXT DEFAULT 'Pending');

    CREATE TABLE IF NOT EXISTS time_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, artist_id INTEGER,
        shot_id INTEGER, log_date TEXT, duration_ms INTEGER DEFAULT 0,
        note TEXT, created_at TEXT DEFAULT (datetime('now')));

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, vendor TEXT,
        amount REAL DEFAULT 0, pay_month TEXT, project_id INTEGER,
        project_name TEXT, pct REAL DEFAULT 100, note TEXT,
        pay_date TEXT DEFAULT (date('now')));

    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT, inv_no TEXT UNIQUE,
        project_id INTEGER, inv_date TEXT, due_date TEXT, inv_month TEXT,
        pct REAL DEFAULT 100, studio TEXT DEFAULT 'Nitya VFX Studio',
        amount REAL DEFAULT 0, paid_amount REAL DEFAULT 0,
        notes TEXT, status TEXT DEFAULT 'Unpaid');

    CREATE TABLE IF NOT EXISTS shot_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT, shot_id INTEGER,
        version TEXT, name TEXT, link TEXT, note TEXT,
        uploaded_by TEXT, uploaded_by_role TEXT, ts INTEGER);

    CREATE TABLE IF NOT EXISTS shot_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, shot_id INTEGER,
        by_name TEXT, by_role TEXT, log_text TEXT, ts INTEGER);

    CREATE TABLE IF NOT EXISTS admin_creds (
        id INTEGER PRIMARY KEY, username TEXT DEFAULT 'admin',
        password TEXT DEFAULT 'admin');

    CREATE TABLE IF NOT EXISTS coord_creds (
        id INTEGER PRIMARY KEY, username TEXT DEFAULT 'coord',
        password TEXT DEFAULT 'coord');
    """)
    conn.execute("INSERT OR IGNORE INTO admin_creds(id,username,password) VALUES(1,'admin','admin')")
    conn.execute("INSERT OR IGNORE INTO coord_creds(id,username,password) VALUES(1,'coord','coord')")

    # Seed if empty
    if conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
        conn.executemany("INSERT INTO projects(name,client,deadline,budget,desc,status) VALUES(?,?,?,?,?,?)", [
            ('Project Aurora','Netflix India','2025-08-30',500000,'High-end VFX for feature film.','Active'),
            ('Project Nebula','Amazon Prime','2025-07-15',300000,'Series VFX work.','Active'),
            ('Project Comet','Hotstar','2025-09-20',200000,'Short film VFX.','Active'),
        ])
        conn.executemany("INSERT INTO artists(name,role,rate,password) VALUES(?,?,?,?)", [
            ('Ravi Kumar','VFX Artist',312,'ravi123'),
            ('Priya Mehra','Compositor',375,'priya123'),
            ('Sahil Verma','Rotoscoper',250,'sahil123'),
        ])
        conn.executemany("INSERT INTO shots(project_id,name,status,est_hours) VALUES(?,?,?,?)", [
            (1,'SH_0010','In Progress',8),(1,'SH_0020','Not Started',12),
            (2,'SH_0030','In Progress',6),(2,'SH_0040','Review',10),
            (3,'SH_0050','Not Started',5),
        ])
        conn.executemany("INSERT OR IGNORE INTO artist_shots VALUES(?,?)",
                         [(1,1),(1,2),(2,3),(3,4),(3,5)])
    conn.commit(); conn.close()

init_db()

# ─────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────
def db_rows(sql, params=()):
    conn = get_db()
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close(); return rows

def db_one(sql, params=()):
    conn = get_db()
    r = conn.execute(sql, params).fetchone()
    conn.close(); return dict(r) if r else None

def db_exec(sql, params=()):
    conn = get_db()
    cur = conn.execute(sql, params)
    conn.commit(); last = cur.lastrowid; conn.close(); return last

def today(): return datetime.date.today().isoformat()
def now_ms(): return int(datetime.datetime.now().timestamp() * 1000)
def fmt_inr(n): return f"₹{int(n):,}"
def fmt_hrs(ms): h=int(ms//3600000); m=int((ms%3600000)//60000); return f"{h}h {m}m"
def status_color(s):
    return {'Active':'#00D4FF','Complete':'#00E5A0','Hold':'#FFD60A',
            'Archived':'#5A6278','In Progress':'#00D4FF','Review':'#FFD60A',
            'Not Started':'#5A6278','Paused':'#FF6B35'}.get(s,'#5A6278')

def get_shot_logged_ms(shot_id):
    rows = db_rows("SELECT SUM(duration_ms) as total FROM time_logs WHERE shot_id=?", (shot_id,))
    return rows[0]['total'] or 0 if rows else 0

def get_project_logged_ms(project_id):
    rows = db_rows("""SELECT SUM(t.duration_ms) as total FROM time_logs t
        JOIN shots s ON s.id=t.shot_id WHERE s.project_id=?""", (project_id,))
    return rows[0]['total'] or 0 if rows else 0

def get_project_inhouse_cost(project_id):
    shots = db_rows("SELECT id FROM shots WHERE project_id=? AND outsourced=0", (project_id,))
    total = 0
    for shot in shots:
        assignments = db_rows("""SELECT a.rate, SUM(t.duration_ms) as ms
            FROM artist_shots ast JOIN artists a ON a.id=ast.artist_id
            LEFT JOIN time_logs t ON t.shot_id=ast.shot_id AND t.artist_id=a.id
            WHERE ast.shot_id=? GROUP BY a.id""", (shot['id'],))
        for row in assignments:
            total += (row['rate'] or 0) * ((row['ms'] or 0) / 3600000)
    return total

def get_project_outsource_cost(project_id):
    row = db_one("""SELECT SUM(o.cost) as total FROM outsource o
        JOIN shots s ON s.id=o.shot_id WHERE s.project_id=?""", (project_id,))
    return row['total'] or 0 if row else 0

def get_artist_shots(artist_id):
    return db_rows("""SELECT s.*, p.name as project_name FROM artist_shots ast
        JOIN shots s ON s.id=ast.shot_id
        LEFT JOIN projects p ON p.id=s.project_id
        WHERE ast.artist_id=?""", (artist_id,))

def get_artist_today_ms(artist_id):
    row = db_one("SELECT SUM(duration_ms) as total FROM time_logs WHERE artist_id=? AND log_date=?",
                 (artist_id, today()))
    return row['total'] or 0 if row else 0

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
def ss(key, default=None):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

ss('role', None)       # 'admin' | 'coord' | 'artist'
ss('user', None)       # artist dict if role==artist
ss('page', 'login')
ss('admin_tab', 'Projects')
ss('coord_tab', 'Projects')
ss('view_project', None)
ss('msg', None)

def set_page(p): st.session_state.page = p
def set_tab(tab, role='admin'):
    if role == 'admin': st.session_state.admin_tab = tab
    else: st.session_state.coord_tab = tab
def show_msg(m, t='success'): st.session_state.msg = (m, t)

# ─────────────────────────────────────────
# NAV
# ─────────────────────────────────────────
def render_nav():
    role = st.session_state.role
    pill_class = {'admin':'admin','coord':'coord','artist':'artist'}.get(role,'')
    pill_label = {'admin':'Nitya Admin','coord':'Coordinator',
                  'artist': st.session_state.user['name'] if st.session_state.user else ''}.get(role,'')

    col1, col2, col3 = st.columns([3,6,2])
    with col1:
        st.markdown('<div class="nx-logo">🎬 Nitya <span>VFX Studio</span></div>', unsafe_allow_html=True)
    with col3:
        if role:
            st.markdown(f'<div class="nx-pill nx-pill-{pill_class}">{pill_label}</div>', unsafe_allow_html=True)
            if st.button("⇤ Logout", key="nav_logout"):
                for k in ['role','user','page','view_project']:
                    st.session_state[k] = None if k != 'page' else 'login'
                st.rerun()
    st.divider()

def show_flash():
    msg = st.session_state.get('msg')
    if msg:
        text, typ = msg
        if typ == 'success': st.success(text)
        elif typ == 'error': st.error(text)
        else: st.info(text)
        st.session_state.msg = None

# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────
def page_login():
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px;">
      <div style="font-size:48px;margin-bottom:12px;">🎬</div>
      <h1 style="font-size:28px;font-weight:800;margin:0;">Nitya VFX Studio</h1>
      <p style="color:#5A6278;margin-top:6px;">Production Management System</p>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1,2,1])[1]
    with col:
        with st.container():
            role = st.selectbox("Login as", ["Admin", "Coordinator", "Artist"], key="login_role_sel")

            if role == "Admin":
                with st.form("admin_form"):
                    u = st.text_input("Username", placeholder="admin")
                    p = st.text_input("Password", type="password", placeholder="••••••")
                    if st.form_submit_button("Enter Admin Portal", use_container_width=True, type="primary"):
                        cred = db_one("SELECT * FROM admin_creds WHERE id=1")
                        if cred and cred['username']==u and cred['password']==p:
                            st.session_state.role='admin'; st.session_state.page='admin'
                            st.session_state.admin_tab='Projects'; st.rerun()
                        else: st.error("Wrong username or password")

            elif role == "Coordinator":
                with st.form("coord_form"):
                    u = st.text_input("Username", placeholder="coord")
                    p = st.text_input("Password", type="password", placeholder="••••••")
                    if st.form_submit_button("Enter Coordinator Portal", use_container_width=True, type="primary"):
                        cred = db_one("SELECT * FROM coord_creds WHERE id=1")
                        if cred and cred['username']==u and cred['password']==p:
                            st.session_state.role='coord'; st.session_state.page='coord'
                            st.session_state.coord_tab='Projects'; st.rerun()
                        else: st.error("Wrong username or password")

            else:
                artists = db_rows("SELECT id, name FROM artists ORDER BY name")
                names = {a['name']: a['id'] for a in artists}
                with st.form("artist_form"):
                    sel = st.selectbox("Your Name", list(names.keys()))
                    p   = st.text_input("Password", type="password", placeholder="••••••")
                    if st.form_submit_button("Enter Artist Portal", use_container_width=True, type="primary"):
                        aid = names[sel]
                        artist = db_one("SELECT * FROM artists WHERE id=?", (aid,))
                        if artist and artist['password']==p:
                            st.session_state.role='artist'
                            st.session_state.user=dict(artist)
                            st.session_state.page='artist'; st.rerun()
                        else: st.error("Wrong password")

# ─────────────────────────────────────────
# ADMIN PORTAL
# ─────────────────────────────────────────
def page_admin():
    show_flash()
    tabs = ["Projects","Artists","Shots","Time Logs","Outsource","Salary","Outsource Payment"]
    tab_objs = st.tabs(tabs)

    with tab_objs[0]: admin_projects()
    with tab_objs[1]: admin_artists()
    with tab_objs[2]: admin_shots()
    with tab_objs[3]: admin_timelogs()
    with tab_objs[4]: admin_outsource()
    with tab_objs[5]: admin_salary()
    with tab_objs[6]: admin_payments()

# ── ADMIN: PROJECTS ──
def admin_projects():
    st.markdown('<div class="sec-title">📁 Projects</div>', unsafe_allow_html=True)

    # Stats
    projects = db_rows("SELECT * FROM projects ORDER BY id")
    active = sum(1 for p in projects if p['status']=='Active')
    total_budget = sum(p['budget'] or 0 for p in projects)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Projects", len(projects))
    with c2: st.metric("Active", active)
    with c3: st.metric("Total Budget", fmt_inr(total_budget))
    with c4: st.metric("Completed", sum(1 for p in projects if p['status']=='Complete'))

    # Add project
    with st.expander("➕ New Project"):
        with st.form("add_proj"):
            c1,c2 = st.columns(2)
            name   = c1.text_input("Project Name *")
            client = c2.text_input("Client Name")
            c1,c2,c3 = st.columns(3)
            start  = c1.date_input("Start Date", value=None)
            dead   = c2.date_input("Deadline", value=None)
            budget = c3.number_input("Budget (₹)", min_value=0, step=10000)
            desc   = st.text_area("Description", height=70)
            status = st.selectbox("Status", ["Active","Complete","Hold","Archived"])
            if st.form_submit_button("Create Project", type="primary"):
                if not name: st.error("Project name required")
                else:
                    db_exec("INSERT INTO projects(name,client,start_date,deadline,budget,desc,status) VALUES(?,?,?,?,?,?,?)",
                            (name, client, str(start) if start else None, str(dead) if dead else None, budget, desc, status))
                    show_msg(f"Project '{name}' created!"); st.rerun()

    # List
    search = st.text_input("🔍 Search projects", key="proj_search")
    for p in projects:
        if search and search.lower() not in (p['name']+p.get('client','')).lower(): continue

        shots = db_rows("SELECT * FROM shots WHERE project_id=?", (p['id'],))
        done  = sum(1 for s in shots if s['status']=='Complete')
        pct   = int(done/len(shots)*100) if shots else 0
        inh   = get_project_inhouse_cost(p['id'])
        ost   = get_project_outsource_cost(p['id'])
        logged_ms = get_project_logged_ms(p['id'])

        status_badge = f'<span class="badge badge-{"green" if p["status"]=="Active" else "muted"}">{p["status"]}</span>'

        with st.container():
            st.markdown(f"""
            <div class="nx-card nx-card-blue">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div style="font-size:16px;font-weight:800;">{p['name']}</div>
                  <div style="font-size:12px;color:#5A6278;margin-top:2px;">
                    🏢 {p.get('client') or '—'} &nbsp;|&nbsp; Deadline: {p.get('deadline') or '—'}
                  </div>
                </div>
                <div style="text-align:right;">{status_badge}
                  <div style="font-size:11px;color:#5A6278;margin-top:4px;">Budget: <span style="color:#00D4FF;">{fmt_inr(p.get('budget',0))}</span></div>
                </div>
              </div>
              <div style="margin-top:12px;">
                <div style="display:flex;justify-content:space-between;font-size:11px;color:#5A6278;margin-bottom:4px;">
                  <span>Progress: {pct}% ({done}/{len(shots)} shots)</span>
                  <span>Logged: {fmt_hrs(logged_ms)} | In-house: {fmt_inr(inh)} | Outsource: {fmt_inr(ost)}</span>
                </div>
                <div class="prog-bar-bg"><div class="prog-bar-fill" style="width:{pct}%;"></div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            c1,c2,c3,c4,c5 = st.columns([2,2,2,2,1])
            with c1:
                if st.button("📋 View Shots", key=f"view_{p['id']}"):
                    st.session_state.view_project = p['id']
                    st.session_state.admin_tab = 'Shots'
                    st.rerun()
            with c2:
                if st.button("✏️ Edit", key=f"edit_p_{p['id']}"):
                    st.session_state[f'edit_proj_{p["id"]}'] = True
            with c3:
                if st.button("📥 Import Shots", key=f"imp_{p['id']}"):
                    st.session_state[f'import_proj'] = p['id']
            with c5:
                if st.button("🗑️", key=f"del_p_{p['id']}", help="Delete project"):
                    db_exec("DELETE FROM projects WHERE id=?", (p['id'],))
                    show_msg(f"Project deleted"); st.rerun()

            # Edit form inline
            if st.session_state.get(f'edit_proj_{p["id"]}'):
                with st.form(f"edit_proj_form_{p['id']}"):
                    ec1,ec2 = st.columns(2)
                    en = ec1.text_input("Name", value=p['name'])
                    ec = ec2.text_input("Client", value=p.get('client',''))
                    ec1,ec2,ec3 = st.columns(3)
                    es = st.selectbox("Status", ["Active","Complete","Hold","Archived"],
                                     index=["Active","Complete","Hold","Archived"].index(p['status']) if p['status'] in ["Active","Complete","Hold","Archived"] else 0)
                    eb = ec3.number_input("Budget", value=float(p.get('budget',0)), min_value=0.0)
                    ed = st.text_area("Desc", value=p.get('desc',''))
                    if st.form_submit_button("Update", type="primary"):
                        db_exec("UPDATE projects SET name=?,client=?,budget=?,desc=?,status=? WHERE id=?",
                                (en,ec,eb,ed,es,p['id']))
                        st.session_state[f'edit_proj_{p["id"]}'] = False
                        show_msg("Project updated!"); st.rerun()
                    if st.form_submit_button("Cancel"):
                        st.session_state[f'edit_proj_{p["id"]}'] = False; st.rerun()

            # Import shots from CSV/pasted data
            if st.session_state.get('import_proj') == p['id']:
                st.markdown("**Import Shots** — paste data (one shot per line: `Shot Name, Frames, Task, Est Hours`)")
                raw = st.text_area("Paste shot data", key=f"import_raw_{p['id']}",
                                   placeholder="SH_0010, 120, Roto, 8\nSH_0020, 240, Comp, 12")
                uploaded = st.file_uploader("Or upload CSV", type=['csv'], key=f"csv_{p['id']}")
                if st.button("Import Now", key=f"do_import_{p['id']}", type="primary"):
                    lines = []
                    if uploaded:
                        import io
                        df = pd.read_csv(io.BytesIO(uploaded.read()))
                        for _, row in df.iterrows():
                            lines.append(list(row))
                    elif raw:
                        for line in raw.strip().split('\n'):
                            parts = [x.strip() for x in line.split(',')]
                            if parts: lines.append(parts)
                    count = 0
                    for parts in lines:
                        if not parts or not parts[0]: continue
                        nm = parts[0]; fr = int(parts[1]) if len(parts)>1 and str(parts[1]).isdigit() else 0
                        task = parts[2] if len(parts)>2 else ''; est = float(parts[3]) if len(parts)>3 else 0
                        try: est = float(str(parts[3]).strip()) if len(parts)>3 else 0
                        except: est = 0
                        db_exec("INSERT INTO shots(project_id,name,frames,task,est_hours,status) VALUES(?,?,?,?,?,?)",
                                (p['id'], nm, fr, task, est, 'Not Started'))
                        count += 1
                    st.session_state.import_proj = None
                    show_msg(f"{count} shots imported!"); st.rerun()
                if st.button("Cancel Import", key=f"cancel_imp_{p['id']}"):
                    st.session_state.import_proj = None; st.rerun()

# ── ADMIN: ARTISTS ──
def admin_artists():
    st.markdown('<div class="sec-title">👤 Artists</div>', unsafe_allow_html=True)
    artists = db_rows("SELECT * FROM artists ORDER BY name")

    with st.expander("➕ Add Artist"):
        with st.form("add_artist"):
            c1,c2,c3,c4 = st.columns(4)
            name = c1.text_input("Name *")
            role = c2.text_input("Role", placeholder="Compositor")
            rate = c3.number_input("Rate (₹/hr)", min_value=0, step=50)
            pw   = c4.text_input("Password *", type="password")
            if st.form_submit_button("Add Artist", type="primary"):
                if not name or not pw: st.error("Name and password required")
                else:
                    db_exec("INSERT INTO artists(name,role,rate,password) VALUES(?,?,?,?)", (name,role,rate,pw))
                    show_msg(f"Artist '{name}' added!"); st.rerun()

    # Table
    for a in artists:
        shots = db_rows("SELECT s.name FROM artist_shots ast JOIN shots s ON s.id=ast.shot_id WHERE ast.artist_id=?", (a['id'],))
        today_ms = get_artist_today_ms(a['id'])
        earn_today = int(a['rate'] * today_ms / 3600000)

        with st.container():
            c1,c2,c3,c4,c5,c6 = st.columns([3,2,2,2,2,1])
            c1.markdown(f"**{a['name']}** <br><span style='color:#5A6278;font-size:11px;'>{a.get('role','')}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#00D4FF;font-weight:700;'>₹{a['rate']}/hr</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='color:#00E5A0;'>{fmt_hrs(today_ms)}</span> today", unsafe_allow_html=True)
            c4.markdown(f"<span style='color:#FFD60A;'>₹{earn_today}</span> earned", unsafe_allow_html=True)
            c5.markdown(f"{len(shots)} shots assigned", unsafe_allow_html=True)
            with c6:
                if st.button("🗑️", key=f"del_a_{a['id']}"):
                    db_exec("DELETE FROM artists WHERE id=?", (a['id'],)); show_msg("Artist deleted"); st.rerun()

            # Edit rate inline
            with st.expander(f"Edit {a['name']}", expanded=False):
                with st.form(f"edit_a_{a['id']}"):
                    ec1,ec2,ec3,ec4 = st.columns(4)
                    en = ec1.text_input("Name", value=a['name'])
                    er = ec2.text_input("Role", value=a.get('role',''))
                    erate = ec3.number_input("Rate (₹/hr)", value=float(a['rate']), min_value=0.0, step=50.0)
                    epw = ec4.text_input("New Password (blank=keep)", type="password")
                    if st.form_submit_button("Update", type="primary"):
                        if erate != a['rate']:
                            db_exec("INSERT INTO rate_history(artist_id,old_rate,from_date,to_date) VALUES(?,?,?,?)",
                                    (a['id'], a['rate'], a.get('rate_from') or today(), today()))
                        pw_val = epw if epw else a['password']
                        db_exec("UPDATE artists SET name=?,role=?,rate=?,password=?,rate_from=? WHERE id=?",
                                (en,er,erate,pw_val,today(),a['id']))
                        show_msg("Artist updated!"); st.rerun()
        st.divider()

# ── ADMIN: SHOTS ──
def admin_shots():
    st.markdown('<div class="sec-title">🎬 All Shots</div>', unsafe_allow_html=True)
    projects = db_rows("SELECT * FROM projects ORDER BY name")
    proj_map = {p['id']: p['name'] for p in projects}

    # Filters
    c1,c2,c3 = st.columns([2,2,2])
    proj_filter = c1.selectbox("Filter by Project", ["All"] + [p['name'] for p in projects], key="shot_proj_filter")
    status_filter = c2.selectbox("Filter by Status", ["All","Not Started","In Progress","Review","Complete","Paused"], key="shot_status_filter")

    where = "WHERE 1=1"
    params = []
    if proj_filter != "All":
        pid = next((p['id'] for p in projects if p['name']==proj_filter), None)
        if pid: where += " AND s.project_id=?"; params.append(pid)
    if status_filter != "All":
        where += " AND s.status=?"; params.append(status_filter)

    shots = db_rows(f"""SELECT s.*, p.name as project_name FROM shots s
        LEFT JOIN projects p ON p.id=s.project_id {where} ORDER BY s.id""", params)

    # Add shot
    with st.expander("➕ Add Shot"):
        with st.form("add_shot"):
            c1,c2,c3,c4,c5 = st.columns(5)
            psel  = c1.selectbox("Project", [p['name'] for p in projects], key="add_shot_proj")
            sname = c2.text_input("Shot Name", placeholder="SH_0060")
            stask = c3.text_input("Task", placeholder="Roto / Comp")
            sfr   = c4.number_input("Frames", min_value=0)
            sest  = c5.number_input("Est. Hours", min_value=0.0, step=0.5)
            artists = db_rows("SELECT * FROM artists ORDER BY name")
            asel = st.selectbox("Assign To", ["Unassigned"] + [a['name'] for a in artists], key="add_shot_artist")
            if st.form_submit_button("Add Shot", type="primary"):
                pid = next(p['id'] for p in projects if p['name']==psel)
                sid = db_exec("INSERT INTO shots(project_id,name,task,frames,est_hours,status) VALUES(?,?,?,?,?,?)",
                              (pid,sname,stask,sfr,sest,'Not Started'))
                if asel != "Unassigned":
                    aid = next(a['id'] for a in artists if a['name']==asel)
                    db_exec("INSERT OR IGNORE INTO artist_shots VALUES(?,?)", (aid,sid))
                show_msg("Shot added!"); st.rerun()

    # Show shots table
    for shot in shots:
        logged_ms = get_shot_logged_ms(shot['id'])
        artists_assigned = db_rows("""SELECT a.name FROM artist_shots ast
            JOIN artists a ON a.id=ast.artist_id WHERE ast.shot_id=?""", (shot['id'],))
        files = db_rows("SELECT COUNT(*) as c FROM shot_files WHERE shot_id=?", (shot['id'],))
        logs  = db_rows("SELECT COUNT(*) as c FROM shot_logs WHERE shot_id=?", (shot['id'],))
        file_ct = files[0]['c'] if files else 0
        log_ct  = logs[0]['c'] if logs else 0

        sc = status_color(shot['status'])
        names_str = ", ".join(a['name'] for a in artists_assigned) or "—"

        st.markdown(f"""
        <div style="background:#111318;border:1px solid #1F2430;border-radius:10px;padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;gap:12px;">
          <div style="font-family:monospace;font-weight:700;font-size:14px;min-width:100px;">{shot['name']}</div>
          <div style="flex:1;">
            <span style="font-size:11px;color:#5A6278;">{shot.get('project_name','—')}</span>
            {f'<span class="badge badge-purple" style="font-size:10px;">{shot["task"]}</span>' if shot.get("task") else ''}
            {f'<span class="badge badge-yellow">{shot["frames"]}f</span>' if shot.get("frames") else ''}
          </div>
          <span style="color:{sc};font-size:12px;font-weight:700;">{shot['status']}</span>
          <span style="color:#5A6278;font-size:11px;">{names_str}</span>
          <span style="color:#5A6278;font-size:11px;">{fmt_hrs(logged_ms)}</span>
          {f'<span class="badge badge-purple">📎{file_ct}</span>' if file_ct else ''}
          {f'<span class="badge badge-red">💬{log_ct}</span>' if log_ct else ''}
        </div>
        """, unsafe_allow_html=True)

        c1,c2,c3,c4,c5,c6 = st.columns([2,2,2,2,2,1])
        new_status = c1.selectbox("Status", ["Not Started","In Progress","Review","Complete","Paused"],
                                   index=["Not Started","In Progress","Review","Complete","Paused"].index(shot['status']) if shot['status'] in ["Not Started","In Progress","Review","Complete","Paused"] else 0,
                                   key=f"ss_{shot['id']}")
        if new_status != shot['status']:
            db_exec("UPDATE shots SET status=? WHERE id=?", (new_status, shot['id'])); st.rerun()

        with c2:
            if st.button("📁 Files", key=f"files_{shot['id']}"):
                st.session_state[f'show_files_{shot["id"]}'] = not st.session_state.get(f'show_files_{shot["id"]}', False)
        with c3:
            if st.button("💬 Log", key=f"log_{shot['id']}"):
                st.session_state[f'show_log_{shot["id"]}'] = not st.session_state.get(f'show_log_{shot["id"]}', False)
        with c6:
            if st.button("🗑️", key=f"del_s_{shot['id']}"):
                db_exec("DELETE FROM shots WHERE id=?", (shot['id'],)); show_msg("Shot deleted"); st.rerun()

        # Files panel
        if st.session_state.get(f'show_files_{shot["id"]}'):
            shot_files_panel(shot['id'], 'admin')

        # Correction log panel
        if st.session_state.get(f'show_log_{shot["id"]}'):
            correction_log_panel(shot['id'], 'admin')

def shot_files_panel(shot_id, role):
    with st.container():
        st.markdown("**📁 Shot Files & Links**")
        files = db_rows("SELECT * FROM shot_files WHERE shot_id=? ORDER BY ts DESC", (shot_id,))
        for f in files:
            uploader = f.get('uploaded_by') or '—'
            ver_color = "#00E5A0" if (f.get('uploaded_by_role')=='artist') else "#00D4FF"
            link = f.get('link','')
            link_html = f'<a href="{link}" target="_blank" style="color:#00D4FF;">🔗 Open</a>' if link else ''
            st.markdown(f"""
            <div class="file-card">
              <span style="background:rgba(0,212,255,0.1);color:{ver_color};border:1px solid;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;">{f.get('version','—')}</span>
              <div style="flex:1;font-size:13px;font-weight:600;">{f.get('name','—')}
                <div style="font-size:10px;color:#5A6278;">{uploader} · {f.get('note','')}</div>
              </div>
              {link_html}
            </div>
            """, unsafe_allow_html=True)

        # Add link
        with st.form(f"add_file_{shot_id}"):
            c1,c2,c3 = st.columns(3)
            ver   = c1.text_input("Version", placeholder="v01")
            fname = c2.text_input("File Name")
            note  = c3.text_input("Note")
            link  = st.text_input("Google Drive / Dropbox Link", placeholder="https://drive.google.com/...")
            if st.form_submit_button("Add Link", type="primary"):
                if not link: st.error("Please paste a link")
                else:
                    uploader = "Nitya Admin" if role=='admin' else "Coordinator"
                    ver = ver or f"v{len(files)+1:02d}"
                    db_exec("INSERT INTO shot_files(shot_id,version,name,link,note,uploaded_by,uploaded_by_role,ts) VALUES(?,?,?,?,?,?,?,?)",
                            (shot_id, ver, fname, link, note, uploader, role, now_ms()))
                    show_msg("Link added!"); st.rerun()

def correction_log_panel(shot_id, role):
    with st.container():
        st.markdown("**💬 Correction Log**")
        logs = db_rows("SELECT * FROM shot_logs WHERE shot_id=? ORDER BY ts DESC", (shot_id,))
        for log in logs:
            ts = datetime.datetime.fromtimestamp((log['ts'] or 0)/1000).strftime('%d %b %Y %H:%M') if log.get('ts') else '—'
            st.markdown(f"""
            <div class="correction-card">
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-weight:700;color:#FF9F43;font-size:12px;">{log.get('by_name','—')}</span>
                <span style="color:#5A6278;font-size:10px;">{ts}</span>
              </div>
              <div style="font-size:13px;">{log.get('log_text','')}</div>
            </div>
            """, unsafe_allow_html=True)

        with st.form(f"add_log_{shot_id}_{role}"):
            text = st.text_area("Correction / Note", placeholder="Describe what needs to be fixed...")
            if st.form_submit_button("Save Correction", type="primary"):
                if not text: st.error("Please enter a note")
                else:
                    by = "Nitya Admin" if role=='admin' else "Coordinator"
                    db_exec("INSERT INTO shot_logs(shot_id,by_name,by_role,log_text,ts) VALUES(?,?,?,?,?)",
                            (shot_id, by, role, text, now_ms()))
                    show_msg("Correction logged!"); st.rerun()

# ── ADMIN: TIME LOGS ──
def admin_timelogs():
    st.markdown('<div class="sec-title">⏱ Time Logs</div>', unsafe_allow_html=True)
    logs = db_rows("""SELECT t.*, a.name as artist_name, s.name as shot_name, p.name as project_name
        FROM time_logs t
        JOIN artists a ON a.id=t.artist_id
        JOIN shots s ON s.id=t.shot_id
        JOIN projects p ON p.id=s.project_id
        ORDER BY t.created_at DESC LIMIT 200""")

    if not logs:
        st.info("No time logs yet. Artists need to log time from their portal.")
        return

    c1,c2 = st.columns(2)
    total_ms = sum(l['duration_ms'] or 0 for l in logs)
    c1.metric("Total Hours Logged", f"{total_ms/3600000:.1f}h")
    c2.metric("Sessions", len(logs))

    df = pd.DataFrame([{
        'Date': l['log_date'], 'Artist': l['artist_name'],
        'Project': l['project_name'], 'Shot': l['shot_name'],
        'Duration': fmt_hrs(l['duration_ms'] or 0)
    } for l in logs])
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── ADMIN: OUTSOURCE ──
def admin_outsource():
    st.markdown('<div class="sec-title">🔗 Outsource</div>', unsafe_allow_html=True)
    entries = db_rows("""SELECT o.*, s.name as shot_name, p.name as project_name
        FROM outsource o JOIN shots s ON s.id=o.shot_id
        JOIN projects p ON p.id=s.project_id ORDER BY o.id""")

    total_cost = sum(e['cost'] or 0 for e in entries)
    c1,c2 = st.columns(2)
    c1.metric("Total Outsource Cost", fmt_inr(total_cost))
    c2.metric("Entries", len(entries))

    # Add
    shots = db_rows("SELECT s.id, s.name, p.name as pname FROM shots s JOIN projects p ON p.id=s.project_id ORDER BY s.id")
    with st.expander("➕ Add Outsource Entry"):
        with st.form("add_out"):
            shot_opts = {f"{s['pname']} → {s['name']}": s['id'] for s in shots}
            c1,c2,c3 = st.columns(3)
            ssel   = c1.selectbox("Shot", list(shot_opts.keys()))
            vendor = c2.text_input("Vendor / Studio")
            cost   = c3.number_input("Cost (₹)", min_value=0, step=1000)
            c1,c2 = st.columns(2)
            ddate  = c1.date_input("Delivery Date", value=None)
            status = c2.selectbox("Status", ["Pending","Delivered","Revision","Cancelled"])
            if st.form_submit_button("Add", type="primary"):
                sid = shot_opts[ssel]
                db_exec("UPDATE shots SET outsourced=1 WHERE id=?", (sid,))
                db_exec("INSERT INTO outsource(shot_id,vendor,cost,delivery_date,status) VALUES(?,?,?,?,?)",
                        (sid, vendor, cost, str(ddate) if ddate else None, status))
                show_msg("Outsource entry added!"); st.rerun()

    for e in entries:
        c1,c2,c3,c4,c5,c6 = st.columns([2,2,2,2,2,1])
        c1.markdown(f"**{e['shot_name']}** <br><span style='color:#5A6278;font-size:11px;'>{e['project_name']}</span>", unsafe_allow_html=True)
        c2.text(e.get('vendor','—'))
        c3.markdown(f"<span style='color:#F59E0B;font-weight:700;'>{fmt_inr(e['cost'] or 0)}</span>", unsafe_allow_html=True)
        new_st = c4.selectbox("", ["Pending","Delivered","Revision","Cancelled"],
                               index=["Pending","Delivered","Revision","Cancelled"].index(e['status']) if e['status'] in ["Pending","Delivered","Revision","Cancelled"] else 0,
                               key=f"ost_{e['id']}")
        if new_st != e['status']:
            db_exec("UPDATE outsource SET status=? WHERE id=?", (new_st, e['id'])); st.rerun()
        c5.text(e.get('delivery_date','—'))
        with c6:
            if st.button("🗑️", key=f"del_o_{e['id']}"):
                db_exec("DELETE FROM outsource WHERE id=?", (e['id'],)); show_msg("Deleted"); st.rerun()

# ── ADMIN: SALARY ──
def admin_salary():
    st.markdown('<div class="sec-title">💰 Salary Report</div>', unsafe_allow_html=True)
    artists = db_rows("SELECT * FROM artists ORDER BY name")

    c1,c2 = st.columns(2)
    month_filter = c1.text_input("Filter by month (YYYY-MM)", placeholder="2025-05")

    for a in artists:
        where = "WHERE t.artist_id=?"
        params = [a['id']]
        if month_filter:
            where += " AND t.log_date LIKE ?"
            params.append(month_filter + '%')

        logs = db_rows(f"""SELECT t.shot_id, t.log_date, t.duration_ms, s.name as shot_name, p.name as proj_name
            FROM time_logs t JOIN shots s ON s.id=t.shot_id JOIN projects p ON p.id=s.project_id
            {where} ORDER BY t.log_date""", params)

        total_ms = sum(l['duration_ms'] or 0 for l in logs)
        total_hrs = total_ms / 3600000
        salary = int(a['rate'] * total_hrs)

        with st.expander(f"**{a['name']}** — {a.get('role','')} — ₹{a['rate']}/hr | {total_hrs:.1f}h | Salary: {fmt_inr(salary)}"):
            if logs:
                df = pd.DataFrame([{
                    'Date': l['log_date'], 'Project': l['proj_name'],
                    'Shot': l['shot_name'], 'Hours': f"{(l['duration_ms'] or 0)/3600000:.2f}h",
                    'Earned': f"₹{int(a['rate']*(l['duration_ms'] or 0)/3600000)}"
                } for l in logs])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No time logs found for this period.")

# ── ADMIN: PAYMENTS ──
def admin_payments():
    st.markdown('<div class="sec-title">💳 Outsource Payments</div>', unsafe_allow_html=True)

    out_entries = db_rows("SELECT o.vendor, SUM(o.cost) as total FROM outsource o GROUP BY o.vendor")
    payments = db_rows("SELECT * FROM payments ORDER BY id DESC")
    vendor_paid = {}
    for p in payments:
        vendor_paid[p['vendor']] = vendor_paid.get(p['vendor'], 0) + (p['amount'] or 0)

    # Stats
    total_owed = sum(e['total'] or 0 for e in out_entries)
    total_paid = sum(p['amount'] or 0 for p in payments)
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Owed to Vendors", fmt_inr(total_owed))
    c2.metric("Total Paid", fmt_inr(total_paid))
    c3.metric("Balance", fmt_inr(max(0, total_owed - total_paid)))

    vendors = [e['vendor'] for e in out_entries if e['vendor']]
    projects = db_rows("SELECT * FROM projects ORDER BY name")

    with st.expander("➕ Record Payment"):
        with st.form("add_payment"):
            c1,c2,c3 = st.columns(3)
            vendor = c1.selectbox("Vendor", vendors) if vendors else c1.text_input("Vendor")
            month  = c2.text_input("Month (YYYY-MM)", value=today()[:7])
            proj   = c3.selectbox("Project", ["—"] + [p['name'] for p in projects])
            c1,c2,c3 = st.columns(3)
            pct    = c1.number_input("Payment %", min_value=1, max_value=100, value=100)
            amount = c2.number_input("Amount (₹)", min_value=0, step=1000)
            note   = c3.text_input("Note")
            if st.form_submit_button("Record Payment", type="primary"):
                if not amount: st.error("Enter amount")
                else:
                    pid = next((p['id'] for p in projects if p['name']==proj), None)
                    db_exec("INSERT INTO payments(vendor,amount,pay_month,project_id,project_name,pct,note) VALUES(?,?,?,?,?,?,?)",
                            (vendor, amount, month, pid, proj if proj!='—' else None, pct, note))
                    show_msg("Payment recorded!"); st.rerun()

    # Per-vendor breakdown
    for e in out_entries:
        v = e['vendor']
        owed = e['total'] or 0
        paid = vendor_paid.get(v, 0)
        bal  = owed - paid
        pcts = min(100, int(paid/owed*100)) if owed > 0 else 100

        status_c = "#00E5A0" if bal<=0 else "#FFD60A" if bal<owed else "#FF4444"
        status_t = "FULLY PAID" if bal<=0 else "PARTIAL" if paid>0 else "UNPAID"

        with st.expander(f"**{v}** — Owed: {fmt_inr(owed)} | Paid: {fmt_inr(paid)} | Balance: {fmt_inr(max(0,bal))}"):
            st.markdown(f'<span style="color:{status_c};font-weight:700;">{status_t}</span>', unsafe_allow_html=True)
            vp = [p for p in payments if p['vendor']==v]
            if vp:
                df = pd.DataFrame([{'Month':p['pay_month'],'Project':p.get('project_name','—'),
                    'Amount':fmt_inr(p['amount']),'%':f"{p.get('pct',100)}%",'Note':p.get('note','')} for p in vp])
                st.dataframe(df, use_container_width=True, hide_index=True)

            # Delete payments
            for p in vp:
                if st.button(f"Delete ₹{int(p['amount'])} ({p['pay_month']})", key=f"delpay_{p['id']}"):
                    db_exec("DELETE FROM payments WHERE id=?", (p['id'],)); show_msg("Deleted"); st.rerun()

# ─────────────────────────────────────────
# COORDINATOR PORTAL
# ─────────────────────────────────────────
def page_coord():
    show_flash()
    tabs = st.tabs(["Projects","Shots","Artists","Outsource"])
    with tabs[0]: coord_projects()
    with tabs[1]: coord_shots()
    with tabs[2]: coord_artists()
    with tabs[3]: admin_outsource()

def coord_projects():
    st.markdown('<div class="sec-title">📁 Projects</div>', unsafe_allow_html=True)
    projects = db_rows("SELECT * FROM projects ORDER BY id")
    for p in projects:
        shots = db_rows("SELECT * FROM shots WHERE project_id=?", (p['id'],))
        done  = sum(1 for s in shots if s['status']=='Complete')
        pct   = int(done/len(shots)*100) if shots else 0
        st.markdown(f"""
        <div class="nx-card nx-card-orange">
          <div style="font-size:15px;font-weight:800;">{p['name']}</div>
          <div style="font-size:12px;color:#5A6278;">🏢 {p.get('client','—')} | Deadline: {p.get('deadline','—')}</div>
          <div style="margin-top:8px;">
            <div style="font-size:11px;color:#5A6278;margin-bottom:4px;">{pct}% complete ({done}/{len(shots)} shots)</div>
            <div class="prog-bar-bg"><div class="prog-bar-fill" style="width:{pct}%;background:#FF9F43;"></div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def coord_shots():
    st.markdown('<div class="sec-title">🎬 Shots</div>', unsafe_allow_html=True)
    shots = db_rows("""SELECT s.*, p.name as project_name FROM shots s
        LEFT JOIN projects p ON p.id=s.project_id ORDER BY s.id""")
    artists = db_rows("SELECT * FROM artists ORDER BY name")

    for shot in shots:
        sc = status_color(shot['status'])
        logged_ms = get_shot_logged_ms(shot['id'])
        assigned = db_rows("""SELECT a.name FROM artist_shots ast
            JOIN artists a ON a.id=ast.artist_id WHERE ast.shot_id=?""", (shot['id'],))
        names_str = ", ".join(a['name'] for a in assigned) or "Unassigned"

        c1,c2,c3,c4,c5 = st.columns([2,2,2,2,2])
        c1.markdown(f"**{shot['name']}**<br><span style='font-size:11px;color:#5A6278;'>{shot.get('project_name','—')}</span>", unsafe_allow_html=True)
        c2.markdown(f"<span style='color:{sc};font-weight:700;'>{shot['status']}</span>", unsafe_allow_html=True)
        c3.text(names_str)
        c4.text(fmt_hrs(logged_ms))

        with c5:
            if st.button("📁 Files", key=f"cf_{shot['id']}"):
                st.session_state[f'cfiles_{shot["id"]}'] = not st.session_state.get(f'cfiles_{shot["id"]}', False)

        if st.session_state.get(f'cfiles_{shot["id"]}'):
            shot_files_panel(shot['id'], 'coord')
            correction_log_panel(shot['id'], 'coord')

        # Assign artist
        with st.expander(f"Assign Artist to {shot['name']}", expanded=False):
            with st.form(f"ca_{shot['id']}"):
                asel = st.selectbox("Artist", [a['name'] for a in artists], key=f"cas_{shot['id']}")
                if st.form_submit_button("Assign"):
                    aid = next(a['id'] for a in artists if a['name']==asel)
                    db_exec("INSERT OR IGNORE INTO artist_shots VALUES(?,?)", (aid, shot['id']))
                    show_msg(f"{asel} assigned to {shot['name']}!"); st.rerun()
        st.divider()

def coord_artists():
    st.markdown('<div class="sec-title">👤 Artists Overview</div>', unsafe_allow_html=True)
    artists = db_rows("SELECT * FROM artists ORDER BY name")
    for a in artists:
        today_ms = get_artist_today_ms(a['id'])
        shots = get_artist_shots(a['id'])
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(f"**{a['name']}**<br><span style='color:#5A6278;font-size:11px;'>{a.get('role','')}</span>", unsafe_allow_html=True)
        c2.metric("Today", fmt_hrs(today_ms))
        c3.metric("Shots", len(shots))
        c4.metric("Rate", f"₹{a['rate']}/hr")
        st.divider()

# ─────────────────────────────────────────
# ARTIST PORTAL
# ─────────────────────────────────────────
def page_artist():
    show_flash()
    a = st.session_state.user
    if not a:
        st.session_state.page = 'login'; st.rerun()

    today_ms  = get_artist_today_ms(a['id'])
    earn_today = int(a['rate'] * today_ms / 3600000)
    shots = get_artist_shots(a['id'])

    # Header stats
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Today Hours", fmt_hrs(today_ms))
    c2.metric("Today Earned", fmt_inr(earn_today))
    c3.metric("Rate", f"₹{a['rate']}/hr")
    c4.metric("My Shots", len(shots))

    st.divider()

    # Time logging
    st.markdown('<div class="sec-title">⏱ Log Time</div>', unsafe_allow_html=True)

    if shots:
        with st.form("log_time_form"):
            c1,c2,c3 = st.columns([3,2,2])
            shot_opts = {f"{s['project_name']} → {s['name']}" + (f" [{s.get('task','')}]" if s.get('task') else ''): s['id'] for s in shots}
            sel_shot = c1.selectbox("Shot", list(shot_opts.keys()))
            hours    = c2.number_input("Hours", min_value=0, max_value=24, step=1)
            minutes  = c3.number_input("Minutes", min_value=0, max_value=59, step=5)
            note     = st.text_input("Note (optional)", placeholder="What did you work on?")
            if st.form_submit_button("✅ Log Time", type="primary"):
                sid = shot_opts[sel_shot]
                ms  = (hours * 3600 + minutes * 60) * 1000
                if ms <= 0: st.error("Enter hours or minutes")
                else:
                    db_exec("INSERT INTO time_logs(artist_id,shot_id,log_date,duration_ms,note) VALUES(?,?,?,?,?)",
                            (a['id'], sid, today(), ms, note))
                    show_msg(f"Logged {hours}h {minutes}m!"); st.rerun()
    else:
        st.info("No shots assigned to you yet. Ask your admin or coordinator.")

    # Today's log
    today_logs = db_rows("""SELECT t.*, s.name as shot_name, p.name as proj_name
        FROM time_logs t JOIN shots s ON s.id=t.shot_id JOIN projects p ON p.id=s.project_id
        WHERE t.artist_id=? AND t.log_date=? ORDER BY t.id DESC""", (a['id'], today()))

    if today_logs:
        st.markdown('<div class="sec-title">📋 Today\'s Sessions</div>', unsafe_allow_html=True)
        for l in today_logs:
            c1,c2,c3 = st.columns([3,2,2])
            c1.markdown(f"**{l['shot_name']}** <span style='color:#5A6278;font-size:11px;'>({l['proj_name']})</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#00D4FF;font-weight:700;'>{fmt_hrs(l['duration_ms'] or 0)}</span>", unsafe_allow_html=True)
            c3.text(l.get('note',''))

    st.divider()

    # My shots with files & corrections
    st.markdown('<div class="sec-title">🎬 My Shots</div>', unsafe_allow_html=True)
    for shot in shots:
        logged_ms = get_shot_logged_ms(shot['id'])
        corrections = db_rows("SELECT * FROM shot_logs WHERE shot_id=? ORDER BY ts DESC", (shot['id'],))
        files = db_rows("SELECT * FROM shot_files WHERE shot_id=? ORDER BY ts DESC", (shot['id'],))
        admin_files = [f for f in files if f.get('uploaded_by_role') != 'artist']
        sc = status_color(shot['status'])

        # Correction alert
        corr_alert = ""
        if corrections:
            corr_alert = f'<div style="background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.25);border-radius:6px;padding:6px 10px;font-size:11px;color:#FF4444;margin-top:6px;">💬 {len(corrections)} correction note{"s" if len(corrections)>1 else ""} from coordinator</div>'

        st.markdown(f"""
        <div class="nx-card nx-card-green">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="font-size:15px;font-weight:800;">{shot['name']}</div>
              <div style="font-size:11px;color:#5A6278;">{shot.get('project_name','—')}
                {f' · <span style="color:#FF9F43;">{shot["task"]}</span>' if shot.get("task") else ''}
                {f' · <span style="color:#FFD60A;font-family:monospace;">{shot["frames"]}f</span>' if shot.get("frames") else ''}
              </div>
            </div>
            <span style="color:{sc};font-weight:700;">{shot['status']}</span>
          </div>
          <div style="font-size:12px;color:#5A6278;margin-top:6px;">Logged: <span style="color:#00D4FF;">{fmt_hrs(logged_ms)}</span>
            {f' | Est: {shot["est_hours"]}h' if shot.get("est_hours") else ''}
          </div>
          {corr_alert}
        </div>
        """, unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        with c1:
            if admin_files and st.button(f"📥 Source Files ({len(admin_files)})", key=f"af_{shot['id']}"):
                st.session_state[f'afiles_{shot["id"]}'] = not st.session_state.get(f'afiles_{shot["id"]}', False)
        with c2:
            if st.button(f"📤 My Output ({len([f for f in files if f.get('uploaded_by_role')=='artist'])})", key=f"mf_{shot['id']}"):
                st.session_state[f'myfiles_{shot["id"]}'] = not st.session_state.get(f'myfiles_{shot["id"]}', False)
        with c3:
            if corrections and st.button(f"💬 View Corrections ({len(corrections)})", key=f"vcorr_{shot['id']}"):
                st.session_state[f'vcorr_{shot["id"]}'] = not st.session_state.get(f'vcorr_{shot["id"]}', False)

        # Show source files (read-only)
        if st.session_state.get(f'afiles_{shot["id"]}'):
            st.markdown("**📥 Source / Reference Files from Admin:**")
            for f in admin_files:
                link = f.get('link','')
                if link:
                    st.markdown(f"- **{f.get('version','—')}** {f.get('name','—')} — [{f.get('note','')or'Open'}]({link})")

        # Upload output link
        if st.session_state.get(f'myfiles_{shot["id"]}'):
            st.markdown("**📤 Upload Output Link:**")
            my_files = [f for f in files if f.get('uploaded_by_role')=='artist']
            for f in my_files:
                link = f.get('link','')
                st.markdown(f"- **{f.get('version','—')}** {f.get('name','—')} {f.get('note','')}" + (f" — [Open]({link})" if link else ""))

            with st.form(f"artist_upload_{shot['id']}"):
                c1,c2 = st.columns(2)
                ver   = c1.text_input("Version", placeholder="v01", key=f"av_{shot['id']}")
                fname = c2.text_input("File Name", key=f"afn_{shot['id']}")
                link  = st.text_input("Google Drive / Dropbox Link", key=f"al_{shot['id']}")
                note  = st.text_input("Note", placeholder="e.g. Roto pass complete", key=f"an_{shot['id']}")
                if st.form_submit_button("Submit Output", type="primary"):
                    if not link: st.error("Please paste a link")
                    else:
                        ver = ver or f"v{len(my_files)+1:02d}"
                        db_exec("INSERT INTO shot_files(shot_id,version,name,link,note,uploaded_by,uploaded_by_role,ts) VALUES(?,?,?,?,?,?,?,?)",
                                (shot['id'], ver, fname, link, note, a['name'], 'artist', now_ms()))
                        show_msg("Output submitted!"); st.rerun()

        # View corrections
        if st.session_state.get(f'vcorr_{shot["id"]}'):
            st.markdown("**💬 Correction Notes:**")
            for log in corrections:
                ts = datetime.datetime.fromtimestamp((log['ts'] or 0)/1000).strftime('%d %b %Y %H:%M') if log.get('ts') else '—'
                st.markdown(f"""
                <div class="correction-card">
                  <div style="font-size:11px;color:#FF9F43;font-weight:700;">{log.get('by_name','—')} · {ts}</div>
                  <div style="margin-top:4px;">{log.get('log_text','')}</div>
                </div>
                """, unsafe_allow_html=True)

    # Edit own rate
    st.divider()
    st.markdown('<div class="sec-title">⚙️ My Settings</div>', unsafe_allow_html=True)
    with st.expander("Change My Rate"):
        with st.form("artist_rate"):
            new_rate = st.number_input("New Rate (₹/hr)", value=float(a['rate']), min_value=0.0, step=50.0)
            if st.form_submit_button("Update Rate"):
                if new_rate != a['rate']:
                    db_exec("INSERT INTO rate_history(artist_id,old_rate,from_date,to_date) VALUES(?,?,?,?)",
                            (a['id'], a['rate'], today(), today()))
                    db_exec("UPDATE artists SET rate=?,rate_from=? WHERE id=?", (new_rate, today(), a['id']))
                    st.session_state.user['rate'] = new_rate
                    show_msg("Rate updated! Applies from today."); st.rerun()

# ─────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────
render_nav()

page = st.session_state.get('page', 'login')
role = st.session_state.get('role')

if page == 'login' or not role:
    page_login()
elif page == 'admin' and role == 'admin':
    page_admin()
elif page == 'coord' and role == 'coord':
    page_coord()
elif page == 'artist' and role == 'artist':
    page_artist()
else:
    st.session_state.page = 'login'
    st.session_state.role = None
    st.rerun()
