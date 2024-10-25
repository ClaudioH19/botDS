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
    'options': '-vn -reconnect 3 -reconnect_streamed 3 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queue = []
loop=False

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


async def play_next(ctx):
    if len(queue) > 0:
        next_song_url= queue.pop(0)
        player = await YTDLSource.from_url(next_song_url,loop=bot.loop, stream=True)
        ctx.voice_client.play(player,after=lambda e: bot.loop.create_task(play_next(ctx)))
        await ctx.send(f"Reproduciendo: {player.title}")
    else:
        await ctx.send("La cola ha terminado.")


@bot.command()
async def play(ctx, url: str):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()

        queue.append(url)
        await ctx.send(f"Agregado a la cola: {url}")

        #reproducir si no hay nada reproduciendo
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
    else:
        await ctx.send("Debes estar en un canal de voz para poder usar este comando.")

@bot.command()
async def songs(ctx):
    if len(queue)>0:
        await ctx.send(f"Cola de reproducción: {', '.join(queue)}")
    else:
        await ctx.send("La cola está vacía.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Saltando canción.")
    else:
        await ctx.send("No se está reproduciendo ninguna canción.")


# Comando para detener la reproducción
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("Reproducción detenida.")


@bot.command()
async def saludo(ctx):
    await ctx.send("¡Hola, soy Clune!")

# Corre el bot
bot.run(DISCORD_BOT_TOKEN)
