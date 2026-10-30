import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. إضافة رأس العمود (Header) في الجدول
if '<th>الوصف</th>' not in code:
    code = code.replace('<th>الشركة</th>', '<th>الشركة</th>\n<th>الوصف</th>')

# 2. إضافة خلية البيانات (Data Cell) أسفل اسم الشركة
# الكود يبحث عن الخلية التي تحتوي على الشركة ويضيف بجانبها الوصف
company_pattern = r'(<td>\s*\{\{\s*([a-zA-Z_]+)(?:\[\'company\'\]|\.company)\s*\}\}\s*</td>)'

def replace_company(match):
    original_td = match.group(1)
    var_name = match.group(2)
    
    # التحقق مما إذا كان الوصف مضافاً مسبقاً لتجنب التكرار
    if f'{{{{ {var_name}.description }}}}' in code or f'{{{{ {var_name}[\'description\'] }}}}' in code:
        return original_td
        
    # إضافة خلية الوصف بجانب خلية الشركة
    desc_td = f'\n<td style="font-size: 0.85em; max-width: 200px; word-wrap: break-word;">{{{{ {var_name}.description }}}}</td>'
    return original_td + desc_td

code = re.sub(company_pattern, replace_company, code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("\n✅ تم إضافة عمود الوصف إلى جدول لوحة الإدارة بنجاح!")
