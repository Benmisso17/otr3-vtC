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
    execute_query("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, ign TEXT, age TEXT, role TEXT, company TEXT, description TEXT, status TEXT
        )
    """)
    try: execute_query("ALTER TABLE applications ADD COLUMN description TEXT")
    except Exception: pass

    execute_query("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE
        )
    """)
    
    res = execute_query("SELECT count(*) FROM companies")
    count = int(res["rows"][0][0]["value"]) if res and res.get("rows") else 0
    if count == 0:
        default_companies = ["شركة الشمال (North)", "شركة الصحراء (Sahara)", "شركة السريع (Express)"]
        for c in default_companies:
            execute_query("INSERT INTO companies (name) VALUES (?)", [c])

    execute_query("CREATE TABLE IF NOT EXISTS family_staff (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, color TEXT)")
    execute_query("CREATE TABLE IF NOT EXISTS family_events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT)")
    execute_query("CREATE TABLE IF NOT EXISTS family_shop (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, price TEXT)")
    
    res_staff = execute_query("SELECT count(*) FROM family_staff")
    staff_count = int(res_staff["rows"][0][0]["value"]) if res_staff and res_staff.get("rows") else 0
    if staff_count == 0:
        default_staff = [
            ("Ammar", "Community Manager", "red-900"), ("!IDRIS", "Lead", "red-500"), ("BEN MISSO", "Lead", "red-500"),
            ("Qx", "Lead", "red-500"), ("Riso", "Lead", "red-500"), ("Rumi", "Lead", "red-500"),
            ("Goodman", "Administrator", "yellow-500"), ("Nashmi", "Administrator", "yellow-500"),
            ("Staff Abdo", "Staff", "purple-500"), ("Staff ABDO", "Staff", "purple-500"), ("Staff Abdulrahman", "Staff", "purple-500"),
            ("Staff khalil", "Staff", "purple-500"), ("Staff Saidi", "Staff", "purple-500"), ("Staff SALIH", "Staff", "purple-500"),
            ("Staff shs", "Staff", "purple-500"), ("Staff Yazan", "Staff", "purple-500")
        ]
        for s in default_staff:
            execute_query("INSERT INTO family_staff (name, role, color) VALUES (?, ?, ?)", list(s))

init_db()

def get_companies():
    res = execute_query("SELECT id, name FROM companies ORDER BY id ASC")
    if not res or not res.get("rows"): return []
    return [{"id": row[0]["value"], "name": row[1]["value"]} for row in res["rows"]]

HTML_LAYOUT = """
<!doctype html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Of Europe3 online | VTC</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  :root { --primary: #5865F2; --primary-hover: #4752C4; --bg-dark: #0f1115; --card-bg: rgba(30, 33, 36, 0.7); --text-main: #f2f3f5; --text-muted: #b5bac1; --success: #23a559; --danger: #da373c; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Tajawal', sans-serif; background: linear-gradient(135deg, #0f1115 0%, #1a1c23 100%); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; align-items: center; }
  .header { width: 100%; padding: 30px 20px; text-align: center; background: rgba(15, 17, 21, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); margin-bottom: 30px; }
  .header h1 { font-size: 28px; font-weight: 800; color: #fff; text-shadow: 0 0 20px rgba(88, 101, 242, 0.5); }
  .header h1 span { color: var(--primary); }
  .container { width: 100%; max-width: 700px; background: var(--card-bg); border-radius: 16px; padding: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 40px; }
  .form-group { margin-bottom: 20px; position: relative; }
  label { display: block; margin-bottom: 8px; color: var(--text-muted); font-weight: 500; font-size: 15px; }
  input, select, textarea { width: 100%; padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0, 0, 0, 0.2); color: #fff; font-size: 16px; font-family: inherit; transition: all 0.3s ease; }
  input:focus, select:focus, textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 10px rgba(88, 101, 242, 0.3); background: rgba(0, 0, 0, 0.4); }
  textarea { resize: vertical; min-height: 80px; }
  .btn { width: 100%; padding: 15px; border: none; border-radius: 10px; background: linear-gradient(90deg, var(--primary) 0%, #7289da 100%); color: white; font-size: 18px; font-weight: bold; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 15px rgba(88, 101, 242, 0.4); font-family: inherit; }
  .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(88, 101, 242, 0.6); }
  .alert { padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 10px;}
  .alert-error { background: rgba(218, 55, 60, 0.2); color: #f87171; border: 1px solid rgba(218, 55, 60, 0.3); }
  .table-container { overflow-x: auto; width: 100%; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 30px;}
</style>
</head>
<body>
  <div class="header"><h1>🚚 <span>Of Europe3</span> online | نظام الشركات</h1></div>
  <div class="container">{{ content|safe }}</div>
</body>
</html>
"""

