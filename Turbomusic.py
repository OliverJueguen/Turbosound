import discord
from discord.ext import commands
import yt_dlp as youtube_dl

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

# Set up the bot prefix and description
bot_prefix = "!"
bot_description = "Este es un bot de música."

# Set up the intents
intents = discord.Intents.all()

# Create the bot instance with the set prefix, description, and intents
bot = commands.Bot(command_prefix=bot_prefix, description=bot_description, intents=intents)


# Check if the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} está listo para la música!")


# Join the voice channel of the user who summoned the bot
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


# Leave the voice channel of the bot
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


# Play the requested song
@bot.command()
async def play(ctx, *, query):
    voice_client = ctx.voice_client or await ctx.author.voice.channel.connect()

    with youtube_dl.YoutubeDL({
        'outtmpl': 'song.%(ext)s',
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'no-call-home': True
    }) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info['title']

        voice_client.stop()
        source = await discord.FFmpegOpusAudio.from_probe(url, method='fallback')
        voice_client.play(source)

        await ctx.send(f"Reproduciendo: {title}")


# Pause the current song
@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Pausado.")


# Resume the current song
@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Reanudado.")


# Stop playing the current song
@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Detenido.")


# Set up error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if isinstance(original, discord.ClientException):
            await ctx.send("Ya estoy reproduciendo una canción.")
        elif isinstance(original, youtube_dl.utils.ExtractorError):
            await ctx.send("No se puede reproducir la canción.")
    else:
        raise error


# Run the bot
bot.run("TOKEN")
