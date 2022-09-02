import requests
import random
import re
import asyncio
from . import common

MIN_CONFIDENCE_SCORE = 15000


async def convert(txt):
    sentence = txt
    # async for message in ctx.channel.history(limit=1, before=ctx.message):
    #     sentence = message.content.strip()
    #     if len(sentence) == 0 and len(message.embeds) > 0:
    #         sentence = message.embeds[0].description
    return await thesaurize(sentence)


async def thesaurize(sentence):
    if len(sentence) > 0:
        for word in re.findall(r'\b\w+\b', sentence):
            # word = match.group()
            if word not in common.WORDS:
                new_word = await get_synonym(word)
                sentence = sentence.replace(word, new_word, 1)
        return sentence
    else:
        return ""


async def get_synonym(word):
    url = 'https://api.datamuse.com/words?ml=%s' % word
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, requests.get, url)
    response = await future
    # response = requests.get(url)
    choices = response.json()
    try:
        if len(choices) > 0:
            word_choices = [choice['word'] for choice in choices if choice['score'] > MIN_CONFIDENCE_SCORE]
            if len(word_choices) > 0:
                return random.choice(word_choices)
    except KeyError as e:
        print(e)
    return word
