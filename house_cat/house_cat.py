import discord.ext.commands as commands
from comic_generator.comic_cog import ComicGeneratorCog
from meme_generator.meme_gen_cog import MemeGeneratorCog
from responses.response_cog import ResponseCog
from games.game_cog import GameCog
from util.discord_db import DiscordDb
from util.discord_bots_api import DiscordBotsOrgAPI
import logging
import os


class HouseCatBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = 0x5297d5

        self.database = DiscordDb(host=os.environ['PG_HOST'],
                                  port=os.environ['PG_PORT'],
                                  dbname=os.environ['PG_DATABASE'],
                                  user=os.environ['PG_USER'],
                                  password=os.environ['PG_PASSWORD'])

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    @property
    def guilds(self):
        """
        Cache guilds every time we query them in the database.
        """
        guilds = super().guilds
        self.database.set_guilds(guilds)
        return guilds


logger = logging.getLogger('house-cat')
logger.setLevel(logging.DEBUG)
bot = HouseCatBot(command_prefix='$')
bot.remove_command('help')
bot.add_cog(ComicGeneratorCog(bot))
bot.add_cog(MemeGeneratorCog(bot))
bot.add_cog(ResponseCog(bot))
bot.add_cog(GameCog(bot))
bot.add_cog(DiscordBotsOrgAPI(bot))
bot.run(os.environ["ACCESS_TOKEN"])
