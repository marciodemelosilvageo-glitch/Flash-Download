import os
import re
import json
import uuid
import time
import requests
import threading
from flask import Flask, request, jsonify, render_template_string, send_file, Response

app = Flask(__name__)

DOWNLOADS_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!doctype html>
<html lang="pt-BR" style="height: 100%; margin: 0;">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Macim Download</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <style>
    body {
      margin: 0;
      background-color: #020617;
      color: #f8fafc;
      font-family: 'Outfit', sans-serif;
      overflow-x: hidden;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .glass-panel {
      background: rgba(255, 255, 255, 0.03);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 2.5rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    .glass-input {
      background: rgba(2, 6, 23, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.05);
      color: white;
      transition: all 0.3s ease;
    }
    .glass-input:focus {
      border-color: rgba(139, 92, 246, 0.5);
      box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.5);
      outline: none;
    }
    .blob {
      position: absolute;
      border-radius: 50%;
      filter: blur(120px);
      z-index: -1;
      animation: float 10s infinite ease-in-out alternate;
    }
    .blob-1 { top: -10%; left: -5%; width: 500px; height: 500px; background: rgba(124, 58, 237, 0.25); }
    .blob-2 { bottom: -10%; right: -5%; width: 600px; height: 600px; background: rgba(37, 99, 235, 0.2); animation-delay: -5s; }
    .blob-3 { top: 20%; right: 10%; width: 300px; height: 300px; background: rgba(99, 102, 241, 0.15); animation-delay: -2s; }
    @keyframes float {
      0% { transform: translate(0, 0) scale(1); }
      100% { transform: translate(30px, 50px) scale(1.1); }
    }
    .loader-ring {
      width: 24px; height: 24px;
      border: 3px solid rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 1s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .fade-in-up { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    #toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 50;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
    }
    .toast {
      padding: 16px 20px;
      border-radius: 1rem;
      color: white;
      font-weight: 500;
      font-size: 0.875rem;
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
      display: flex;
      align-items: center;
      gap: 12px;
      animation: toastIn 0.3s ease-out forwards;
      pointer-events: auto;
    }
    .toast.error { background: rgba(225, 29, 72, 0.9); }
    .toast.success { background: rgba(16, 185, 129, 0.9); }
    .toast.fade-out { animation: toastOut 0.3s ease-in forwards; }
    @keyframes toastIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes toastOut {
      from { opacity: 1; transform: translateY(0); }
      to { opacity: 0; transform: translateY(20px); }
    }
  </style>
</head>
<body>
  <div class="relative flex items-center justify-center p-4 min-h-screen font-sans w-full">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <main class="w-full max-w-4xl glass-panel overflow-hidden fade-in-up flex flex-col relative z-10 p-8 sm:p-12 gap-8">
      <div class="text-center space-y-4 relative">
        <h1 class="text-5xl sm:text-7xl font-black tracking-tighter leading-none mb-2">
          Macim <span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-blue-400">Download</span>
        </h1>
        <p class="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto font-medium">
          Baixe vídeos em alta qualidade direto no seu dispositivo.
        </p>
      </div>

      <div class="w-full">
        <form id="download-form" class="flex flex-col sm:flex-row gap-4 mb-8">
          <div class="relative flex-1">
            <input
              type="url"
              id="url-input"
              class="w-full glass-input rounded-2xl py-6 px-6 text-lg sm:text-xl focus:outline-none transition-all placeholder-slate-500 font-medium"
              placeholder="Cole o link do vídeo aqui..."
              required
              autocomplete="off"
            />
          </div>
          <button
            type="submit"
            id="submit-btn"
            class="px-10 py-6 bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 rounded-2xl font-bold text-lg shadow-lg shadow-violet-500/20 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed text-white flex items-center justify-center gap-3 transition-all min-w-[200px]"
          >
            <span id="btn-text">Baixar Agora</span>
          </button>
        </form>

        <div class="flex justify-center gap-6 sm:gap-10 items-center grayscale opacity-50 flex-wrap mt-10">
          <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-red-500"></div><span class="text-xs font-bold uppercase tracking-widest text-slate-300">YouTube</span></div>
          <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-pink-500"></div><span class="text-xs font-bold uppercase tracking-widest text-slate-300">TikTok</span></div>
          <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-blue-400"></div><span class="text-xs font-bold uppercase tracking-widest text-slate-300">Twitter</span></div>
          <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-blue-600"></div><span class="text-xs font-bold uppercase tracking-widest text-slate-300">Facebook</span></div>
          <div class="flex items-center gap-2 text-violet-400 grayscale-0 opacity-100"><div class="w-3 h-3 rounded-full bg-violet-400 animate-pulse"></div><span class="text-xs font-bold uppercase tracking-widest">+ 40 Mais</span></div>
        </div>
      </div>
    </main>
    
    <div id="toast-container"></div>
  </div>

  <script>
    const form = document.getElementById('download-form');
    const input = document.getElementById('url-input');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const toastContainer = document.getElementById('toast-container');

    function showToast(message, type = 'error') {
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      toast.innerHTML = `<span>${message}</span>`;
      toastContainer.appendChild(toast);
      setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const url = input.value.trim();
      
      if (!url) return;
      
      if (url.toLowerCase().includes('instagram.com')) {
        // Permitir instagram
      }

      submitBtn.disabled = true;
      const originalText = btnText.innerText;
      btnText.innerHTML = '<div class="loader-ring"></div> Processando...';

      try {
        const response = await fetch('/api/download_video', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
          showToast('Processamento concluído! O download começará em instantes.', 'success');
          
          if (data.direto) {
            const a = document.createElement('a');
            a.href = data.url;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          } else {
            const a = document.createElement('a');
            a.href = `/api/download_file?id=${data.id}&ext=${data.ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          }
          input.value = '';
        } else {
          showToast(data.erro || 'Ocorreu um erro ao processar o vídeo.', 'error');
        }
      } catch (error) {
        showToast('Erro de conexão. Tente novamente mais tarde.', 'error');
      } finally {
        submitBtn.disabled = false;
        btnText.innerText = originalText;
      }
    });
  </script>
</body>
</html>
"""

def clean_old_files():
    now = time.time()
    for filename in os.listdir(DOWNLOADS_DIR):
        file_path = os.path.join(DOWNLOADS_DIR, filename)
        if os.path.isfile(file_path):
            if os.stat(file_path).st_mtime < now - 3600:
                try:
                    os.remove(file_path)
                except:
                    pass

def get_cobalt_direct_link(url):
    # Usando uma abordagem mais robusta para APIs de terceiros para Youtube e Douyin
    instances = [
        "https://co.wuk.sh",
        "https://api.cobalt.tools"
    ]
    
    payload = {
        "url": url,
        "videoQuality": "1080"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    for instance in instances:
        try:
            # Cobalt v11 API uses POST /
            response = requests.post(instance, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Em v11 status: "redirect" or "tunnel" com "url"
                if data.get('status') in ['redirect', 'tunnel'] and 'url' in data:
                    return data['url']
        except Exception:
            continue
            
    return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/download_video', methods=['POST'])
def process_download():
    # Limpa arquivos antigos do servidor assincronamente
    threading.Thread(target=clean_old_files).start()
    
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({"sucesso": False, "erro": "URL ausente."}), 400
        
    url_lower = url.lower()
    
    if 'instagram.com' in url_lower:
        pass # Permitir
        
    # Youtube e Douyin são agressivos contra bloqueios, tentamos a API Ninja primeiro
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower or 'douyin' in url_lower:
        direct_link = get_cobalt_direct_link(url)
        if direct_link:
            return jsonify({"sucesso": True, "direto": True, "url": direct_link})
            
        if 'youtube' in url_lower:
            return jsonify({"sucesso": False, "erro": "A segurança do YouTube impediu a extração neste momento. Tente novamente mais tarde."})
            
    # Fallback para yt-dlp para as demais plataformas (TikTok, Facebook, Twitter, Kwai, etc.)
    file_id = str(uuid.uuid4())
    ext = 'mp4'
    output_path = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")
    
    import yt_dlp
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"sucesso": True, "id": file_id, "ext": ext})
    except Exception as e:
        print(f"Erro yt-dlp: {e}")
        return jsonify({"sucesso": False, "erro": "Falha ao processar o vídeo. Verifique se o link é público e válido."})

@app.route('/api/download_file', methods=['GET'])
def download_file():
    file_id = request.args.get('id')
    ext = request.args.get('ext', 'mp4')
    
    if not file_id:
        return "ID ausente", 400
        
    file_path = os.path.join(DOWNLOADS_DIR, f"{file_id}.{ext}")
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"macim_download.{ext}")
    else:
        return "Arquivo não encontrado ou expirou.", 404

if __name__ == '__main__':
    # Para o Render.com o gunicorn vai usar esta app
    app.run(host='0.0.0.0', port=5000)