HOME_HTML = """
<style>
    :root { --primary: #00f2fe; --secondary: #4facfe; --dark-bg: #0f172a; --glass-bg: rgba(255, 255, 255, 0.05); --glass-border: rgba(255, 255, 255, 0.1); }
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
    .vtc-wrapper { display: flex; justify-content: center; align-items: center; min-height: 80vh; position: relative; }
    #particles-js { position: absolute; width: 100%; height: 100%; top: 0; left: 0; z-index: -1; }
    .split-container { position: relative; z-index: 1; display: flex; width: 100%; max-width: 1200px; background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 20px; box-shadow: 0 25px 45px rgba(0, 0, 0, 0.5); overflow: hidden; margin: 20px auto; }
    .info-side { flex: 1; padding: 50px; display: flex; flex-direction: column; justify-content: center; background: linear-gradient(135deg, rgba(0, 242, 254, 0.1), rgba(79, 172, 254, 0.05)); border-left: 1px solid var(--glass-border); }
    .info-side h1 { font-size: 3rem; font-weight: 800; background: linear-gradient(to right, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
    .info-side p { font-size: 1.1rem; line-height: 1.8; color: #cbd5e1; margin-bottom: 30px; }
    .rules-box { background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 12px; border-right: 4px solid var(--primary); }
    .rules-box h3 { margin-bottom: 10px; color: var(--primary); }
    .rules-box ul { list-style: none; padding-right: 0; }
    .rules-box li { margin-bottom: 8px; font-size: 0.95rem; color: #e2e8f0; display: flex; align-items: center; gap: 10px; }
    .rules-box li::before { content: '✦'; color: var(--secondary); }
    .form-side { flex: 1.2; padding: 50px; }
    .form-side h2 { font-size: 2rem; margin-bottom: 30px; font-weight: 600; }
    .input-group { position: relative; margin-bottom: 25px; }
    .input-group label { display: block; margin-bottom: 8px; font-size: 0.9rem; color: #94a3b8; }
    .input-group input, .input-group select, .input-group textarea { width: 100%; padding: 15px; background: rgba(0, 0, 0, 0.3); border: 1px solid var(--glass-border); border-radius: 10px; color: white; font-size: 1rem; transition: all 0.3s ease; outline: none; }
    .input-group input:focus, .input-group select:focus, .input-group textarea:focus { border-color: var(--primary); box-shadow: 0 0 15px rgba(0, 242, 254, 0.3); background: rgba(0, 0, 0, 0.5); }
    .input-group select option { background: var(--dark-bg); color: white; }
    .input-group textarea { resize: none; height: 100px; }
    .char-count { position: absolute; bottom: -20px; left: 0; font-size: 0.8rem; color: #64748b; }
    .btn-submit { width: 100%; padding: 16px; background: linear-gradient(to right, var(--primary), var(--secondary)); border: none; border-radius: 10px; color: #0f172a; font-size: 1.2rem; font-weight: 800; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; margin-top: 10px; display: flex; justify-content: center; align-items: center; gap: 10px; }
    .btn-submit:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0, 242, 254, 0.4); }
    @media (max-width: 900px) { .split-container { flex-direction: column; } .info-side { border-left: none; border-bottom: 1px solid var(--glass-border); padding: 30px; text-align: center; } .info-side h1 { font-size: 2.2rem; } .form-side { padding: 30px; } }
</style>

<div class="vtc-wrapper">
    <div id="particles-js"></div>
    <div class="split-container">
        <div class="info-side">
            <h1>OTR3 VTC</h1>
            <p>مرحباً بك في منصة التسجيل الرسمية لشركات النقل (VTC) في سيرفر <strong>Of Europe3 online</strong>. انضم إلى نخبة السائقين وابدأ رحلتك الاحترافية معنا.</p>
            <div class="rules-box">
                <h3>شروط التسجيل:</h3>
                <ul>
                    <li>الالتزام بقوانين السيرفر المرورية.</li><li>امتلاك رخصة قيادة سارية.</li><li>التوفر والاحترافية في التعامل.</li><li>عدم استخدام أي برامج غش.</li>
                </ul>
            </div>
        </div>
        <div class="form-side">
            <h2>تقديم طلب انضمام</h2>
            <form id="vtcForm" action="/apply" method="POST">
                <div class="input-group"><label>اسم الديسكورد (Discord)</label><input type="text" name="discord_name" id="discord" placeholder="مثال: User#1234" required></div>
                <div class="input-group"><label>اسم اللعبة (In-Game Name)</label><input type="text" name="ign" id="game_name" placeholder="مثال: Ahmed_TR" required></div>
                <div class="input-group"><label>العمر (Age)</label><input type="number" name="age" id="age" placeholder="مثال: 21" min="15" max="99" required></div>
                <div class="input-group">
                    <label>التقديم بصفة (Apply As)</label>
                    <select name="role" id="rank" required>
                        <option value="" disabled selected>اختر نوع التقديم...</option><option value="سائق">سائق (Driver)</option><option value="مدير شركة">مدير شركة (Company Manager)</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>الشركة المراد الانضمام إليها (Company)</label>
                    <select name="company" id="company" required>
                        <option value="" disabled selected>اختر الشركة...</option>
                        {% for c in companies %}<option value="{{ c.name }}">{{ c.name }}</option>{% endfor %}
                    </select>
                </div>
                <div class="input-group"><label>نبذة عنك (Bio)</label><textarea name="description" id="bio" placeholder="اكتب عن خبرتك في القيادة..." maxlength="200" required></textarea><span class="char-count" id="charCount">0 / 200</span></div>
                <button type="submit" class="btn-submit" id="submitBtn"><span>إرسال الطلب</span></button>
            </form>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
<script>
    particlesJS("particles-js", { "particles": { "number": { "value": 60, "density": { "enable": true, "value_area": 800 } }, "color": { "value": ["#00f2fe", "#4facfe"] }, "shape": { "type": "circle" }, "opacity": { "value": 0.5, "random": true }, "size": { "value": 3, "random": true }, "line_linked": { "enable": true, "distance": 150, "color": "#4facfe", "opacity": 0.2, "width": 1 }, "move": { "enable": true, "speed": 1.5, "direction": "none", "random": true, "out_mode": "out" } }, "interactivity": { "detect_on": "canvas", "events": { "onhover": { "enable": true, "mode": "grab" }, "onclick": { "enable": true, "mode": "push" } }, "modes": { "grab": { "distance": 140, "line_linked": { "opacity": 0.5 } } } }, "retina_detect": true });
    const bioInput = document.getElementById('bio'); const charCount = document.getElementById('charCount');
    bioInput.addEventListener('input', () => { charCount.textContent = `${bioInput.value.length} / 200`; });
</script>
"""

