import asyncio
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red


class SINOffice(commands.Cog):
    """Daily SIN Corporation office announcements."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9872314560013, force_registration=True)
        self.config.register_guild(
            enabled=False,
            post_channel_id=None,
            quote_channel_id=None,
            chatquotes=False,
            start_hour=10,
            end_hour=13,
            next_post_at=None,
            last_post_date=None,
            quote_pool=[],
            color=0x9B59B6,
        )
        self._task = asyncio.create_task(self._scheduler_loop())

        self.departments = [
            "HR", "Research", "IT", "Security", "Accounting", "Containment", "Cafeteria", "Janitorial",
            "Marketing", "Legal", "Public Relations", "The Basement Office", "Infernal Logistics", "Reception",
        ]
        self.subjects = [
            "the coffee machine", "a printer", "the elevator", "a cursed stapler", "the break room fridge",
            "an intern", "a motivational poster", "the vending machine", "one suspiciously shiny memo",
            "the office chair in Meeting Room 3", "a spreadsheet", "the company mascot", "a training dummy",
            "the CEO's emergency snack drawer", "a portal marked 'Definitely Safe'",
        ]
        self.actions = [
            "requested paid vacation", "started glowing ominously", "filed a complaint against reality",
            "printed the word 'no' seven hundred times", "became emotionally attached to a clipboard",
            "declared itself middle management", "briefly opened a portal to accounting", "ate three reports",
            "began humming boss music", "achieved sentience and immediately regretted it", "summoned glitter",
            "locked itself in a meeting", "approved its own promotion", "started a union with the office plants",
        ]
        self.outcomes = [
            "HR says this is technically progress.", "Security is pretending this was planned.",
            "The CEO has been informed and is choosing chaos.", "IT fixed it by turning it off and whispering threats.",
            "Nobody was injured, except the budget.", "Everyone received emotional damage and one cookie.",
            "Legal refuses to acknowledge this event happened.", "The situation is under control, which means it is absolutely not.",
            "Janitorial has requested hazard pay again.", "All Dwellers are advised to act normal until further notice.",
        ]
        self.ceo_reminders = [
            "You do not need to defeat the entire day at once. One small victory still counts as victory.",
            "Progress is still progress, even if it arrives wearing pajamas and carrying coffee.",
            "Be kind to yourself today. The world is already weird enough without you bullying your own brain.",
            "Your pace is allowed to be your pace. SIN Corp does not charge rent for slow growth. Yet.",
            "Do the next small thing. Then the next. That is how castles are built.",
            "You are allowed to rest before you collapse. Preventive laziness is sometimes advanced strategy.",
            "Today does not need to be perfect. It only needs to be lived through with a little bit of spite and sparkle.",
            "You are more capable than the anxious little gremlin in your brain claims.",
            "Drink water, stretch your mortal vessel, and continue your villain arc responsibly.",
            "Even on quiet days, you still matter here.",
        ]

    def cog_unload(self):
        self._task.cancel()

    async def _scheduler_loop(self):
        await self.bot.wait_until_red_ready()
        while True:
            try:
                await self._check_guilds()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[SINOffice] Scheduler error: {exc}")
            await asyncio.sleep(60)

    async def _check_guilds(self):
        now = datetime.now()
        for guild in self.bot.guilds:
            data = await self.config.guild(guild).all()
            if not data["enabled"] or not data["post_channel_id"]:
                continue

            next_post_at = data.get("next_post_at")
            if not next_post_at:
                await self._schedule_next(guild, now=now)
                continue

            try:
                target = datetime.fromisoformat(next_post_at)
            except ValueError:
                await self._schedule_next(guild, now=now)
                continue

            if now >= target:
                today = now.date().isoformat()
                if data.get("last_post_date") != today:
                    await self._send_daily_notice(guild)
                    await self.config.guild(guild).last_post_date.set(today)
                await self._schedule_next(guild, now=now + timedelta(days=1), force_tomorrow=True)

    async def _schedule_next(self, guild: discord.Guild, now: Optional[datetime] = None, force_tomorrow: bool = False):
        now = now or datetime.now()
        data = await self.config.guild(guild).all()
        start = int(data.get("start_hour", 10))
        end = int(data.get("end_hour", 13))
        if end < start:
            end = start

        day = now.date()
        if force_tomorrow:
            day = day + timedelta(days=1)

        hour = random.randint(start, end)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        target = datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute, second=second)

        if target <= datetime.now():
            target = target + timedelta(days=1)

        await self.config.guild(guild).next_post_at.set(target.isoformat(timespec="seconds"))

    async def _send_daily_notice(self, guild: discord.Guild):
        data = await self.config.guild(guild).all()
        channel = guild.get_channel(data["post_channel_id"])
        if not isinstance(channel, discord.TextChannel):
            return

        now = datetime.now()
        incident = self._make_incident()
        reminder = random.choice(self.ceo_reminders)
        quote = await self._get_random_quote(guild) if data.get("chatquotes") else None

        embed = discord.Embed(
            title="🏢 SIN CORPORATION DAILY NOTICE",
            description="Good morning, Dwellers. Please read today’s official office bulletin before touching anything glowing.",
            color=int(data.get("color", 0x9B59B6)),
            timestamp=now,
        )
        embed.add_field(
            name="📅 Today",
            value=f"**{now.strftime('%A, %d %B %Y')}**\nOffice time: **{now.strftime('%H:%M')}**",
            inline=False,
        )
        embed.add_field(name="📋 Incident Report", value=incident, inline=False)
        if quote:
            embed.add_field(name="💬 Dweller Quote", value=f"“{quote['content']}” - **{quote['author']}**", inline=False)
        embed.add_field(name="🖤 CEO Reminder", value=reminder, inline=False)
        embed.set_footer(text="SIN Corp HR Department • Mandatory morale has been scheduled")

        await channel.send(embed=embed)

    def _make_incident(self) -> str:
        department = random.choice(self.departments)
        subject = random.choice(self.subjects)
        action = random.choice(self.actions)
        outcome = random.choice(self.outcomes)
        return f"**{department}** reports that {subject} {action}. {outcome}"

    async def _get_random_quote(self, guild: discord.Guild) -> Optional[Dict[str, str]]:
        quotes: List[Dict[str, str]] = await self.config.guild(guild).quote_pool()
        cutoff = datetime.utcnow() - timedelta(hours=24)
        fresh = []
        for q in quotes:
            try:
                ts = datetime.fromisoformat(q.get("timestamp", ""))
            except ValueError:
                continue
            if ts >= cutoff:
                fresh.append(q)

        if not fresh:
            return None
        return random.choice(fresh)

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        data = await self.config.guild(message.guild).all()
        quote_channel_id = data.get("quote_channel_id")
        if not quote_channel_id or message.channel.id != quote_channel_id:
            return

        cleaned = self._clean_quote(message.content)
        if not cleaned:
            return

        entry = {
            "content": cleaned,
            "author": message.author.display_name,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }
        async with self.config.guild(message.guild).quote_pool() as quotes:
            quotes.append(entry)
            del quotes[:-250]

    def _clean_quote(self, content: str) -> Optional[str]:
        content = content.strip()
        if not content:
            return None
        if content.startswith(("!", "?", "/", ".", ",", ";", "$")):
            return None
        if len(content) < 12 or len(content) > 180:
            return None
        if "http://" in content.lower() or "https://" in content.lower() or "discord.gg" in content.lower():
            return None
        if content.count("\n") > 1:
            return None
        content = discord.utils.escape_mentions(content)
        content = re.sub(r"\s+", " ", content)
        return content

    @commands.hybrid_group(name="sinoffice", aliases=["office"], invoke_without_command=True)
    @commands.guild_only()
    async def sinoffice(self, ctx: commands.Context):
        """Configure SIN Corporation daily office announcements."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @sinoffice.command(name="setpostchannel")
    @commands.admin_or_permissions(manage_guild=True)
    async def setpostchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel where daily notices are posted."""
        await self.config.guild(ctx.guild).post_channel_id.set(channel.id)
        await ctx.send(f"Daily SIN Office notices will be posted in {channel.mention}.")

    @sinoffice.command(name="setquotechannel")
    @commands.admin_or_permissions(manage_guild=True)
    async def setquotechannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the one channel allowed for Dweller Quote collection."""
        await self.config.guild(ctx.guild).quote_channel_id.set(channel.id)
        await ctx.send(f"Dweller Quotes will only be collected from {channel.mention}.")

    @sinoffice.command(name="chatquotes")
    @commands.admin_or_permissions(manage_guild=True)
    async def chatquotes(self, ctx: commands.Context, enabled: bool):
        """Turn Dweller Quotes on or off."""
        await self.config.guild(ctx.guild).chatquotes.set(enabled)
        await ctx.send(f"Dweller Quotes are now **{'enabled' if enabled else 'disabled'}**.")

    @sinoffice.command(name="toggle")
    @commands.admin_or_permissions(manage_guild=True)
    async def toggle(self, ctx: commands.Context, enabled: bool):
        """Turn automatic daily notices on or off."""
        await self.config.guild(ctx.guild).enabled.set(enabled)
        if enabled:
            await self._schedule_next(ctx.guild)
        await ctx.send(f"Automatic SIN Office notices are now **{'enabled' if enabled else 'disabled'}**.")

    @sinoffice.command(name="time")
    @commands.admin_or_permissions(manage_guild=True)
    async def time_window(self, ctx: commands.Context, start_hour: int, end_hour: int):
        """Set the random posting window using 24-hour time. Example: 10 13."""
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            await ctx.send("Please use hours between 0 and 23, like `10 13`.")
            return
        if end_hour < start_hour:
            await ctx.send("The end hour needs to be the same as or later than the start hour.")
            return
        await self.config.guild(ctx.guild).start_hour.set(start_hour)
        await self.config.guild(ctx.guild).end_hour.set(end_hour)
        await self._schedule_next(ctx.guild)
        await ctx.send(f"Daily notices will post randomly between **{start_hour:02d}:00** and **{end_hour:02d}:59**.")

    @sinoffice.command(name="test")
    @commands.admin_or_permissions(manage_guild=True)
    async def test(self, ctx: commands.Context):
        """Send a test SIN Office notice now."""
        await self._send_daily_notice(ctx.guild)
        await ctx.send("Test notice sent.")

    @sinoffice.command(name="status")
    @commands.admin_or_permissions(manage_guild=True)
    async def status(self, ctx: commands.Context):
        """Show current SIN Office settings."""
        data = await self.config.guild(ctx.guild).all()
        post_channel = ctx.guild.get_channel(data.get("post_channel_id"))
        quote_channel = ctx.guild.get_channel(data.get("quote_channel_id"))
        embed = discord.Embed(title="SIN Office Status", color=int(data.get("color", 0x9B59B6)))
        embed.add_field(name="Enabled", value=str(data.get("enabled")), inline=True)
        embed.add_field(name="Post Channel", value=post_channel.mention if post_channel else "Not set", inline=True)
        embed.add_field(name="Quote Channel", value=quote_channel.mention if quote_channel else "Not set", inline=True)
        embed.add_field(name="Chat Quotes", value=str(data.get("chatquotes")), inline=True)
        embed.add_field(name="Time Window", value=f"{data.get('start_hour', 10):02d}:00 to {data.get('end_hour', 13):02d}:59", inline=True)
        embed.add_field(name="Next Post", value=data.get("next_post_at") or "Not scheduled", inline=False)
        await ctx.send(embed=embed)

    @sinoffice.command(name="clearquotes")
    @commands.admin_or_permissions(manage_guild=True)
    async def clearquotes(self, ctx: commands.Context):
        """Clear the stored Dweller Quote pool."""
        await self.config.guild(ctx.guild).quote_pool.set([])
        await ctx.send("Stored Dweller Quotes have been cleared.")
