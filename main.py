import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from io import BytesIO
from promptpay import qrcode

load_dotenv()
bottoken = os.getenv('bot')

class PayBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = PayBot()

import discord
import qrcode
from io import BytesIO

@client.tree.command(name="pay", description="Process a payment")
@app_commands.describe(method="The payment method to use")
async def pay(interaction: discord.Interaction, method: str):
    await interaction.response.send_message(f"Processing payment using {method}...")

    # สร้างข้อมูลสำหรับ QR Code (ปรับตามรูปแบบของ Thai QR)
    phone_number = method
    amount = "100.00"
    other_details = "สินค้า A, บิลเลขที่ B"
    qr_data = f"PaymentID={phone_number}&Amount={amount}&OtherDetails={other_details}"

    # สร้าง QR Code
    payload = qrcode.make(method)

    # สร้างภาพ QR Code และแปลงเป็นไฟล์
    img = payload.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)

    # ส่งไฟล์ QR Code ผ่าน DM
    await interaction.user.send(file=discord.File(buffer, 'qr_code.png'))
client.run(bottoken)