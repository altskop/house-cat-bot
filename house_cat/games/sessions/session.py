from abc import ABC, abstractmethod
import discord
import time
import asyncio


class Session(ABC):
    """
    A base abstract class for all game sessions.
    Implementations of this class MUST implement their
    own on_private_message() and on_public_message() methods.
    """

    __slots__ = 'cog', 'ctx', 'args', 'thread_lock', 'life_time', 'expire_time', 'one_per_channel'

    def __init__(self, cog, ctx, args, life_time, one_per_channel=False):
        """
        Base init method. Requires Context passed to it.
        :param cog: Cog
            Invoking Cog
        :param ctx:
            invocation Context (game sessions must be invoked via a Command)
        :param args: list
            command args
        :param life_time: int
            Life time of a session in seconds if nobody interacts with it
        :param one_per_channel: bool
            True if only one Session of the type is allowed per channel
        """
        self.cog = cog
        self.ctx = ctx
        self.args = args
        # self.thread_lock = asyncio.Lock()  # Sessions provide a thread lock to help avoid thread-unsafe operations
        self.life_time = life_time
        self.expire_time = time.time() + life_time
        self.one_per_channel = one_per_channel
        self.active = True

    @property
    def primary_channel(self):
        return self.ctx.channel

    async def on_message(self, message):
        if self.active:
            if isinstance(message.channel, discord.DMChannel):
                if self.is_private_message_expected(message):
                    self.refresh()
                    await self.on_private_message(message)
            else:
                if self.is_public_message_expected(message):
                    self.refresh()
                    await self.on_public_message(message)

    @abstractmethod
    async def create(self):
        """
        This method needs to be implemented by Session subclasses.
        It will be called after instantiation with the purpose of
        creating the session and making async calls outside of the
        constructor.

        Basically, this is where you want your announcement messages
        and stuff to go.
        """
        raise NotImplementedError

    async def start(self):
        """
        This method is called by the invoking Cog to start the Session.
        It only returns after the session is over or expired.
        :return:
        """
        if self.one_per_channel:
            if self.cog.is_session_in_channel(type(self), self.primary_channel):
                raise ValueError("This game is already in progress in this channel.")
        await self.create()
        self.cog.subscribe(self)
        await self.expire_after()

    def stop(self):
        """
        The Session subclasses need to call this method whenever they're over so they can be
        stopped and destroyed.
        :return:
        """
        self.active = False
        self.cog.unsubscribe(self)

    async def expire_after(self):
        while time.time() < self.expire_time and self.active:
            await asyncio.sleep(5)
        if self.active:
            # Session is still active but expired
            print("Session reached the end of its lifetime.")
            await self.on_expiration()
            self.stop()
        else:
            # Session is already over
            print("Session is over before expiration time.")

    def refresh(self):
        """
        This method can be called by subclasses of Session to refresh the created_time.
        Should be used to prolong the lifetime of the Session.

        By default, is called every time an expected message comes in.
        """
        self.expire_time = time.time() + self.life_time

    @abstractmethod
    async def on_expiration(self):
        """
        This method is being called when the Session expires.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def is_private_message_expected(self, message):
        """
        This method needs to be implemented by every Session subclass.
        It will be called to check whether or not an incoming message is
        expected by the session. Subclasses can specify all kind of different
        conditions here related to the message.
        :param message: incoming message through the broadcast
        :return: True if satisfies conditions, False if not
        """
        raise NotImplementedError

    @abstractmethod
    def is_public_message_expected(self, message):
        """
        This method needs to be implemented by every Session subclass.
        It will be called to check whether or not an incoming message is
        expected by the session. Subclasses can specify all kind of different
        conditions here related to the message.
        :param message: incoming message through the broadcast
        :return: True if satisfies conditions, False if not
        """
        raise NotImplementedError

    @abstractmethod
    async def on_private_message(self, message):
        """
        This method needs to be implemented by every Session subclass.
        Outlines the actions the session needs to take when an expected
        private message comes in.
        :param message: incoming message
        """
        raise NotImplementedError

    @abstractmethod
    async def on_public_message(self, message):
        """
        This method needs to be implemented by every Session subclass.
        Outlines the actions the session needs to take when an expected
        public message comes in.
        :param message: incoming message
        """
        raise NotImplementedError
