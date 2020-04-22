import discord

from discord.ext import commands

from db import get_user_by_id, upsert_user_data, remove_user_data
from .user import User as user
from utils import (
    format_insert_price,
    format_insert_server,
    format_remove_price,
    get_user_date,
)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def admin_add(self, ctx, name: str, id: int, price: int, period=""):
        user_data = get_user_by_id(id)
        date = get_user_date(user_data)
        day = date.strftime("%a")
        period = date.strftime("%p") if period == "" else period.upper()
        set = format_insert_price(name, day, price, period)
        addToSet = format_insert_server(ctx.message.server)
        if upsert_user_data(id, set, addToSet):
            await ctx.send("Added {}'s price of {}.".format(name, price))
            await user.today(self, ctx)
            await user.trends(self, ctx)

    @commands.command()
    @commands.is_owner()
    async def admin_remove(self, ctx, name: str, id: int, op: str, period=""):
        user_data = get_user_by_id(id)
        date = get_user_date(user_data)
        day = date.strftime("%a")
        period = period.upper()
        if op == "sell" and period == "":
            period = date.strftime("%p")
            other_period = "AM" if period == "PM" else "PM"
            other_data = format_remove_price(day, other_period)
            remove_user_data(id, other_data)
        data = format_remove_price(day, period)
        if remove_user_data(id, data):
            await ctx.send("Cleared {}'s {} price".format(name, op))


def setup(bot):
    bot.add_cog(Admin(bot))
