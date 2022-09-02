import random
import re


class GameDie:
    @classmethod
    def roll(cls, name, args: tuple):

        if len(args) == 0:
            count = 1
            sides = 20
        elif len(args) == 1:
            count, sides = cls.parse_dice(args[0])
        else:
            return "Sorry, combining dice is not implemented yet."  # TODO eventually if I ever need it
        rolls = []
        for i in range(count):
            rolls.append(random.randint(1, sides))
        text = '{0} rolled a :game_die: **{1}**!'.format(name, sum(rolls))
        if count > 1:
            text = text + " All rolls: " + " ".join([":game_die:{0}".format(roll) for roll in rolls])
        return text

    @staticmethod
    def parse_dice(arg):
        """ Parse strings like "2d6" or "1d20" and roll accordingly """
        pattern = re.compile(r'^(?P<count>[0-9]*d)?(?P<sides>[0-9]+)$')
        match = re.match(pattern, arg)
        if not match:
            raise ValueError()  # invalid input string

        sides = int(match.group('sides'))
        try:
            count = int(match.group('count')[:-1])
        except (TypeError, ValueError):
            count = 1

        return count, sides
