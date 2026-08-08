import os
import asyncio
from aiohttp import web
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

ROLE_ID = 1534885735180664862 
APPLICATIONS_CHANNEL_ID = 1535593260565663794 

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def find_member_flexible(guild, input_username):
    target = input_username.strip().lower()
    clean_target = target.replace(".", "").replace("_", "")
    
    # محاولة جلب الأعضاء لضمان وجود القائمة
    try:
        await guild.chunk()
    except Exception:
        pass

    # 1. البحث بالتطابق المباشر أو الـ ID
    for m in guild.members:
        if m.name.lower() == target or str(m.id) == target or m.display_name.lower() == target:
            return m

    # 2. البحث بالتطابق المرن
    for m in guild.members:
        clean_name = m.name.lower().replace(".", "").replace("_", "")
        clean_display = m.display_name.lower().replace(".", "").replace("_", "")
        if clean_target and (clean_target in clean_name or clean_target in clean_display or clean_name in clean_target):
            return m
            
    return None

class ReasonModal(Modal):
    def __init__(self, action_type, applicant_username, view_instance):
        title_text = "سبب القبول" if action_type == "accept" else "سبب الرفض"
        super().__init__(title=title_text)
        self.action_type = action_type
        self.applicant_username = applicant_username
        self.view_instance = view_instance

        self.reason_input = TextInput(
            label="السبب",
            style=discord.TextStyle.paragraph,
            placeholder="اكتب السبب هنا...",
            required=True,
            max_length=300
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        admin_mention = interaction.user.mention
        reason = self.reason_input.value.strip()
        
        member = await find_member_flexible(guild, self.applicant_username)
        applicant_display = member.mention if member else f"`{self.applicant_username}`"

        # تعطيل أزرار رسالة التحكم (الرسالة الثانية)
        self.view_instance.disable_all_items()
        try:
            await interaction.message.edit(view=self.view_instance)
        except Exception as e:
            print(f"Edit message error: {e}")

        if self.action_type == "accept":
            # 1. إعطاء الرتبة
            if member:
                role = guild.get_role(ROLE_ID)
                if role:
                    try:
                        await member.add_roles(role)
                        print(f"Role added to {member.name}")
                    except Exception as e:
                        print(f"Failed to add role: {e}")
                
                # 2. إرسال للخاص عند القبول
                try:
                    await member.send(
                        f"🎉 أهلاً بك {member.mention}!\n"
                        f"**تم قبول تقديمك وتفعيلك بنجاح في عائلة آل تارغيريان.**\n"
                        f"✨ تم إعطاؤك الرتبة بالسيرفر."
                    )
                except Exception as e:
                    print(f"Failed to send DM: {e}")

            # 3. إرسال الرسالة الثالثة (السجل) في روم التقديمات
            await interaction.channel.send(
                f"✅ **[ سجل القرار - قبول ]**\n"
                f"👤 **المتقدم:** {applicant_display}\n"
                f"👑 **المشرف المسؤول:** {admin_mention}\n"
                f"📝 **سبب القبول:** {reason}"
            )
            await interaction.followup.send(f"✅ تم قبول الطلب وإعطاء الرتبة بنجاح.", ephemeral=True)

        elif self.action_type == "reject":
            # 1. إرسال للخاص عند الرفض
            if member:
                try:
                    await member.send(
                        f"❌ أهلاً بك {member.mention}،\n"
                        f"**للأسف تم رفض تقديمك للانضمام إلى آل تارغيريان.**\n"
                        f"🛑 **المشرف المسؤول:** {admin_mention}\n"
                        f"📝 **سبب الرفض:** {reason}"
                    )
                except Exception as e:
                    print(f"Failed to send DM: {e}")

            # 2. إرسال الرسالة الثالثة (السجل) في روم التقديمات
            await interaction.channel.send(
                f"❌ **[ سجل القرار - رفض ]**\n"
                f"👤 **المتقدم:** {applicant_display}\n"
                f"🛑 **المشرف المسؤول:** {admin_mention}\n"
                f"📝 **سبب الرفض:** {reason}"
            )
            await interaction.followup.send(f"❌ تم رفض الطلب.", ephemeral=True)

class ApplicationView(View):
    def __init__(self, applicant_username):
        super().__init__(timeout=None)
        self.applicant_username = applicant_username.strip().lower()

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.success, custom_id="accept_btn")
    async def accept(self, interaction: discord.Interaction, button: Button):
        modal = ReasonModal(action_type="accept", applicant_username=self.applicant_username, view_instance=self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.danger, custom_id="reject_btn")
    async def reject(self, interaction: discord.Interaction, button: Button):
        modal = ReasonModal(action_type="reject", applicant_username=self.applicant_username, view_instance=self)
        await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم: {bot.user}')

@bot.event
async def on_message(message):
    if message.channel.id == APPLICATIONS_CHANNEL_ID and message.webhook_id:
        if message.embeds:
            embed = message.embeds[0]
            applicant_username = None
            
            for field in embed.fields:
                if field.name and "ديسكورد" in field.name:
                    applicant_username = field.value
                    break
            
            if not applicant_username and len(embed.fields) >= 3:
                applicant_username = embed.fields[2].value

            if applicant_username:
                view = ApplicationView(applicant_username)
                await message.channel.send(
                    content=f"⚙️ **التحكم بالطلب الخاص بـ:** `{applicant_username}`", 
                    view=view
                )

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
    await bot.start("MTUzNTU5NTM4Mzg2OTI4NDQyMw.GtrwhM.pxtKfET5DPFfZIIV-Vi3DUl_Z_qYynoHKETHr4")

if __name__ == "__main__":
    asyncio.run(main())
