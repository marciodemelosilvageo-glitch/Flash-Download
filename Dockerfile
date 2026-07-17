FROM node:20-bullseye-slim

# Instala dependências do sistema necessárias para o yt-dlp (Python, FFmpeg)
RUN apt-get update && apt-get install -y \
    python3 \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos de configuração e instala dependências do Node.js
COPY package*.json ./
RUN npm install

# Copia o restante dos arquivos do aplicativo
COPY . .

# Baixa o binário do yt-dlp diretamente durante o build
RUN mkdir -p ./bin && \
    wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O ./bin/yt-dlp && \
    chmod +x ./bin/yt-dlp

# Compila o site (frontend e backend)
RUN npm run build

# Expõe a porta 3000
EXPOSE 3000

# Comando para iniciar o servidor
CMD ["npm", "start"]
