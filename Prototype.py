import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from io import BytesIO
import qrcode
from datetime import datetime
from discord import app_commands, utils
from discord.ext import commands
from discord.ui import Button, View

load_dotenv()
bottoken = os.getenv('bot')
guild_id = int(os.getenv('guild'))  
role_id = int(os.getenv('role'))

class PayBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.synced = False
        self.added = False
        self.ticket_mod = None  # Initialize as None

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await self.tree.sync(guild=discord.Object(id=guild_id))
            self.synced = True
        if not self.added:
            self.add_view(ticket_launcher())
            self.add_view(main())
            self.added = True
        print(f"We have logged in as {self.user}.")

    async def pay_interaction(self, interaction: discord.Interaction, method: str):
        await interaction.response.send_message(f"Processing payment using {method}...", ephemeral=True)
    
        # Create a view with buttons for confirmation or cancellation
        view = View(timeout=None)
        confirm_button = Button(label="Confirm Payment", style=discord.ButtonStyle.green)
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)
    
        async def confirm_payment(button_interaction: discord.Interaction):
            phone_number = method
            qr_data = f'https://promptpay.io/{phone_number}'  # Generate QR code URL
            #Send the QR code link in the current channel instead of privately
            await interaction.channel.send(f"{button_interaction.user.mention}, here is your QR code for payment:\n{qr_data}")
            await button_interaction.response.send_message("Payment confirmed. QR code sent in the channel.", ephemeral=True)
    
        async def cancel_payment(button_interaction: discord.Interaction):
            await interaction.channel.send(f"{button_interaction.user.mention}, the payment has been cancelled.")
            await button_interaction.response.send_message("Payment cancelled.", ephemeral=True)
    
        # Assign the callbacks to the buttons
        confirm_button.callback = confirm_payment
        cancel_button.callback = cancel_payment
    
        # Add buttons to the view
        view.add_item(confirm_button)
        view.add_item(cancel_button)
    
        # Send the view with buttons in the current channel
        await interaction.followup.send("Confirm or cancel payment:", view=view, ephemeral=True)

intents = discord.Intents.default()
client = PayBot()

class ticket_launcher(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 600, commands.BucketType.member)
    
    @discord.ui.button(label="Create a Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()
        if retry: 
            return await interaction.response.send_message(f"Slow down! Try again in {round(retry, 1)} seconds!", ephemeral=True)
        
        ticket = utils.get(interaction.guild.text_channels, name=f"ticket-for-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")
        if ticket is not None:
            return await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral=True)

        # Fetch the role only if it's None
        if client.ticket_mod is None:
            client.ticket_mod = interaction.guild.get_role(role_id)

        if client.ticket_mod is None:
            print(f"Role ID {role_id} not found in the guild.")
            return await interaction.response.send_message("Ticket moderator role not found! Please check my permissions and the role ID.", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), 
            client.ticket_mod: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True),
        }
        try:
            channel = await interaction.guild.create_text_channel(name=f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}", overwrites=overwrites, reason=f"Ticket for {interaction.user}")
        except Exception as e:
            return await interaction.response.send_message("Ticket creation failed! Make sure I have `manage_channels` permissions!", ephemeral=True)
        
        await channel.send(f"{client.ticket_mod.mention}, {interaction.user.mention} created a ticket!", view=main())
        await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!", ephemeral=True)
class confirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.channel.delete()
        except Exception as e:
            await interaction.response.send_message("Channel deletion failed! Make sure I have `manage_channels` permissions!", ephemeral=True)

class main(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Are you sure you want to close this ticket?", color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=confirm(), ephemeral=True)

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.blurple, custom_id="transcript")
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if os.path.exists(f"{interaction.channel.id}.md"):
            return await interaction.followup.send(f"A transcript is already being generated!", ephemeral=True)
        with open(f"{interaction.channel.id}.md", 'a') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")
                if message.edited_at:
                    edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                    f.write(f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n")
                else:
                    f.write(f"{message.author} on {created}: {message.clean_content}\n")
            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*Generated at {generated} by {client.user}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*")
        
        with open(f"{interaction.channel.id}.md", 'rb') as f:
            await interaction.followup.send(file=discord.File(f, f"{interaction.channel.name}.md"))
        
        os.remove(f"{interaction.channel.id}.md")

@client.tree.context_menu(name="Open a Ticket")
@app_commands.guilds(discord.Object(id=guild_id))
@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.cooldown(3, 20, key=lambda i: (i.guild_id, i.user.id))
@app_commands.checks.bot_has_permissions(manage_channels=True)
async def open_ticket_context_menu(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=True)
    ticket = utils.get(interaction.guild.text_channels, name=f"ticket-for-{user.name.lower().replace(' ', '-')}-{user.discriminator}")
    if ticket is not None:
        return await interaction.followup.send(f"{user.mention} already has a ticket open at {ticket.mention}!", ephemeral=True)

    # Fetch the role only if it's None
    if client.ticket_mod is None:
        client.ticket_mod = interaction.guild.get_role(role_id)

    if client.ticket_mod is None:
        print(f"Role ID {role_id} not found in the guild.")
        return await interaction.followup.send("Ticket moderator role not found! Please check my permissions and the role ID.", ephemeral=True)

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), 
        client.ticket_mod: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True),
    }
        
    channel = await interaction.guild.create_text_channel(name=f"ticket-for-{user.name}-{user.discriminator}", overwrites=overwrites, reason=f"Ticket for {user}, generated by {interaction.user}")
    await channel.send(f"{interaction.user.mention} created a ticket for {user.mention}!", view=main())   
    await interaction.followup.send(f"I've opened a ticket for {user.mention} at {channel.mention}!", ephemeral=True)

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.followup.send(str(error), ephemeral=True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        return await interaction.followup.send(str(error), ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.followup.send("An error occurred!", ephemeral=True)
        raise error

@client.tree.command(name="pay", description="Process a payment")
@app_commands.guilds(discord.Object(id=guild_id))
@app_commands.describe(method="The payment method to use (e.g., phone number)")
async def pay(interaction: discord.Interaction, method: str):
    await client.pay_interaction(interaction, method)

client.run(bottoken)
