import io
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp

# إعدادات البوت والصلاحيات (Intents)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ثوابت البوت والقنوات
WELCOME_CHANNEL_ID = 1563529178630848523  # أيدي قناة الترحيب
SERVER_IP = "99aurasmp@aternos.me"       # آيبي السيرفر
CREATE_VOICE_NAME = "create room +"        # اسم روم الصوت المؤقت
CREATE_CHAT_NAME = "+ create chat"         # اسم القناة أو الكلمة المفتاحية لإنشاء شات


# ==========================================
# 1. حدث التشغيل والمزامنة (On Ready)
# ==========================================
@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول بنجاح! البوت يعمل باسم: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 تم مزامنة {len(synced)} أمر من أوامر Slash Commands.")
    except Exception as e:
        print(f"❌ خطأ أثناء مزامنة الأوامر: {e}")


# ==========================================
# 2. أمر القوانين الاحترافي (/rules)
# ==========================================
@bot.tree.command(name="rules", description="عرض القوانين الرسمية والشاملة لسيرفر AURA SMP")
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 القوانين الرسمية والأساسية لسيرفر AURA SMP",
        description="مرحباً بك في مجتمعنا! لضمان تجربة ممتعة وعادلة للجميع، يرجى الالتزام التام بالقوانين الآتية:",
        color=discord.Color.gold()
    )
    embed.add_field(name="🤝 1. الاحترام المتبادل والآداب العامة", value="• يمنع منعاً باتاً السب، الشتم، أو توجيه الإهانة لأي عضو.\n• يمنع إثارة المشاكل الطائفية، السياسية، أو العنصرية.\n• احترام الإدارة وأعضاء الفريق إلزامي.", inline=False)
    embed.add_field(name="🛡️ 2. منع التخريب والغريف (Griefing)", value="• يمنع سرقة ممتلكات وأغراض اللاعبين الآخرين في الأماكن المحمية.\n• يمنع تخريب أو هدم مباني ومشاريع اللاعبين دون إذن صاحبها.", inline=False)
    embed.add_field(name="⚡ 3. الهاكات والبرمجيات الخبيثة (Cheating)", value="• يُحظر نهائياً استخدام أي نوع من الهاكات، الأكواد، أو المودات الممنوعة (مثل X-Ray).\n• استغلال الثغرات البرمجية أو أخطاء السيرفر يعرضك للباند النهائي المباشر.", inline=False)
    embed.add_field(name="📢 4. منع الإعلانات والسبام (Spam & Ads)", value="• يمنع نشر روابط سيرفرات ديسكورد أخرى أو الإعلان عن قنوات خارجية.\n• يمنع التكرار المزعج للرسائل (Spam) في الشات العام أو الخاص.", inline=False)
    embed.add_field(name="🎫 5. الدعم الفني والتذاكر", value="• لأي مشكلة أو استفسار، يرجى استخدام نظام التذاكر حصرياً وعدم إزعاج الإدارة بالخاص.", inline=False)
    
    embed.set_footer(text="AURA SMP Network • مخالفة هذه القوانين تعرض حسابك للعقوبة المباشرة.")
    if interaction.guild and interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
    await interaction.response.send_message(embed=embed)


# ==========================================
# 3. نظام التذاكر المطور (Dropdown Ticket System)
# ==========================================
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Technical Support", description="Report bugs, crashes, lag, or technical issues.", emoji="💻", value="tech"),
            discord.SelectOption(label="Ban Appeal", description="Appeal a ban, mute, or other punishment.", emoji="⚖️", value="ban"),
            discord.SelectOption(label="Staff Report", description="Report a staff member with evidence.", emoji="🛡️", value="staff"),
            discord.SelectOption(label="Player Report", description="Report a player with evidence.", emoji="👤", value="player"),
            discord.SelectOption(label="Partnership", description="Partnership requests and collaborations.", emoji="🤝", value="partner"),
            discord.SelectOption(label="Store Support", description="Issues with purchases, donations, or the store.", emoji="🛍️", value="store"),
            discord.SelectOption(label="General Support", description="Anything else you need help with.", emoji="🏷️", value="general"),
            discord.SelectOption(label="Media Application", description="Apply for a media/content creator role.", emoji="🎬", value="media"),
            discord.SelectOption(label="Discord Unban Appeal", description="Appeal a ban from this Discord server.", emoji="💬", value="discord_unban")
        ]
        super().__init__(placeholder="Choose a ticket type...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel_name = f"ticket-{interaction.user.name}-{self.values[0]}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"Support Ticket - {self.values[0].capitalize()}",
            description=f"Need help? Select a category below that best matches your issue and a private ticket channel will be created for you.\n\nWelcome {interaction.user.mention}! Please describe your issue clearly.",
            color=discord.Color.purple()
        )
        await ticket_channel.send(content=interaction.user.mention, embed=embed)
        await interaction.response.send_message(f"✅ Your private ticket channel has been created: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.tree.command(name="ticket_panel", description="إرسال لوحة التذاكر الاحترافية للسيرفر")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Support Tickets",
        description="Need help? Select a category below that best matches your issue and a private ticket channel will be created for you.\n\nPlease only open one ticket per issue — duplicate tickets may be closed.",
        color=discord.Color.dark_embed()
    )
    if interaction.guild and interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
    embed.add_field(name="💻 Technical Support", value="Report bugs, crashes, lag, or technical issues.", inline=False)
    embed.add_field(name="⚖️ Ban Appeal", value="Appeal a ban, mute, or other punishment.", inline=False)
    embed.add_field(name="🛡️ Staff Report", value="Report a staff member with evidence.", inline=False)
    embed.add_field(name="👤 Player Report", value="Report a player with evidence.", inline=False)
    embed.add_field(name="🤝 Partnership", value="Partnership requests and collaborations.", inline=False)
    embed.add_field(name="🛍️ Store Support", value="Issues with purchases, donations, or the store.", inline=False)
    embed.add_field(name="🏷️ General Support", value="Anything else you need help with.", inline=False)
    embed.add_field(name="🎬 Media Application", value="Apply for a media/content creator role.", inline=False)
    embed.add_field(name="💬 Discord Unban Appeal", value="Appeal a ban from this Discord server.", inline=False)
    
    embed.set_footer(text="Your Server • Support System")
    
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ تم إنشاء لوحة التذاكر بنجاح.", ephemeral=True)


