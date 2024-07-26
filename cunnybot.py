import discord
import os
import sqlite3
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
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

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

#random stuff
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    """ping and shit."""
    await interaction.response.send_message(f"Pong :sob: {interaction.user.mention}")

@bot.tree.command(name="add")
async def add(interaction: discord.Interaction, left: int, right: int):
  """Adds two numbers together."""
  await interaction.response.send_message(left + right)

@bot.tree.command(name="winrate")
async def roll(interaction: discord.Interaction, win: int, lose: int):
  """roll upto a number(default 100)"""
  tg = win+lose
  wr = (win/tg)*100
  await interaction.response.send_message(wr)
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
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

    return flex_tier, flex_rank, flex_wins, flex_losses, solo_tier, solo_rank, solo_wins, solo_losses, flex_lp, solo_lp

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
    
    #sd 
    games_sd = summ_info[6] + summ_info[7]
    qt_sd = (summ_info[6]/games_sd) * 100
    #flex
    games_flex = summ_info[2] + summ_info[3]
    qt_flex = (summ_info[2]/games_flex) * 100
    
    embed = discord.Embed(title=riot_name, description=lol_info[0], color=0xFFD500)
    embed.set_thumbnail(url=lol_info[1])
    embed.add_field(name='Ranked Solo/Duo', value=f'{summ_info[4]} {summ_info[5]} LP: {summ_info[8]} W: {summ_info[6]} L: {summ_info[7]} Winrate: {qt_sd:.2f}%', inline=False)
    embed.add_field(name='Ranked Flex', value=f'{summ_info[0]} {summ_info[1]} LP: {summ_info[9]} W: {summ_info[2]} L: {summ_info[3]} Winrate: {qt_flex:.2f}%', inline=False)
    await interaction.response.send_message(embed=embed)
  
# def clearNameSpaces(nameWithSpaces):
#   result = ""
#   for n in nameWithSpaces:
#     result = result + " " + str(n)
#   return result

# def getProfile(region, name):
#     if region == "ph":
#         API_Riot = "https://ph2.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + RIOT_TOKEN
#     response = requests.get(API_Riot)
#     jsonDataSummoner = response.json()
#     sEncryptedId = jsonDataSummoner['id']
#     sName = jsonDataSummoner['name']
#     sLevel = "Lvl. " + str(jsonDataSummoner['summonerLevel'])
#     sIcon = "http://ddragon.leagueoflegends.com/cdn/13.22.1/img/profileicon/" + str(jsonDataSummoner['profileIconId']) + ".png"
#     return (sName, sLevel, sIcon, sEncryptedId)

# def fetchRanks(region, sEncryptedId):
#     if region == "ph":
#         API_Riot = "https://ph2.api.riotgames.com/lol/league/v4/entries/by-summoner/" + sEncryptedId + "?api_key=" + RIOT_TOKEN
#     response = requests.get(API_Riot)
#     jsonDataSummoner = response.json()
#     calls = {0:"queueType", 1:"tier", 2:"rank", 3:"leaguePoints", 4:"wins", 5:"losses"}
#     ranks = []
#     try:
#         for i in range(3):
#             for j in range(6):
#                 ranks.append(jsonDataSummoner[i][calls[j]])
#     except:
#         pass
#     return ranks

# @bot.command()
# async def summoner(ctx, *nameWithSpaces):
#     name = clearNameSpaces(nameWithSpaces)
#     summoner = getProfile("ph", name)
#     summonerRanking = fetchRanks("ph", summoner[3])
#     embed = discord.Embed(title=summoner[0], description=summoner[1], color=0xFFD500)
#     embed.set_thumbnail(url=summoner[2])
    
#     # solo duo
#     try:
#         g = summonerRanking[10] + summonerRanking[11]
#         wr = (summonerRanking[10]/g)*100        
#         tmp = f"{summonerRanking[7]} {summonerRanking[8]} • LP: {summonerRanking[9]} • W: {summonerRanking[10]} • L: {summonerRanking[11]} • WR: {wr:.2f}%"
#         qt = ""
#         if summonerRanking[6] == "RANKED_SOLO_5x5":
#           qt="Solo Duo"
#         elif summonerRanking[6] == "RANKED_FLEX_SR":
#           qt="Flex"
#         else:
#           qt="nigga, that shit is wrong as fuck"
#         embed.add_field(name=qt, value=tmp, inline=False)
#     except:
#         embed.add_field(name=qt, value="Rank Unavailable", inline=False)
        
#     # flex
#     try:
#         g = summonerRanking[4] + summonerRanking[5]
#         wr = (summonerRanking[4]/g)*100  
#         tmp = f"{summonerRanking[1]} {summonerRanking[2]} • LP:{summonerRanking[3]} • Wins: {summonerRanking[4]} • Losses: {summonerRanking[5]} • WR: {wr:.2f}%"
#         qt = ""
#         if summonerRanking[0] == "RANKED_SOLO_5x5":
#           qt="Solo Duo"
#         elif summonerRanking[0] == "RANKED_FLEX_SR":
#           qt="Flex"
#         else:
#           qt="nigga, that shit is wrong as fuck"
#         embed.add_field(name=qt, value=tmp, inline=False)
#     except:
#         embed.add_field(name=qt, value="Rank Unavailable", inline=False)
#     await ctx.send(embed=embed)

#roll
@bot.command()
async def roll(ctx, upto: int):
  if upto is None:
    await ctx.channel.send(random.randint(0, 100))
  else:
    await ctx.channel.send(random.randint(0, upto))
    
#random stuff
@bot.command()
async def motivation(ctx):
  await ctx.channel.send(ctx.author.mention + ' bobo ka kase *slaps*')



@bot.command()
async def choose(ctx, *choices: str):
    await ctx.send(random.choice(choices))

@bot.command()
async def winrate(ctx, w: int, g: int):
  calc = (w/g) * 100
  await ctx.send("Winrate: "+str(calc)+"%")

@bot.command()
async def ars(ctx, ars: float):
  hehe = ars*3.298
  heehee = hehe*0.85
  await ctx.channel.send("PHP to ARS: "+str(hehe)+" total after fees: ~"+str(heehee))

@bot.command()
async def php(ctx, php: float):
  hehe = php/3.298
  heehee = hehe*0.85
  await ctx.channel.send("ARS to PHP: "+str(hehe)+" total after fees: ~"+str(heehee))

@bot.command()
async def casino(ctx, choice: int):
  if choice > 36:
    await ctx.send("Choices should be between 0-36")
    return
  else:
    if choice == 0:
      await ctx.send("Your choice is "+str(choice)+" Green")
    elif (choice % 2) == 0:
      await ctx.send("Your choice is "+str(choice)+" Black")
    else:
      await ctx.send("Your choice is "+str(choice)+" Red")
    
    roll = int(random.randint(0,36))
    if roll == 0:
      await ctx.send("The number is "+str(roll)+" Green")
    elif (roll % 2) == 0:
      await ctx.send("The number is "+str(roll)+" Black")
    else:
      await ctx.send("The number is "+str(roll)+" Red")
    
    if choice == roll:
      await ctx.send("CONGRATULATIONS your choice: ",str(choice)," WON the JACKPOT")
    elif roll % 2 == 0 and choice % 2 == 0:
      await ctx.send("YOU WON")
    elif roll % 2 == 1 and choice % 2 == 1:
      await ctx.send("YOU WON")
    else:
      await ctx.send("YOU LOSE")
  




bot.run(f'{key.API_KEY}')