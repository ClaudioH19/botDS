# Usa una imagen base de Python con una versión moderna
FROM python:3.12-slim

# Actualiza el sistema e instala las dependencias necesarias, incluyendo FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Copia el archivo requirements.txt al contenedor (si lo tienes)
COPY requirements.txt ./

# Instala las dependencias necesarias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Si no tienes un requirements.txt, instala las dependencias directamente aquí
RUN pip install --no-cache-dir discord.py yt-dlp

# Copia todos los archivos del proyecto (incluyendo bot.py) al contenedor
COPY . .

# Comando para ejecutar el bot de Discord
CMD ["python", "./bot.py"]