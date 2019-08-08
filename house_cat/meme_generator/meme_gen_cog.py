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
        embed = discord.Embed(title="",
                              description=":white_check_mark: Check your DMs for the list of all templates available on this server.",
                              color=self.bot.color)
        await ctx.send(embed=embed)
        await self.global_list(ctx)
        await self.guild_list(ctx)

    async def global_list(self, ctx):
        global_memes = self.bot.database.list_global_memes()
        chunks_templates = list(utils.chunks(global_memes, 24))
        embed = discord.Embed(title="Global Meme Templates", description="", color=self.bot.color)
        for chunk in chunks_templates:  # TODO move this to a class (Embed wrapper?)
            for template in chunk:
                embed.add_field(name=template['name'], value="Fields: `"+str(len(template['metadata']['fields']))+"`", inline=True)
            await ctx.author.send(embed=embed)
            embed = discord.Embed(title="", description="", color=self.bot.color)

    async def guild_list(self, ctx):
        guild_memes = self.bot.database.list_guild_memes(ctx.guild.id)
        chunks_templates = list(utils.chunks(guild_memes, 24))
        embed = discord.Embed(title="Meme Templates of **"+ctx.guild.name+"**", description="", color=self.bot.color)
        for chunk in chunks_templates:  # TODO move this to a class (Embed wrapper?)
            for template in chunk:
                embed.add_field(name=template['name'], value="by "+template['author'], inline=True)
            await ctx.author.send(embed=embed)
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
            guild = ctx.guild.id
            template = self.bot.database.get_meme_template(id, guild)
            image_blob = bytes(template['image'])
            gen = generator.MemeGenerator(image_blob, template['metadata'], text)
            image = gen.generate()
            await ctx.send(file=discord.File(image, "%s.png" % id))
        except ValueError as e:
            print(e)
            await ctx.send(e)
        except KeyError as e:
            print(e)
            await ctx.send("No such meme format as %s" % id)

