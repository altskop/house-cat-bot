from util import database_handler
import random


class CahDb(database_handler.DBHandler):
    def __init__(self):
        database_handler.DBHandler.__init__(self, "/storage/db/cards-against-humanity.db")
        self.seed = 0
        self.new_seed()
        self.black_index = 0
        self.white_index = 0
        self.discard_pile = []

    def initialize_db(self):
        pass

    def get_next_black(self):
        conn = self.conn
        with conn:
            c = conn.cursor()
            stmt = "select * from black_cards order by (substr(id * {0}, length(id)+2)) limit 1 offset {1};"\
                .format(self.seed, self.black_index)
            c.execute(stmt)
            self.black_index += 1
            result = c.fetchone()
            if result is None:
                self.new_seed()
                self.black_index = 0
                return self.get_next_black()
            return result

    def new_seed(self):
        self.seed = random.randrange(0, 100) + random.random()

    def get_white_cards(self, amount):
        cards = []
        cards_needed = amount - len(self.discard_pile)
        if cards_needed > 0:
            cards.extend(self.discard_pile)
            self.discard_pile = []
            cards.extend(self._get_white_cards(cards_needed))
        else:
            cards.extend(self.discard_pile[:cards_needed])
            self.discard_pile = self.discard_pile[cards_needed:]
        random.shuffle(cards)
        return cards

    def _get_white_cards(self, amount):
        conn = self.conn
        with conn:
            c = conn.cursor()
            stmt = "select * from white_cards order by (substr(id * {0}, length(id)+2)) limit {1} offset {2};". \
                format(self.seed, amount, self.white_index)
            c.execute(stmt)
            self.white_index += amount
            result = [card['text'] for card in c.fetchall()]
            if len(result) < amount:
                self.new_seed()
                self.white_index = 0
                extra_card_amount = amount - len(result)
                extra_cards = self._get_white_cards(extra_card_amount)
                result.extend(extra_cards)
            return result

    def discard(self, cards: list):
        self.discard_pile.extend(cards)

