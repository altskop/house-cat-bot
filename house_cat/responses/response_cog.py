import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from .response_builder import ResponseBuilder
from .poll import Poll
from .thesaurus import thesaurus
from . import magic8ball
from util import logger
import random


class ResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_builder = ResponseBuilder()

        self.bot.application_command(name="poll",
                                     description="Use `poll \"Question\" \"Option 1\" \"Option 2\"` to create a poll. ",
                                     cls=discord.SlashCommand)(self.poll)
        self.bot.application_command(name="thesaurize", cls=discord.SlashCommand)(self.thesaurize)
        self.bot.application_command(name="magic8ball", cls=discord.SlashCommand)(self.magic_8_ball)
        self.bot.application_command(name="stats", cls=discord.SlashCommand)(self.stats)
        self.bot.application_command(name="help", cls=discord.SlashCommand)(self.help)

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        # if len(message.content) > 0:
        #     if message.content[0] == "$":
        #         logger.log_command(message, message.content)
        #         return
        chance_of_reaction = 0.005
        if not isinstance(message.channel, discord.DMChannel):
            if message.channel.permissions_for(message.guild.me).add_reactions:
                if random.random() < chance_of_reaction:
                    await message.add_reaction("❤")
        if message.author == self.bot.user:
            return

    async def poll(self, ctx, text):
        poll = Poll(ctx, text)
        await poll.poll()

    async def thesaurize(self, ctx, text):
        response = await thesaurus.convert(text)
        if len(response) > 0:
            embed = discord.Embed(title="", description=response, color=self.bot.color)
            await ctx.respond(embed=embed)

    async def magic_8_ball(self, ctx, question):
        response = magic8ball.get_response()
        embed = discord.Embed(title="", description=response['text'], color=response['color'])
        await ctx.respond(embed=embed)

    async def stats(self, ctx):
        if await self.bot.is_owner(ctx.author):
            guilds = list(self.bot.guilds)
            user_count = str(len(self.bot.users))
            latency = str(self.bot.latency)

            embed = discord.Embed(title="Bot stats", description="", color=self.bot.color)
            embed.add_field(name="Number of guilds:", value=str(len(guilds)), inline=False)
            embed.add_field(name="User Count:", value=user_count, inline=False)
            embed.add_field(name="Latency:", value=latency, inline=False)

            await ctx.respond(embed=embed)

    async def help(self, ctx):
        embed = discord.Embed(title="",
                              description="Please visit http://housecat.altskop.com/commands to view the list of all commands."
                              , color=self.bot.color)
        await ctx.respond(embed=embed)
