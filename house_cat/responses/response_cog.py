import discord
import discord.ext.commands as commands
from .response_builder import ResponseBuilder
from .poll import Poll
from .thesaurus import thesaurus
from . import magic8ball
from util import utils
from util import logger
import random


class ResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_builder = ResponseBuilder()

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if len(message.content) > 0:
            if message.content[0] == "$":
                logger.info(message, message.content)
                return
            else:
                logger.debug(message, message.content)
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

    @commands.command(name="thesaurize")
    async def thesaurize(self, ctx, *args):
        response = await thesaurus.convert(ctx)
        if len(response) > 0:
            embed = discord.Embed(title="", description=response, color=self.bot.color)
            await ctx.send(embed=embed)

    @commands.command(name="magic8ball")
    async def magic_8_ball(self, ctx, *args):
        response = magic8ball.get_response()
        embed = discord.Embed(title="", description=response['text'], color=response['color'])
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx, *args):
        if await self.bot.is_owner(ctx.author):
            guilds = list(self.bot.guilds)
            user_count = str(len(self.bot.users))
            latency = str(self.bot.latency)

            embed = discord.Embed(title="Bot stats", description="", color=self.bot.color)
            embed.add_field(name="Number of guilds:", value=str(len(guilds)), inline=False)
            embed.add_field(name="User Count:", value=user_count, inline=False)
            embed.add_field(name="Latency:", value=latency, inline=False)

            await ctx.send(embed=embed)

            guilds_chunked = utils.chunks(guilds, 24)
            embed = discord.Embed(title="Servers", description="", color=self.bot.color)
            for chunk in guilds_chunked:  # TODO move this to a class (Embed wrapper?)
                for guild in chunk:
                    value = "{0} channels, {1} users, owned by {2}".format(len(guild.text_channels), len(guild.members), guild.owner.name)
                    embed.add_field(name=guild.name, value=value, inline=True)
                await ctx.send(embed=embed)
                embed = discord.Embed(title="", description="", color=self.bot.color)

    @commands.command(name="help")
    async def help(self, ctx, *args):
        # TODO this will likely change to a simple link to a webpage when the dashboard is complete.
        embed = discord.Embed(title="",
                              description="Please visit http:/housecat.altskop.com/commands to view the list of all commands."
                              , color=self.bot.color)
        return await ctx.send(embed=embed)
