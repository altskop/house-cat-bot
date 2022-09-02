from .session import Session
from aenum import MultiValueEnum
from enum import Enum
from typing import Optional
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
    rock = ":white_medium_square:"
    paper = ":page_facing_up:"
    scissors = ":scissors:"


class RockPaperScissorsView(discord.ui.View):
    def __init__(self, player, callback, *items, timeout: Optional[float] = 180.0, disable_on_timeout: bool = False):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.player = player
        self.callback = callback

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        new_text = self.message.content + "\n\nUnfortunately, you did not respond in time."
        await self.message.edit(content=new_text, view=self)

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.secondary,
                       emoji="🪨")
    async def rock_callback(self, button, interaction):
        for child in self.children:  # loop through all the children of the view
            child.disabled = True  # set the button to disabled
        new_text = self.message.content + "\n\nYou played 🪨!"
        await interaction.response.edit_message(content=new_text, view=self)
        await self.callback(self.player, Choice.rock)

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.secondary,
                       emoji="📄")
    async def paper_callback(self, button, interaction):
        for child in self.children:  # loop through all the children of the view
            child.disabled = True  # set the button to disabled
        new_text = self.message.content + "\n\nYou played 📄!"
        await interaction.response.edit_message(content=new_text, view=self)
        await self.callback(self.player, Choice.paper)

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.secondary,
                       emoji="✂")
    async def scissors_callback(self, button, interaction):
        for child in self.children:  # loop through all the children of the view
            child.disabled = True  # set the button to disabled
        new_text = self.message.content + "\n\nYou played ✂!"
        await interaction.response.edit_message(content=new_text, view=self)
        await self.callback(self.player, Choice.scissors)


class RockPaperScissorsSession(Session):
    def __init__(self, cog, ctx, args, bot):
        Session.__init__(self, cog, ctx, args, life_time=120)
        self.players = []
        self.player_choices = {}
        self.bot = bot
        self.interaction = None
        self.original_message = ""

    async def create(self):
        if len(self.args) == 0:
            raise ValueError("No players specified.")
        for user in self.args:
            if user.bot:
                raise ValueError("Contender can't be a bot.")
        if self.ctx.author in self.args:
            raise ValueError("You can't challenge yourself.")

        self.players.append(self.ctx.author)
        for player in self.args:
            if player not in self.players:
                self.players.append(player)
        await self._issue_challenge()

    async def _issue_challenge(self):
        challenge_text = "{0} challenges {1} to a game of Rock-Paper-Scissors!\n" \
                         "Contenders, please check your DMs to make your move." \
            .format(self.ctx.author.mention,
                    ", ".join([player.mention for player in self.players if player != self.ctx.author]))
        self.original_message = challenge_text
        embed = discord.Embed(title="",
                              description=challenge_text,
                              color=self.bot.color)
        await self.ctx.respond(embed=embed)

        instruction_text = "{0} challenges you to a game of Rock-Paper-Scissors in **{1}** server, **{2}** channel!\n" \
                                "Select your move!" \
                                .format(self.ctx.author.mention, self.ctx.guild.name,
                                        self.ctx.channel.name)
        for player in self.players:
            try:
                view = RockPaperScissorsView(player=player, callback=self.on_react, timeout=120)
                await player.send(instruction_text, view=view)
            except (discord.HTTPException, discord.Forbidden):
                raise ValueError("Couldn't send a DM to {0}.".format(player.mention))

    async def on_react(self, player, choice: Choice):
        if self.player_choices.get(choice) is None:
            self.player_choices[choice] = []
        self.player_choices[choice].append(player)
        self.players.remove(player)
        if len(self.players) == 0:
            await self._announce_victor()


    async def on_private_message(self, message):
        pass
    # async def on_private_message(self, message):
    #     try:
    #         choice = Choice(message.content.lower())
    #         if self.player_choices.get(choice) is None:
    #             self.player_choices[choice] = []
    #         self.player_choices[choice].append(message.author)
    #         await message.channel.send("You played {0}".format(choice.value))
    #         # After the player made their move, remove them from listening
    #         self.players.remove(message.author)
    #         if len(self.players) == 0:
    #             await self._announce_victor()
    #     except KeyError as e:
    #         print(e)
    #         await message.author.send("Invalid input, please try again.")

    async def _announce_victor(self):
        text = self._list_player_choices()
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
            text += "\n**🏆 {0} {1} the game!**".format(victors_str, verb)
        else:
            # it's a Tie
            text += "\n**🤝 It's a tie!**"

        new_text = self.original_message + "\n\n" + text
        embed = discord.Embed(title="",
                              description=new_text,
                              color=self.bot.color)
        await self.ctx.edit(embed=embed)
        self.stop()

    def is_private_message_expected(self, message):
        if message.author in self.players:
            return True
        return False

    def is_public_message_expected(self, message):
        return False

    async def on_expiration(self):
        text = self._list_player_choices()
        for player in self.players:
            text += "> {0} has not responded in due time.\n".format(player.mention)
        await self.primary_channel.send(text)

    async def on_public_message(self, message):
        pass

    def _list_player_choices(self) -> str:
        text = ""
        for choice, player_list in self.player_choices.items():
            for player in player_list:
                text += "> {0} plays {1}{2}!\n".format(player.mention, choice.value, RPSEmoji[choice.value].value)
        return text