ADMIN_LOGIN_HTML = """
<h2 style="text-align:center; margin-bottom: 25px;">لوحة الإدارة</h2>
{% if error %}<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> {{ error }}</div>{% endif %}
<form method="post" action="/admin">
  <div class="form-group"><label><i class="fas fa-key"></i> كلمة المرور</label><input type="password" name="password" required style="text-align: center; font-size: 20px; letter-spacing: 2px;"></div>
  <button type="submit" class="btn">دخول</button>
</form>
"""

ADMIN_DASHBOARD_HTML = """
<div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; margin-top: 20px; text-align: right;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
        <h2 style="color: #00f2fe; font-size: 1.5rem; margin: 0;">الطلبات المعلقة</h2>
        <a href="/logout" style="color: #ef4444; text-decoration: none; font-weight: bold; background: rgba(239, 68, 68, 0.1); padding: 8px 15px; border-radius: 8px;">خروج 🚪</a>
    </div>
    <div style="overflow-x: auto; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.3);">
        <table style="width: 100%; border-collapse: collapse; text-align: right; min-width: 1000px; font-size: 0.95rem; color: #ffffff;">
            <thead style="background: rgba(0,0,0,0.6); color: #00f2fe;">
                <tr style="border-bottom: 2px solid #00f2fe;">
                    <th style="padding: 15px;">الديسكورد</th><th style="padding: 15px;">اسم اللعبة</th><th style="padding: 15px;">العمر</th><th style="padding: 15px;">الرتبة</th><th style="padding: 15px;">الشركة</th><th style="padding: 15px;">الوصف</th><th style="padding: 15px;">الحالة</th><th style="padding: 15px;">إجراء</th>
                </tr>
            </thead>
            <tbody style="color: #e2e8f0;">
                {% for app in apps %}
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 15px; color: #4facfe; font-weight: bold;">{{ app['discord_name'] if app['discord_name'] else 'غير متوفر' }}</td>
                    <td style="padding: 15px;">{{ app['ign'] if app['ign'] else 'غير متوفر' }}</td><td style="padding: 15px;">{{ app['age'] }}</td>
                    <td style="padding: 15px;">{{ app['role'] if app['role'] else app['rank'] if app['rank'] else 'غير متوفر' }}</td>
                    <td style="padding: 15px;">{{ app['company'] }}</td>
                    <td style="padding: 15px; max-width: 250px; word-wrap: break-word; white-space: pre-wrap; font-size: 0.85rem; color: #cbd5e1;">{{ app['description'] if app['description'] else app['bio'] if app['bio'] else 'لا يوجد وصف' }}</td>
                    <td style="padding: 15px;"><span style="background: {% if app['status']|lower == 'pending' %}#f59e0b{% elif app['status']|lower == 'accepted' %}#22c55e{% else %}#ef4444{% endif %}; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; color: #fff; font-weight: bold; display: inline-block; text-align: center; min-width: 70px;">{{ app['status'] }}</span></td>
                    <td style="padding: 15px; white-space: nowrap;">
                        {% if app['status']|lower == 'pending' %}
                        <form action="/action/{{ app['id'] }}" method="POST" style="display:inline;"><input type="hidden" name="action" value="accept"><button type="submit" style="background: #22c55e; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-bottom: 5px; width: 100%;">قبول ✓</button></form>
                        <form action="/action/{{ app['id'] }}" method="POST" style="display:inline;"><input type="hidden" name="action" value="reject"><button type="submit" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">رفض ✗</button></form>
                        {% else %}<span style="color: #64748b; font-size: 0.9rem;">تمت المعالجة</span>{% endif %}
                    </td>
                </tr>
                {% else %}<tr><td colspan="8" style="text-align: center; padding: 20px; color: #64748b;">لا توجد طلبات حالياً</td></tr>{% endfor %}
            </tbody>
        </table>
    </div>
    <h2 style="color: #00f2fe; font-size: 1.5rem; margin-top: 40px; margin-bottom: 20px;">إدارة الشركات</h2>
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <form action="/add_company" method="POST" style="display: flex; gap: 10px; width: 100%;">
            <input type="text" name="company_name" placeholder="اسم الشركة الجديدة..." required style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; outline: none;">
            <button type="submit" style="background: #22c55e; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s;">+ إضافة</button>
        </form>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px;">
        {% for c in companies %}
        <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.1); color: #fff;">
            <span style="font-weight: 600;">{{ c['name'] if c['name'] else c.name }}</span>
            <form action="/delete_company/{{ c['id'] if c['id'] else c.id }}" method="POST" style="margin: 0;"><button type="submit" style="background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; padding: 8px 12px; border-radius: 5px; cursor: pointer;">🗑️</button></form>
        </div>
        {% endfor %}
    </div>
</div>
"""

