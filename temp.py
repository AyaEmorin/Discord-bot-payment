import discord
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('bot')

intents = discord.Intents.default()
intents.message_content = True  # เปิด intent สำหรับข้อความ
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# เมื่อบอทพร้อมทำงาน
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


# ฟังก์ชันสร้างห้องสำหรับ Ticket
async def create_ticket_channel(interaction):
    guild = interaction.guild
    member = interaction.user

    # สิทธิ์สำหรับห้องที่สร้าง (เฉพาะคนที่สร้างกับทีมงานที่เห็นได้)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),  # ซ่อนจากทุกคน
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True),  # ให้ผู้สร้างเห็น
        discord.utils.get(guild.roles, name="support_team"): discord.PermissionOverwrite(view_channel=True, send_messages=True)  # ให้ทีมงานเห็น
    }

    # สร้างห้องส่วนตัวสำหรับ ticket
    ticket_channel = await guild.create_text_channel(f'ticket-{member.name}', overwrites=overwrites)

    await ticket_channel.send(f'Hello {member.mention}, this is your private ticket. A support team member will assist you shortly.')

    # Mention ทีมงาน
    support_role = discord.utils.get(guild.roles, name="support_team")
    if support_role:
        await ticket_channel.send(f'{support_role.mention}, a new ticket has been created!')

    return ticket_channel

# ฟังก์ชันปิด Ticket
async def close_ticket_channel(interaction):
    channel = interaction.channel
    await channel.delete()

# ปุ่มเปิด ticket
class OpenTicketButton(Button):
    def __init__(self):
        super().__init__(label="Open Ticket",style=ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        # เมื่อกดปุ่มแล้วให้สร้างห้อง Ticket
        await interaction.response.send_message("Creating ticket...", ephemeral=True)
        await create_ticket_channel(interaction)

# ปุ่มปิด ticket
class CloseTicketButton(Button):
    def __init__(self):
        super().__init__(label="Close Ticket", style=ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        # เมื่อกดปุ่มแล้วให้ลบห้อง Ticket
        await interaction.response.send_message("Closing ticket...", ephemeral=True)
        await close_ticket_channel(interaction)

# Command สำหรับการแสดงปุ่มเปิด ticket
@bot.command(name='ticket')
async def ticket(ctx):
    view = View()
    view.add_item(OpenTicketButton())  # เพิ่มปุ่มเปิด ticket
    await ctx.send("Click the button below to create a ticket.", view=view)

# Command สำหรับการแสดงปุ่มปิด ticket (ใส่ในห้อง ticket เท่านั้น)
@bot.command(name='close')
async def close(ctx):
    view = View()
    view.add_item(CloseTicketButton())  # เพิ่มปุ่มปิด ticket
    await ctx.send("Click the button below to close this ticket.", view=view)

bot.run(token)