import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


ADMIN_ID = 660066534093357066

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

client = commands.Bot(command_prefix='!', intents=intents, owner_id=ADMIN_ID)
tree_commands = client.tree

@client.event
async def on_ready():
    # 1. Charger les Cogs (extensions)
    cogs_to_load = ['cogs.moderation', 'cogs.cards']
    
    for cog in cogs_to_load:
        try:
            await client.load_extension(cog) 
            print(f"✅ Cog chargé : {cog}")
        except commands.ExtensionNotFound:
            print(f"⚠️ Avertissement : Le fichier {cog}.py n'a pas été trouvé. Ignoré.")
        except Exception as e:
            print(f"❌ Erreur critique lors du chargement de {cog} : {e}")
        
    # 2. Synchroniser les Commandes Slash
    try:
        synced = await tree_commands.sync() 
        print(f"✅ Commandes slash synchronisées. ({len(synced)} commandes)")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes : {e}")

    print(f'🚀 Lancement du bot ! {client.user}')

@client.event
async def on_member_join(member: discord.Member):
    member_channel = client.get_channel(1448251619320926238) 
    if member_channel:
        await member_channel.send(f'Bienvenue <@{member.id}> !')

@client.event
async def on_member_leave(member: discord.Member):
    member_channel = client.get_channel(1448251656755085442) 
    if member_channel:
        await member_channel.send(f'<@{member.id}> a quitté le serveur.')

client.run(os.getenv('DISCORD_TOKEN'))