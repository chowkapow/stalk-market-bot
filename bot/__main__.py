import logging
import os
import sys

import utils

from dotenv import load_dotenv

from bot import Bot


env = "dev" if len(sys.argv) == 1 else sys.argv[1]

# Logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=env + "_discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

load_dotenv()
if env == "dev":
    TOKEN = os.getenv("dev_DISCORD_TOKEN")
elif env == "dcbc":
    TOKEN = os.getenv("dcbc_DISCORD_TOKEN")
else:
    TOKEN = os.getenv("leftovers_DISCORD_TOKEN")

bot = Bot(
    env=env, command_prefix="$", help_command=None, owner_id=int(os.getenv("owner_id"))
)

for file in os.listdir("bot/cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(TOKEN)
