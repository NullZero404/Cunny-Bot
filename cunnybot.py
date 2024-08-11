import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import random
import json
import urllib.parse
from urllib import response
import requests
from discord import player
from discord.ext import commands
from discord import app_commands
import key

#start
bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)

#exit
@bot.tree.command(name="exit")
@commands.is_owner()
async def exit(interaction: discord.Interaction):
  await interaction.response.send_message(f"adios, {interaction.user.mention}")
  exit()

#error feedback
@bot.event
async def on_message_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Error")

#COMMAND STUFF
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    """ping and shit."""
    await interaction.response.send_message(f"Pong :sob: {interaction.user.mention} ping = {bot.latency:.2f}")
      
#Riot Api 
#resets everyday
RIOT_TOKEN = "RGAPI-31049c8e-2435-4ad6-8b0e-feda788d5c44"

def getRiotInfo(Name, tagLine):
  API_RIOT = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{Name}/{tagLine}?api_key={RIOT_TOKEN}'
  response = requests.get(API_RIOT)
  jsonDataRiot = response.json()

  riotPuuid = jsonDataRiot['puuid']
  riotName = jsonDataRiot['gameName']
  riotTagLine = jsonDataRiot['tagLine']
  return riotPuuid, riotName, riotTagLine

#Name, TagLine, Puuid = getRiotInfo(name, tagLine)

def getLoLInfo(riotPuuid):
  API_SUMMONER = f'https://ph2.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{riotPuuid}?api_key={RIOT_TOKEN}'
  response = requests.get(API_SUMMONER)
  jsonDataSummoner = response.json()
  
  #summonerLevel = jsonDataSummoner['summonerLevel']
  summonerID = jsonDataSummoner['id']
  
  sLevel = "Lvl. " + str(jsonDataSummoner['summonerLevel'])
  sIcon = "http://ddragon.leagueoflegends.com/cdn/14.14.1/img/profileicon/" + str(jsonDataSummoner['profileIconId']) + ".png"
  return sLevel, sIcon, summonerID

#lvl, id = getLoLInfo()

def getSummonerInfo(summonerID):
    API_SUMMONER = f'https://ph2.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}?api_key={RIOT_TOKEN}'
    response = requests.get(API_SUMMONER)
    jsonDataSummoner = response.json()

    flex_tier = " "
    flex_rank = " "
    flex_wins = 0
    flex_losses = 0
    flex_lp = 0
    solo_tier = " "
    solo_rank = " "
    solo_wins = 0
    solo_losses = 0
    solo_lp = 0
    arena_wins = 0
    arena_losses = 0

    for entry in jsonDataSummoner:
        if entry["queueType"] == "RANKED_FLEX_SR":
            flex_tier = entry["tier"]
            flex_rank = entry["rank"]
            flex_wins = entry["wins"]
            flex_losses = entry["losses"]
            flex_lp = entry['leaguePoints']
        elif entry["queueType"] == "RANKED_SOLO_5x5":
            solo_tier = entry["tier"]
            solo_rank = entry["rank"]
            solo_wins = entry["wins"]
            solo_losses = entry["losses"]
            solo_lp = entry['leaguePoints']
        elif entry["queueType"] == "CHERRY":
            arena_wins = entry["wins"]
            arena_losses = entry["losses"]

    return flex_tier, flex_rank, flex_lp, flex_wins, flex_losses, solo_tier, solo_rank, solo_lp, solo_wins, solo_losses, arena_wins, arena_losses 

def calcWinrate(win, lose):
  games = win + lose
  calc = (win/games) * 100
  return calc

@bot.command()
async def summoner(ctx, RiotName, RiotTag):
  
  convertedName = urllib.parse.quote(RiotName)
  riotInfo = getRiotInfo(convertedName, RiotTag)
  lolInfo = getLoLInfo(riotInfo[0])
  summInfo = getSummonerInfo(lolInfo[2])
  
  embed = discord.Embed(title=RiotName, description=lolInfo[0], color=0xFFD500)
  embed.set_thumbnail(url=lolInfo[1])
  await ctx.send(embed=embed)
  
@bot.tree.command(name="summoner", description="Get Summoner Information, PH Only")
@app_commands.describe(riot_name="The summoner's Riot name", riot_tag="The summoner's Riot tag")
async def summoner(interaction: discord.Interaction, riot_name: str, riot_tag: str):
    converted_name = urllib.parse.quote(riot_name)
    riot_info = getRiotInfo(converted_name, riot_tag)
    lol_info = getLoLInfo(riot_info[0])
    summ_info = getSummonerInfo(lol_info[2])
    
    #winrate
    #sd 
    games_sd = summ_info[8] + summ_info[9]
    qt_sd = (summ_info[8]/games_sd) * 100
    #flex
    games_flex = summ_info[3] + summ_info[4]
    qt_flex = (summ_info[3]/games_flex) * 100
    #arena
    games_arena = summ_info[10] + summ_info[11]
    qt_arena = (summ_info[10]/games_arena) * 100
    
    embed = discord.Embed(title=riot_name, description=lol_info[0], color=0xFFD500)
    embed.set_thumbnail(url=lol_info[1])
    embed.add_field(name='Ranked Solo/Duo', value=f'{summ_info[5]} {summ_info[6]} LP: {summ_info[7]} W: {summ_info[8]} L: {summ_info[9]} Winrate: {qt_sd:.2f}%', inline=False)
    embed.add_field(name='Ranked Flex', value=f'{summ_info[0]} {summ_info[1]} LP: {summ_info[2]} W: {summ_info[3]} L: {summ_info[4]} Winrate: {qt_flex:.2f}%', inline=False)
    embed.add_field(name='Arena', value=f'W: {summ_info[10]} L: {summ_info[11]} Winrate: {qt_arena:.2f}%', inline=False)
    await interaction.response.send_message(embed=embed)
    
