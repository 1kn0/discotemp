import discord
from discord.ext import commands

from discotemp import welcomebot

intents = discord.Intents.default()
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)


welcome = welcomebot.WelcomeBot(
    channel_id=1537379426461810721,  # <- replace with your welcome channel ID
    template="welcome.json",         # or "welcome_embed.json", or a dict
)

# Auto-hooks on_member_join for you:
welcome.attach(bot)


# --- Or, wire it manually if you want more control ------------------------
#
# @bot.event
# async def on_member_join(member: discord.Member):
#     await welcome.send(member)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


if __name__ == "__main__":
    bot.run("MTUzNzM4OTY2Njk0NzMwMTM3OA.GYGzP9.pO6Aczys7M8W6G4ckY_7xZ6cFpRdAq-K_rfuRA")
