import asyncio

from datetime import datetime, timedelta
from discord.ext import commands, tasks

from constants import reset_time
from db import remove_users_data


class Background_Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_prices.start()

    @tasks.loop(hours=168)
    async def reset_prices(self):
        remove_users_data({"prices": ""})

    @reset_prices.before_loop
    async def before(self):
        d = datetime.now()
        t = timedelta((12 - d.weekday()) % 7)
        saturday = d + t
        reset = datetime(
            year=saturday.year,
            month=saturday.month,
            day=saturday.day,
            hour=23,
            minute=59,
            second=59,
        )
        await asyncio.sleep((reset - d).total_seconds())
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Background_Tasks(bot))
