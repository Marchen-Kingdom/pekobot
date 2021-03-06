# pylint: skip-file
import asyncio
import logging
import os
import sqlite3

import aiohttp
import brotli

from pekobot.bot import Pekobot
from pekobot.utils import config

# Setup logging
logger = logging.getLogger('pekobot')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename='pekobot.log',
                                   encoding='utf-8',
                                   mode='w')
formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}',
                              '%Y-%m-%d %H:%M:%S',
                              style='{')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

conf = config.load_config()


async def run():
    # Download redive_jp.db from https://redive.estertion.win/ if it doesn't exist
    if not os.path.exists("redive_jp.db"):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://redive.estertion.win/db/redive_jp.db.br") as resp:
                brotli_result = await resp.read()
                data = brotli.decompress(brotli_result)
                with open("redive_jp.db", "wb") as f:
                    f.write(data)

    pcr_db = sqlite3.connect("redive_jp.db")
    bot = Pekobot(command_prefix=("!", "！"), pcr_db=pcr_db)
    for cog in conf["cogs"]:
        bot.load_extension(f"pekobot.cogs.{cog}")
        logger.info("%s has been loaded.", cog)

    @bot.event
    async def on_ready():
        logger.info('%s has connected to Discord!', bot.user)

    try:
        await bot.start(conf['discord_token'])
    except KeyboardInterrupt:
        pcr_db.close()
        await bot.logout()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
