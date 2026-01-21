import os
import glob
import eel
import markdown
import shutil
from pathlib import Path

# === Bottle для HTTP-роутов ===
from bottle import route, response, request

# === Пути ===
SCRIPT_DIR = Path(__file__).resolve().parent
HELP_DOC_DIR = SCRIPT_DIR / "help_doc"
WAL_SRC = SCRIPT_DIR / "Wal" / "wal.png"
WEB_DIR = SCRIPT_DIR / "web"
ICONS_DIR = WEB_DIR / "icons"

WEB_DIR.mkdir(exist_ok=True)
ICONS_DIR.mkdir(exist_ok=True)

# === Копируем wal.png в web/ ОДИН РАЗ ===
WAL_WEB = WEB_DIR / "wal.png"
if WAL_SRC.exists() and not WAL_WEB.exists():
    WAL_WEB.write_bytes(WAL_SRC.read_bytes())

# Используем /wal.png для всего
wal_url_http = "/wal.png" if WAL_WEB.exists() else ""

def copy_icon_to_web(icon_src_path: Path) -> str:
    if not icon_src_path.exists():
        return "/icons/fallback.png"
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in icon_src_path.name)
    target = ICONS_DIR / safe_name
    try:
        if not target.exists() or target.stat().st_mtime < icon_src_path.stat().st_mtime:
            shutil.copy2(icon_src_path, target)
        return f"/icons/{safe_name}"
    except Exception:
        return "/icons/fallback.png"

def create_fallback_icon():
    fallback = ICONS_DIR / "fallback.png"
    if not fallback.exists():
        import base64
        data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP4/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")
        fallback.write_bytes(data)

def parse_ldp_conf():
    conf_path = SCRIPT_DIR / "ldp.conf"
    if not conf_path.exists():
        return []
    try:
        content = conf_path.read_text(encoding='utf-8').strip()
    except Exception:
        return []
    entries = []
    blocks = [block.strip() for block in content.split('***') if block.strip()]
    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) >= 3:
            name = lines[0]
            exec_cmd = lines[1]
            icon_path_str = lines[2]
            icon_src = Path(icon_path_str)
            icon_url = copy_icon_to_web(icon_src)
            entries.append({
                'name': name,
                'exec': exec_cmd,
                'icon': icon_url
            })
    return entries

def get_markdown_files():
    docs = []
    for md_path in glob.glob(str(HELP_DOC_DIR / "*.md")):
        name = Path(md_path).stem
        # Сохраняем относительный путь от HELP_DOC_DIR
        rel_path = md_path[len(str(HELP_DOC_DIR)) + 1:]
        docs.append({"name": name, "path": rel_path})
    return docs

