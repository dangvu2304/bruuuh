import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta, timezone

BIRTHDAYS_FILE = "birthdays.json"
TIMEZONE = timezone(timedelta(hours=7))  # UTC+7
BIRTHDAY_CATEGORY_ID = 1372778328028614666  # General category for birthday channels


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    def load_birthdays(self):
        """Load birthdays from JSON file"""
        if not os.path.exists(BIRTHDAYS_FILE):
            return {}
        try:
            with open(BIRTHDAYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("birthdays", {})
        except (json.JSONDecodeError, IOError):
            return {}

    def save_birthdays(self, birthdays):
        """Save birthdays to JSON file"""
        data = {"birthdays": birthdays}
        try:
            with open(BIRTHDAYS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving birthdays: {e}")

    def get_days_until_birthday(self, month, day):
        """Calculate days until next occurrence of a birthday"""
        now = datetime.now(TIMEZONE)
        current_year = now.year

        birthday_this_year = datetime(current_year, month, day, tzinfo=TIMEZONE)

        if birthday_this_year < now:
            # Birthday has passed this year, calculate for next year
            birthday_this_year = datetime(current_year + 1, month, day, tzinfo=TIMEZONE)

        days_until = (birthday_this_year - now).days
        return days_until

    async def create_birthday_channel(self, guild, user_id, username, nickname, month, day, ping_everyone=True):
        """Create a birthday channel with proper permissions"""
        try:
            channel_name = f"🎂┃{username.lower().replace(' ', '-')}-{day}-{month:02d}"

            # Get the user object
            try:
                user = await self.bot.fetch_user(user_id)
            except discord.NotFound:
                print(f"User {user_id} not found")
                return None

            # Get the category
            category = guild.get_channel(BIRTHDAY_CATEGORY_ID)
            if not category:
                print(f"Birthday category {BIRTHDAY_CATEGORY_ID} not found in guild {guild.id}")
                return None

            # Set up permission overwrites
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                user: discord.PermissionOverwrite(view_channel=False, send_messages=False)
            }

            # Create the channel in the specified category
            channel = await guild.create_text_channel(
                channel_name,
                overwrites=overwrites,
                category=category,
                topic=f"🎂 Birthday celebration for {username}! (Upcoming: {day}/{month})"
            )

            # Send birthday announcement message
            if channel:
                if ping_everyone:
                    await channel.send(f"Hey @everyone, {nickname}'s birthday is coming in 7 days. Let's do some this special for them! 🥳")
                else:
                    await channel.send(f"Hey everyone, {nickname}'s birthday is coming in 7 days. Let's do some this special for them! 🥳")

            return channel
        except Exception as e:
            print(f"Error creating birthday channel: {e}")
            return None

    async def delete_birthday_channel(self, guild, channel_id):
        """Delete a birthday channel"""
        try:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.delete()
                return True
        except Exception as e:
            print(f"Error deleting birthday channel: {e}")
        return False

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Background task to check and manage birthday channels"""
        await self.bot.wait_until_ready()

        # Get current time in UTC+7
        now = datetime.now(TIMEZONE)

        # Only run this at midnight to avoid running multiple times
        if now.hour != 0:
            return

        birthdays = self.load_birthdays()

        for guild in self.bot.guilds:
            channels_to_delete = []

            for user_id_str, birthday_data in list(birthdays.items()):
                user_id = int(user_id_str)
                month = birthday_data.get("month")
                day = birthday_data.get("day")
                channel_id = birthday_data.get("channel_id")

                if not month or not day:
                    continue

                days_until = self.get_days_until_birthday(month, day)

                # Create channel if 7 days away and doesn't exist
                if days_until == 7 and not channel_id:
                    username = birthday_data.get("name", f"User{user_id}")
                    nickname = birthday_data.get("nickname", username)

                    # Check if the birthday person is an admin
                    try:
                        member = await guild.fetch_member(user_id)
                        is_admin = member.guild_permissions.administrator
                    except:
                        is_admin = False

                    if is_admin:
                        # Send DM to all other users in the birthdays list
                        for other_user_id_str, other_birthday_data in birthdays.items():
                            if other_user_id_str != user_id_str:
                                try:
                                    other_user = await self.bot.fetch_user(int(other_user_id_str))
                                    await other_user.send(f"Hey! {nickname}'s birthday is coming in 7 days ({day}/{month}). Create a private chat with other members to come up with a special plan for them! 🥳 (You are receiving this message because I can't create a private channel that can hide from {nickname})")
                                except Exception as e:
                                    print(f"Failed to send DM to {other_user_id_str}: {e}")
                        # Mark as processed by setting channel_id to a placeholder
                        birthdays[user_id_str]["channel_id"] = "notified"
                        self.save_birthdays(birthdays)
                    else:
                        # Create channel as usual
                        channel = await self.create_birthday_channel(guild, user_id, username, nickname, month, day)
                        if channel:
                            birthdays[user_id_str]["channel_id"] = channel.id
                            self.save_birthdays(birthdays)

                # Delete channel if birthday has passed
                if days_until == 0 and channel_id:
                    if channel_id == "notified":
                        # Already notified, just clear the marker
                        birthdays[user_id_str]["channel_id"] = None
                        self.save_birthdays(birthdays)
                    else:
                        # Delete the actual channel
                        channels_to_delete.append((user_id_str, channel_id))

            # Delete channels for birthdays that have passed
            for user_id_str, channel_id in channels_to_delete:
                if await self.delete_birthday_channel(guild, channel_id):
                    birthdays[user_id_str]["channel_id"] = None
                    self.save_birthdays(birthdays)

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        """Wait until bot is ready before starting the task"""
        await self.bot.wait_until_ready()

    @app_commands.command(name="viewbirthdays", description="View all stored birthdays")
    async def view_birthdays(self, interaction: discord.Interaction):
        """View all birthdays in the server"""
        birthdays = self.load_birthdays()

        if not birthdays:
            await interaction.response.send_message(
                "📭 No birthdays stored yet",
                ephemeral=True
            )
            return

        # Create embed with birthday information
        embed = discord.Embed(
            title="🎂 Birthday Calendar",
            color=discord.Color.blue()
        )

        for user_id_str, birthday_data in sorted(birthdays.items()):
            username = birthday_data.get("name", f"User{user_id_str}")
            month = birthday_data.get("month")
            day = birthday_data.get("day")

            if month and day:
                days_until = self.get_days_until_birthday(month, day)

                if days_until == 0:
                    status = "🎉 Today!"
                elif days_until == 1:
                    status = "⏰ Tomorrow!"
                elif days_until <= 7:
                    status = f"⏳ {days_until} days away"
                else:
                    status = f"📅 {days_until} days away"

                embed.add_field(
                    name=f"{username}",
                    value=f"{day}/{month} - {status}",
                    inline=False
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="testbirthday", description="Manually trigger birthday channel creation (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        member="The member to test birthday channel for",
        ping_everyone="Whether to ping @everyone in the message (default: True)"
    )
    async def test_birthday(self, interaction: discord.Interaction, member: discord.Member, ping_everyone: bool = True):
        """Test birthday channel creation for a specific user"""
        birthdays = self.load_birthdays()
        user_id_str = str(member.id)

        if user_id_str not in birthdays:
            await interaction.response.send_message(
                f"❌ No birthday found for {member.mention}",
                ephemeral=True
            )
            return

        birthday_data = birthdays[user_id_str]
        month = birthday_data.get("month")
        day = birthday_data.get("day")
        username = birthday_data.get("name", member.name)
        nickname = birthday_data.get("nickname", username)

        # Check if the birthday person is an admin
        is_admin = member.guild_permissions.administrator

        if is_admin:
            # Send test DM only to the person who ran the command
            try:
                await interaction.user.send(f"Hey! {nickname}'s birthday is coming in 7 days ({day}/{month}). Let's do something special for them! 🥳")
                await interaction.response.send_message(
                    f"✅ Test DM sent to you for {nickname}'s birthday!",
                    ephemeral=True
                )
            except Exception as e:
                print(f"Failed to send test DM: {e}")
                await interaction.response.send_message(
                    "❌ Failed to send test DM",
                    ephemeral=True
                )
        else:
            # Create channel as usual
            channel = await self.create_birthday_channel(interaction.guild, member.id, username, nickname, month, day, ping_everyone)

            if channel:
                birthdays[user_id_str]["channel_id"] = channel.id
                self.save_birthdays(birthdays)
                await interaction.response.send_message(
                    f"✅ Test channel created: {channel.mention}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Failed to create birthday channel",
                    ephemeral=True
                )


async def setup(bot):
    """Load the birthday cog"""
    await bot.add_cog(Birthday(bot))
