import { useState, FormEvent, useEffect } from 'react';
import { 
  Zap, 
  Youtube, 
  Twitter, 
  Facebook, 
  Link2, 
  ArrowRight, 
  CheckCircle, 
  ShieldCheck, 
  Download, 
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface VideoData {
  titulo: string;
  thumb: string;
}

interface ToastMessage {
  id: number;
  message: string;
  type: 'sucesso' | 'erro';
}

export default function App() {
  const [url, setUrl] = useState('');
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [quality, setQuality] = useState('alta');
  const [downloadState, setDownloadState] = useState<'idle' | 'downloading' | 'ready' | 'error'>('idle');
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = (message: string, type: 'sucesso' | 'erro' = 'erro') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleFetchInfo = async (e: FormEvent) => {
    e.preventDefault();
    if (!url.trim().startsWith('http://') && !url.trim().startsWith('https://')) {
      return showToast('Por favor, insira uma ligação válida.', 'erro');
    }

    if (url.toLowerCase().includes('instagram.com')) {
      // Allow instagram
    }

    setLoadingInfo(true);
    setVideoData(null);
    setDownloadState('idle');

    try {
      const res = await fetch('/api/info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      
      if (data.sucesso) {
        setVideoData(data.dados);
      } else {
        showToast(data.erro || 'Erro ao ler o vídeo. Verifique se o link está correto.', 'erro');
      }
    } catch (e) {
      showToast('Falha de conexão com o servidor.', 'erro');
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleDownload = async () => {
    setDownloadState('downloading');
    try {
      const res = await fetch('/api/download_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, qualidade: quality })
      });
      const data = await res.json();
      
      if (data.sucesso) {
        setDownloadState('ready');
        showToast('Download iniciado com sucesso!', 'sucesso');
        
        if (data.direto) {
          const a = document.createElement('a');
          a.href = data.url;
          a.target = '_blank';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        } else {
          const a = document.createElement('a');
          a.href = `/api/download_file?id=${data.id}&titulo=${encodeURIComponent(videoData?.titulo || '')}&ext=${data.ext}`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }

        setTimeout(() => {
          setDownloadState('idle');
          setVideoData(null);
          setUrl('');
        }, 5000);
      } else {
        showToast(data.erro || 'Falha na extração. Tente noutro momento.', 'erro');
        setDownloadState('error');
      }
    } catch (e) {
      showToast('Perda de conexão.', 'erro');
      setDownloadState('error');
    }
  };

  return (
    <div className="relative flex items-center justify-center p-4 min-h-screen font-sans">
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>

      <main className="w-full max-w-5xl glass-panel rounded-[2.5rem] overflow-hidden fade-in-up flex flex-col relative z-10 p-10 gap-8">
        <div className="text-center space-y-3 relative">
          <div className="inline-flex items-center justify-center p-4 bg-white/5 rounded-2xl mb-4 border border-white/10 shadow-lg backdrop-blur-md relative group mx-auto">
            <div className="absolute inset-0 bg-gradient-to-r from-violet-500 to-blue-500 opacity-20 group-hover:opacity-40 transition-opacity rounded-2xl blur-md"></div>
            <Zap className="w-10 h-10 text-violet-400 relative z-10" />
          </div>
          <h1 className="text-4xl sm:text-6xl font-black tracking-tighter leading-none mb-2">
            Flash <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-blue-400">Dowlooad</span>
          </h1>
          <p className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto">
            A nova geração de downloads em Alta Qualidade.
          </p>
        </div>

        <div className="w-full">
          <form onSubmit={handleFetchInfo} className="flex flex-col sm:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none text-slate-500">
                <Link2 className="w-6 h-6" />
              </div>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full bg-slate-950/50 border border-white/5 rounded-2xl py-6 pl-16 pr-6 text-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 transition-all placeholder-slate-600 text-white"
                placeholder="Cole a ligação do vídeo (TikTok, FB, YT...)"
                required
                autoComplete="off"
              />
            </div>
            
            <button
              type="submit"
              disabled={loadingInfo}
              className="px-10 py-6 bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 rounded-2xl font-bold text-lg shadow-lg shadow-violet-500/20 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed text-white flex items-center justify-center gap-2 transition-all"
            >
              <span>{loadingInfo ? 'A procurar...' : 'Processar Vídeo'}</span>
              {!loadingInfo && <ArrowRight className="w-5 h-5" />}
            </button>
          </form>

          <div className="mt-8 flex justify-center gap-6 sm:gap-10 items-center grayscale opacity-60 flex-wrap">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">YouTube</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-pink-500"></div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">TikTok</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-400"></div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Twitter / X</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-600"></div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Facebook</span>
            </div>
            <div className="flex items-center gap-2 text-violet-400 grayscale-0 opacity-100">
              <div className="w-3 h-3 rounded-full bg-violet-400 animate-pulse"></div>
              <span className="text-xs font-bold uppercase tracking-widest">+ 40 Mais</span>
            </div>
          </div>

          {loadingInfo && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="loader-ring mb-6"></div>
              <p className="text-violet-300 text-sm font-semibold tracking-widest uppercase animate-pulse">
                A procurar informações...
              </p>
            </div>
          )}

          {videoData && !loadingInfo && (
            <div className="mt-8 fade-in-up">
              <div className="bg-white/[0.03] backdrop-blur-md border border-white/5 rounded-3xl p-6 flex flex-col sm:flex-row gap-5 items-start mb-6">
                <div className="relative w-full sm:w-48 h-32 bg-slate-800 rounded-xl overflow-hidden group shrink-0">
                  <div className="absolute inset-0 bg-gradient-to-br from-violet-500/40 to-transparent z-10"></div>
                  <img src={videoData.thumb} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 relative z-0" alt="Video thumbnail" />
                  <div className="absolute bottom-2 right-2 bg-black/80 backdrop-blur-sm text-white text-[10px] font-bold px-2 py-0.5 rounded z-20 flex items-center gap-1 font-mono">
                    <CheckCircle className="w-3 h-3 text-emerald-400" /> Pronto
                  </div>
                </div>
                
                <div className="flex-1 min-w-0 w-full flex flex-col justify-between h-full">
                  <div>
                    <h2 className="text-sm sm:text-base font-bold text-white line-clamp-2 leading-snug mb-1" title={videoData.titulo}>
                      {videoData.titulo}
                    </h2>
                    <p className="text-[10px] text-emerald-400 font-bold uppercase mt-1 tracking-wider flex items-center gap-1 mb-3">
                      <ShieldCheck className="w-3 h-3 text-emerald-400" /> Pronto para descarregar
                    </p>
                  </div>
                  
                  <div className="mt-auto">
                    <select
                      value={quality}
                      onChange={(e) => setQuality(e.target.value)}
                      className="block w-full px-4 py-3 bg-slate-900 border border-white/5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50 text-slate-200 font-bold cursor-pointer transition-colors"
                    >
                      <option value="alta">🎥 MP4 - Alta Qualidade</option>
                      <option value="media">🎥 MP4 - Qualidade Média</option>
                      <option value="audio">🎵 MP3 - Apenas Áudio</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <button
                onClick={handleDownload}
                disabled={downloadState === 'downloading'}
                className={`w-full font-bold py-5 px-6 rounded-2xl transition-all duration-300 flex items-center justify-center gap-3 active:scale-[0.98] text-lg
                  ${downloadState === 'idle' 
                    ? 'bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 text-white shadow-lg shadow-violet-500/20' 
                    : downloadState === 'downloading'
                    ? 'bg-slate-700 text-white cursor-not-allowed'
                    : downloadState === 'ready'
                    ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-900'
                    : 'bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 text-white' 
                  }`}
              >
                {downloadState === 'idle' || downloadState === 'error' ? (
                  <>
                    {downloadState === 'error' ? <RefreshCw className="w-6 h-6" /> : <Download className="w-6 h-6" />}
                    <span>{downloadState === 'error' ? 'Tentar Novamente' : 'Baixar Agora'}</span>
                  </>
                ) : downloadState === 'downloading' ? (
                  <>
                    <div className="loader-ring !w-5 !h-5 !border-2 !border-t-white mr-2"></div>
                    <span>A baixar no servidor...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-6 h-6" />
                    <span>Pronto! A enviar ficheiro...</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Toast Notifications */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className={`flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl text-white font-medium text-sm backdrop-blur-md border border-white/20 pointer-events-auto
                ${toast.type === 'erro' ? 'bg-rose-500/90' : 'bg-emerald-500/90'}`}
            >
              {toast.type === 'erro' ? (
                <AlertTriangle className="w-5 h-5 shrink-0" />
              ) : (
                <CheckCircle className="w-5 h-5 shrink-0" />
              )}
              <span>{toast.message}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
