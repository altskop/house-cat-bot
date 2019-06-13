from ..session import Session
import discord
import random
from .cah_db import CahDb

MAX_WHITE_CARDS = 10
MAX_PLAYERS = 10
MAX_BLANK_CARD_LENGTH = 140  # Characters


class CardsAgainstHumanitySession(Session):
    def __init__(self, cog, ctx, args):
        Session.__init__(self, cog, ctx, args, life_time=600, one_per_channel=True)
        self.players = {}
        self.session_seed = random.randrange(0, 100) + random.random()
        self.round = 0
        self.host = self.ctx.message.author
        self.dealer = CahDb(self.session_seed)
        self.black_card = None  # Current black card in play
        self.czar_index = None
        self.played_cards = []
        self.round_players = []
        self.round_blank_players = []  # Players that are playing blank cards
        self.round_points = 1  # 1 by default, but can be increased if somebody decides to gamble

    # ------------------------------------------------------------
    # Implementing Session methods here
    # ------------------------------------------------------------

    async def create(self):
        self._add_player(self.host)
        await self._announce()

    async def on_private_message(self, message):
        player = message.author
        if player in self.round_players:
            # This player is expected to make a turn
            try:
                if player in self.round_blank_players:
                    if 0 < len(message.content) < MAX_BLANK_CARD_LENGTH:
                        self.round_blank_players.remove(player)
                        card = message.content
                    else:
                        await player.send("Message too long, limit is {0} characters".format(MAX_BLANK_CARD_LENGTH))
                        return
                else:
                    card = self.players[player]['cards'].pop(int(message.content))
                await self._play_card(player, card)
                if player in self.round_players:
                    if player not in self.round_blank_players:
                        await self._show_cards_to_player(player)
                else:
                    if len(self.round_players) == 0:
                        await self._end_round()
                    await player.send("You played card \"{0}\"".format(message.content))
            except (ValueError, IndexError):
                await message.author.send("Invalid input, please try again.")
        else:
            # The player has already made their turn but may still gamble
            if message.content == "gamble":
                if player != self.card_czar and len(self.round_players) > 0:
                    if self.players[player]['points'] > 0:
                        self.round_players.append(player)
                        self.players[player]['points'] -= 1
                        await player.send("You get to choose card(s) again!")

    async def on_public_message(self, message):
        if message.content == "cah join":
            if message.author not in self.players.keys():
                if len(self.players.keys()) < MAX_PLAYERS:
                    self._add_player(message.author)
                    text = "{0} joins!\n".format(message.author.mention)
                    text += self._list_players()
                    await self.primary_channel.send(text)
                else:
                    await self.primary_channel.send("There are already too many players in the game.")
        elif message.content == "cah start":
            if message.author == self.host:
                if len(self.players.keys()) > 2:
                    await self.primary_channel.send("Let the games begin!")
                    await self._game_round()
                else:
                    await self.primary_channel.send("Not enough players to start.")

        elif message.content == "cah leave":
            if message.author in self.players:
                self.players.pop(message.author)
                text = "{0} leaves the game.\n".format(message.author.mention)
                if len(self.players.keys()) > 0:
                    if message.author == self.host:
                        if len(self.players.keys()) > 0:
                            self.host = random.choice(self.players.keys())
                            text += "{0} is the new host!\n".format(self.host.mention)
                    text += self._list_players()
                else:
                    self.stop()
                await self.primary_channel.send(text)

        elif message.content == "cah end":
            text = "{0} ends the game. Final Scores:\n"
            text += self._list_players()
            await self.primary_channel.send(text)
            self.stop()

        elif message.content.startswith("cah kick "):
            if len(message.mentions) > 0 and message.author == self.host:
                player_to_kick = message.mentions[0]
                if player_to_kick in self.players:
                    self.players.pop(player_to_kick)
                    text = "{0} kicks {1}.\n".format(message.author.mention, player_to_kick.mention)
                    text += self._list_players()
                    await self.primary_channel.send(text)

        elif message.content.startswith("cah host "):
            if len(message.mentions) == 1 and message.author == self.host:
                new_host = message.mentions[0]
                if new_host in self.players:
                    if new_host != self.host:
                        self.host = new_host
                        await self.primary_channel.send("{0} is the new game host!".format(new_host.mention))
                else:
                    await self.primary_channel.send("{0} is not in the game.".format(new_host.mention))

        elif message.author == self.card_czar:
            if len(self.round_players) == 0:
                try:
                    winning_card = self.played_cards[int(message.content)]
                    await self._round_results(winning_card)
                except (ValueError, IndexError):
                    await self.primary_channel.send("Invalid input, please try again")

    async def on_expiration(self):
        text = "CAH session has expired due to inactivity :(\n\nFinal Scores:\n"
        text += self._list_players()
        await self.primary_channel.send(text)

    def is_private_message_expected(self, message):
        if message.author in self.players.keys():
            return True
        return False

    def is_public_message_expected(self, message):
        if message.channel == self.primary_channel:
            if message.content.startswith("cah "):
                return True
            elif message.author == self.card_czar:
                return True
        return False

    # ------------------------------------------------------------
    # Own methods here
    # ------------------------------------------------------------

    async def _announce(self):
        text = "{0} is hosting a Cards Against Humanity game!\n" \
               "To join, type \"cah join\" in the channel.\n" \
               "```When ready, the host can start the game by typing \"cah start\".\n" \
               "If someone wants to leave during the game, they can do so by typing \"cah leave\".\n" \
               "The host may end the game at any time by typing \"cah end\", " \
               "and kick players using \"cah kick @PLAYER\"." \
               "The host may also transfer the host priviliges by typing \"cah host @PLAYER\".```\n" \
               "You will need at least 3 players in order to play.".format(self.host.mention)
        await self.primary_channel.send(text)

    def _add_player(self, user):
        if self.players.get(user) is None:
            self.players[user] = {"cards": [], "points": 0}

    def _list_players(self):
        text = ""
        for player, values in self.players.items():
            text += "> {0} - {1} Awesome Points\n".format(player.mention, values['points'])
        return text

    async def _game_round(self):
        await self._deal_cards()
        self.played_cards = []
        self.round_points = 1
        self.round += 1
        self.black_card = self.dealer.get_next_black()
        self._next_czar()
        self._get_players_for_round()
        text = "**Round {0}!**\n".format(self.round)
        text += "{0} is the Card Czar! " \
                "They can choose the winning card by typing in its number when the round is over.\n".format(self.card_czar.mention)
        text += "```{0}```".format(self.black_card['text'])
        await self.primary_channel.send(text)

    async def _end_round(self):
        random.shuffle(self.played_cards)
        text = "The choices are made!\n"
        text += "```{0}```\n".format(self.black_card['text'])
        text += "White cards:\n"
        for i, card in enumerate(self.played_cards):
            card_text = "\"" + "\" | \"".join(card['cards']) + "\""
            text += "`{0}. {1}`\n".format(i, card_text)
        await self.primary_channel.send(text)

    async def _round_results(self, winning_card):
        winner = winning_card['player']
        self.players[winner]['points'] += self.round_points
        text = "**{0} wins the round and gets {1} Awesome Points!**\n".format(winner.mention, self.round_points)
        text += self._list_players()
        await self.primary_channel.send(text)
        await self._game_round()

    async def _display_cards(self):
        for player in self.players.keys():
            await self._show_cards_to_player(player)

    async def _show_cards_to_player(self, player):
        cards = self.players[player]['cards']
        text = "Your cards:\n```"
        for i, card in enumerate(cards):
            text += "{0}. {1}\n".format(i, card)
        text += "```\nSend the number of the card to play it."
        await player.send(text)

    async def _deal_cards(self):
        white_cards = 0
        for player, value in self.players.items():
            white_cards += MAX_WHITE_CARDS - len(value['cards'])
        cards = self.dealer.get_white_cards(white_cards)
        print("Got {0} cards from dealer".format(len(cards)))
        offset = 0
        for player, value in self.players.items():
            need_cards = MAX_WHITE_CARDS - len(value['cards'])
            value['cards'].extend(cards[offset:offset+need_cards])
            offset += need_cards
        await self._display_cards()

    def _next_czar(self):
        if self.czar_index is None:
            index = random.randrange(0, len(self.players.keys()) - 1)
        else:
            index = self.czar_index + 1
            if index == len(self.players.keys()):
                index = 0
        self.czar_index = index

    @property
    def card_czar(self):
        if self.czar_index is not None:
            return list(self.players.keys())[self.czar_index]
        return None

    def _get_players_for_round(self):
        players = list(self.players.keys())
        players.remove(self.card_czar)
        self.round_players = players

    async def _play_card(self, player, card):
        if card == "<BLANK>":
            self.round_blank_players.append(player)
            await player.send("Type in the card text. It can not be longer than {0} characters.".format(MAX_BLANK_CARD_LENGTH))
            return
        for played_card in self.played_cards:
            if played_card['player'] == player:
                if len(played_card['cards']) < self.black_card['pick']:
                    played_card['cards'].append(card)
                    if len(played_card['cards']) == self.black_card['pick']:
                        self.round_players.remove(player)
                    return
        # new played card for the player
        self.played_cards.append({"player": player, "cards": []})
        await self._play_card(player, card)
