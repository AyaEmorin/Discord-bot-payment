import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from io import BytesIO
import qrcode

load_dotenv()
bottoken = os.getenv('bot')

class PayBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.tree.sync()

client = PayBot()

@client.tree.command(name="pay", description="Process a payment")
@app_commands.describe(method="The payment method to use")
async def pay(interaction: discord.Interaction, phonenumber: str):
    await interaction.response.send_message(f"Processing payment using {phonenumber}... Amount {amount}")

    phone_number = phonenumber
    total = amount
    qr_data = f'https://promptpay.io/{phone_number}/{amount}'

    await interaction.user.send_message(qr_data)
   

client.run(bottoken)