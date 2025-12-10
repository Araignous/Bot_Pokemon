from dotenv import load_dotenv
load_dotenv()

from discord.ext import commands
from discord import app_commands
import random
import discord
import os

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)
tree_commands = client.tree

@client.event
async def on_ready():
    # 1. Charger tous les cogs
    try:
        await client.load_extension('cogs.moderation')
        await client.load_extension('cogs.cards')
        print("Cogs chargés.")
    except Exception as e:
        print(f"Erreur lors du chargement des cogs : {e}")
        
    # 2. Synchroniser les commandes slash
    # C'est l'étape cruciale pour les commandes /
    try:
        synced = await tree_commands.sync() 
        print(f"Commandes slash synchronisées. ({len(synced)} commandes)")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

    print(f'Lancement du bot ! {client.user}')
@client.event
async def on_member_join(member: discord.Member):
    print(f'nouveau membre a rejoins le discord !')
    # envoyer un msg bans le salon nouveau-membre
    member_channel = client.get_channel(1448251619320926238)
    await member_channel.send(f'le <@{member.id}> a rejoins le serveur !')

@client.event
async def on_member_leave(member: discord.Member):
    print(f'un membre a quittes le discord !')
    # envoyer un msg bans le salon nouveau-membre
    member_channel = client.get_channel(1448251656755085442)
    await member_channel.send(f'le <@{member.id}> a quittes le serveur !')

client.run(os.getenv('DISCORD_TOKEN'))
