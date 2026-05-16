import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="cadv", intents=intents, case_insensitive=True)

# ================= READY =================
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

    print(f"🔥 Bot online: {bot.user}")

# ================= WEBHOOK CORE =================
async def get_webhook(channel: discord.TextChannel):
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="dv_webhook")

    if webhook is None:
        webhook = await channel.create_webhook(name="dv_webhook")

    return webhook


async def send_as(channel, member, text):
    webhook = await get_webhook(channel)

    await webhook.send(
        content=text,
        username=member.display_name,
        avatar_url=member.display_avatar.url
    )

# ================= SLASH COMMAND =================
@bot.tree.command(name="dv", description="Đóng giả người khác (ẩn)")
@app_commands.describe(member="Người bạn muốn đóng giả", message="Nội dung")
async def dv(interaction: discord.Interaction, member: discord.Member, message: str):

    await interaction.response.defer(ephemeral=True)

    try:
        await send_as(interaction.channel, member, message)
        await interaction.followup.send("✅ Đã gửi", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Lỗi: {e}", ephemeral=True)

# ================= MESSAGE PREFIX (cadv @user msg) =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # dùng: cadv @user nội dung
    if message.content.startswith("cadv "):
        parts = message.content.split(" ", 2)

        if len(parts) < 3:
            return

        if not message.mentions:
            await message.channel.send("❌ Bạn phải mention người dùng")
            return

        member = message.mentions[0]
        text = parts[2]

        try:
            await message.delete()
        except:
            pass

        try:
            await send_as(message.channel, member, text)
        except Exception as e:
            await message.channel.send(f"❌ Lỗi: {e}")

    # vẫn cho command khác hoạt động
    await bot.process_commands(message)

# ================= CLEAN WEBHOOK =================
@bot.command()
@commands.has_permissions(administrator=True)
async def cleardv(ctx):
    webhooks = await ctx.guild.webhooks()
    count = 0

    for w in webhooks:
        if w.name == "dv_webhook":
            await w.delete()
            count += 1

    await ctx.send(f"🧹 Đã xóa {count} webhook dv")

# ================= RUN =================
bot.run(TOKEN)