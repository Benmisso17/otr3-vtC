import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# البحث عن قسم لوحة الإدارة
admin_start = code.find('ADMIN_DASHBOARD_HTML')
if admin_start != -1:
    # البحث عن الجدول داخل قسم لوحة الإدارة
    table_match = re.search(r'(<table.*?>)(.*?)(</table>)', code[admin_start:], re.DOTALL | re.IGNORECASE)
    if table_match:
        table_content = table_match.group(2)
        
        # محاولة الاحتفاظ بأزرار القبول والرفض القديمة كما هي
        action_td_match = re.search(r'<td[^>]*>(?:(?!<td).)*?(?:<form|<a|<button).*?(?:</form>|</a>|</button>).*?</td>', table_content, re.DOTALL)
        if action_td_match:
            action_td = action_td_match.group(0)
        else:
            # في حال لم يجدها، يضع أزراراً افتراضية
            action_td = '<td style="padding: 12px;"><form action="/action/{{ app.id }}" method="POST" style="display:inline;"><input type="hidden" name="action" value="accept"><button type="submit" style="background: #22c55e; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold;">قبول ✓</button></form> <form action="/action/{{ app.id }}" method="POST" style="display:inline;"><input type="hidden" name="action" value="reject"><button type="submit" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold;">رفض ✗</button></form></td>'

        # بناء الجدول الجديد المنظم
        new_table = """
        <div style="overflow-x: auto; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-top: 15px;">
        <table style="width: 100%; border-collapse: collapse; text-align: right; min-width: 800px; font-size: 0.9rem;">
            <thead style="background: rgba(0,0,0,0.2);">
                <tr style="border-bottom: 2px solid rgba(255,255,255,0.1);">
                    <th style="padding: 15px;">الديسكورد</th>
                    <th style="padding: 15px;">اللعبة</th>
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
                    <td style="padding: 15px;">{{ app.discord_name }}</td>
                    <td style="padding: 15px;">{{ app.ign }}</td>
                    <td style="padding: 15px;">{{ app.age }}</td>
                    <td style="padding: 15px;">{{ app.role }}</td>
                    <td style="padding: 15px;">{{ app.company }}</td>
                    <td style="padding: 15px; max-width: 250px; word-wrap: break-word; white-space: pre-wrap;">{{ app.description }}</td>
                    <td style="padding: 15px;">{{ app.status }}</td>
                    """ + action_td + """
                </tr>
                {% endfor %}
            </tbody>
        </table>
        </div>
        """
        
        # استبدال الجدول القديم بالجديد
        start_idx = admin_start + table_match.start()
        end_idx = admin_start + table_match.end()
        code = code[:start_idx] + new_table + code[end_idx:]

        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("\n✅ تم إصلاح الجدول بنجاح! سيظهر الآن بشكل مرتب مع الوصف.")
    else:
        print("\n❌ لم يتم العثور على جدول.")
else:
    print("\n❌ لم يتم العثور على ADMIN_DASHBOARD_HTML.")
