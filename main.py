import discord 
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os 
import asyncio
 

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')

async def load():
    await bot.load_extension("cogs.lunch")
    await bot.load_extension("cogs.birthday")
    await bot.load_extension("cogs.lunch_reminder")

async def main():
    async with bot:
        await load()
        await bot.start(token)
    

asyncio.run(main())