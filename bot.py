import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # قراءة محتوى الرسائل

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1534885735180664862 
APPLICATIONS_CHANNEL_ID = 1535593260565663794  # ضع هنا ID روم التقديمات

class ApplicationView(View):
    def __init__(self, applicant_username):
        super().__init__(timeout=None)
        self.applicant_username = applicant_username

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.success, custom_id="accept_btn")
    async def accept(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = discord.utils.find(
            lambda m: m.name.lower() == self.applicant_username.lower() or str(m.id) == self.applicant_username or m.display_name.lower() == self.applicant_username.lower(), 
            guild.members
        )
        
        if member:
            role = guild.get_role(ROLE_ID)
            if role:
                await member.add_roles(role)
            try:
                await member.send("🎉 **مبارك! تم قبول تقديمك في عائلة آل تارغيريان.**\nتم إعطاؤك الرتبة بنجاح.")
            except:
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
            lambda m: m.name.lower() == self.applicant_username.lower() or str(m.id) == self.applicant_username or m.display_name.lower() == self.applicant_username.lower(), 
            guild.members
        )
        
        if member:
            try:
                await member.send("❌ **للأسف، تم رفض تقديمك للانضمام إلى آل تارغيريان.**")
            except:
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
    # الفحص لضمان معالجة رسائل الـ Webhook في قناة التقديمات
    if message.channel.id == APPLICATIONS_CHANNEL_ID and message.webhook_id:
        if message.embeds:
            embed = message.embeds[0]
            applicant_username = None
            
            # استخراج اسم المستخدم الخاص بالديسكورد من الـ Embed
            for field in embed.fields:
                if "ديسكورد" in field.name:
                    applicant_username = field.value.strip()
                    break
            
            if applicant_username:
                view = ApplicationView(applicant_username)
                await message.edit(view=view)

    await bot.process_commands(message)

# استبدل التوكن بالجديد بعد عمل Reset
bot.run("MTUzNTU5NTM4Mzg2OTI4NDQyMw.GtrwhM.pxtKfET5DPFfZIIV-Vi3DUl_Z_qYynoHKETHr4")
