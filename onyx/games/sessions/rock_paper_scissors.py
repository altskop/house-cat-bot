from .session import Session
from aenum import MultiValueEnum
from enum import Enum
import discord


class Choice(MultiValueEnum):
    rock = "rock", "1"
    paper = "paper", "2"
    scissors = "scissors", "3"


beats = {
    Choice.scissors: Choice.rock,
    Choice.rock: Choice.paper,
    Choice.paper: Choice.scissors,
}


class RPSEmoji(Enum):
    rock = ":large_blue_diamond:"
    paper = ":page_facing_up:"
    scissors = ":scissors:"


class RockPaperScissorsSession(Session):
    def __init__(self, cog, ctx, *args):
        Session.__init__(self, cog, ctx, args)
        self.players = []
        self.player_choices = {}

    async def create(self):
        if len(self.ctx.message.mentions) == 0:
            raise ValueError("No players specified.")
        for user in self.ctx.message.mentions:
            if user.bot:
                raise ValueError("Contender can't be a bot.")
        if self.ctx.message.author in self.ctx.message.mentions:
            raise ValueError("You can't challenge yourself.")

        self.players.append(self.ctx.message.author)
        self.players.extend(self.ctx.message.mentions)
        await self._issue_challenge()

    async def _issue_challenge(self):
        challenge_text = "{0} challenges {1} to a game of Rock-Paper-Scissors! " \
                         "Contenders, please check your DMs to make your move." \
            .format(self.ctx.message.author.mention, ", ".join([member.mention for member in self.ctx.message.mentions]))
        await self.ctx.send(challenge_text)
        instruction_text = "To make your move in Rock Paper Scissors game, " \
                           "reply with a number of your choice or its value " \
                           "(for example, your reply could be either \"1\" or \"Rock\" to play a Rock):\n" \
                           "1. Rock {0}\n" \
                           "2. Paper {1} \n" \
                           "3. Scissors {2}".format(RPSEmoji.rock.value, RPSEmoji.paper.value, RPSEmoji.scissors.value)
        for player in self.players:
            try:
                await player.send(instruction_text)
            except (discord.HTTPException, discord.Forbidden):
                raise ValueError("Couldn't send a DM to {0}.".format(player.mention))

    async def on_private_message(self, message):
        if message.author in self.players:
            try:
                choice = Choice(message.content.lower())
                if self.player_choices.get(choice) is None:
                    self.player_choices[choice] = []
                self.player_choices[choice].append(message.author)
                # After the player made their move, remove them from listening
                self.players.remove(message.author)
                await message.channel.send("You played {0}".format(choice.value))
                if len(self.players) == 0:
                    await self._announce_victor()
            except KeyError as e:
                print(e)
                await message.author.send("Invalid input, please try again.")

    async def _announce_victor(self):
        text = ""
        for choice, player_list in self.player_choices.items():
            for player in player_list:
                text += "{0} plays {1}{2}!\n".format(player.mention, choice.value, RPSEmoji[choice.value].value)
        choice_list = list(self.player_choices.keys())
        if len(choice_list) == 2:
            # Can define a victor
            if choice_list[0] == beats[choice_list[1]]:
                victors = self.player_choices[choice_list[0]]
            else:
                victors = self.player_choices[choice_list[1]]
            victors_str = ", ".join([victor.mention for victor in victors])
            if len(victors) == 1:
                verb = "wins"
            else:
                verb = "win"
            text += "**{0} {1} the game!**".format(victors_str, verb)
        else:
            # it's a Tie
            text += "**It's a tie!**"
        await self.ctx.send(text)
        self.stop()

    async def on_public_message(self, message):
        pass
