import discord 
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os 
import asyncio
from collections import deque
import random

from keep_alive import keep_alive   

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

keep_alive()

print(f"Token: {token}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


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


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "xin nghỉ" in message.content.lower():
        await message.channel.send("Nghỉ gì nghỉ hoài vậy ba")

    await bot.process_commands(message)

@bot.command()
async def gachaLunch(ctx):
    await ctx.send("Trưa nay bạn nên ăn: " + random.choice(lunchOptions))

bot.run(token)
