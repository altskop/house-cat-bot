import dbl
import discord
import os
from discord.ext import commands

import asyncio
import logging


class DiscordBotsOrgAPI(commands.Cog):
    """Handles interactions with the discordbots.org API"""
    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ['DBL_TOKEN']
        self.dblpy = dbl.Client(self.bot, self.token)
        self.updating = self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        while not self.bot.is_closed():
            logging.debug('Attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                logging.debug('Posted server count ({})'.format(self.dblpy.guild_count()))
            except Exception as e:
                logging.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)

