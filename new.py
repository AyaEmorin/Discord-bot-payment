import discord
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os

load_dotenv()
bottoken = os.getenv('bot')

class PayBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.tree.sync()
    
    async def pay_interaction(self, interaction: discord.Interaction, method: str):
        await interaction.response.send_message(f"Processing payment using {method}...")
        
        view = View(timeout=None)
        confirm_button = Button(label="Confirm Payment", style=discord.ButtonStyle.green)
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)
        
        async def confirm_payment(button_interaction: discord.Interaction):
            phone_number = method
            qr_data = f'https://promptpay.io/{phone_number}'
            await button_interaction.response.send_message(f"Sending QR code to you privately...")
            await button_interaction.user.send(qr_data)
        
        async def cancel_payment(button_interaction: discord.Interaction):
            await button_interaction.response.send_message("Payment cancelled.")
        
        confirm_button.callback = confirm_payment
        cancel_button.callback = cancel_payment
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await interaction.followup.send("Confirm or cancel payment:", view=view)

intents = discord.Intents.default()
client = PayBot()

@client.tree.command(name="pay", description="Process a payment")
@app_commands.describe(method="The payment method to use (e.g., phone number)")
async def pay(interaction: discord.Interaction, method: str):
    await client.pay_interaction(interaction, method)

client.run(bottoken)