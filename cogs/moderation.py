import discord
from discord.ext import commands
from discord import app_commands

class ModerationCog(commands.Cog):

    # au chargement du bot -> cog
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        
        #anti insulte
        words_blacklist = ['fdp', 'pd', 'negro', 'pute', 'tg', 'salope', 'connard']

        # recuperer chaque mot
        for mot in message.content.split():
            if mot in words_blacklist:
                await message.delete()
                await message.channel.send(f'<@{message.author.id}> Merci de respecter les règles !')
                break

    @app_commands.command(name="kick", description="ejecter quelqu'un du serveur")
    async def kick_command(self, interaction: discord.Interaction, member: discord.Member):
        # --> /kick @pseudo
        await member.send ("Dommage tu aurais du respecter les regles")
        await member.kick (reason="Non respect des regles")
        await interaction.response.send_message("le membre a ete expulse avec succes !")

        # prepare une fonction setup qui va enregistrer le cog dans le bot
async def setup(client):
    await client.add_cog(ModerationCog(client))




