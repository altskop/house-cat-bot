from util import database_handler


class CahDb(database_handler.DBHandler):
    def __init__(self, seed):
        database_handler.DBHandler.__init__(self, "/storage/db/cards-against-humanity.db")
        self.seed = seed
        self.black_index = 0
        self.white_index = 0

    def initialize_db(self):
        pass

    def get_next_black(self):
        conn = self.conn
        with conn:
            c = conn.cursor()
            stmt = "select * from black_cards order by (substr(id * {0}, length(id)+2)) limit 1 offset {1};".\
                format(self.seed, self.black_index)
            c.execute(stmt)
            self.black_index += 1
            return c.fetchone()

    def get_white_cards(self, amount):
        conn = self.conn
        with conn:
            c = conn.cursor()
            stmt = "select * from white_cards order by (substr(id * {0}, length(id)+2)) limit {1} offset {2};". \
                format(self.seed, amount, self.white_index)
            c.execute(stmt)
            self.white_index += amount
            result = c.fetchall()
            return [card['text'] for card in result]
