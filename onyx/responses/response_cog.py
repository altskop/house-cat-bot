import discord
import discord.ext.commands as commands
from .response_builder import ResponseBuilder
from .poll import Poll
import random


class Slapper(commands.Converter):
    async def convert(self, ctx, argument):
        members = ctx.message.mentions
        if len(members) > 0:
            for member in members:
                argument = argument.replace(member.mention, '')
                argument = argument.strip()
            if len(argument) == 0:
                argument = "just because"
            to_slap = ", ".join([member.mention for member in members])
        else:
            member = random.choice(ctx.guild.members)
            to_slap = member.mention
        return '{0.author.mention} slapped {1} because \"*{2}*\"!'.format(ctx, to_slap, argument)


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
        if len(message.content) > 0:
            if message.content[0] == "$":
                return
        if self.response_builder.msg_fits_template("IM-SO-TIRED", message.content):
            text = self.response_builder.get_response("CLEANING-HALLWAY")
            await message.channel.send(text)

    @commands.command(name="slap")
    async def slap(self, ctx, *, response: Slapper):
        await ctx.send(response)

    @commands.command(name="poll")
    async def poll(self, ctx, *args):
        try:
            poll = Poll(ctx, *args)
            await poll.poll()
        except (IndexError, ValueError) as e:
            await ctx.send(str(e))
