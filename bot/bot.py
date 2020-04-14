from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._env = env
        self._buy_prices = {}
        self._sell_morning_prices = {}
        self._sell_afternoon_prices = {}
