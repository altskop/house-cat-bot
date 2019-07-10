import random
import enum


class ResponseColor(enum.Enum):
    POSITIVE = 0x00ff00
    UNSURE = 0xffff00
    NEGATIVE = 0xff0000


responses = [
    ("It is certain.", ResponseColor.POSITIVE),
    ("It is decidedly so.", ResponseColor.POSITIVE),
    ("Without a doubt.", ResponseColor.POSITIVE),
    ("Yes - definitely.", ResponseColor.POSITIVE),
    ("You may rely on it.", ResponseColor.POSITIVE),
    ("As I see it, yes.", ResponseColor.POSITIVE),
    ("Most likely.", ResponseColor.POSITIVE),
    ("Outlook good.", ResponseColor.POSITIVE),
    ("Yes.", ResponseColor.POSITIVE),
    ("Signs point to yes.", ResponseColor.POSITIVE),
    ("Reply hazy, try again.", ResponseColor.UNSURE),
    ("Ask again later.", ResponseColor.UNSURE),
    ("Better not tell you now.", ResponseColor.UNSURE),
    ("Cannot predict now.", ResponseColor.UNSURE),
    ("Concentrate and ask again.", ResponseColor.UNSURE),
    ("Don't count on it.", ResponseColor.NEGATIVE),
    ("My reply is no.", ResponseColor.NEGATIVE),
    ("My sources say no.", ResponseColor.NEGATIVE),
    ("Outlook not so good.", ResponseColor.NEGATIVE),
    ("Very doubtful.", ResponseColor.NEGATIVE)
]


def get_response():
    response = random.choice(responses)
    text = ":8ball: " + response[0]
    return {"text": text, "color": response[1].value}
