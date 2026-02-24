import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone

HAO_USER_ID = 1053683908220289075
TIMEZONE = timezone(timedelta(hours=7))  # UTC+7


class LunchReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_lunch_reminder.start()

    @tasks.loop(hours=24)
    async def send_lunch_reminder(self):
        """Send lunch reminder to Hào at mid-day (12:00 PM UTC+7)"""
        await self.bot.wait_until_ready()

        # Get current time in UTC+7
        now = datetime.now(TIMEZONE)

        # Check if it's noon (12:00 PM)
        if now.hour == 12 and now.minute < 1:  # Run during the 12:00 hour
            try:
                user = await self.bot.fetch_user(HAO_USER_ID)
                await user.send("🍽️ Hey! It's lunch time! Don't forget to eat lunch today!:3")
                print(f"Lunch reminder sent to Hào at {now}")
            except Exception as e:
                print(f"Failed to send lunch reminder to Hào: {e}")

    @send_lunch_reminder.before_loop
    async def before_send_lunch_reminder(self):
        """Wait until bot is ready before starting the task"""
        await self.bot.wait_until_ready()


async def setup(bot):
    """Load the lunch reminder cog"""
    await bot.add_cog(LunchReminder(bot))