FAMILY_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Family | مجتمعنا</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <!-- مكتبة الأيقونات الاحترافية -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: #0a0a1a; min-height: 100vh; overflow-x: hidden; position: relative; display: flex; align-items: center; justify-content: center; padding: 20px 0; }
        .animated-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(-45deg, #0a0a1a, #1a0a2e, #0a1a2e, #1a0a1a); background-size: 400% 400%; animation: gradientShift 15s ease infinite; z-index: -2; }
        @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .orb { position: fixed; border-radius: 50%; filter: blur(80px); opacity: 0.4; z-index: -1; animation: float 20s ease-in-out infinite; }
        .orb-1 { width: 400px; height: 400px; background: #8b5cf6; top: -100px; right: -100px; }
        .orb-2 { width: 350px; height: 350px; background: #06b6d4; bottom: -100px; left: -100px; animation-delay: -7s; }
        .orb-3 { width: 300px; height: 300px; background: #ec4899; top: 50%; left: 50%; animation-delay: -14s; }
        @keyframes float { 0%, 100% { transform: translate(0, 0) scale(1); } 25% { transform: translate(50px, -50px) scale(1.1); } 50% { transform: translate(-30px, 30px) scale(0.9); } 75% { transform: translate(30px, 50px) scale(1.05); } }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }
        .btn { position: relative; transition: all 0.3s ease; }
        .btn:hover { transform: translateY(-3px); }
        .btn-shine { overflow: hidden; }
        .btn-shine::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); transition: left 0.6s ease; }
        .btn-shine:hover::before { left: 100%; }
        .animated-text { background: linear-gradient(90deg, #c084fc, #f472b6, #22d3ee, #c084fc); background-size: 300% auto; -webkit-background-clip: text; background-clip: text; color: transparent; animation: gradientText 3s linear infinite; }
        @keyframes gradientText { 0% { background-position: 0% center; } 100% { background-position: 300% center; } }
        .pulse-dot { width: 10px; height: 10px; background: #10b981; border-radius: 50%; position: relative; display: inline-block; }
        .pulse-dot::after { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; background: #10b981; animation: pulse 2s ease-out infinite; }
        @keyframes pulse { 0% { transform: scale(1); opacity: 0.7; } 100% { transform: scale(2.5); opacity: 0; } }
        .modal { display: none; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(5px); z-index: 100; align-items: center; justify-content: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: rgba(30, 30, 50, 0.95); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; max-width: 500px; width: 100%; padding: 24px; animation: modalIn 0.3s ease; max-height: 85vh; overflow-y: auto; }
        @keyframes modalIn { from { opacity: 0; transform: scale(0.9) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }
        
        /* شارة قريباً تم إصلاحها */
        .badge-new { position: absolute; top: -10px; right: -10px; background: linear-gradient(135deg, #f43f5e, #ec4899); color: white; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; animation: bounce 2s ease infinite; z-index: 50; box-shadow: 0 0 15px rgba(236, 72, 153, 0.6); border: 1px solid rgba(255,255,255,0.2); white-space: nowrap;}
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        
        .fade-in { animation: fadeIn 0.8s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .glow-purple { box-shadow: 0 0 20px rgba(139, 92, 246, 0.3); } .glow-purple:hover { box-shadow: 0 0 40px rgba(139, 92, 246, 0.6); }
        .glow-cyan { box-shadow: 0 0 20px rgba(6, 182, 212, 0.3); } .glow-cyan:hover { box-shadow: 0 0 40px rgba(6, 182, 212, 0.6); }
        .glow-pink { box-shadow: 0 0 20px rgba(236, 72, 153, 0.3); } .glow-pink:hover { box-shadow: 0 0 40px rgba(236, 72, 153, 0.6); }
        .glow-emerald { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); } .glow-emerald:hover { box-shadow: 0 0 40px rgba(16, 185, 129, 0.6); }
        
        /* تأثير توهج للأيقونات */
        .icon-glow-cyan { filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.8)); }
        .icon-glow-pink { filter: drop-shadow(0 0 8px rgba(236, 72, 153, 0.8)); }
        .icon-glow-emerald { filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.8)); }
        .icon-glow-amber { filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.8)); }
        .icon-glow-purple { filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.8)); }
    </style>
