import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord import Member
from typing import Optional
from .game_die import GameDie
from .sessions.rock_paper_scissors import RockPaperScissorsSession
from .sessions.cards_against_humanity.cards_against_humanity import CardsAgainstHumanitySession

games = {"rock-paper-scissors": RockPaperScissorsSession,
         "rps": RockPaperScissorsSession,
         "cards-against-humanity": CardsAgainstHumanitySession,
         "cah": CardsAgainstHumanitySession}


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_sessions = []

        self.bot.application_command(name="roll", cls=discord.SlashCommand)(self.roll)

    game_commands = SlashCommandGroup("game", "Game commands")

    async def roll(self, ctx, args):
        args = args.split(" ")
        text = GameDie.roll(ctx.author.mention, args)
        embed = discord.Embed(title="",
                              description=text,
                              color=self.bot.color)
        await ctx.respond(embed=embed)

    @game_commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="",
                              description="There are 2 games available at the moment.\n"
                                          "To play Rock-Paper-Scissors, use `$game rps @PLAYER`, or `$game rock-paper-scissors @PLAYER`. "
                                          "You can mention multiple people to play with.\n"
                                          "To play Cards-Against-Humanity, use `game cah` or `game cards-against-humanity`.\n"
                                          "Use $help for more info.",
                              color=self.bot.color)
        await ctx.respond(embed=embed)

        # try:
        #     game_id = args[0]
        #     game = games[game_id](self, ctx, list(args[1:]))
        #     await game.start()
        # except KeyError:
        #     await ctx.send("No such game available.")
        # except IndexError:
        #     pass
        # except ValueError as e:
        #     await ctx.send(e)

    @game_commands.command(alias=["rock-paper-scissors"])
    async def rps(self, ctx, player_1: Option(Member, "Player", required=True),
                  player_2: Option(Member, "Player", required=False),
                  player_3: Option(Member, "Player", required=False),
                  player_4: Option(Member, "Player", required=False)
                  ):
        try:
            players = [player_1, player_2, player_3, player_4]
            players = [player for player in players if player is not None]
            if isinstance(ctx.channel, discord.DMChannel):
                return
            game = RockPaperScissorsSession(self, ctx, players, self.bot)
            await game.start()
        except ValueError as e:
            await ctx.respond(e)

    @game_commands.command()
    async def cah(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        await ctx.respond("Cards Against Humanity is temporarily unavailable.")
        return
        # game = CardsAgainstHumanitySession(self, ctx)
        # await game.start()

    # @commands.Cog.listener("on_message")
    # async def on_message(self, message):
    #     for session in self.game_sessions:
    #         await session.on_message(message)

    def subscribe(self, session):
        self.game_sessions.append(session)
        print("Session subscribed! Current list: ")
        print(self.game_sessions)

    def unsubscribe(self, session):
        self.game_sessions.remove(session)
        print("Session unsubscribed! Current list: ")
        print(self.game_sessions)

    def is_session_in_channel(self, session_type, channel):
        for session in self.game_sessions:
            if type(session) == session_type:
                if session.primary_channel == channel:
                    return True
        return False
