import os
import uuid
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── HTML Template ─────────────────────────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Chỉ Tay Huyền Bí · Palmistry AI</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap" rel="stylesheet"/>
<style>
  :root {
    --ink:      #0d0b14;
    --deep:     #110e1f;
    --gold:     #c9a84c;
    --gold2:    #e8c97a;
    --mystic:   #7b4fa6;
    --glow:     #b06ef3;
    --blood:    #8b1a1a;
    --cream:    #f5edd6;
    --muted:    #7a6e8a;
    --line:     rgba(201,168,76,0.25);
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }

  body {
    font-family: 'Cormorant Garamond', serif;
    background: var(--ink);
    color: var(--cream);
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
  }

  /* ── Stars background ── */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 50% -10%, rgba(123,79,166,0.35) 0%, transparent 70%),
      radial-gradient(ellipse 50% 40% at 90% 80%, rgba(139,26,26,0.2) 0%, transparent 60%),
      radial-gradient(ellipse 40% 30% at 10% 90%, rgba(201,168,76,0.1) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
  }

  /* Animated stars */
  .stars {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    overflow: hidden;
  }
  .star {
    position: absolute;
    background: white;
    border-radius: 50%;
    animation: twinkle var(--dur, 3s) ease-in-out infinite;
    animation-delay: var(--del, 0s);
    opacity: 0;
  }
  @keyframes twinkle {
    0%, 100% { opacity: 0; transform: scale(0.5); }
    50%       { opacity: var(--op, 0.8); transform: scale(1); }
  }

  main { position: relative; z-index: 1; }

  /* ── Header ── */
  header {
    text-align: center;
    padding: 60px 20px 30px;
    border-bottom: 1px solid var(--line);
  }
  .eye-symbol {
    font-size: 3rem;
    display: block;
    margin-bottom: 12px;
    filter: drop-shadow(0 0 16px var(--glow));
    animation: float 4s ease-in-out infinite;
  }
  @keyframes float {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
  }
  h1 {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(1.6rem, 4vw, 2.8rem);
    font-weight: 900;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold2) 50%, var(--gold) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 0.06em;
    text-shadow: none;
    line-height: 1.2;
  }
  .tagline {
    margin-top: 10px;
    font-size: 1.05rem;
    font-style: italic;
    color: var(--muted);
    letter-spacing: 0.1em;
  }
  .ornament {
    margin: 18px auto 0;
    color: var(--gold);
    font-size: 1.2rem;
    letter-spacing: 0.5em;
    opacity: 0.6;
  }

  /* ── Upload section ── */
  .upload-section {
    max-width: 600px;
    margin: 50px auto 0;
    padding: 0 20px;
  }

  .drop-zone {
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 48px 32px;
    text-align: center;
    cursor: pointer;
    background: rgba(201,168,76,0.03);
    transition: background 0.3s, border-color 0.3s;
    position: relative;
    overflow: hidden;
  }
  .drop-zone::before, .drop-zone::after {
    content: '';
    position: absolute;
    width: 40px; height: 40px;
    border-color: var(--gold);
    border-style: solid;
    opacity: 0.5;
  }
  .drop-zone::before { top: 12px; left: 12px; border-width: 1px 0 0 1px; }
  .drop-zone::after  { bottom: 12px; right: 12px; border-width: 0 1px 1px 0; }
  .drop-zone:hover, .drop-zone.drag-over {
    background: rgba(201,168,76,0.07);
    border-color: rgba(201,168,76,0.6);
  }

  .drop-icon { font-size: 3rem; margin-bottom: 14px; opacity: 0.8; }
  .drop-text { font-size: 1.1rem; color: var(--cream); font-style: italic; }
  .drop-sub  { margin-top: 6px; font-size: 0.85rem; color: var(--muted); }

  #file-input { display: none; }

  /* Preview */
  #preview-wrap {
    margin-top: 24px;
    display: none;
    text-align: center;
  }
  #preview-img {
    max-width: 100%; max-height: 280px;
    border: 1px solid var(--line);
    border-radius: 4px;
    filter: sepia(0.15) contrast(1.05);
  }

  /* ── Buttons ── */
  .btn-divine {
    display: block;
    width: 100%;
    margin-top: 28px;
    padding: 16px 32px;
    font-family: 'Cinzel Decorative', serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: var(--ink);
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold2) 50%, var(--gold) 100%);
    border: none;
    border-radius: 2px;
    cursor: pointer;
    text-transform: uppercase;
    transition: opacity 0.2s, transform 0.2s;
  }
  .btn-divine:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
  .btn-divine:disabled { opacity: 0.4; cursor: not-allowed; }

  /* ── Loading ── */
  #loading {
    display: none;
    text-align: center;
    padding: 40px 20px;
  }
  .crystal-ball {
    font-size: 4rem;
    display: inline-block;
    animation: spin-glow 2s linear infinite;
  }
  @keyframes spin-glow {
    0%   { filter: drop-shadow(0 0 8px var(--mystic)); transform: scale(1); }
    50%  { filter: drop-shadow(0 0 24px var(--glow)); transform: scale(1.1); }
    100% { filter: drop-shadow(0 0 8px var(--mystic)); transform: scale(1); }
  }
  .loading-text {
    margin-top: 16px;
    font-style: italic;
    color: var(--muted);
    font-size: 1.05rem;
    animation: pulse-text 1.8s ease-in-out infinite;
  }
  @keyframes pulse-text { 0%,100%{opacity:0.5} 50%{opacity:1} }

  /* ── Result card ── */
  #result {
    display: none;
    max-width: 640px;
    margin: 40px auto 60px;
    padding: 0 20px;
  }

  .result-card {
    border: 1px solid var(--line);
    border-radius: 4px;
    background: rgba(17,14,31,0.8);
    overflow: hidden;
    animation: reveal 0.8s ease;
  }
  @keyframes reveal {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .card-header {
    background: linear-gradient(135deg, rgba(123,79,166,0.4), rgba(139,26,26,0.3));
    padding: 28px 32px 22px;
    text-align: center;
    border-bottom: 1px solid var(--line);
    position: relative;
  }
  .destiny-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 8px;
    filter: drop-shadow(0 0 12px var(--glow));
  }
  .destiny-name {
    font-family: 'Cinzel Decorative', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gold2);
    letter-spacing: 0.08em;
  }
  .destiny-title {
    margin-top: 6px;
    font-size: 1rem;
    font-style: italic;
    color: var(--muted);
    letter-spacing: 0.12em;
  }
  .cluster-badge {
    position: absolute; top: 14px; right: 18px;
    font-size: 0.7rem;
    color: var(--muted);
    font-family: monospace;
    letter-spacing: 0.1em;
  }

  .card-body { padding: 28px 32px; }

  .info-row {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }
  .info-chip {
    flex: 1; min-width: 140px;
    padding: 12px 16px;
    border: 1px solid var(--line);
    border-radius: 3px;
    background: rgba(201,168,76,0.04);
  }
  .chip-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    margin-bottom: 5px;
  }
  .chip-value { font-size: 1rem; color: var(--cream); }

  .divider {
    border: none;
    border-top: 1px solid var(--line);
    margin: 20px 0;
  }

  .destiny-desc {
    font-size: 1.05rem;
    line-height: 1.8;
    color: rgba(245,237,214,0.85);
    font-style: italic;
    text-align: center;
  }

  .lucky-row {
    margin-top: 22px;
    padding: 16px 20px;
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 3px;
    background: rgba(201,168,76,0.03);
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .lucky-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--gold);
    white-space: nowrap;
  }
  .lucky-values { font-size: 0.95rem; color: var(--cream); }

  /* Confidence bar */
  .conf-wrap { margin-top: 22px; }
  .conf-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
  }
  .conf-bar-bg {
    height: 4px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    overflow: hidden;
  }
  .conf-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--mystic), var(--gold));
    border-radius: 2px;
    transition: width 1.2s cubic-bezier(.16,1,.3,1);
  }

  .btn-reset {
    display: block;
    width: 100%;
    margin-top: 24px;
    padding: 12px;
    background: transparent;
    border: 1px solid var(--line);
    color: var(--muted);
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    cursor: pointer;
    border-radius: 2px;
    transition: color 0.2s, border-color 0.2s;
  }
  .btn-reset:hover { color: var(--cream); border-color: var(--gold); }

  /* Error */
  .error-box {
    padding: 20px 24px;
    border: 1px solid rgba(139,26,26,0.6);
    border-radius: 3px;
    background: rgba(139,26,26,0.1);
    color: #e07070;
    font-style: italic;
    text-align: center;
  }

  /* Footer */
  footer {
    text-align: center;
    padding: 24px;
    font-size: 0.78rem;
    color: var(--muted);
    border-top: 1px solid var(--line);
    letter-spacing: 0.08em;
  }