</head>
<body>
    <div class="animated-bg"></div><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div>
    <main class="w-full max-w-2xl px-4 fade-in relative z-10">
        <div class="text-center mb-8">
            <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-4"><span class="pulse-dot"></span><span class="text-white/90 text-sm font-semibold">مجتمع Family متصل الآن</span></div>
            <h1 class="text-5xl md:text-6xl font-black mb-3"><span class="animated-text">Family</span></h1><p class="text-white/70 text-lg">مجتمعنا • عائلتنا • نجاحنا</p>
        </div>
        <div class="glass rounded-3xl p-6 md:p-8 mb-8">
            <h2 class="text-white font-bold text-xl mb-6 text-center">اختر ما تريد</h2>
            <a href="https://discord.gg/z978P5MMB" target="_blank" rel="noopener" class="btn btn-shine glow-purple block w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-lg py-4 rounded-2xl text-center mb-4 flex justify-center items-center gap-3">
                <i class="fas fa-rocket text-2xl icon-glow-purple"></i> <span class="relative z-10">ادخل للسيرفر</span>
            </a>
            <div class="grid grid-cols-2 gap-4">
                
                <!-- أيقونة الفعاليات (كأس احتفال) -->
                <button onclick="openModal('eventsModal')" class="btn glow-cyan bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-400/30 text-white font-bold py-4 rounded-2xl flex flex-col items-center gap-2">
                    <i class="fas fa-champagne-glasses text-3xl text-cyan-400 icon-glow-cyan"></i>
                    <span>فعاليات</span>
                </button>
                
                <!-- أيقونة المسابقات (كأس) -->
                <button onclick="openModal('competitionsModal')" class="btn glow-pink bg-gradient-to-br from-pink-500/20 to-rose-500/20 border border-pink-400/30 text-white font-bold py-4 rounded-2xl flex flex-col items-center gap-2">
                    <i class="fas fa-trophy text-3xl text-pink-400 icon-glow-pink"></i>
                    <span>مسابقات</span>
                </button>
                
                <!-- أيقونة الطاقم (مجموعة أشخاص) -->
                <button onclick="openModal('teamModal')" class="btn glow-emerald bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-400/30 text-white font-bold py-4 rounded-2xl flex flex-col items-center gap-2">
                    <i class="fas fa-users text-3xl text-emerald-400 icon-glow-emerald"></i>
                    <span>الطاقم</span>
                </button>
                
                <!-- أيقونة المتجر (عربة تسوق) مع شارة قريباً المصححة -->
                {% if shop_items %}
                <button onclick="openModal('shopModal')" class="btn glow-pink bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-400/30 text-white font-bold py-4 rounded-2xl flex flex-col items-center gap-2">
                    <i class="fas fa-store text-3xl text-amber-400 icon-glow-amber"></i>
                    <span>متجر الشحن</span>
                </button>
                {% else %}
                <button onclick="openModal('shopModal')" class="btn relative bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-400/30 text-white font-bold py-4 rounded-2xl flex flex-col items-center gap-2 opacity-80">
                    <span class="badge-new">قريباً</span>
                    <i class="fas fa-store text-3xl text-amber-400 icon-glow-amber"></i>
                    <span>متجر الشحن</span>
                </button>
                {% endif %}
            </div>
        </div>
        <div class="glass rounded-3xl p-4 flex justify-center mb-8">
            <div class="w-full max-w-[350px]"><iframe src="https://discord.com/widget?id=1528147384914153512&theme=dark" width="100%" height="350" allowtransparency="true" frameborder="0" sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts" class="rounded-2xl"></iframe></div>
        </div>
        <p class="text-center text-white/40 text-sm mb-4">© 2025 Family • All Rights Reserved</p>
    </main>

    <!-- نافذة الفعاليات -->
    <div id="eventsModal" class="modal" onclick="closeModalOnBg(event, 'eventsModal')">
        <div class="modal-content">
            <div class="flex justify-between items-center mb-4"><h3 class="text-white text-2xl font-bold flex items-center gap-2"><i class="fas fa-champagne-glasses text-cyan-400"></i> الفعاليات</h3><button onclick="closeModal('eventsModal')" class="text-white/60 hover:text-white text-2xl"><i class="fas fa-times"></i></button></div>
            <div class="space-y-3 mt-4">
                {% for event in events %}<div class="bg-cyan-500/10 border border-cyan-400/30 p-4 rounded-xl"><h4 class="text-white font-bold text-lg mb-1">{{ event.title }}</h4><p class="text-white/70 text-sm">{{ event.description }}</p></div>
                {% else %}<div class="text-center py-8"><i class="fas fa-calendar-xmark text-6xl text-cyan-400/50 mb-4"></i><p class="text-white/80 text-lg font-semibold mb-2">ترقبوا الفعاليات القادمة!</p></div>{% endfor %}
            </div>
        </div>
    </div>
    
    <!-- نافذة المسابقات -->
    <div id="competitionsModal" class="modal" onclick="closeModalOnBg(event, 'competitionsModal')">
        <div class="modal-content">
            <div class="flex justify-between items-center mb-4"><h3 class="text-white text-2xl font-bold flex items-center gap-2"><i class="fas fa-trophy text-pink-400"></i> المسابقات</h3><button onclick="closeModal('competitionsModal')" class="text-white/60 hover:text-white text-2xl"><i class="fas fa-times"></i></button></div>
            <div class="text-center py-8"><i class="fas fa-medal text-6xl text-pink-400/50 mb-4"></i><p class="text-white/80 text-lg font-semibold mb-2">لا توجد مسابقات حالياً</p></div>
        </div>
    </div>
    
    <!-- نافذة الطاقم -->
    <div id="teamModal" class="modal" onclick="closeModalOnBg(event, 'teamModal')">
        <div class="modal-content">
            <div class="flex justify-between items-center mb-4"><h3 class="text-white text-2xl font-bold flex items-center gap-2"><i class="fas fa-users text-emerald-400"></i> طاقم Family</h3><button onclick="closeModal('teamModal')" class="text-white/60 hover:text-white text-2xl"><i class="fas fa-times"></i></button></div>
            <div class="space-y-3 mt-4">
                {% for member in staff %}<div class="flex justify-between items-center bg-{{ member.color }}/20 border border-{{ member.color }}/30 p-3 rounded-xl"><span class="text-white font-bold">{{ member.name }}</span><span class="text-{{ member.color }} text-sm font-semibold">{{ member.role }}</span></div>{% endfor %}
            </div>
        </div>
    </div>
    
    <!-- نافذة المتجر -->
    <div id="shopModal" class="modal" onclick="closeModalOnBg(event, 'shopModal')">
        <div class="modal-content">
            <div class="flex justify-between items-center mb-4"><h3 class="text-white text-2xl font-bold flex items-center gap-2"><i class="fas fa-store text-amber-400"></i> متجر الشحن</h3><button onclick="closeModal('shopModal')" class="text-white/60 hover:text-white text-2xl"><i class="fas fa-times"></i></button></div>
            <div class="space-y-3 mt-4">
                {% for item in shop_items %}<div class="bg-amber-500/10 border border-amber-400/30 p-4 rounded-xl flex justify-between items-center"><div><h4 class="text-white font-bold text-lg mb-1">{{ item.title }}</h4><p class="text-white/70 text-sm">{{ item.description }}</p></div><span class="text-amber-400 font-bold text-xl bg-black/30 px-3 py-1 rounded-lg">{{ item.price }}</span></div>
                {% else %}<div class="text-center py-8"><i class="fas fa-screwdriver-wrench text-6xl text-amber-400/50 mb-4"></i><p class="text-white/80 text-lg font-semibold mb-2">قيد التجهيز</p></div>{% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function openModal(id) { document.getElementById(id).classList.add('active'); document.body.style.overflow = 'hidden'; }
        function closeModal(id) { document.getElementById(id).classList.remove('active'); document.body.style.overflow = ''; }
        function closeModalOnBg(event, id) { if (event.target.id === id) closeModal(id); }
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { document.querySelectorAll('.modal.active').forEach(m => m.classList.remove('active')); document.body.style.overflow = ''; } });
    </script>
