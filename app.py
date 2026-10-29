import os
import requests
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'otr3_secret_key_2026'

# إعدادات Turso
TURSO_URL = os.environ.get("TURSO_URL", "").strip().replace("libsql://", "https://")
TURSO_TOKEN = os.environ.get("TURSO_TOKEN", "").strip()

def execute_query(sql, args=None):
    if not TURSO_URL or not TURSO_TOKEN:
        raise Exception("TURSO_URL or TURSO_TOKEN is missing")
        
    url = TURSO_URL + "/v2/pipeline"
    headers = {
        "Authorization": f"Bearer {TURSO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    stmt = {"sql": sql}
    if args:
        stmt["args"] = [{"type": "text", "value": str(a)} for a in args]
        
    payload = {
        "requests": [
            {"type": "execute", "stmt": stmt},
            {"type": "close"}
        ]
    }
    
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    if r.status_code != 200:
        raise Exception(f"HTTP Error {r.status_code}: {r.text}")
        
    data = r.json()
    if "results" in data and len(data["results"]) > 0:
        res = data["results"][0]
        if res.get("type") == "error":
            raise Exception(f"Turso Error: {res.get('error', {}).get('message')}")
        if "response" in res and res["response"].get("type") == "execute":
            return res["response"]["result"]
    return None

def init_db():
    # جدول المتقدمين
    execute_query("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            discord_name TEXT, 
            ign TEXT, 
            age TEXT, 
            role TEXT, 
            company TEXT, 
            description TEXT,
            status TEXT
        )
    """)
    try:
        execute_query("ALTER TABLE applications ADD COLUMN description TEXT")
    except Exception: pass

    # جدول الشركات
    execute_query("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    
    # إضافة شركات افتراضية إذا كان الجدول فارغاً
    res = execute_query("SELECT count(*) FROM companies")
    count = int(res["rows"][0][0]["value"]) if res and res.get("rows") else 0
    if count == 0:
        default_companies = ["شركة الشمال (North)", "شركة الصحراء (Sahara)", "شركة السريع (Express)"]
        for c in default_companies:
            execute_query("INSERT INTO companies (name) VALUES (?)", [c])

init_db()

def get_companies():
    res = execute_query("SELECT id, name FROM companies ORDER BY id ASC")
    if not res or not res.get("rows"): return []
    return [{"id": row[0]["value"], "name": row[1]["value"]} for row in res["rows"]]

# --- التصميم الجديد ---
HTML_LAYOUT = """
<!doctype html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Of Europe3 online | VTC</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  :root {
    --primary: #5865F2;
    --primary-hover: #4752C4;
    --bg-dark: #0f1115;
    --card-bg: rgba(30, 33, 36, 0.7);
    --text-main: #f2f3f5;
    --text-muted: #b5bac1;
    --success: #23a559;
    --danger: #da373c;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { 
    font-family: 'Tajawal', sans-serif; 
    background: linear-gradient(135deg, #0f1115 0%, #1a1c23 100%);
    color: var(--text-main); 
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .header { 
    width: 100%; 
    padding: 30px 20px; 
    text-align: center; 
    background: rgba(15, 17, 21, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    margin-bottom: 30px;
  }
  .header h1 { 
    font-size: 28px; 
    font-weight: 800;
    color: #fff;
    text-shadow: 0 0 20px rgba(88, 101, 242, 0.5);
  }
  .header h1 span { color: var(--primary); }
  
  .container { 
    width: 100%;
    max-width: 700px; 
    background: var(--card-bg); 
    border-radius: 16px; 
    padding: 30px; 
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 40px;
  }
  
  .form-group { margin-bottom: 20px; position: relative; }
  label { display: block; margin-bottom: 8px; color: var(--text-muted); font-weight: 500; font-size: 15px; }
  input, select, textarea { 
    width: 100%; 
    padding: 14px; 
    border-radius: 10px; 
    border: 1px solid rgba(255,255,255,0.1); 
    background: rgba(0, 0, 0, 0.2); 
    color: #fff; 
    font-size: 16px; 
    font-family: inherit;
    transition: all 0.3s ease;
  }
  input:focus, select:focus, textarea:focus { 
    outline: none; 
    border-color: var(--primary); 
    box-shadow: 0 0 10px rgba(88, 101, 242, 0.3);
    background: rgba(0, 0, 0, 0.4);
  }
  textarea { resize: vertical; min-height: 80px; }
  
  .btn { 
    width: 100%; 
    padding: 15px; 
    border: none; 
    border-radius: 10px; 
    background: linear-gradient(90deg, var(--primary) 0%, #7289da 100%);
    color: white; 
    font-size: 18px; 
    font-weight: bold; 
    cursor: pointer; 
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 15px rgba(88, 101, 242, 0.4);
    font-family: inherit;
  }
  .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(88, 101, 242, 0.6); }
  .btn:active { transform: translateY(0); }
  
  .alert { padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 10px;}
  .alert-success { background: rgba(35, 165, 89, 0.2); color: #4ade80; border: 1px solid rgba(35, 165, 89, 0.3); }
  .alert-error { background: rgba(218, 55, 60, 0.2); color: #f87171; border: 1px solid rgba(218, 55, 60, 0.3); }
  
  a { color: var(--primary); text-decoration: none; transition: color 0.2s; }
  a:hover { color: #7289da; }
  
  .table-container { overflow-x: auto; width: 100%; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 30px;}
  .admin-table { width: 100%; border-collapse: collapse; text-align: right; }
  .admin-table th, .admin-table td { padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); }
  .admin-table th { background: rgba(0,0,0,0.3); color: var(--text-muted); font-weight: 700; font-size: 14px; }
  .admin-table tr:hover { background: rgba(255,255,255,0.02); }
  
  .badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; }
  .badge-driver { background: rgba(88, 101, 242, 0.2); color: #a3b8ff; }
  .badge-manager { background: rgba(168, 85, 247, 0.2); color: #d8b4fe; }
  
  .actions { display: flex; gap: 8px; }
  .btn-sm { padding: 8px 12px; border-radius: 8px; border: none; cursor: pointer; font-family: inherit; font-weight: bold; color: #fff; transition: 0.2s; display: flex; align-items: center; gap: 5px; font-size: 13px;}
  .btn-accept { background: var(--success); }
  .btn-accept:hover { background: #1e8e4c; }
  .btn-reject { background: var(--danger); }
  .btn-reject:hover { background: #b9282d; }
  
  .login-link { text-align: center; margin-top: 20px; font-size: 14px; }
  
  /* إدارة الشركات */
  .manage-companies { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
  .company-list { list-style: none; padding: 0; margin-top: 15px; }
  .company-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 8px; }
</style>
</head>
<body>
  <div class="header">
    <h1>🚚 <span>Of Europe3</span> online | نظام الشركات</h1>
  </div>
  <div class="container">
    {{ content|safe }}
  </div>
</body>
</html>
"""

HOME_HTML = """
<h2 style="margin-bottom: 15px; font-size: 22px;">مرحباً بك في نظام التوظيف</h2>
<p style="color: var(--text-muted); margin-bottom: 25px; line-height: 1.6;">انضم إلى أحد شركاتنا الكبرى في سيرفر Of Europe3 online. املأ الاستمارة بدقة وسيتواصل معك المدير قريباً.</p>
{% if msg %}<div class="alert alert-success"><i class="fas fa-check-circle"></i> {{ msg }}</div>{% endif %}
<form method="post" action="/apply">
  <div class="form-group">
    <label><i class="fab fa-discord"></i> اسمك في الديسكورد</label>
    <input type="text" name="discord_name" required placeholder="مثال: Ben_Misso#1234">
  </div>
  <div class="form-group">
    <label><i class="fas fa-gamepad"></i> اسمك داخل اللعبة (IGN)</label>
    <input type="text" name="ign" required placeholder="الاسم الذي تظهر به في OTR3">
  </div>
  <div class="form-group">
    <label><i class="fas fa-calendar-alt"></i> العمر</label>
    <input type="number" name="age" required min="10" max="99">
  </div>
  <div class="form-group">
    <label><i class="fas fa-user-tie"></i> نوع الطلب</label>
    <select name="role" required>
      <option value="سائق">سائق (Driver)</option>
      <option value="مدير شركة">مدير شركة (Manager)</option>
    </select>
  </div>
  <div class="form-group">
    <label><i class="fas fa-building"></i> الشركة المطلوبة</label>
    <select name="company" required>
      {% for c in companies %}
      <option value="{{ c.name }}">{{ c.name }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="form-group">
    <label><i class="fas fa-pen"></i> نبذة عنك (اختياري)</label>
    <textarea name="description" rows="3" placeholder="اكتب خبرتك، عدد ساعات لعبك، أو لماذا نختارك..."></textarea>
  </div>
  <button type="submit" class="btn"><i class="fas fa-paper-plane"></i> إرسال الطلب</button>
</form>
<div class="login-link"><a href="/admin"><i class="fas fa-lock"></i> دخول الإدارة</a></div>
"""

ADMIN_LOGIN_HTML = """
<h2 style="text-align:center; margin-bottom: 25px;">لوحة الإدارة</h2>
{% if error %}<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> {{ error }}</div>{% endif %}
<form method="post" action="/admin">
  <div class="form-group">
    <label><i class="fas fa-key"></i> كلمة المرور</label>
    <input type="password" name="password" required style="text-align: center; font-size: 20px; letter-spacing: 2px;">
  </div>
  <button type="submit" class="btn">دخول</button>
</form>
"""

ADMIN_DASHBOARD_HTML = """
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
  <h2>الطلبات المعلقة</h2>
  <div>
    <a href="/" style="margin-left: 15px;"><i class="fas fa-home"></i> الرئيسية</a>
    <a href="/logout" style="color: var(--danger);"><i class="fas fa-sign-out-alt"></i> خروج</a>
  </div>
</div>
<div class="table-container">
  <table class="admin-table">
    <tr><th>الديسكورد</th><th>اسم اللعبة</th><th>العمر</th><th>الرتبة</th><th>الشركة</th><th>النبذة</th><th>إجراء</th></tr>
    {% for app in apps %}
    <tr>
      <td style="font-weight: bold; color: #a3b8ff;">{{ app[1] }}</td>
      <td>{{ app[2] }}</td>
      <td>{{ app[3] }}</td>
      <td>
        {% if app[4] == 'مدير شركة' %}
          <span class="badge badge-manager">{{ app[4] }}</span>
        {% else %}
          <span class="badge badge-driver">{{ app[4] }}</span>
        {% endif %}
      </td>
      <td>{{ app[5] }}</td>
      <td style="max-width: 150px; font-size: 13px; color: #b5bac1;">{{ app[6] or '-' }}</td>
      <td>
        <div class="actions">
          <form method="post" action="/action/{{ app[0] }}" style="display:inline;">
            <button name="action" value="accept" class="btn-sm btn-accept"><i class="fas fa-check"></i> قبول</button>
            <button name="action" value="reject" class="btn-sm btn-reject"><i class="fas fa-times"></i> رفض</button>
          </form>
        </div>
      </td>
    </tr>
    {% else %}
    <tr><td colspan="7" style="text-align:center; padding: 30px; color: var(--text-muted);">لا توجد طلبات جديدة حالياً.</td></tr>
    {% endfor %}
  </table>
</div>

<div class="manage-companies">
  <h3 style="margin-bottom: 15px; color: #fff;"><i class="fas fa-city"></i> إدارة الشركات</h3>
  <form method="post" action="/add_company" style="display: flex; gap: 10px;">
    <input type="text" name="company_name" required placeholder="اسم الشركة الجديدة..." style="margin-bottom: 0;">
    <button type="submit" class="btn-sm btn-accept" style="padding: 12px 20px; font-size: 15px;"><i class="fas fa-plus"></i> إضافة</button>
  </form>
  <ul class="company-list">
    {% for comp in companies %}
    <li class="company-item">
      <span><i class="fas fa-building" style="color: var(--primary);"></i> {{ comp.name }}</span>
      <form method="post" action="/delete_company/{{ comp.id }}" style="margin:0;">
        <button type="submit" class="btn-sm btn-reject" style="padding: 6px 10px;"><i class="fas fa-trash"></i></button>
      </form>
    </li>
    {% endfor %}
  </ul>
</div>
"""

@app.route("/", methods=["GET"])
def home():
    msg = request.args.get("msg")
    companies = get_companies()
    return render_template_string(HTML_LAYOUT, content=render_template_string(HOME_HTML, companies=companies, msg=msg))

@app.route("/apply", methods=["POST"])
def apply():
    discord_name = request.form.get("discord_name")
    ign = request.form.get("ign")
    age = request.form.get("age")
    role = request.form.get("role")
    company = request.form.get("company")
    description = request.form.get("description", "")
    
    try:
        execute_query(
            "INSERT INTO applications (discord_name, ign, age, role, company, description, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')",
            [discord_name, ign, age, role, company, description]
        )
        return redirect(url_for('home', msg="تم إرسال طلبك بنجاح! انتظر مراجعة الإدارة."))
    except Exception as e:
        return f"<div class='alert alert-error'>حدث خطأ في قاعدة البيانات: {str(e)}</div>", 500

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == "admin123":
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template_string(HTML_LAYOUT, content=render_template_string(ADMIN_LOGIN_HTML, error="كلمة المرور خاطئة"))
    
    if not session.get('admin'):
        return render_template_string(HTML_LAYOUT, content=render_template_string(ADMIN_LOGIN_HTML, error=None))
    
    try:
        result = execute_query("SELECT * FROM applications WHERE status='pending' ORDER BY id DESC")
        raw_rows = result.get("rows", []) if result else []
        apps = []
        for row in raw_rows:
            parsed_row = [col.get("value") for col in row]
            apps.append(parsed_row)
    except Exception as e:
        return f"<div class='alert alert-error'>خطأ في الإدارة: {str(e)}</div>", 500
        
    companies = get_companies()
    return render_template_string(HTML_LAYOUT, content=render_template_string(ADMIN_DASHBOARD_HTML, apps=apps, companies=companies))

@app.route("/add_company", methods=["POST"])
def add_company():
    if not session.get('admin'): return redirect(url_for('admin'))
    name = request.form.get("company_name").strip()
    if name:
        try:
            execute_query("INSERT INTO companies (name) VALUES (?)", [name])
        except Exception:
            pass # تجاهل الخطأ إذا كانت الشركة موجودة مسبقاً
    return redirect(url_for('admin'))

@app.route("/delete_company/<int:id>", methods=["POST"])
def delete_company(id):
    if not session.get('admin'): return redirect(url_for('admin'))
    execute_query("DELETE FROM companies WHERE id=?", [str(id)])
    return redirect(url_for('admin'))

@app.route("/action/<int:id>", methods=["POST"])
def action(id):
    if not session.get('admin'): return redirect(url_for('admin'))
    action = request.form.get("action")
    status = "accepted" if action == "accept" else "rejected"
    
    execute_query("UPDATE applications SET status=? WHERE id=?", [status, str(id)])
    return redirect(url_for('admin'))

@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
