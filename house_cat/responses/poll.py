import random
import re
import time


class Poll:
    def __init__(self, ctx, *args):
        self.ctx = ctx
        self.title = args[0]
        self.choices = list(args[1:])
        if len(self.choices) < 2:
            raise ValueError("Too few choices")
        elif len(self.choices) > 9:
            raise ValueError("Too many choices, currently unsupported")  # TODO
        self.poll_message = None

    async def poll(self):
        await self.create_poll()
        # time.sleep(60)  # TODO do I want the bot to make the verdict on poll results?
        # await self.update_poll()

    async def create_poll(self):
        text = "**Poll!**\n {0}\n\n".format(self.title) + \
               "\n".join([str(i+1)+"️\u20E3 "+str(choice) for i, choice in enumerate(self.choices)])
        self.poll_message = await self.ctx.respond(text)
        for i in range(len(self.choices)):
            await self.poll_message.add_reaction(str(i+1)+"\u20E3")

    async def update_poll(self):
        pass
