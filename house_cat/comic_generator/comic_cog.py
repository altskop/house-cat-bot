import discord
import discord.ext.commands as commands
from .comic_generator import ComicGenerator


class ComicGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="comic")
    async def comic(self, ctx, amount: int = 3):
        try:
            if amount < 1 or amount > 6:
                raise ValueError("Currently only accepting values from 1 to 6.")
            guild = None
            if ctx.guild is not None:
                guild = ctx.guild.id
            panels = self.bot.database.get_random_comics(amount, "cyanide", guild)
            image = ComicGenerator(panels).generate()
            await ctx.send(file=discord.File(image, "comic.png"))
        except ValueError as e:
            print(e)
            await ctx.send(e)
        except KeyError as e:
            print(e)
            await ctx.send("No such meme format as %s" % id)
