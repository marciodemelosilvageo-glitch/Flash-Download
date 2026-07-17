FROM node:20-bullseye-slim

# Install system dependencies required by yt-dlp (Python, FFmpeg)
RUN apt-get update && apt-get install -y \
    python3 \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Download the yt-dlp binary explicitly during the build step
RUN mkdir -p ./bin && \
    wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O ./bin/yt-dlp && \
    chmod +x ./bin/yt-dlp

# Build the frontend and backend
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
