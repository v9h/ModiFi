import discord
from discord.ext import commands
import os
import subprocess
import random

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
    if duration > 180:
        await ctx.send("The audio file is longer than 180 seconds and cannot be processed.")
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

@bot.command()
async def noisebypass(ctx): # Adds noise to the audio file, hopefully bypassing certain sound-checks
    if not ctx.message.attachments:
        await ctx.send("Please attach an audio file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(('.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg')):
        await ctx.send("Please attach a valid audio file.")
        return

    await attachment.save(attachment.filename)

    duration = get_audio_duration(attachment.filename)
    if duration > 180:
        await ctx.send("The audio file is longer than 180 seconds and cannot be processed.")
        os.remove(attachment.filename)
        return

    output_filename = f"noisebypass_{attachment.filename}"
    command = [
        'ffmpeg', '-i', attachment.filename, '-filter_complex', 'anoisesrc=color=white:amplitude=0.05 [noise]; [0][noise] amix', output_filename
    ]
    subprocess.run(command)

    await ctx.send(file=discord.File(output_filename))

    os.remove(attachment.filename)
    os.remove(output_filename)

@bot.command()
async def freqfilter(ctx, filter_type: str): # Low-pass or high-pass filter
    if not ctx.message.attachments:
        await ctx.send("Please attach an audio file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(('.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg')):
        await ctx.send("Please attach a valid audio file.")
        return

    await attachment.save(attachment.filename)

    duration = get_audio_duration(attachment.filename)
    if duration > 180:
        await ctx.send("The audio file is longer than 180 seconds and cannot be processed.")
        os.remove(attachment.filename)
        return

    if filter_type.lower() not in ['low-pass', 'high-pass']:
        await ctx.send("Please specify a valid filter type: 'low-pass' or 'high-pass'.")
        os.remove(attachment.filename)
        return

    output_filename = f"filtered_{attachment.filename}"
    filter_option = 'lowpass=f=3000' if filter_type.lower() == 'low-pass' else 'highpass=f=3000'
    command = [
        'ffmpeg', '-i', attachment.filename, '-filter:a', filter_option, output_filename
    ]
    subprocess.run(command)

    await ctx.send(file=discord.File(output_filename))

    os.remove(attachment.filename)
    os.remove(output_filename)

@bot.command()
async def metamask(ctx): # Randomizes the metadata of the audio file
    if not ctx.message.attachments:
        await ctx.send("Please attach an audio file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(('.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg')):
        await ctx.send("Please attach a valid audio file.")
        return

    await attachment.save(attachment.filename)

    duration = get_audio_duration(attachment.filename)
    if duration > 180:
        await ctx.send("The audio file is longer than 180 seconds and cannot be processed.")
        os.remove(attachment.filename)
        return

    output_filename = f"metamask_{attachment.filename}"
    random_artist = f"Artist_{random.randint(1000, 9999)}"
    random_album = f"Album_{random.randint(1000, 9999)}"
    random_title = f"Title_{random.randint(1000, 9999)}"
    random_genre = f"Genre_{random.randint(1000, 9999)}"
    command = [
        'ffmpeg', '-i', attachment.filename, '-metadata', f'artist={random_artist}', '-metadata', f'album={random_album}', '-metadata', f'title={random_title}', '-metadata', f'genre={random_genre}', output_filename
    ]
    subprocess.run(command)

    await ctx.send(file=discord.File(output_filename))

    os.remove(attachment.filename)
    os.remove(output_filename)

@bot.command()
async def dynamiceq(ctx): # Applies dynamic equalization to the audio file
    if not ctx.message.attachments:
        await ctx.send("Please attach an audio file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(('.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg')):
        await ctx.send("Please attach a valid audio file.")
        return

    await attachment.save(attachment.filename)

    duration = get_audio_duration(attachment.filename)
    if duration > 180:
        await ctx.send("The audio file is longer than 180 seconds and cannot be processed.")
        os.remove(attachment.filename)
        return

    output_filename = f"dynamiceq_{attachment.filename}"
    command = [
        'ffmpeg', '-i', attachment.filename, '-af', 'bandpass=f=1000:w=500,compand=attacks=1:decays=100:points=-80/-80|-20/-10|0/-3:soft-knee=6', output_filename
    ]
    subprocess.run(command)

    await ctx.send(file=discord.File(output_filename))

    os.remove(attachment.filename)
    os.remove(output_filename)

bot.run(TOKEN)