# ==========================================
# 4. نظام الترحيب بالصورة المخصصة (مضبوط الإحداثيات داخل الدائرة الكبيرة)
# ==========================================
@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    try:
        # تحميل صورة البروفايل الخاصة بالعضو
        avatar_url = member.display_avatar.with_format("png").url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status != 200:
                    return
                avatar_bytes = await resp.read()

        # فتح صورة الخلفية وصورة البروفايل
        background = Image.open("welcome.jpg").convert("RGBA")
        avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

        # 1. تجهيز صورة البروفايل لتناسب الدائرة الكبيرة على اليمين بدقة
        avatar_size = (310, 310)
        avatar_img = avatar_img.resize(avatar_size, Image.Resampling.LANCZOS)

        # إنشاء قناع دائري
        mask = Image.new('L', avatar_size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)

        # إحداثيات الدائرة الكبيرة على اليمين (مضبوطة تماماً داخل الكوكب الأسود)
        avatar_x, avatar_y = 615, 230
        background.paste(avatar_img, (avatar_x, avatar_y), mask)

        # 2. إضافة النصوص (المنطقة الصفراء والخضراء)
        draw = ImageDraw.Draw(background)

        try:
            font_title = ImageFont.truetype("arial.ttf", 40)
            font_name = ImageFont.truetype("arial.ttf", 35)
        except IOError:
            font_title = ImageFont.load_default()
            font_name = ImageFont.load_default()

        # النص الأصفر (أهلاً وسهلاً بك في) في أعلى اليمين
        yellow_text = "أهلاً وسهلاً بك في"
        draw.text((450, 60), yellow_text, fill=(255, 215, 0), font=font_title)

        # النص الأخضر (اسم الشخص) في الشريط الأسفل
        green_text = f"{member.name}"
        draw.text((200, 480), green_text, fill=(50, 205, 50), font=font_name)

        # حفظ الصورة في الذاكرة وإرسالها
        with io.BytesIO() as image_binary:
            background.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='welcome_aura.png')
            
            await channel.send(
                content=f"🎉 أهلاً بك {member.mention} في سيرفر **AURA SMP**! نورتنا.",
                file=file
            )

    except Exception as e:
        print(f"❌ خطأ أثناء إنشاء صورة الترحيب: {e}")


# ==========================================
# 5. نظام الرومات الصوتية والشات الخاص (+ create chat / روم صوتي)
# ==========================================
@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # إنشاء روم صوتي مؤقت عند الدخول للروم المحدد
    if after.channel and after.channel.name.lower() == CREATE_VOICE_NAME.lower():
        category = after.channel.category
        new_channel = await member.guild.create_voice_channel(
            name=f"🔊 {member.display_name}'s Room",
            category=category
        )
        await member.move_to(new_channel)

    # حذف الروم الصوتي عند خروج جميع الأعضاء منه
    if before.channel and before.channel.name.startswith("🔊 "):
        if len(before.channel.members) == 0:
            await before.channel.delete()

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    msg = message.content.strip()

    # ميزة إنشاء شات نصي خاص بالكتابة (+ create chat [الاسم])
    if msg.lower().startswith("+ create chat"):
        chat_title = msg[len("+ create chat"):].strip()
        if not chat_title:
            chat_title = f"chat-{message.author.name}"
        
        guild = message.guild
        category = message.channel.category
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            message.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        new_text_channel = await guild.create_text_channel(name=chat_title, category=category, overwrites=overwrites)
        await message.channel.send(f"✅ تم إنشاء الشات الخاص بك بنجاح: {new_text_channel.mention}", delete_after=10)
        try:
            await message.delete()
        except:
            pass
        return

    # الرد التلقائي المطوّر لعرض الآيبي
    msg_lower = msg.lower()
    if "ip" in msg_lower or "ايبي" in msg_lower or "آيبي" in msg_lower:
        embed = discord.Embed(
            title="🎮 معلومات الاتصال بسيرفر AURA SMP",
            description="انضم إلينا الآن وشارك أصدقاءك المتعة في عالمنا!",
            color=discord.Color.purple()
        )
        embed.add_field(name="🌐 Java & Bedrock Server IP:", value=f"`{SERVER_IP}`", inline=False)
        embed.add_field(name="📊 حالة السيرفر:", value="`Online / 24 ساعـة`", inline=False)
        embed.set_footer(text="AURA SMP Network • نسعد بانضمامك")
        if message.guild and message.guild.icon:
            embed.set_thumbnail(url=message.guild.icon.url)
        
        await message.channel.send(embed=embed)

    await bot.process_commands(message)


# ==========================================
# 6. تشغيل البوت
# ==========================================
# ضع توكن البوت الحقيقي الخاص بك هنا بدلاً من النص التجريبي
bot.run("MTU2MzI5NzY5ODE5MzQ3NzgxNA.GvRpvS.yqUwzmU49hdZNjRmXVF0j8sisCtXMq3Zg5dkhc")