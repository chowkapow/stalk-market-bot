import logging
import os
import sys

import utils

from discord.ext import commands
from dotenv import load_dotenv

env = "prod" if len(sys.argv) == 1 else "dev"
# Logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename=env + "-stalk-market-bot.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") if env == "prod" else os.getenv("dev_DISCORD_TOKEN")

bot = commands.Bot(
    command_prefix="$", help_command=None, owner_id=int(os.getenv("owner_id"))
)

for file in os.listdir("bot/cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(TOKEN)
