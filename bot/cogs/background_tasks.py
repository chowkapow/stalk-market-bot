import asyncio

from datetime import datetime, timedelta
from discord.ext import commands, tasks

from constants import reset_time
from db import remove_all_data


class Background_Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_buy_prices.start()
        self.reset_sell_prices.start()

    @tasks.loop(hours=168)
    async def reset_buy_prices(self):
        self.bot._buy_prices.clear()
        self.bot._sell_morning_prices.clear()
        self.bot._sell_afternoon_prices.clear()
        remove_all_prices({"prices": ""})

    @reset_buy_prices.before_loop
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

    @tasks.loop(hours=24)
    async def reset_sell_prices(self):
        self.bot._sell_morning_prices.clear()
        self.bot._sell_afternoon_prices.clear()

    @reset_sell_prices.before_loop
    async def before(self):
        d = datetime.now()
        tomorrow = d + timedelta(days=1)
        reset = datetime(
            year=tomorrow.year,
            month=tomorrow.month,
            day=tomorrow.day,
            hour=reset_time,
            minute=0,
            second=0,
        )
        await asyncio.sleep((reset - d).total_seconds())
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Background_Tasks(bot))
