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
        # Debug statements below: making sure sessions don't leak memory
        # obj = objgraph.by_type('games.sessions.rock_paper_scissors.RockPaperScissorsSession')
        # print(len(obj))
        # print(obj)

    def is_session_in_channel(self, session_type, channel):
        for session in self.game_sessions:
            if type(session) == session_type:
                if session.primary_channel == channel:
                    return True
        return False
