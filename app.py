import os
import yt_dlp
import threading
import queue
import json
import tempfile
import uuid
import time
from flask import Flask, render_template, request, Response, jsonify, send_from_directory, after_this_request

# --- CONFIGURAÇÃO DOS TRABALHADORES ---
WORKER_COUNT = 3
job_queue = queue.Queue()

# --- CONFIGURAÇÃO GERAL ---
DOWNLOAD_FOLDER = tempfile.gettempdir()
MAX_FILE_AGE_SECONDS = 3600

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

progress_queue = queue.Queue()
job_info = {'total': 0, 'completed': 0}
job_lock = threading.Lock()

class YtdlpLogger:
    def __init__(self, download_id):
        self.download_id = download_id
    def debug(self, msg):
        if msg.startswith('[debug]'): return
        self.info(msg)
    def info(self, msg):
        progress_queue.put({"id": self.download_id, "status": "logging", "text": msg})
    def warning(self, msg): self.info(f"AVISO: {msg}")
    def error(self, msg): self.info(f"ERRO: {msg}")

def baixar_video_thread(url, download_id):
    final_filepath = None
    try:
        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes')
                percentage = 0
                if total_bytes and downloaded_bytes:
                    percentage = (downloaded_bytes / total_bytes) * 100
                progress_queue.put({
                    "id": download_id, "status": "downloading", "percentage": percentage,
                    "title": d.get('info_dict', {}).get('title', 'video')[:50]
                })

        def postprocessor_hook(d):
            nonlocal final_filepath
            if d['status'] == 'finished':
                final_filepath = d['info_dict'].get('filepath')

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{uuid.uuid4()}_%(title)s.%(ext)s'),
            'noplaylist': True, 'logger': YtdlpLogger(download_id),
            'progress_hooks': [progress_hook], 'postprocessor_hooks': [postprocessor_hook],
            'nocolor': True, 'ignoreerrors': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if not final_filepath:
                final_filepath = ydl.prepare_filename(info_dict)
        
        if final_filepath and os.path.exists(final_filepath):
            final_filename = os.path.basename(final_filepath)
            progress_queue.put({
                "id": download_id, "status": "done",
                "text": f"Pronto para Salvar: {os.path.basename(info_dict['title'])}.mp4",
                "filename": final_filename
            })
        else:
             raise Exception("Arquivo final não foi encontrado.")

    except Exception as e:
        progress_queue.put({"id": download_id, "status": "error", "text": f"❌ Erro ao baixar {url}: {e}"})
    
    finally:
        with job_lock:
            job_info['completed'] += 1
            if job_info['completed'] >= job_info['total']:
                progress_queue.put({"status": "batch_complete"})

def worker():
    while True:
        url, download_id = job_queue.get()
        print(f"Trabalhador {threading.get_ident()} pegou a tarefa: {url}")
        baixar_video_thread(url, download_id)
        job_queue.task_done()

def cleanup_old_files():
    now = time.time()
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) and (now - os.path.getmtime(file_path)) > MAX_FILE_AGE_SECONDS:
                os.remove(file_path)
        except Exception as e:
            print(f"Erro ao limpar arquivo antigo {filename}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    cleanup_old_files()
    data = request.get_json()
    links = data.get('links', [])
    
    with job_lock:
        job_info['total'] = len(links)
        job_info['completed'] = 0

    for link in links:
        download_id = f"dl-{uuid.uuid4()}"
        progress_queue.put({"id": download_id, "status": "queued", "text": f"Na fila: {link}"})
        job_queue.put((link, download_id))
        
    return jsonify({"status": "success"})

@app.route('/get-file/<path:filename>')
def get_file(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception as error:
            print(f"Erro ao remover arquivo {filename}: {error}")
        return response
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            data = progress_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(), mimetype='text/event-stream')

# --- MUDANÇA IMPORTANTE: INICIANDO OS TRABALHADORES AQUI ---
# Este código agora roda quando o Gunicorn importa o arquivo,
# garantindo que os trabalhadores sejam iniciados.
for _ in range(WORKER_COUNT):
    threading.Thread(target=worker, daemon=True).start()

# O bloco abaixo agora serve APENAS para desenvolvimento local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)