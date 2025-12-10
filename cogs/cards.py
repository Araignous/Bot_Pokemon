import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import os
import asyncio
from typing import Dict, List, Any

DATA_FILE = "data/economy.json"

ADMIN_ID = 660066534093357066 

class CardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_data()
        
        self.POKEMON_CARDS = {
            "commune": ["Pikachu", "Salameche", "Carapuce", "Bulbizarre", "Aspicot", "Chenipan", "Roucool"],
            "rare": ["Dracaufeu", "Tortank", "Florizarre", "Léviator", "Arcanin"],
            "legendaire": ["Mewtwo", "Rayquaza", "Arceus", "Zacian", "Zamazenta"]
        }

    def load_data(self):
        if not os.path.isdir("data"): os.makedirs("data")
        if not os.path.isfile(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
            with open(DATA_FILE, "w") as f: json.dump({}, f)
        try:
            with open(DATA_FILE, "r") as f: self.data: Dict[str, Dict[str, Any]] = json.load(f)
        except json.JSONDecodeError:
            self.data = {}; self.save_data()

    def save_data(self):
        with open(DATA_FILE, "w") as f: json.dump(self.data, f, indent=4)

    def _get_user_data(self, user_id: int) -> Dict[str, Any]:
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            self.data[user_id_str] = {"money": 0, "inventory": []}; self.save_data()
        return self.data[user_id_str]

    def get_money(self, user_id: int) -> int:
        return self._get_user_data(user_id).get("money", 0)

    def add_money(self, user_id: int, amount: int):
        user_data = self._get_user_data(user_id)
        user_data["money"] += amount; self.save_data()
        
    def add_card(self, user_id: int, card_name: str):
        user_data = self._get_user_data(user_id)
        user_data["inventory"].append(card_name); self.save_data()


    @app_commands.command(name="money", description="Voir ton argent")
    async def money(self, interaction: discord.Interaction):
        amount = self.get_money(interaction.user.id)
        await interaction.response.send_message(f"💰 Tu as **{amount} pièces**.", ephemeral=True)


    @app_commands.command(name="challenge", description="Mini défi pour gagner de l'argent")
    async def challenge(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False) 
        
        number1 = random.randint(1, 20)
        number2 = random.randint(1, 20)
        answer = number1 + number2
        REWARD = random.randint(20, 50)
        TIMEOUT = 10.0

        message_content = f"🧠 **Mini défi !**\nTu as **{TIMEOUT} secondes**.\n\n➡️ Combien font **{number1} + {number2}** ?"
        
        await interaction.followup.send(message_content, ephemeral=False)

        def check(m: discord.Message):
            return (m.author.id == interaction.user.id and m.channel.id == interaction.channel_id and m.content.isdigit())

        try:
            msg = await self.bot.wait_for("message", timeout=TIMEOUT, check=check)
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏳ Trop lent ! Challenge raté.")

        if int(msg.content) == answer:
            self.add_money(interaction.user.id, REWARD)
            await interaction.followup.send(f"✅ Bonne réponse de **{interaction.user.display_name}** ! Tu gagnes **{REWARD}💰** !")
        else:
            await interaction.followup.send(f"❌ Mauvaise réponse de **{interaction.user.display_name}** ! La réponse était **{answer}**.")


    @app_commands.command(name="buy_booster", description="Achète un booster pack de cartes (coût: 100 💰)")
    async def buy_booster(self, interaction: discord.Interaction):
        COST = 100
        user_id = interaction.user.id
        
        if self.get_money(user_id) < COST:
            return await interaction.response.send_message(f"❌ Tu n'as pas assez d'argent. Il te faut **{COST}💰** pour un booster.", ephemeral=True)
            
        self.add_money(user_id, -COST)
        new_cards = []
        
        for _ in range(5):
            roll = random.randint(1, 100)
            if roll <= 5: rarity = "legendaire"
            elif roll <= 20: rarity = "rare"
            else: rarity = "commune"
                
            card_name = random.choice(self.POKEMON_CARDS[rarity])
            self.add_card(user_id, card_name)
            new_cards.append(f"**{card_name}** (_{rarity.capitalize()}_)")
            
        cards_list_str = "\n".join(new_cards)
        await interaction.response.send_message(
            f"🎉 **Félicitations, {interaction.user.display_name} !**\nTu as dépensé **{COST}💰** et ouvert un booster !\n\n"
            f"**Cartes obtenues :**\n{cards_list_str}\n\n"
            f"Ton nouveau solde est de **{self.get_money(user_id)}💰**.",
            ephemeral=False
        )


    @app_commands.command(name="inventory", description="Affiche l'inventaire de tes cartes")
    async def inventory(self, interaction: discord.Interaction):
        user_inventory = self._get_user_data(interaction.user.id).get("inventory", [])
        
        if not user_inventory:
            return await interaction.response.send_message("🎒 Ton inventaire est vide ! Achète un booster avec `/buy_booster`.", ephemeral=True)
            
        card_counts = {}
        for card in user_inventory: card_counts[card] = card_counts.get(card, 0) + 1
            
        inventory_display = [f"- {card} x{count}" for card, count in card_counts.items()]
            
        embed = discord.Embed(title=f"🎒 Inventaire de {interaction.user.display_name}", description="\n".join(inventory_display), color=discord.Color.blue())
        embed.set_footer(text=f"Total de {len(user_inventory)} cartes.")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="masterset", description="Affiche toutes les cartes disponibles à collectionner")
    async def masterset(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📚 Master Set de Cartes Pokémon", description="Voici toutes les cartes que vous pouvez obtenir :", color=discord.Color.red())
        
        for rarity, cards_list in self.POKEMON_CARDS.items():
            cards_str = ", ".join(cards_list)
            
            if rarity == "commune": field_title = "🟩 Communes (80% de chance)"
            elif rarity == "rare": field_title = "🟦 Rares (15% de chance)"
            elif rarity == "legendaire": field_title = "🟧 Légendaires (5% de chance)"
            else: field_title = rarity.capitalize()
                
            embed.add_field(name=field_title, value=cards_str, inline=False)
        embed.set_footer(text="Achetez des boosters pour compléter votre collection !")
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="give", description="[Admin] Donne de l'argent à un utilisateur.")
    # Vérifie l'ID utilisateur
    @app_commands.check(lambda i: i.user.id == ADMIN_ID) 
    async def give_money_slash(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1, None]):
        
        await interaction.response.defer(ephemeral=True)
        
        self.add_money(member.id, amount)
        current_amount = self.get_money(member.id)
        
        await interaction.followup.send(
            f"✅ **{amount}💰** ont été ajoutées à **{member.display_name}**."
            f" Son nouveau solde est : **{current_amount}💰**.",
            ephemeral=True
        )

    @give_money_slash.error
    async def give_money_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        
        if not interaction.response.is_done():
            send_func = interaction.response.send_message
        else:
            send_func = interaction.followup.send
            
        if isinstance(error, app_commands.CheckFailure):
            message = "🚫 Vous n'avez pas l'autorisation d'utiliser cette commande (Admin uniquement)."
        else:
            message = f"❌ Une erreur inattendue s'est produite: {error}"

        await send_func(message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(CardsCog(bot))