</style>
</head>
<body>

<!-- Stars -->
<div class="stars" id="stars"></div>

<main>
  <header>
    <span class="eye-symbol">🔮</span>
    <h1>Chỉ Tay Huyền Bí</h1>
    <p class="tagline">Khám phá vận mệnh qua dấu ấn bàn tay · Palmistry AI</p>
    <div class="ornament">✦ ✦ ✦</div>
  </header>

  <div class="upload-section">
    <div class="drop-zone" id="drop-zone" onclick="document.getElementById('file-input').click()">
      <div class="drop-icon">🖐️</div>
      <div class="drop-text">Đặt ảnh bàn tay vào đây</div>
      <div class="drop-sub">hoặc nhấn để chọn ảnh · JPG / PNG · tối đa 10 MB</div>
      <input type="file" id="file-input" accept="image/*"/>
    </div>

    <div id="preview-wrap">
      <img id="preview-img" alt="Preview"/>
    </div>

    <button class="btn-divine" id="btn-read" disabled onclick="submitImage()">
      ✦ &nbsp; Đọc Vận Mệnh &nbsp; ✦
    </button>
  </div>

  <div id="loading">
    <div class="crystal-ball">🔮</div>
    <div class="loading-text">Đang giải mã bàn tay của bạn…</div>
  </div>

  <div id="result"></div>
</main>

