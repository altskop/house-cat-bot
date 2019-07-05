import discord
import discord.ext.commands as commands
from responses import response_builder as resp
from util import database_handler
from voice import voice as vc
from meme_generator.meme_gen_cog import MemeGeneratorCog
from responses.response_cog import ResponseCog
from games.game_cog import GameCog
import asyncio
import random
import os


class OnyxBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}
        self.color = 0x5297d5
        self.read_config()
        # self.db = database_handler.DBHandler("../storage/db/discord_data.db")
        self.responseBuilder = resp.ResponseBuilder()
        self.voice = vc.Voice(self)

    # # @event
    # # What to do when we receive a message
    # async def on_message(self, message):
    #     # we do not want the bot to parse itself
    #     if message.author == bot.user:
    #         return
    #
    #     print(message.content)
    #
    #     if isinstance(message.channel, discord.DMChannel):
    #         msg = await self.handle_private_message(message)
    #     else:
    #         msg = await self.handle_public_message(message)
    #     if type(msg)==str:
    #         if msg != "":
    #             print("Replying: "+msg)
    #             await message.channel.send(msg.format(message))
    #     else:
    #         await message.channel.send(file=discord.File(msg, "meme.png"))

    # If the message is in a public server
    async def handle_public_message(self, message):

        if message.content.startswith("&"):
            return await self.handle_command(message)

        elif str(self.config.get("CREATOR_ID")) + ">" in message.content:
            return self.responseBuilder.get_response("MAX-NOTIFICATIONS")

        elif bot.user in message.mentions:

            msg = self.responseBuilder.truncate_mentions(message.content).lower()
            if len(msg) > 0:

                if self.responseBuilder.msg_fits_template("INSULT", msg):
                    return self.responseBuilder.get_response("IF-INSULTED")

            else:
                return self.responseBuilder.get_response("WHAT-YOU-WANT")

        return ""

    # If the starts with & and the message was in public server
    async def handle_command(self, message):
        if message.content == "&disconnect":
            # leave voice channel
            await self.voice.disconnect_voice_from_guild(message.guild)
        elif message.content.startswith("&meme its-retarded"):
            text = [message.content[len("&meme its-retarded"):]]
            gen = generator.MemeGenerator("its-retarded", text)
            image = gen.add_text_to_image()
            return image
        return ""

    # If the message was a DM
    async def handle_private_message(self, message):

        # Use TTS
        if message.content.startswith("say "):
            channel = self.voice.find_channel_by_user(message.author)
            if channel is not None:
                if len(message.content) <= int(self.config.get("TTS_MAX_CHARS")):
                    voice_client = await self.voice.get_voice_client_for_channel(channel)
                    await self.voice.play_tts(voice_client, message.content[3:])
                    return ""
                else:
                    return "Your message is too big."
            else:
                return "You're not connected to any voice channels"
        elif message.content.startswith("call me "):
            return self.call_me(message.author.id, message.content[8:])

        return "Sorry, Max hasn't taught me how to answer to private messages yet."

    # @event
    async def on_voice_state_update(self, member, before, after):
        if member == bot.user:
            return

        if self.voice.is_in_voice_in_guild(member.guild):
            if after.channel is not None:
                if self.voice.is_in_voice_channel(after.channel):
                    if self.db.get_boolean("guilds", "welcome_voice", "guildid", member.guild.id):
                        if not self.db.is_in_timeframe("users", "last_seen", "userid", member.id, int(self.config.get("GREETING_TIMEOUT"))):
                            name = self.db.get_value_by_key("users", "pref_name", "userid", member.id)
                            if name is None:
                                name = member.display_name
                            else:
                                name = random.choice(name.split(";"))
                            asyncio.sleep(2)
                            voice_client = await self.voice.get_voice_client_for_channel(after.channel)
                            msg = self.responseBuilder.get_response("GREETINGS") + ", " + name
                            await self.voice.play_tts(voice_client, msg)

    def call_me(self, id, text):
        self.db.get_and_update("users", "userid", id, "pref_name", text)
        return "Okay, I'll call you that from now on."

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


bot = OnyxBot(command_prefix='$')
bot.add_cog(MemeGeneratorCog(bot))
bot.add_cog(ResponseCog(bot))
bot.add_cog(GameCog(bot))
bot.run(bot.config.get("ACCESS_TOKEN"))

