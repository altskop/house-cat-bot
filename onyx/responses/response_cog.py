import discord
import discord.ext.commands as commands
from .response_builder import ResponseBuilder
from .poll import Poll
from .thesaurus import thesaurus
from . import magic8ball
import random


class ResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_builder = ResponseBuilder()

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if len(message.content) > 0:
            if message.content[0] == "$":
                return
        chance_of_reaction = 0.006
        if random.random() < chance_of_reaction:
            await message.add_reaction("❤")
        if message.author == self.bot.user:
            return
        # if self.response_builder.msg_fits_template("IM-SO-TIRED", message.content):
        #     text = self.response_builder.get_response("CLEANING-HALLWAY")
        #     await message.channel.send(text)

    @commands.command(name="poll")
    async def poll(self, ctx, *args):
        try:
            poll = Poll(ctx, *args)
            await poll.poll()
        except (IndexError, ValueError) as e:
            await ctx.send(str(e))

    @commands.command(name="thesaurizethis")
    async def thesaurize(self, ctx, *args):
        response = await thesaurus.convert(ctx)
        if len(response) > 0:
            embed = discord.Embed(title="", description=response, color=self.bot.color)
            await ctx.send(embed=embed)

    @commands.command(name="magic8ball")
    async def thesaurize(self, ctx, *args):
        response = magic8ball.get_response()
        embed = discord.Embed(title="", description=response['text'], color=response['color'])
        await ctx.send(embed=embed)
