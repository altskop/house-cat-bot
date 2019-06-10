from abc import ABC, abstractmethod
import discord


class Session(ABC):
    """
        A base abstract class for all game sessions.
        Implementations of this class MUST implement their
        own on_private_message() and on_public_message() methods.
        """

    __slots__ = 'cog', 'ctx', 'args'

    def __init__(self, cog, ctx, *args):
        """
        Base init method. Requires Context passed to it.
        :param ctx: invocation Context (game sessions must be invoked via a Command)
        """
        self.cog = cog
        self.ctx = ctx
        self.args = args

    @property
    def primary_channel(self):
        return self.ctx.channel

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            await self.on_private_message(message)
        else:
            await self.on_public_message(message)

    async def create(self):
        pass

    async def start(self):
        await self.create()
        self.cog.subscribe(self)

    def stop(self):
        self.cog.unsubscribe(self)

    @abstractmethod
    async def on_private_message(self, message):
        return NotImplementedError

    @abstractmethod
    async def on_public_message(self, message):
        return NotImplementedError
