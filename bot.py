import os
import asyncio
from aiohttp import web
import discord
from discord.ext import commands
from discord.ui import Button, View

ROLE_ID = 1534885735180664862 
APPLICATIONS_CHANNEL_ID = 1535593260565663794 

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ApplicationView(View):
    def __init__(self, applicant_username):
        super().__init__(timeout=None)
        self.applicant_username = applicant_username.strip().lower()

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.success, custom_id="accept_btn")
    async def accept(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = discord.utils.find(
            lambda m: m.name.lower() == self.applicant_username 
            or str(m.id) == self.applicant_username 
            or m.display_name.lower() == self.applicant_username, 
            guild.members
        )
        
        if member:
            role = guild.get_role(ROLE_ID)
            if role:
                await member.add_roles(role)
            try:
                await member.send("🎉 **مبارك! تم قبول تقديمك في عائلة آل تارغيريان.**\nتم إعطاؤك الرتبة بنجاح.")
            except Exception:
                pass
            await interaction.response.send_message(f"✅ تم قبول {member.mention} وإعطائه الرتبة.", ephemeral=True)
            self.disable_all_items()
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message(f"⚠️ لم يتم العثور على `{self.applicant_username}` في السيرفر!", ephemeral=True)

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.danger, custom_id="reject_btn")
    async def reject(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = discord.utils.find(
            lambda m: m.name.lower() == self.applicant_username 
            or str(m.id) == self.applicant_username 
            or m.display_name.lower() == self.applicant_username, 
            guild.members
        )
        
        if member:
            try:
                await member.send("❌ **للأسف، تم رفض تقديمك للانضمام إلى آل تارغيريان.**")
            except Exception:
                pass
            await interaction.response.send_message(f"❌ تم رفض {member.mention} وإرسال رسالة بالخاص.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ تم رفض الطلب (العضو غير موجود بالسيرفر).", ephemeral=True)
            
        self.disable_all_items()
        await interaction.message.edit(view=self)

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم: {bot.user}')

@bot.event
async def on_message(message):
    # التأكد من القناة وأن الرسالة قادمة من الـ Webhook
    if message.channel.id == APPLICATIONS_CHANNEL_ID and message.webhook_id:
        if message.embeds:
            embed = message.embeds[0]
            applicant_username = None
            
            for field in embed.fields:
                # الفحص التكيفي لاسم الحقل (يشمل الكلمات المسبوقة بإيموجي)
                if field.name and "ديسكورد" in field.name:
                    applicant_username = field.value
                    break
            
            if applicant_username:
                view = ApplicationView(applicant_username)
                await message.edit(view=view)

    await bot.process_commands(message)

# Web Server لتجنب توقف Render
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await start_web_server()
    # استبدل التوكن هنا
    await bot.start("MTUzNTU5NTM4Mzg2OTI4NDQyMw.GtrwhM.pxtKfET5DPFfZIIV-Vi3DUl_Z_qYynoHKETHr4")

if __name__ == "__main__":
    asyncio.run(main())
