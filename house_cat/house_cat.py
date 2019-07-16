import discord.ext.commands as commands
from meme_generator.meme_gen_cog import MemeGeneratorCog
from responses.response_cog import ResponseCog
from games.game_cog import GameCog
import logging
import os


class HouseCatBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = 0x5297d5

    async def on_ready(self):
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')


logger = logging.getLogger('house-cat')
logger.setLevel(logging.DEBUG)
bot = HouseCatBot(command_prefix='$')
bot.remove_command('help')
bot.add_cog(MemeGeneratorCog(bot))
bot.add_cog(ResponseCog(bot))
bot.add_cog(GameCog(bot))
bot.run(os.environ["ACCESS_TOKEN"])

