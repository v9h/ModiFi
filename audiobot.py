import discord
from discord.ext import commands
import os
import subprocess

TOKEN = 'YOUR_BOT_TOKEN'

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

def get_audio_duration(filename):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

@bot.command()
async def speed(ctx, speed: float): # Use a speed from 9.2 to 9.6, reversal speed will be calculated upon completion
    if not ctx.message.attachments:
        await ctx.send("Please attach an MP3 or OGG file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(('.mp3', '.ogg')):
        await ctx.send("Please attach a valid MP3 or OGG file.")
        return

    await attachment.save(attachment.filename)

    duration = get_audio_duration(attachment.filename)
    if duration > 75:
        await ctx.send("The audio file is longer than 75 seconds and cannot be processed.")
        os.remove(attachment.filename)
        return

    output_filename = f"modified_{attachment.filename}"
    command = [
        'ffmpeg', '-i', attachment.filename, '-filter:a', f'asetrate=44100*{speed},atempo=1/{speed}', output_filename
    ]
    subprocess.run(command)

    revert_speed = 1 / speed
    await ctx.send(file=discord.File(output_filename))
    await ctx.send(f"To play the original sound file, slow it down to {revert_speed:.7f} speed.")

    os.remove(attachment.filename)
    os.remove(output_filename)

@bot.command()
async def convert(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please attach an audio file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(('.mp3', '.wav', '.flac', '.aac', '.m4a')):
        await ctx.send("Please attach a valid audio file.")
        return

    await attachment.save(attachment.filename)

    duration = get_audio_duration(attachment.filename)
    if duration > 75:
        await ctx.send("The audio file is longer than 75 seconds and cannot be processed.")
        os.remove(attachment.filename)
        return

    output_filename = f"{os.path.splitext(attachment.filename)[0]}.ogg"
    command = [
        'ffmpeg', '-i', attachment.filename, '-c:a', 'libvorbis', '-q:a', '5', output_filename
    ]
    subprocess.run(command)

    await ctx.send(file=discord.File(output_filename))

    os.remove(attachment.filename)
    os.remove(output_filename)

bot.run(TOKEN)