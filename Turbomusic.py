import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import youtube_dl
import asyncio

bot = commands.Bot(command_prefix='!', description='Este es un bot de música.')
bot_token = 'TOKEN_DEL_BOT'

@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command()
async def play(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client

    try:
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(player, after=lambda e: print('Error: %s' % e) if e else None)
        await ctx.send('Reproduciendo: {}'.format(player.title))

    except:
        await ctx.send('Error: No se puede reproducir la canción.')

@bot.command()
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({'format': 'bestaudio/best', 'quiet': True}).extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else youtube_dl.utils.sanitize_filename(data['title'], restricted=True)
        url = data['url']
        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)

if __name__ == '__main__':
    bot.run(bot_token)
