import discord
import discord.ext.commands as commands
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

    @commands.command(name="roll")
    async def roll(self, ctx, *args):
        text = GameDie.roll(ctx.message.author.mention, args)
        await ctx.send(text)

    @commands.command(name="game")
    async def game(self, ctx, *args):
        if len(args) == 0:
            embed = discord.Embed(title="",
                                  description="There are 2 games available at the moment.\n"
                                              "To play Rock-Paper-Scissors, use `$game rps @PLAYER`, or `$game rock-paper-scissors @PLAYER`. "
                                              "You can mention multiple people to play with.\n"
                                              "To play Cards-Against-Humanity, use `game cah` or `game cards-against-humanity`.\n"
                                              "Use $help for more info.",
                                  color=self.bot.color)
            await ctx.send(embed=embed)
            return

        if isinstance(ctx.channel, discord.DMChannel):
            return

        try:
            game_id = args[0]
            game = games[game_id](self, ctx, list(args[1:]))
            await game.start()
        except KeyError:
            await ctx.send("No such game available.")
        except IndexError:
            pass
        except ValueError as e:
            await ctx.send(e)

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        for session in self.game_sessions:
            await session.on_message(message)

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
