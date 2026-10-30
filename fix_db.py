with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# الكود القديم الذي يجلب البيانات كقائمة (List)
old_code = """        result = execute_query("SELECT * FROM applications WHERE status='pending' ORDER BY id DESC")
        raw_rows = result.get("rows", []) if result else []
        apps = []
        for row in raw_rows:
            parsed_row = [col.get("value") for col in row]
            apps.append(parsed_row)"""

# الكود الجديد الذي يحول البيانات إلى قاموس (Dictionary) مع أسماء الأعمدة
new_code = """        result = execute_query("SELECT * FROM applications WHERE status='pending' ORDER BY id DESC")
        apps = []
        if result:
            cols = [c.get("name") for c in result.get("cols", [])]
            raw_rows = result.get("rows", [])
            for row in raw_rows:
                row_values = [col.get("value") for col in row]
                apps.append(dict(zip(cols, row_values)))"""

# استبدال الكود القديم بالجديد
if old_code in code:
    code = code.replace(old_code, new_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("\n✅ تم إصلاح جلب البيانات بنجاح! (الآن ستظهر الأسماء والأوصاف)")
else:
    print("\n❌ لم يتم العثور على الكود القديم. تأكد من أنك لم تقم بتعديله يدوياً.")
