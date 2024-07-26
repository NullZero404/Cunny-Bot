import json
import urllib.parse
import requests

RIOT_TOKEN = "RGAPI-31049c8e-2435-4ad6-8b0e-feda788d5c44"
mypuuid = "oFLm9ovonyBOUlnJpIbaCnIkpOaVRq7V_mSs30oivp8iB4rIHJuCWOpF9OQZJ_oZMrEYPvOiGAvqiw"
mySummonerID = "WtLySKxD5w0TTeH9oCNxmHB-mw0nfbvqNPHsBlllMwr4AXZEnIDfz9Y3Qg"

rawName = "a minor"
name = urllib.parse.quote(rawName)
tagLine = "null0"

def getRiotInfo(name, tagLine):
    API_RIOT = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tagLine}?api_key={RIOT_TOKEN}'
    response = requests.get(API_RIOT)
    jsonDataRiot = response.json()

    riotPuuid = jsonDataRiot['puuid']
    riotName = jsonDataRiot['gameName']
    riotTagLine = jsonDataRiot['tagLine']
    return riotName, riotTagLine, riotPuuid

Name, TagLine, Puuid = getRiotInfo(name, tagLine)

def getLoLInfo():
    API_LOL = f'https://ph2.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{mypuuid}?api_key={RIOT_TOKEN}'
    response = requests.get(API_LOL)
    jsonDataLol = response.json()
    
    summonerLevel = jsonDataLol['summonerLevel']
    summonerID = jsonDataLol['id']
    return summonerLevel, summonerID

lvl, id = getLoLInfo()

def getSummonerInfo():
    API_SUMMONER = f'https://ph2.api.riotgames.com/lol/league/v4/entries/by-summoner/{mySummonerID}?api_key={RIOT_TOKEN}'
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

    return flex_tier, flex_rank, flex_wins, flex_losses, solo_tier, solo_rank, solo_wins, solo_losses

flex_tier, flex_rank, flex_wins, flex_losses, solo_tier, solo_rank, solo_wins, solo_losses = getSummonerInfo()

# Print the results
print(f'my Riot Name is: {Name} and my Riot TagLine is: {TagLine}')
print(f'my summoner level is: {lvl}')
print(f'summoner id: {id}')
print(f'Ranked Flex Wins: {flex_wins}')
print(f'Ranked Flex Losses: {flex_losses}')
print(f'{solo_tier} {solo_rank} W: {solo_wins} L: {solo_losses}')