#MUSIC
# Music-related variables
voice_clients = {}
music_queue = {}
looping = {}
search_results = {}

ytdl_format_options = {'format': 'bestaudio/best'}
ffmpeg_options = {'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def play_next(ctx):
    if len(music_queue[ctx.guild.id]) > 0:
        next_song = music_queue[ctx.guild.id].pop(0)
        player = discord.FFmpegPCMAudio(next_song['url'], **ffmpeg_options)
        ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

        if looping.get(ctx.guild.id, False):
            music_queue[ctx.guild.id].append(next_song)

        embed = discord.Embed(title="Now Playing", description=next_song['title'], color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        await ctx.voice_client.disconnect()
        await ctx.send(embed=discord.Embed(title="Queue Ended", description="No more songs in the queue.", color=0xff0000))

@bot.command()
async def p(ctx, *, search: str):
    if ctx.author.voice is None:
        await ctx.send(embed=discord.Embed(title="Error", description="You need to join a voice channel first!", color=0xff0000))
        return

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        voice_clients[ctx.guild.id] = voice_client
        music_queue[ctx.guild.id] = []
        looping[ctx.guild.id] = False
        await ctx.send(embed=discord.Embed(title="Connected", description="Connected to the voice channel!", color=0x00ff00))
    else:
        voice_client = ctx.voice_client

    try:
        search_query = f"ytsearch:{search}"
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))
        song_info = {
            'url': data['entries'][0]['url'],
            'title': data['entries'][0]['title']
        }

        music_queue[ctx.guild.id].append(song_info)

        if not voice_client.is_playing():
            await play_next(ctx)
        else:
            await ctx.send(embed=discord.Embed(title="Added to Queue", description=song_info['title'], color=0x00ff00))

    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="Error", description="There was an error adding the song to the queue.", color=0xff0000))

@bot.command()
async def psearch(ctx, *, search: str):
    if ctx.author.voice is None:
        await ctx.send(embed=discord.Embed(title="Error", description="You need to join a voice channel first!", color=0xff0000))
        return

    try:
        search_query = f"ytsearch10:{search}"
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))

        results = []
        for i, entry in enumerate(data['entries'], start=1):
            results.append(f"{i}. {entry['title']}")

        search_results[ctx.author.id] = data['entries']

        embed = discord.Embed(title="Search Results", description="\n".join(results), color=0x00ff00)
        embed.set_footer(text="Type the number of the song you want to play.")
        await ctx.send(embed=embed)

    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="Error", description="There was an error fetching search results.", color=0xff0000))

@bot.command()
async def pick(ctx, number: int):
    if ctx.author.voice is None:
        await ctx.send(embed=discord.Embed(title="Error", description="You need to join a voice channel first!", color=0xff0000))
        return

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        voice_clients[ctx.guild.id] = voice_client
        music_queue[ctx.guild.id] = []
        looping[ctx.guild.id] = False
        await ctx.send(embed=discord.Embed(title="Connected", description="Connected to the voice channel!", color=0x00ff00))
    else:
        voice_client = ctx.voice_client

    if ctx.author.id not in search_results or not (1 <= number <= len(search_results[ctx.author.id])):
        await ctx.send(embed=discord.Embed(title="Error", description="Invalid selection or no search results found.", color=0xff0000))
        return

    song_info = {
        'url': search_results[ctx.author.id][number - 1]['url'],
        'title': search_results[ctx.author.id][number - 1]['title']
    }

    music_queue[ctx.guild.id].append(song_info)

    if not voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(embed=discord.Embed(title="Added to Queue", description=song_info['title'], color=0x00ff00))

# View the queue
@bot.command()
async def q(ctx):
    if ctx.guild.id not in music_queue or len(music_queue[ctx.guild.id]) == 0:
        await ctx.send(embed=discord.Embed(title="Queue", description="The queue is currently empty.", color=0xff0000))
    else:
        current_song = "No song currently playing" if not ctx.voice_client.is_playing() else music_queue[ctx.guild.id][0]['title']
        queue_list = '\n'.join([f"{idx + 1}. {song['title']}" for idx, song in enumerate(music_queue[ctx.guild.id])])
        embed = discord.Embed(title="Current Queue", description=f"**Now Playing:**\n{current_song}\n\n**Up Next:**\n{queue_list}", color=0x00ff00)
        await ctx.send(embed=embed)

# Skip the current song
@bot.command()
async def s(ctx):
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        await ctx.send(embed=discord.Embed(title="Error", description="No song is currently playing!", color=0xff0000))
    else:
        ctx.voice_client.stop()
        await ctx.send(embed=discord.Embed(title="Skipped", description="The current song was skipped!", color=0x00ff00))

# Toggle looping of the queue
@bot.command()
async def l(ctx):
    if ctx.guild.id not in looping:
        looping[ctx.guild.id] = False

    looping[ctx.guild.id] = not looping[ctx.guild.id]
    status = "enabled" if looping[ctx.guild.id] else "disabled"
    await ctx.send(embed=discord.Embed(title="Looping", description=f"Looping has been {status}.", color=0x00ff00))

# Disconnect from voice channel
@bot.command()
async def dc(ctx):
    if ctx.voice_client is None:
        await ctx.send(embed=discord.Embed(title="Error", description="I am not connected to any voice channel!", color=0xff0000))
        return
    await ctx.voice_client.disconnect()
    await ctx.send(embed=discord.Embed(title="Disconnected", description="Disconnected from the voice channel!", color=0x00ff00))

load_dotenv()
TOKEN = os.getenv('discord_token')
bot.run(f'{TOKEN}')