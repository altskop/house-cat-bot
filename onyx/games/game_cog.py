import discord
import discord.ext.commands as commands
from .game_die import GameDie
from .sessions.rock_paper_scissors import RockPaperScissorsSession
import gc

games = {"rock-paper-scissors": RockPaperScissorsSession,
         "rps": RockPaperScissorsSession}


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
            game = games[game_id](self, ctx, *args[1:])
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
        # gc.collect()
        # refs = gc.get_referrers(session)
        # print(refs)
