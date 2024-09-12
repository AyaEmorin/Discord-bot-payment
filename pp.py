import discord
from discord import app_commands
from discord.ui import Modal, TextInput

class MyModal(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(TextInput(label="Name", placeholder="Your name here"))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello, {self.children[0].value}! Your response has been submitted.')

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

client = MyClient()

@client.tree.command(name="open_modal", description="Opens a modal dialog")
@app_commands.describe(method="The payment method to use")
async def open_modal(interaction: discord.Interaction):
    modal = MyModal(title="My Cool Modal")
    await interaction.response.send_modal(modal)

client.run('MTI4MzY3NDc3MzEwODQyODg1Mg.G0uvSj.T9iflcssGD03uBatYgIYwEhEaXLTpBVOnx2P2s')