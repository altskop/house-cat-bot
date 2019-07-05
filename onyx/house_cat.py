import discord.ext.commands as commands
from responses import response_builder as resp
from voice import voice as vc
from meme_generator.meme_gen_cog import MemeGeneratorCog
from responses.response_cog import ResponseCog
from games.game_cog import GameCog
import logging


class HouseCatBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}
        self.color = 0x5297d5
        self.read_config()
        # self.db = database_handler.DBHandler("../storage/db/discord_data.db")
        self.responseBuilder = resp.ResponseBuilder()
        self.voice = vc.Voice(self)

    def read_config(self):
        with open("config.yml", "r") as file:
            lines = [line.lstrip().rstrip() for line in file]
            for line in lines:
                conf = line.split(":", 1)
                key = conf[0]
                value = conf[1].split("#", 1)
                self.config[key] = value[0].lstrip().rstrip()
        print("Configuration loaded.")
        print(self.config)

    async def on_ready(self):
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')


logger = logging.getLogger('house-cat')
logger.setLevel(logging.DEBUG)
bot = HouseCatBot(command_prefix='$')
bot.add_cog(MemeGeneratorCog(bot))
bot.add_cog(ResponseCog(bot))
bot.add_cog(GameCog(bot))
bot.run(bot.config.get("ACCESS_TOKEN"))

