import discord
import discord.ext.commands as commands
from .game_die import GameDie
from .response_builder import ResponseBuilder
import random


class ResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_builder = ResponseBuilder()

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        chance_of_reaction = 0.02
        if random.random() < chance_of_reaction:
            await message.add_reaction("❤")
        if message.author == self.bot.user:
            return
        if self.response_builder.msg_fits_template("IM-SO-TIRED", message.content):
            text = self.response_builder.get_response("CLEANING-HALLWAY")
            await message.channel.send(text)

    @commands.command(name="roll")
    async def roll(self, ctx, *args):
        text = GameDie.roll(ctx.message.author.mention, args)
        await ctx.send(text)
