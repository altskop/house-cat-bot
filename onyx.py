import discord
import response_builder as resp

config = {}


def read_config():
    with open("config", "r") as file:
        lines = [line.rstrip('\n') for line in file]
        for line in lines:
            conf = line.split("=")
            config[conf[0]] = conf[1]
    print("Configuration loaded.")
    #print(config)


class OnyxBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responseBuilder = resp.ResponseBuilder(config)

    async def on_message(self, message):
        # we do not want the bot to parse itself
        if message.author == bot.user:
            return

        print(message.content)

        if isinstance(message.channel, discord.DMChannel):
            msg = self.handle_private_message(message)
        else:
            msg = self.handle_public_message(message)
        if msg != "":
            print("Replying: "+msg)
            await message.channel.send(msg.format(message))

    def handle_public_message(self, message):

        #print(message.mentions)

        if message.content.startswith("&"):
            return self.handle_command(message)

        elif str(config.get("CREATOR_ID")) + ">" in message.content:
            return self.responseBuilder.get_response("MAX-NOTIFICATIONS")

        elif bot.user in message.mentions:

            msg = self.responseBuilder.truncate_mentions(message.content).lower()
            if len(msg) > 0:

                if self.responseBuilder.msg_fits_template("INSULT", msg):
                    return self.responseBuilder.get_response("IF-INSULTED")

            else:
                return self.responseBuilder.get_response("WHAT-YOU-WANT")

        return ""

    def handle_command(self, message):
        if message.content == "&disconnect":
            # leave voice channel
            return "Leaving channel..."
        return ""

    def handle_private_message(self, message):

        if message.content.startswith("say "):
            if message.author.voice_channel is not None:
                return "Right now I can't really talk, sorry."
            else:
                return "You're not connected to any voice channels"

        return "Sorry, Max hasn't taught me how to answer to private messages yet."

    async def on_ready(self):
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')


read_config()
bot = OnyxBot()
bot.run(config.get("ACCESS_TOKEN"))
