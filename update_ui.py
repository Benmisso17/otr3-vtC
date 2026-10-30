import os

# هذه هي الواجهة الجديدة التي سنضعها
new_html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTR3 | التسجيل في الشركات</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00f2fe;
            --secondary: #4facfe;
            --dark-bg: #0f172a;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
        body { background-color: var(--dark-bg); color: white; min-height: 100vh; display: flex; justify-content: center; align-items: center; overflow-x: hidden; position: relative; }
        #particles-js { position: absolute; width: 100%; height: 100%; top: 0; left: 0; z-index: 0; }
        .split-container { position: relative; z-index: 1; display: flex; width: 90%; max-width: 1200px; background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 20px; box-shadow: 0 25px 45px rgba(0, 0, 0, 0.5); overflow: hidden; }
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
        .btn-submit:active { transform: translateY(0); }
        .toast-container { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; display: flex; flex-direction: column; gap: 10px; }
        .toast { padding: 15px 30px; border-radius: 10px; color: white; font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,0.5); animation: slideDown 0.3s ease forwards; backdrop-filter: blur(10px); }
        .toast.success { background: rgba(34, 197, 94, 0.9); border: 1px solid #4ade80; }
        .toast.error { background: rgba(239, 68, 68, 0.9); border: 1px solid #f87171; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 900px) { .split-container { flex-direction: column; width: 95%; margin: 20px 0; } .info-side { border-left: none; border-bottom: 1px solid var(--glass-border); padding: 30px; text-align: center; } .info-side h1 { font-size: 2.2rem; } .form-side { padding: 30px; } }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    <div class="toast-container" id="toastContainer"></div>
    <div class="split-container">
        <div class="info-side">
            <h1>OTR3 VTC</h1>
            <p>مرحباً بك في منصة التسجيل الرسمية لشركات النقل (VTC) في سيرفر <strong>Of Europe3 online</strong>. انضم إلى نخبة السائقين وابدأ رحلتك الاحترافية معنا.</p>
            <div class="rules-box">
                <h3>شروط التسجيل:</h3>
                <ul>
                    <li>الالتزام بقوانين السيرفر المرورية.</li>
                    <li>امتلاك رخصة قيادة سارية.</li>
                    <li>التوفر والاحترافية في التعامل.</li>
                    <li>عدم استخدام أي برامج غش.</li>
                </ul>
            </div>
        </div>
        <div class="form-side">
            <h2>تقديم طلب انضمام</h2>
            <form id="vtcForm" action="/submit" method="POST">
                <div class="input-group">
                    <label>اسم الديسكورد (Discord)</label>
                    <input type="text" name="discord" id="discord" placeholder="مثال: User#1234" required>
                </div>
                <div class="input-group">
                    <label>اسم اللعبة (In-Game Name)</label>
                    <input type="text" name="game_name" id="game_name" placeholder="مثال: Ahmed_TR" required>
                </div>
                <div class="input-group">
                    <label>العمر (Age)</label>
                    <input type="number" name="age" id="age" placeholder="مثال: 21" min="15" max="99" required>
                </div>
                <div class="input-group">
                    <label>الرتبة الحالية (Rank)</label>
                    <select name="rank" id="rank" required>
                        <option value="" disabled selected>اختر رتبتك...</option>
                        <option value="مبتدئ">مبتدئ (Beginner)</option>
                        <option value="متوسط">متوسط (Intermediate)</option>
                        <option value="محترف">محترف (Professional)</option>
                        <option value="خبير">خبير (Expert)</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>الشركة المراد الانضمام إليها (Company)</label>
                    <select name="company" id="company" required>
                        <option value="" disabled selected>اختر الشركة...</option>
                        <option value="شركة النخبة">شركة النخبة (Elite)</option>
                        <option value="السرعة القصوى">السرعة القصوى (Max Speed)</option>
                        <option value="النقل الآمن">النقل الآمن (Safe Transport)</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>نبذة عنك (Bio)</label>
                    <textarea name="bio" id="bio" placeholder="اكتب عن خبرتك في القيادة..." maxlength="200" required></textarea>
                    <span class="char-count" id="charCount">0 / 200</span>
                </div>
                <button type="submit" class="btn-submit" id="submitBtn">
                    <span>إرسال الطلب</span>
                </button>
            </form>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        particlesJS("particles-js", {
            "particles": { "number": { "value": 60, "density": { "enable": true, "value_area": 800 } }, "color": { "value": ["#00f2fe", "#4facfe"] }, "shape": { "type": "circle" }, "opacity": { "value": 0.5, "random": true }, "size": { "value": 3, "random": true }, "line_linked": { "enable": true, "distance": 150, "color": "#4facfe", "opacity": 0.2, "width": 1 }, "move": { "enable": true, "speed": 1.5, "direction": "none", "random": true, "out_mode": "out" } },
            "interactivity": { "detect_on": "canvas", "events": { "onhover": { "enable": true, "mode": "grab" }, "onclick": { "enable": true, "mode": "push" } }, "modes": { "grab": { "distance": 140, "line_linked": { "opacity": 0.5 } } } },
            "retina_detect": true
        });
        const bioInput = document.getElementById('bio');
        const charCount = document.getElementById('charCount');
        bioInput.addEventListener('input', () => { charCount.textContent = `${bioInput.value.length} / 200`; });
        function showToast(message, type) {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            container.appendChild(toast);
            setTimeout(() => { toast.remove(); }, 4000);
        }
        document.getElementById('vtcForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span>جاري الإرسال...</span>';
            btn.disabled = true;
            const formData = new FormData(e.target);
            try {
                const response = await fetch('/submit', { method: 'POST', body: formData });
                if (response.ok) {
                    showToast('تم إرسال طلبك بنجاح! يرجى الانتظار حتى يتم مراجعته.', 'success');
                    e.target.reset();
                    charCount.textContent = '0 / 200';
                } else {
                    showToast('حدث خطأ أثناء الإرسال. يرجى المحاولة لاحقاً.', 'error');
                }
            } catch (error) {
                showToast('تعذر الاتصال بالسيرفر. تحقق من اتصالك.', 'error');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

# قراءة ملف app.py الأصلي
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# البحث عن بداية ونهاية الواجهة القديمة
start_marker = 'return render_template_string("""'
end_marker = '""")'

start_idx = code.find(start_marker)
if start_idx != -1:
    end_idx = code.find(end_marker, start_idx + len(start_marker))
    if end_idx != -1:
        # استبدال الواجهة القديمة بالجديدة دون المساس بباقي الكود
        new_code = code[:start_idx + len(start_marker)] + '\n' + new_html + '\n    ' + code[end_idx:]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_code)
        print("✅ تم تحديث ملف app.py بنجاح! (الواجهة الجديدة جاهزة)")
    else:
        print("❌ لم يتم العثور على نهاية الواجهة القديمة.")
else:
    print("❌ لم يتم العثور على بداية الواجهة القديمة.")

