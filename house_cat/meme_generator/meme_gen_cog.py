import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from . import generator
import random
from util import utils


class MemeGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    meme_gen = SlashCommandGroup("meme", "Meme generator commands")

    @meme_gen.command()
    async def help(self, ctx):
        embed = discord.Embed(title="",
                              description="Use `meme list` to list all available templates. "
                                          "After choosing a template, "
                                          "use `meme TEMPLATE_NAME \"text 1\" \"text 2\"` to generate a meme. "
                                          "Number of fields vary per template, use `meme TEMPLATE_NAME` to get "
                                          "a preview.\n"
                                          "To create your own template, visit http://housecat.altskop.com and "
                                          "use the dashboard.",
                              color=self.bot.color)
        await ctx.respond(embed=embed)
        return

    @meme_gen.command()
    async def meme(self, ctx, meme, text):
        await self.generate_meme(ctx, meme, text)

    @meme_gen.command()
    async def list(self, ctx):
        embed = discord.Embed(title="",
                              description=":ballot_box_with_check: "
                                          "Check your DMs for the list of all templates available on this server.",
                              color=self.bot.color)
        await ctx.respond(embed=embed)
        await self.global_list(ctx)
        if ctx.guild is not None:
            await self.guild_list(ctx)

    async def global_list(self, ctx):
        global_memes = self.bot.database.list_global_memes()
        chunks_templates = list(utils.chunks(global_memes, 24))
        embed = discord.Embed(title="Global Meme Templates",
                              description="These templates are available on any server that the bot is a "
                                          "part of. Use \"$meme TEMPLATE_NAME\" to preview the template.",
                              color=self.bot.color)
        for chunk in chunks_templates:  # TODO move this to a class (Embed wrapper?)
            for template in chunk:
                embed.add_field(name=template['name'], value="Fields: `"+str(len(template['metadata']['fields']))+"`", inline=True)
            await ctx.author.respond(embed=embed)
            embed = discord.Embed(title="", description="", color=self.bot.color)

    async def guild_list(self, ctx):
        guild_memes = self.bot.database.list_guild_memes(ctx.guild.id)
        chunks_templates = list(utils.chunks(guild_memes, 24))
        embed = discord.Embed(title="Meme Templates of **"+ctx.guild.name+"**",
                              description="These templates are user-created and only available at this server. "
                                          "Make your own at http://housecat.altskop.com",
                              color=self.bot.color)
        for chunk in chunks_templates:  # TODO move this to a class (Embed wrapper?)
            for template in chunk:
                embed.add_field(name=template['name'], value="by "+template['author'], inline=True)
            await ctx.author.send(embed=embed)
            embed = discord.Embed(title="", description="", color=self.bot.color)

    @meme_gen.command()
    async def mock_text(self, ctx, text):
        result = await self.text_to_mock(ctx, text)
        await ctx.respond(result)

    @meme_gen.command()
    async def mock(self, ctx, text):
        result = [await self.text_to_mock(ctx, text)]
        await self.generate_meme(ctx, "mocking-spongebob", result)

    async def text_to_mock(self, ctx, text):
        # text = ""
        # if len(args) > 0:
        #     text = " ".join(args)
        # else:
        #     async for message in ctx.channel.history(limit=1, before=ctx.message):
        #         text = message.content
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
            guild = None
            if ctx.guild is not None:
                guild = ctx.guild.id
            template = self.bot.database.get_meme_template(id, guild)
            image_blob = bytes(template['image'])
            gen = generator.MemeGenerator(image_blob, template['metadata'], text)
            image = gen.generate()
            await ctx.respond(file=discord.File(image, "%s.png" % id))
        except ValueError as e:
            print(e)
            await ctx.respond(e)
        except KeyError as e:
            print(e)
            await ctx.respond("No such meme format as %s" % id)