</body>
</html>
"""

FAMILY_ADMIN_LOGIN = """
<h2 style="text-align:center; margin-bottom: 25px;">لوحة إدارة Family</h2>
{% if error %}<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> {{ error }}</div>{% endif %}
<form method="post" action="/family-admin">
  <div class="form-group"><label><i class="fas fa-key"></i> كلمة المرور</label><input type="password" name="password" required style="text-align: center; font-size: 20px; letter-spacing: 2px;"></div>
  <button type="submit" class="btn">دخول</button>
</form>
"""

FAMILY_ADMIN_DASHBOARD = """
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
    <h2 style="color: #c084fc; font-size: 1.5rem; margin: 0;">مركز تحكم Family</h2>
    <a href="/family-logout" style="color: #ef4444; text-decoration: none; font-weight: bold; background: rgba(239, 68, 68, 0.1); padding: 8px 15px; border-radius: 8px;"><i class="fas fa-sign-out-alt"></i> خروج</a>
</div>
<h3 style="color: #a78bfa; margin-bottom: 15px;"><i class="fas fa-users"></i> إدارة الطاقم</h3>
<form action="/family-admin/add_staff" method="POST" style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
    <input type="text" name="name" placeholder="اسم العضو" required style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    
    <input list="roles_list" name="role" placeholder="اسم الرتبة (اكتب أو اختر)" required style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    <datalist id="roles_list">
        <option value="Owner">
        <option value="Founder">
        <option value="Co-Owner">
        <option value="Community Manager">
        <option value="Lead">
        <option value="Administrator">
        <option value="Staff">
        <option value="Moderator">
        <option value="Helper">
    </datalist>
    
    <select name="color" style="padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
        <option value="red-900">أحمر داكن (CM)</option>
        <option value="red-500">أحمر (Lead)</option>
        <option value="yellow-500">أصفر (Admin)</option>
        <option value="purple-500">بنفسجي (Staff)</option>
        <option value="blue-500">أزرق</option>
        <option value="cyan-500">سماوي</option>
        <option value="emerald-500">زمردي (أخضر)</option>
        <option value="orange-500">برتقالي</option>
        <option value="pink-500">وردي</option>
        <option value="indigo-500">نيلي</option>
        <option value="teal-500">أخضر مزرق</option>
        <option value="rose-500">زهري</option>
        <option value="amber-500">كهرماني</option>
        <option value="lime-500">ليموني</option>
        <option value="green-500">أخضر ساطع</option>
        <option value="sky-500">أزرق فاتح</option>
        <option value="violet-500">بنفسجي فاتح</option>
        <option value="fuchsia-500">فوشيا</option>
    </select>
    <button type="submit" class="btn" style="width: auto; padding: 10px 20px; background: #22c55e;">+ إضافة</button>
