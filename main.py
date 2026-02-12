import discord 
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import os 
import asyncio
from collections import deque
import random
import datetime
import pytz

from keep_alive import keep_alive   

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

keep_alive()

print(f"Token: {token}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

BC_CHANNEL_ID = 1372796413909401640

lunchOptions = [
    "Cơm chay",
    "Cơm sườn",
    "Cơm gà luộc",
    "Bún bò",
    "Bánh mì",
    "Bot chiên",
    "Cơm văn phòng",
    "Bánh canh",
    "Deni"
]

tz = pytz.timezone("Asia/Ho_Chi_Minh")
target_time = datetime.time(hour=14,minute=46, tzinfo=tz)

@tasks.loop(time=target_time)
async def daily_message():
    channel = bot.get_channel(BC_CHANNEL_ID)
    if channel:
        print("Sending daily message...")
        await channel.send("@1053683908220289075 Mèo méo meo mèo meo. Ăn trưa thôi cậu chủ ơi!")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')
    daily_message.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    


    await bot.process_commands(message)



@bot.tree.command(name = "lunchgacha", description="Gacha món ăn trưa gần cty")
async def lunchgacha(interaction):
    await interaction.response.send_message("Trưa nay ăn " + random.choice(lunchOptions))


@bot.tree.command(name = "lunchgachawheel", description="Gacha món ăn trưa gần cty bằng wheel of names")
async def lunchgachawheel(interaction):
    await interaction.response.send_message("https://wheelofnames.com/h8j-7bm")

bot.run(token)