def generate_index_html():
    apps = parse_ldp_conf()
    docs = get_markdown_files()
    bg_style = f"background-image: url('{wal_url_http}'); background-size: cover; background-attachment: fixed;" if wal_url_http else ""

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LiveDistro Portal</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            min-height: 100vh;
            {bg_style}
            font-family: sans-serif;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0;
            font-size: 2.2em;
        }}
        .tabs {{
            display: flex;
            justify-content: center;
            gap: 2px;
            margin-bottom: 25px;
        }}
        .tab {{
            padding: 10px 24px;
            cursor: pointer;
            background: rgba(0,0,0,0.3);
            border: none;
            color: white;
            font-weight: bold;
        }}
        .tab.active {{
            background: rgba(60,120,255,0.4);
            border-radius: 6px 6px 0 0;
        }}
        .tab-content {{
            display: none;
            padding: 25px;
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.25);
        }}
        .tab-content.active {{
            display: block;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
            gap: 22px;
            justify-items: center;
        }}
        .shortcut {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100px;
            cursor: pointer;
        }}
        .shortcut-icon {{
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            border-radius: 12px;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.15);
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        .shortcut-icon img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}
        .shortcut-label {{
            text-align: center;
            font-size: 12px;
            line-height: 1.3;
            max-width: 100px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 LiveDistro Portal</h1>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('apps')">Утилиты</button>
            <button class="tab" onclick="switchTab('docs')">Справка</button>
        </div>

        <div id="apps" class="tab-content active">
            <div class="grid">
"""

    if apps:
        for app in apps:
            icon_url = app['icon']
            icon_html = f'<img src="{icon_url}" style="width:100%;height:100%;object-fit:contain;" loading="lazy">'
            html_content += f'''
                <div class="shortcut" onclick="launchApp(`{app['exec']}`)">
                    <div class="shortcut-icon">{icon_html}</div>
                    <div class="shortcut-label">{app['name']}</div>
                </div>
'''
    else:
        html_content += '<p style="text-align:center;">Нет приложений (создайте ldp.conf)</p>'

    html_content += """
            </div>
        </div>

        <div id="docs" class="tab-content">
            <div class="grid">
"""

    if docs:
        for doc in docs:
            html_content += f'''
                <div class="shortcut" onclick="openDoc(`{doc['path']}`)">
                    <div class="shortcut-icon">📘</div>
                    <div class="shortcut-label">{doc['name']}</div>
                </div>
'''
    else:
        html_content += '<p style="text-align:center;">Нет справки</p>'

    html_content += """
            </div>
        </div>
    </div>

    <script type="text/javascript" src="/eel.js"></script>
    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }

        async function launchApp(cmd) {
            try {
                await eel.run_command(cmd)();
            } catch (e) {
                alert('Ошибка запуска: ' + e);
            }
        }

        function openDoc(relPath) {
            // Открываем через HTTP-роут
            window.open('/render_md?path=' + encodeURIComponent(relPath), '_blank', 'width=900,height=700');
        }
    </script>
</body>
</html>
"""
    (WEB_DIR / "index.html").write_text(html_content, encoding='utf-8')

# === HTTP-РОУТ ДЛЯ MARKDOWN ===
@route('/render_md')
def http_render_md():
    path = request.query.path
    if not path:
        response.status = 400
        return "<h2>Путь не указан</h2>"
    
    # Безопасное разрешение пути
    full_path = (HELP_DOC_DIR / path).resolve()
    if not str(full_path).startswith(str(HELP_DOC_DIR.resolve())):
        response.status = 403
        return "<h2>Доступ запрещён</h2>"
    if not full_path.exists():
        response.status = 404
        return "<h2>Файл не найден</h2>"
    
    try:
        md_text = full_path.read_text(encoding='utf-8')
        html_body = markdown.markdown(md_text)
    except Exception as e:
        html_body = f"<h2>Ошибка рендера: {e}</h2>"

    bg_style = f"background-image: url('{wal_url_http}'); background-size: cover; background-attachment: fixed;" if wal_url_http else ""
    response.content_type = 'text/html; charset=utf-8'
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            {bg_style}
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            font-family: sans-serif;
        }}
        .content {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.25);
            padding: 25px;
            border-radius: 12px;
        }}
        a {{ color: #bbf; }}
        pre, code {{
            background: rgba(0,0,0,0.4);
            padding: 8px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="content">
        {html_body}
    </div>
</body>
</html>
"""

# === Eel API ===
@eel.expose
def run_command(cmd):
    import subprocess
    import os
    try:
        env = os.environ.copy()
        if 'DISPLAY' not in env:
            env['DISPLAY'] = ':0'
        safe_cmd = cmd.replace("'", "'\"'\"'")
        full_cmd = f"bash -l -c '{safe_cmd}'"
        subprocess.Popen(
            full_cmd,
            shell=True,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp
        )
        return True
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        return False

# === Запуск ===
if __name__ == "__main__":
    create_fallback_icon()
    generate_index_html()
    eel.init("web")

    import eel.browsers
    eel.browsers.open = lambda urls, args: None

    PORT = 8080
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{PORT}/index.html')

    threading.Thread(target=open_browser, daemon=True).start()

    print(f"\n✅ LiveDistro Portal запущен!")
    print(f"   Откройте: http://localhost:{PORT}/index.html")
    eel.start("index.html", size=(940, 700), port=PORT)