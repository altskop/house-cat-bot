from ..session import Session
import discord
import random
from .cah_db import CahDb

MAX_WHITE_CARDS = 10
MAX_PLAYERS = 10
MAX_BLANK_CARD_LENGTH = 140  # Characters
CARD_CZAR_EMOJI = ":crown:"
LOCK_EMOJI = ":lock:"
UNLOCK_EMOJI = ":unlock:"


class CardsAgainstHumanitySession(Session):
    def __init__(self, cog, ctx, args):
        Session.__init__(self, cog, ctx, args, life_time=600, one_per_channel=True)
        self.players = {}
        self.session_seed = random.randrange(0, 100) + random.random()
        self.round = 0
        self.host = self.ctx.message.author
        self.dealer = CahDb(self.session_seed)
        self.black_card = None  # Current black card in play
        self.can_be_joined = True
        self.point_limit = None
        self.czar = None
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
        # The player has already made their turn but may still gamble
        if message.content == "gamble":
            if player != self.czar and len(self.round_players) > 0:
                if self.players[player]['points'] > 0:
                    self.round_players.append(player)
                    self.players[player]['points'] -= 1
                    self.round_points += 1
                    await player.send("You can now play up to two cards (or combinations) this round!")
                else:
                    await player.send("You don't have enough Awesome Points to gamble! Go earn some first.")
        elif player in self.round_players:
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
                    await self._end_round()
            except (ValueError, IndexError):
                await message.author.send("Invalid input, please try again.")
        elif player == self.czar:
            await message.author.send("You're the Card Czar! You can't both play and judge in the same round. That'd be too easy :)")

    async def on_public_message(self, message):
        if message.content == "cah leave":
            if message.author in self.players:
                await self._remove_player(message.author)
                return

        if message.author == self.host:
            if message.content == "cah start":
                if len(self.players.keys()) > 2:
                    await self.primary_channel.send("Let the games begin!")
                    await self._game_round()
                else:
                    await self.primary_channel.send("Not enough players to start.")

            elif message.content == "cah end":
                text = "{0} ends the game. Final Scores:\n".format(self.host.mention)
                text += self._list_players()
                await self.primary_channel.send(text)
                self.stop()

            elif message.content.startswith("cah kick "):
                if len(message.mentions) > 0:
                    player_to_kick = message.mentions[0]
                    await self._remove_player(player_to_kick, kick=True)

            elif message.content.startswith("cah lock"):
                if self.can_be_joined:
                    self.can_be_joined = False
                    await self.primary_channel.send("{0} The game has been locked, nobody else can join.".format(LOCK_EMOJI))

            elif message.content.startswith("cah unlock"):
                if not self.can_be_joined:
                    self.can_be_joined = True
                    await self.primary_channel.send("{0} The game has been unlocked! Quick,"
                                                    " join before it's too late!".format(UNLOCK_EMOJI))

            elif message.content.startswith("cah limit "):
                try:
                    number = int(message.content.replace("cah limit ", ""))
                    if number <= self._current_leader()['points']:
                        await self.primary_channel.send("Point limit can't be less or equal to the current highscore.")
                    else:
                        self.point_limit = number
                        await self.primary_channel.send("New points limit is {0}!".format(number))
                except ValueError:
                    await self.primary_channel.send("Invalid input, please try again")

            elif message.content.startswith("cah host "):
                if len(message.mentions) == 1:
                    new_host = message.mentions[0]
                    if new_host in self.players:
                        if new_host != self.host:
                            self.host = new_host
                            await self.primary_channel.send("{0} is the new game host!".format(new_host.mention))
                    else:
                        await self.primary_channel.send("{0} is not in the game.".format(new_host.mention))

        elif message.author == self.czar:
            if len(self.round_players) == 0:
                try:
                    winning_card = self.played_cards[int(message.content)]
                    await self._round_results(winning_card)
                except ValueError:
                    pass
                except IndexError:
                    await self.primary_channel.send("Invalid input, please try again")

        else:
            if message.content == "cah join":
                if message.author not in self.players.keys():
                    if self.can_be_joined:
                        if len(self.players.keys()) < MAX_PLAYERS:
                            self._add_player(message.author)
                            text = "{0} joins!\n".format(message.author.mention)
                            text += self._list_players()
                            await self.primary_channel.send(text)
                        else:
                            await self.primary_channel.send("There are already too many players in the game.")
                    else:
                        await self.primary_channel.send("This game is locked.")

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
            elif message.author == self.czar:
                try:
                    int(message.content)
                    return True
                except ValueError:
                    return False
        return False

    # ------------------------------------------------------------
    # Own methods here
    # ------------------------------------------------------------

    async def _announce(self):
        text = "{0} is hosting a Cards Against Humanity game!\n" \
               "To join, type \"cah join\" in the channel.\n" \
               "```" \
               "Play cards by responding to the bot in DMs! " \
               "If you'd like to play two cards or combinations of cards in the same round, they can gamble by"\
               "betting 1 Awesome Point! To do so, send \"gamble\" to the bot in DM when it's your turn to play" \
               " a card.\n" \
               "If someone wants to leave during the game, they can do so by typing \"cah leave\".\n\n" \
               "Host commands:\nWhen ready, the host can start the game by typing \"cah start\".\n" \
               "The host may end the game at any time by typing \"cah end\", " \
               "and kick players using \"cah kick @PLAYER\"." \
               "The host may also transfer the host priviliges by typing \"cah host @PLAYER\".\n" \
               "The host may also lock the game so that nobody else can join it by typing \"cah lock\". Similarly," \
               "they can type \"cah unlock\" to reopen it again.\n" \
               "Type in \"cah limit 5\" or any other number to end the game when somebody reaches the limit." \
               "```\n" \
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
        await self._next_czar()
        self._get_players_for_round()
        text = "**Round {0}!**\n".format(self.round)
        text += "{0} is the Card Czar {1}! " \
                "They can choose the winning card by typing in its number when the round is over.\n".format(self.czar.mention, CARD_CZAR_EMOJI)
        text += "```{0}```".format(self.black_card['text'])
        await self.primary_channel.send(text)

    async def _end_round(self):
        if len(self.round_players) == 0:
            random.shuffle(self.played_cards)
            text = "The cards were played! Card Czar {0}{1}, choose the best one!\n".format(self.czar.mention, CARD_CZAR_EMOJI)
            text += "```{0}```\n".format(self.black_card['text'])
            text += "White cards:\n"
            for i, card in enumerate(self.played_cards):
                card_text = "\"" + "\" | \"".join(card['cards']) + "\""
                text += "`{0}. {1}`\n".format(i, card_text)
            await self.primary_channel.send(text)

    async def _end_game(self):
        text = "**{0} wins the game!**".format(self._current_leader()['player'].mention)
        await self.primary_channel.send(text)
        self.stop()

    async def _round_results(self, winning_card):
        winner = winning_card['player']
        self.players[winner]['points'] += self.round_points
        text = "**{0} wins the round and gets {1} Awesome Points!**\n".format(winner.mention, self.round_points)
        text += self._list_players()
        await self.primary_channel.send(text)
        if self.point_limit is not None:
            if self._current_leader()['points'] >= self.point_limit:
                await self._end_game()
                return
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
        # for player, value in self.players.items():
        #     if len(value['cards']) < 2:
        #         text = "No more white cards remaining. Game over!\n"
        #         text += self._list_players()
        #         await self.primary_channel.send(text)
        #         return
        await self._display_cards()

    async def _next_czar(self):
        if self.czar is None:
            index = random.randrange(0, len(self.players.keys()) - 1)
        else:
            index = list(self.players.keys()).index(self.czar) + 1
            if index == len(self.players.keys()):
                index = 0
        self.czar = list(self.players.keys())[index]
        await self.czar.send("You're the Card Czar {0}!".format(CARD_CZAR_EMOJI))

    def _get_players_for_round(self):
        players = list(self.players.keys())
        players.remove(self.czar)
        self.round_players = players

    async def _remove_player(self, player, kick=False):
        if player in self.players:
            self.dealer.discard(self.players[player]['cards'])
            self.players.pop(player)
            if kick:
                text = "{0} kicks {1}.\n".format(self.host.mention, player.mention)
            else:
                text = "{0} leaves the game.\n".format(player.mention)
            if len(self.players.keys()) > 0:
                if player == self.host:
                    if len(self.players.keys()) > 0:
                        self.host = random.choice(list(self.players.keys()))
                        text += "{0} is the new host!\n".format(self.host.mention)
                text += self._list_players()
            else:
                self.stop()
            await self.primary_channel.send(text)
            if len(self.played_cards) > 0:
                await self._end_round()

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
                        card_text = "\"" + "\" | \"".join(played_card['cards']) + "\""
                        await player.send("You played {0}".format(card_text))
                        self.round_players.remove(player)
                    else:
                        await player.send("You played {0}".format(card))
                    return
        # new played card for the player
        self.played_cards.append({"player": player, "cards": []})
        await self._play_card(player, card)

    def _current_leader(self):
        leader = {"player": None, "points": 0}
        for player, values in self.players.items():
            if values['points'] > leader['points']:
                leader['points'] = values['points']
                leader['player'] = player
        return leader
