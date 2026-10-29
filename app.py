import os
import libsql_client
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'otr3_secret_key_2026'

# ⚠️⚠️ ضع رابط قاعدة البيانات والرمز اللذين نسختهما من Turso هنا ⚠️⚠️
TURSO_URL = os.environ.get("TURSO_URL", "").replace("libsql://", "https://")
TURSO_TOKEN = os.environ.get("TURSO_TOKEN", "")

client = libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)

def init_db():
    client.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            discord_name TEXT, 
            ign TEXT, 
            age TEXT, 
            role TEXT, 
            company TEXT, 
            status TEXT
        )
    """)

init_db()

COMPANIES = ["شركة الشمال (North)", "شركة الصحراء (Sahara)", "شركة السريع (Express)"]

HTML_LAYOUT = """
<!doctype html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Of Europe3 online | VTC</title>
<style>
  body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #1e2124; color: #fff; margin: 0; padding: 0; }
  .header { background: #282b30; padding: 20px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.5); border-bottom: 2px solid #5865F2; }
  .header h1 { margin: 0; color: #5865F2; font-size: 24px; }
  .container { max-width: 600px; margin: 20px auto; padding: 20px; background: #36393f; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 5px; color: #b9bbbe; font-weight: bold; }
  input, select { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #202225; background: #202225; color: #fff; font-size: 16px; box-sizing: border-box; }
  input:focus, select:focus { outline: none; border-color: #5865F2; }
  button { width: 100%; padding: 12px; border: none; border-radius: 8px; background: #5865F2; color: white; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
  button:hover { background: #4752C4; }
  .alert { padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 15px; font-weight: bold; }
  .alert-success { background: #248046; color: #fff; }
  .alert-error { background: #DA373C; color: #fff; }
  a { color: #00b0f4; text-decoration: none; }
  .admin-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
  .admin-table th, .admin-table td { border: 1px solid #202225; padding: 10px; text-align: right; }
  .admin-table th { background: #202225; }
  .btn-accept { background: #248046; padding: 5px 10px; font-size: 12px; width: auto; margin: 0; }
  .btn-reject { background: #DA373C; padding: 5px 10px; font-size: 12px; width: auto; margin: 0 5px; }
</style>
</head>
<body>
  <div class="header">
    <h1>🚚 Of Europe3 online | نظام الشركات</h1>
  </div>
  <div class="container">
    {{ content|safe }}
  </div>
</body>
</html>
"""

HOME_HTML = """
<h2>مرحباً بك في نظام التوظيف</h2>
<p style="color:#b9bbbe; line-height:1.6;">انضم إلى أحد شركاتنا الكبرى في سيرفر Of Europe3 online. املأ الاستمارة وسيتواصل معك المدير قريباً.</p>
{% if msg %}<div class="alert alert-success">{{ msg }}</div>{% endif %}
<form method="post" action="/apply">
  <div class="form-group">
    <label>اسمك في الديسكورد</label>
    <input type="text" name="discord_name" required placeholder="مثال: Ben_Misso#1234">
  </div>
  <div class="form-group">
    <label>اسمك داخل اللعبة (IGN)</label>
    <input type="text" name="ign" required placeholder="الاسم الذي تظهر به في OTR3">
  </div>
  <div class="form-group">
    <label>العمر</label>
    <input type="number" name="age" required min="10" max="99">
  </div>
  <div class="form-group">
    <label>نوع الطلب</label>
    <select name="role" required>
      <option value="سائق">سائق (Driver)</option>
      <option value="مدير شركة">مدير شركة (Manager)</option>
    </select>
  </div>
  <div class="form-group">
    <label>الشركة المطلوبة</label>
    <select name="company" required>
      {% for c in companies %}
      <option value="{{ c }}">{{ c }}</option>
      {% endfor %}
    </select>
  </div>
  <button type="submit">إرسال الطلب</button>
</form>
<p style="text-align:center; margin-top:15px; font-size:12px;"><a href="/admin">دخول الإدارة</a></p>
"""

ADMIN_LOGIN_HTML = """
<h2>لوحة الإدارة</h2>
{% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
<form method="post" action="/admin">
  <div class="form-group">
    <label>كلمة المرور</label>
    <input type="password" name="password" required>
  </div>
  <button type="submit">دخول</button>
</form>
"""

ADMIN_DASHBOARD_HTML = """
<h2>الطلبات المعلقة</h2>
<p><a href="/">عودة للرئيسية</a> | <a href="/logout" style="color:#DA373C;">تسجيل خروج</a></p>
<table class="admin-table">
  <tr><th>الديسكورد</th><th>اسم اللعبة</th><th>الرتبة</th><th>الشركة</th><th>إجراء</th></tr>
  {% for app in apps %}
  <tr>
    <td>{{ app[1] }}</td>
    <td>{{ app[2] }}</td>
    <td>{{ app[4] }}</td>
    <td>{{ app[5] }}</td>
    <td>
      <form method="post" action="/action/{{ app[0] }}" style="display:inline;">
        <button name="action" value="accept" class="btn-accept">قبول</button>
        <button name="action" value="reject" class="btn-reject">رفض</button>
      </form>
    </td>
  </tr>
  {% else %}
  <tr><td colspan="5" style="text-align:center;">لا توجد طلبات جديدة حالياً.</td></tr>
  {% endfor %}
</table>
"""

@app.route("/", methods=["GET"])
def home():
    msg = request.args.get("msg")
    return render_template_string(HTML_LAYOUT, content=render_template_string(HOME_HTML, companies=COMPANIES, msg=msg))

@app.route("/apply", methods=["POST"])
def apply():
    discord_name = request.form.get("discord_name")
    ign = request.form.get("ign")
    age = request.form.get("age")
    role = request.form.get("role")
    company = request.form.get("company")
    
    client.execute(
        "INSERT INTO applications (discord_name, ign, age, role, company, status) VALUES (?, ?, ?, ?, ?, 'pending')",
        [discord_name, ign, age, role, company]
    )
    
    return redirect(url_for('home', msg="تم إرسال طلبك بنجاح! انتظر مراجعة الإدارة."))

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
    
    result = client.execute("SELECT * FROM applications WHERE status='pending' ORDER BY id DESC")
    apps = result.rows
    
    return render_template_string(HTML_LAYOUT, content=render_template_string(ADMIN_DASHBOARD_HTML, apps=apps))

@app.route("/action/<int:id>", methods=["POST"])
def action(id):
    if not session.get('admin'): return redirect(url_for('admin'))
    action = request.form.get("action")
    status = "accepted" if action == "accept" else "rejected"
    
    client.execute("UPDATE applications SET status=? WHERE id=?", [status, id])
    
    return redirect(url_for('admin'))

@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
