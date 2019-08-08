import discord.ext.commands as commands
from meme_generator.meme_gen_cog import MemeGeneratorCog
from responses.response_cog import ResponseCog
from games.game_cog import GameCog
from util.discord_db import DiscordDb
import logging
import os


class HouseCatBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = 0x5297d5

        self._database = DiscordDb(host=os.environ['PG_HOST'],
                                   port=os.environ['PG_PORT'],
                                   dbname='house_cat_db',
                                   user=os.environ['PG_USER'],
                                   password=os.environ['PG_PASSWORD'])

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    @property
    def database(self):
        return self._database


logger = logging.getLogger('house-cat')
logger.setLevel(logging.DEBUG)
bot = HouseCatBot(command_prefix='$')
bot.remove_command('help')
bot.add_cog(MemeGeneratorCog(bot))
bot.add_cog(ResponseCog(bot))
bot.add_cog(GameCog(bot))
bot.run(os.environ["ACCESS_TOKEN"])

