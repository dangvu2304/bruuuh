from discord.ext import commands
from discord import app_commands
import random

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

class Lunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lunchgacha", description="Let Deni decide what you should eat for lunch today")
    async def lunch(self, ctx):
        await ctx.response.send_message("Today you should eat " + random.choice(lunchOptions)+ "! :33")

    @app_commands.command(name="lunchwheel", description="Spin the wheel to decide what you should eat for lunch today")
    async def lunchwheel(self, ctx):
        await ctx.response.send_message("https://wheelofnames.com/h8j-7bm")


async def setup(bot):
    await bot.add_cog(Lunch(bot))