<footer>
  Palmistry AI · Bài 5 – Nhận Dạng Chỉ Tay · IITD Palmprint Dataset · CNN + KMeans
</footer>

<script>
// ── Generate stars ──────────────────────────────────────────────────────────
(function(){
  const c = document.getElementById('stars');
  for(let i=0;i<120;i++){
    const s = document.createElement('div');
    s.className='star';
    const size = Math.random()*2+0.5;
    s.style.cssText = `
      width:${size}px; height:${size}px;
      top:${Math.random()*100}%; left:${Math.random()*100}%;
      --dur:${(Math.random()*4+2).toFixed(1)}s;
      --del:-${(Math.random()*6).toFixed(1)}s;
      --op:${(Math.random()*0.6+0.2).toFixed(2)};
    `;
    c.appendChild(s);
  }
})();

// ── File handling ────────────────────────────────────────────────────────────
let selectedFile = null;

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const btnRead   = document.getElementById('btn-read');

fileInput.addEventListener('change', e => handleFile(e.target.files[0]));

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
  if (!file || !file.type.startsWith('image/')) return;
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = ev => {
    document.getElementById('preview-img').src = ev.target.result;
    document.getElementById('preview-wrap').style.display = 'block';
  };
  reader.readAsDataURL(file);
  btnRead.disabled = false;
  document.getElementById('result').style.display = 'none';
}

// ── Submit ────────────────────────────────────────────────────────────────────
function submitImage() {
  if (!selectedFile) return;
  btnRead.disabled = true;
  document.querySelector('.upload-section').style.opacity = '0.4';
  document.getElementById('loading').style.display = 'block';
  document.getElementById('result').style.display = 'none';

  const fd = new FormData();
  fd.append('image', selectedFile);

  fetch('/predict', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => showResult(data))
    .catch(() => showError('Đã có lỗi xảy ra. Vui lòng thử lại.'))
    .finally(() => {
      document.getElementById('loading').style.display = 'none';
      document.querySelector('.upload-section').style.opacity = '1';
      btnRead.disabled = false;
    });
}

// ── Render result ─────────────────────────────────────────────────────────────
function showResult(data) {
  const el = document.getElementById('result');
  if (data.error) { showError(data.error); return; }

  const d = data.destiny;
  const conf = data.confidence;

  el.innerHTML = `
    <div class="result-card">
      <div class="card-header">
        <span class="cluster-badge">Nhóm #${data.cluster_id}</span>
        <span class="destiny-icon">${d.icon}</span>
        <div class="destiny-name">${d.name}</div>
        <div class="destiny-title">${d.title}</div>
      </div>
      <div class="card-body">
        <div class="info-row">
          <div class="info-chip">
            <div class="chip-label">Loại Bàn Tay</div>
            <div class="chip-value">${data.palm_type_label}</div>
          </div>
          <div class="info-chip">
            <div class="chip-label">Nguyên Tố</div>
            <div class="chip-value">${d.element}</div>
          </div>
        </div>
        <div class="chip-label" style="font-size:0.78rem;color:var(--muted);font-style:italic;margin-bottom:10px;">
          ${data.palm_type_desc}
        </div>

        <hr class="divider"/>

        <p class="destiny-desc">"${d.desc}"</p>

        <div class="lucky-row">
          <span class="lucky-label">✦ May Mắn</span>
          <span class="lucky-values">${d.lucky}</span>
        </div>

        <div class="conf-wrap">
          <div class="conf-label">
            <span>Độ Tin Cậy Phân Loại</span>
            <span>${conf}%</span>
          </div>
          <div class="conf-bar-bg">
            <div class="conf-bar-fill" id="conf-fill" style="width:0%"></div>
          </div>
        </div>

        <button class="btn-reset" onclick="resetApp()">↩ Đọc Bàn Tay Khác</button>
      </div>
    </div>
  `;

  el.style.display = 'block';
  setTimeout(() => {
    document.getElementById('conf-fill').style.width = conf + '%';
  }, 100);
  el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(msg) {
  const el = document.getElementById('result');
  el.innerHTML = `<div class="error-box">⚠ ${msg}</div>`;
  el.style.display = 'block';
}

function resetApp() {
  selectedFile = null;
  document.getElementById('file-input').value = '';
  document.getElementById('preview-wrap').style.display = 'none';
  document.getElementById('preview-img').src = '';
  document.getElementById('result').style.display = 'none';
  document.getElementById('btn-read').disabled = true;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
</script>
</body>
</html>
"""

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/predict", methods=["POST"])
def predict_route():
    if "image" not in request.files:
        return jsonify({"error": "Không tìm thấy ảnh trong request."}), 400

    img_file = request.files["image"]
    if img_file.filename == "":
        return jsonify({"error": "Tên file không hợp lệ."}), 400

    ext = os.path.splitext(img_file.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
        return jsonify({"error": "Định dạng ảnh không được hỗ trợ."}), 400

    tmp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}{ext}")
    try:
        img_file.save(tmp_path)
        from predict import predict
        result = predict(tmp_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý: {str(e)}"}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    print("🔮  Palmistry AI đang khởi động...")
    print("    Truy cập: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)