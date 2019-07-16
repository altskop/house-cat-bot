import discord
import discord.ext.commands as commands
import os
from . import generator
import random
from util import utils


class MemeGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="meme")
    async def meme(self, ctx, *args):
        if args[0].lower() == "list":
            await self.list(ctx)
            return
        id = args[0].lower()
        text = list(args[1:])
        await self.generate_meme(ctx, id, text)

    async def list(self, ctx):
        folders = sorted(list(os.listdir("/storage/memes/templates")))
        chunks_templates = list(utils.chunks(folders, 24))
        embed = discord.Embed(title="List of all Meme Templates", description="", color=self.bot.color)
        for chunk in chunks_templates:  # TODO move this to a class (Embed wrapper?)
            for template in chunk:
                embed.add_field(name=template, value=template, inline=True)
            await ctx.send(embed=embed)
            embed = discord.Embed(title="", description="", color=self.bot.color)

    @commands.command(name="mock-text")
    async def mock_text(self, ctx, text=None):
        result = await self.text_to_mock(ctx, text)
        await ctx.send(result)

    @commands.command(name="mock")
    async def mock(self, ctx, text=None):
        result = [await self.text_to_mock(ctx, text)]
        await self.generate_meme(ctx, "mocking-spongebob", result)

    async def text_to_mock(self, ctx, text):
        if text is None:
            async for message in ctx.channel.history(limit=1, before=ctx.message):
                text = message.content
        result = ""
        chance = 0.5
        for letter in text:
            if random.random() < chance:
                result += letter.upper()
                chance = 0
            else:
                result += letter.lower()
                chance += 0.5
        return result

    async def generate_meme(self, ctx, id, text):
        try:
            gen = generator.MemeGenerator(id, text)
            image = gen.generate()
            await ctx.send(file=discord.File(image, "%s.png" % id))
        except ValueError as e:
            await ctx.send(e)
        except FileNotFoundError:
            await ctx.send("No such meme format as %s" % id)

