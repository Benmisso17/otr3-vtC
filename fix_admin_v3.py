import re

new_admin_dashboard = """
<div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; margin-top: 20px; text-align: right;">
    
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
        <h2 style="color: #00f2fe; font-size: 1.8rem; margin: 0;">الطلبات المعلقة</h2>
        <a href="/logout" style="color: #ef4444; text-decoration: none; font-weight: bold; background: rgba(239, 68, 68, 0.1); padding: 8px 15px; border-radius: 8px;">خروج 🚪</a>
    </div>

    <!-- جدول الطلبات -->
    <div style="overflow-x: auto; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
        <table style="width: 100%; border-collapse: collapse; text-align: right; min-width: 900px; font-size: 0.95rem;">
            <thead style="background: rgba(0,0,0,0.4);">
                <tr style="border-bottom: 2px solid #00f2fe;">
                    <th style="padding: 15px;">الديسكورد</th>
                    <th style="padding: 15px;">اسم اللعبة</th>
                    <th style="padding: 15px;">العمر</th>
                    <th style="padding: 15px;">الرتبة</th>
                    <th style="padding: 15px;">الشركة</th>
                    <th style="padding: 15px;">الوصف</th>
                    <th style="padding: 15px;">الحالة</th>
                    <th style="padding: 15px;">إجراء</th>
                </tr>
            </thead>
            <tbody>
                {% for app in apps %}
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 15px; color: #4facfe; font-weight: bold;">{{ app.discord_name }}</td>
                    <td style="padding: 15px;">{{ app.ign }}</td>
                    <td style="padding: 15px;">{{ app.age }}</td>
                    <td style="padding: 15px;">{{ app.role }}</td>
                    <td style="padding: 15px;">{{ app.company }}</td>
                    <td style="padding: 15px; max-width: 250px; word-wrap: break-word; white-space: pre-wrap; font-size: 0.85rem; color: #cbd5e1;">{{ app.description }}</td>
                    <td style="padding: 15px;">
                        <span style="background: {% if app.status == 'pending' %}#f59e0b{% elif app.status == 'accepted' %}#22c55e{% else %}#ef4444{% endif %}; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; color: #000; font-weight: bold;">{{ app.status }}</span>
                    </td>
                    <td style="padding: 15px; white-space: nowrap;">
                        {% if app.status == 'pending' %}
                        <form action="/action/{{ app.id }}" method="POST" style="display:inline;">
                            <input type="hidden" name="action" value="accept">
                            <button type="submit" style="background: #22c55e; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-bottom: 5px; width: 100%;">قبول ✓</button>
                        </form>
                        <form action="/action/{{ app.id }}" method="POST" style="display:inline;">
                            <input type="hidden" name="action" value="reject">
                            <button type="submit" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">رفض ✗</button>
                        </form>
                        {% else %}
                        <span style="color: #64748b;">تمت المعالجة</span>
                        {% endif %}
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="8" style="text-align: center; padding: 20px; color: #64748b;">لا توجد طلبات حالياً</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- إدارة الشركات -->
    <h2 style="color: #00f2fe; font-size: 1.8rem; margin-top: 50px; margin-bottom: 20px;">إدارة الشركات</h2>
    
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <form action="/add_company" method="POST" style="display: flex; gap: 10px; width: 100%;">
            <input type="text" name="company_name" placeholder="اسم الشركة الجديدة..." required style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; outline: none;">
            <button type="submit" style="background: #22c55e; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s;">+ إضافة</button>
        </form>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px;">
        {% for c in companies %}
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.05);">
            <span style="font-weight: 600;">{{ c.name }}</span>
            <form action="/delete_company/{{ c.id }}" method="POST" style="margin: 0;">
                <button type="submit" style="background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; padding: 8px 12px; border-radius: 5px; cursor: pointer;">🗑️</button>
            </form>
        </div>
        {% endfor %}
    </div>
</div>
"""

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# استبدال لوحة الإدارة بالكامل
pattern = re.compile(r'(ADMIN_DASHBOARD_HTML\s*=\s*)(["\']{3})(.*?)(\2)', re.DOTALL)
match = pattern.search(code)

if match:
    new_code = code[:match.start()] + match.group(1) + '"""' + new_admin_dashboard + '"""' + code[match.end():]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("\n✅ تم إصلاح لوحة الإدارة بالكامل (الجدول + الشركات) بنجاح!")
else:
    print("\n❌ لم يتم العثور على ADMIN_DASHBOARD_HTML")