</form>
<div class="table-container" style="background: rgba(0,0,0,0.2); border-radius: 10px; padding: 10px; margin-bottom: 30px;">
    {% for member in staff %}<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);"><div><span class="text-white font-bold">{{ member.name }}</span> - <span style="color: #94a3b8; font-size: 0.9rem;">{{ member.role }}</span></div><form action="/family-admin/delete_staff/{{ member.id }}" method="POST" style="margin: 0;"><button type="submit" style="background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;"><i class="fas fa-trash"></i></button></form></div>{% endfor %}
</div>
<h3 style="color: #22d3ee; margin-bottom: 15px;"><i class="fas fa-champagne-glasses"></i> إدارة الفعاليات</h3>
<form action="/family-admin/add_event" method="POST" style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
    <input type="text" name="title" placeholder="عنوان الفعالية" required style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    <input type="text" name="description" placeholder="تفاصيل الفعالية" required style="flex: 2; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    <button type="submit" class="btn" style="width: auto; padding: 10px 20px; background: #06b6d4;">+ إضافة</button>
</form>
<div class="table-container" style="background: rgba(0,0,0,0.2); border-radius: 10px; padding: 10px; margin-bottom: 30px;">
    {% for event in events %}<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);"><div><span class="text-white font-bold">{{ event.title }}</span> - <span style="color: #94a3b8; font-size: 0.9rem;">{{ event.description }}</span></div><form action="/family-admin/delete_event/{{ event.id }}" method="POST" style="margin: 0;"><button type="submit" style="background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;"><i class="fas fa-trash"></i></button></form></div>{% endfor %}
</div>
<h3 style="color: #fbbf24; margin-bottom: 15px;"><i class="fas fa-store"></i> إدارة المتجر (العروض)</h3>
<form action="/family-admin/add_shop" method="POST" style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
    <input type="text" name="title" placeholder="اسم العرض (مثال: 100 ألف)" required style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    <input type="text" name="description" placeholder="تفاصيل العرض" required style="flex: 2; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    <input type="text" name="price" placeholder="السعر" required style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);">
    <button type="submit" class="btn" style="width: auto; padding: 10px 20px; background: #f59e0b;">+ إضافة</button>
</form>
<div class="table-container" style="background: rgba(0,0,0,0.2); border-radius: 10px; padding: 10px; margin-bottom: 30px;">
    {% for item in shop %}<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);"><div><span class="text-white font-bold">{{ item.title }}</span> - <span style="color: #94a3b8; font-size: 0.9rem;">{{ item.price }}</span></div><form action="/family-admin/delete_shop/{{ item.id }}" method="POST" style="margin: 0;"><button type="submit" style="background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;"><i class="fas fa-trash"></i></button></form></div>{% endfor %}
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
        execute_query("INSERT INTO applications (discord_name, ign, age, role, company, description, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')", [discord_name, ign, age, role, company, description])
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
        apps = []
        if result:
            cols = [c.get("name") for c in result.get("cols", [])]
            raw_rows = result.get("rows", [])
            for row in raw_rows:
                row_values = [col.get("value") for col in row]
                apps.append(dict(zip(cols, row_values)))
    except Exception as e:
        return f"<div class='alert alert-error'>خطأ في الإدارة: {str(e)}</div>", 500
    companies = get_companies()
    return render_template_string(HTML_LAYOUT, content=render_template_string(ADMIN_DASHBOARD_HTML, apps=apps, companies=companies))

@app.route("/add_company", methods=["POST"])
def add_company():
    if not session.get('admin'): return redirect(url_for('admin'))
    name = request.form.get("company_name").strip()
    if name:
        try: execute_query("INSERT INTO companies (name) VALUES (?)", [name])
        except Exception: pass 
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

@app.route('/family')
def family_page():
    try:
        staff_query = """
            SELECT id, name, role, color FROM family_staff 
            ORDER BY 
                CASE role 
                    WHEN 'Owner' THEN 1
                    WHEN 'Founder' THEN 1
                    WHEN 'المالك' THEN 1
                    WHEN 'المؤسس' THEN 1
                    WHEN 'Co-Owner' THEN 2
                    WHEN 'شريك' THEN 2
                    WHEN 'Community Manager' THEN 3 
                    WHEN 'مدير المجتمع' THEN 3
                    WHEN 'Lead' THEN 4 
                    WHEN 'قائد' THEN 4
                    WHEN 'Administrator' THEN 5
                    WHEN 'إداري' THEN 5
                    WHEN 'Staff' THEN 6
                    WHEN 'طاقم' THEN 6
                    WHEN 'Moderator' THEN 7
                    WHEN 'Helper' THEN 8
                    ELSE 9 
                END ASC, id ASC
        """
        staff_res = execute_query(staff_query)
        staff = []
        if staff_res and staff_res.get("rows"):
            cols = [c.get("name") for c in staff_res.get("cols", [])]
            for row in staff_res["rows"]:
                staff.append(dict(zip(cols, [c.get("value") for c in row])))

        events_res = execute_query("SELECT id, title, description FROM family_events")
        events = []
        if events_res and events_res.get("rows"):
            cols = [c.get("name") for c in events_res.get("cols", [])]
            for row in events_res["rows"]:
                events.append(dict(zip(cols, [c.get("value") for c in row])))

        shop_res = execute_query("SELECT id, title, description, price FROM family_shop")
        shop_items = []
        if shop_res and shop_res.get("rows"):
            cols = [c.get("name") for c in shop_res.get("cols", [])]
            for row in shop_res["rows"]:
                shop_items.append(dict(zip(cols, [c.get("value") for c in row])))

        return render_template_string(FAMILY_HTML, staff=staff, events=events, shop_items=shop_items)
    except Exception as e:
        return f"خطأ في تحميل البيانات: {str(e)}", 500

