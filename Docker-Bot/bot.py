import discord
from discord.ext import commands
import yt_dlp as youtube_dl  # Cambia la importación a yt-dlp
import asyncio
import os

# Intents necesarios para interactuar con mensajes
intents = discord.Intents.default()
intents.message_content = True

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  

# Configuración del bot
bot = commands.Bot(command_prefix="c!", intents=intents)

# Configuración de yt-dlp (anteriormente youtube_dl)
ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}

ffmpeg_options = {
    'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Clase para reproducir audio desde un enlace
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Evento para cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')

@bot.command()
async def play(ctx, url: str):
    # Verifica si el bot ya está conectado a un canal de voz
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send("Debes estar en un canal de voz para que me pueda unir.")
            return
    else:
        voice_client = ctx.voice_client  # Reutiliza la conexión existente

    # Obtener la fuente de audio de YouTube
    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            voice_client.play(player, after=lambda e: print(f"Error en la reproducción: {e}") if e else None)
            await ctx.send(f"Reproduciendo: {player.title}")
        except Exception as e:
            await ctx.send(f"Ocurrió un error: {e}")
            print(f"Error: {e}")
            

# Comando para detener la reproducción
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def saludo(ctx):
    await ctx.send("¡Hola, soy Clune!")

# Corre el bot
bot.run(DISCORD_BOT_TOKEN)