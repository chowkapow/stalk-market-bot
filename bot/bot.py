from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._env = env