@app.route('/team')
def team_page():
    with open('staff.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/family-admin', methods=['GET', 'POST'])
def family_admin_login():
    if request.method == "POST":
        if request.form.get("password") == "family123":
            session['family_admin'] = True
            return redirect(url_for('family_admin_dashboard'))
        else:
            return render_template_string(HTML_LAYOUT, content=render_template_string(FAMILY_ADMIN_LOGIN, error="كلمة المرور خاطئة"))
    if not session.get('family_admin'):
        return render_template_string(HTML_LAYOUT, content=render_template_string(FAMILY_ADMIN_LOGIN, error=None))
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-admin/dashboard')
def family_admin_dashboard():
    if not session.get('family_admin'):
        return redirect(url_for('family_admin_login'))
    
    staff_query = """
        SELECT id, name, role, color FROM family_staff 
        ORDER BY 
            CASE role 
                WHEN 'Owner' THEN 1
                WHEN 'Founder' THEN 1
                WHEN 'المالك' THEN 1
                WHEN 'المؤسس' THEN 1
                WHEN 'Co-Owner' THEN 2
                WHEN 'شريك' THEN 2
                WHEN 'Community Manager' THEN 3 
                WHEN 'مدير المجتمع' THEN 3
                WHEN 'Lead' THEN 4 
                WHEN 'قائد' THEN 4
                WHEN 'Administrator' THEN 5
                WHEN 'إداري' THEN 5
                WHEN 'Staff' THEN 6
                WHEN 'طاقم' THEN 6
                WHEN 'Moderator' THEN 7
                WHEN 'Helper' THEN 8
                ELSE 9 
            END ASC, id ASC
    """
    staff_res = execute_query(staff_query)
    staff = []
    if staff_res and staff_res.get("rows"):
        cols = [c.get("name") for c in staff_res.get("cols", [])]
        for row in staff_res["rows"]:
            staff.append(dict(zip(cols, [c.get("value") for c in row])))

    events_res = execute_query("SELECT id, title, description FROM family_events")
    events = []
    if events_res and events_res.get("rows"):
        cols = [c.get("name") for c in events_res.get("cols", [])]
        for row in events_res["rows"]:
            events.append(dict(zip(cols, [c.get("value") for c in row])))

    shop_res = execute_query("SELECT id, title, description, price FROM family_shop")
    shop_items = []
    if shop_res and shop_res.get("rows"):
        cols = [c.get("name") for c in shop_res.get("cols", [])]
        for row in shop_res["rows"]:
            shop_items.append(dict(zip(cols, [c.get("value") for c in row])))

    return render_template_string(HTML_LAYOUT, content=render_template_string(FAMILY_ADMIN_DASHBOARD, staff=staff, events=events, shop=shop_items))

@app.route('/family-admin/add_staff', methods=['POST'])
def family_add_staff():
    if not session.get('family_admin'): return redirect(url_for('family_admin_login'))
    name = request.form.get("name")
    role = request.form.get("role")
    color = request.form.get("color")
    execute_query("INSERT INTO family_staff (name, role, color) VALUES (?, ?, ?)", [name, role, color])
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-admin/delete_staff/<id>', methods=['POST'])
def family_delete_staff(id):
    if not session.get('family_admin'): return redirect(url_for('family_admin_login'))
    execute_query("DELETE FROM family_staff WHERE id=?", [id])
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-admin/add_event', methods=['POST'])
def family_add_event():
    if not session.get('family_admin'): return redirect(url_for('family_admin_login'))
    title = request.form.get("title")
    description = request.form.get("description")
    execute_query("INSERT INTO family_events (title, description) VALUES (?, ?)", [title, description])
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-admin/delete_event/<id>', methods=['POST'])
def family_delete_event(id):
    if not session.get('family_admin'): return redirect(url_for('family_admin_login'))
    execute_query("DELETE FROM family_events WHERE id=?", [id])
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-admin/add_shop', methods=['POST'])
def family_add_shop():
    if not session.get('family_admin'): return redirect(url_for('family_admin_login'))
    title = request.form.get("title")
    description = request.form.get("description")
    price = request.form.get("price")
    execute_query("INSERT INTO family_shop (title, description, price) VALUES (?, ?, ?)", [title, description, price])
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-admin/delete_shop/<id>', methods=['POST'])
def family_delete_shop(id):
    if not session.get('family_admin'): return redirect(url_for('family_admin_login'))
    execute_query("DELETE FROM family_shop WHERE id=?", [id])
    return redirect(url_for('family_admin_dashboard'))

@app.route('/family-logout')
def family_logout():
    session.pop('family_admin', None)
    return redirect(url_for('family_page'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
