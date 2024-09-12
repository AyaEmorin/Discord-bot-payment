import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from io import BytesIO
import qrcode
from promptpay import qrcode

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
<<<<<<< Updated upstream
async def pay(interaction: discord.Interaction, method: str):
    await interaction.response.send_message(f"Processing payment using {method}...")

    # Validate phone number format (assuming phone number as method)
    if not method.isdigit():
        await interaction.followup.send("Invalid phone number. Please enter a valid Thai phone number.")
        return
=======
async def pay(interaction: discord.Interaction, phonenumber: str):
    await interaction.response.send_message(f"Processing payment using {phonenumber}...")

    phone_number = phonenumber
    qr_data = f'https://promptpay.io/{phone_number}'
>>>>>>> Stashed changes

    # สร้างข้อมูลสำหรับ QR Code (ปรับตามรูปแบบของ Thai QR)
    phone_number = method
    amount = "100.00"
    other_details = "สินค้า A, บิลเลขที่ B"
    qr_data = f"PaymentID={phone_number}&Amount={amount}&OtherDetails={other_details}"

    # สร้าง QR Code using standard qrcode library
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10)
    qr.add_data(method)
    qr.make(fit=True)

    # สร้างภาพ QR Code และแปลงเป็นไฟล์
    img = qrcode.to_image(method)
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)

    # ส่งไฟล์ QR Code ผ่าน DM
    await interaction.user.send(file=discord.File(buffer, 'qr_code.png'))

client.run(bottoken)