import discord
import response_builder as resp
# import database_handler
import voice as vc


class OnyxBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}
        self.read_config()
        self.responseBuilder = resp.ResponseBuilder(self.config)
        self.voice = vc.Voice(self)

    # @event
    # What to do when we receive a message
    async def on_message(self, message):
        # we do not want the bot to parse itself
        if message.author == bot.user:
            return

        print(message.content)

        if isinstance(message.channel, discord.DMChannel):
            msg = await self.handle_private_message(message)
        else:
            msg = await self.handle_public_message(message)
        if msg != "":
            print("Replying: "+msg)
            await message.channel.send(msg.format(message))

    # If the message is in a public server
    async def handle_public_message(self, message):

        #print(message.mentions)

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

        return "Sorry, Max hasn't taught me how to answer to private messages yet."

    # @event
    async def on_voice_state_update(self, member, before, after):
        print("STATE for member "+member.display_name+" Before: "+str(before))
        print("STATE for member "+member.display_name+" After: "+str(after))

    async def on_ready(self):
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')

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


bot = OnyxBot()
bot.run(bot.config.get("ACCESS_TOKEN"))
