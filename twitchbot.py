# "Twitch Hacks Online"
# 2020 - Frank Godo

import logging
from twitchio.ext import commands
from settings import BOT_NICK, CHANNEL_NAME, IRC_TOKEN, GUESS, FOLLOWERS_ONLY

logger = logging.getLogger(__name__)


class TwitchBot(commands.Bot):
    def __init__(self, state, kbd_client):
        self.state = state
        self.kbd_client = kbd_client
        self.uncover_by_guess = GUESS
        self.followers_only = FOLLOWERS_ONLY
        super().__init__(irc_token=IRC_TOKEN, nick=BOT_NICK, prefix='!', initial_channels=[CHANNEL_NAME])
        logger.info("TwitchBot initialized! Guessing is %s, Followers only is %s",
                    "on" if GUESS else "off",
                    "on" if FOLLOWERS_ONLY else "off")

    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def event_message(self, message):
        logger.debug("Received message: %s", message.content)
        if message.author.name.lower() != self.nick.lower():
            keys = self.state.get_keys(message.content, self.uncover_by_guess)
            if keys:
                self.kbd_client.send_keys(keys)
        await self.handle_commands(message)

    @commands.command(name='help')
    async def show_help(self, ctx):
        help_text = """
            Type emotes in chat to press keys, all keys have a corresponding emote.
            Try guessing emotes to figure out what key it corresponds to.
            Lookup uncovered keys by using the !lookup command.
            """
        await ctx.send(help_text)

    @commands.command(name='commands')
    async def list_commands(self, ctx):
        commands = """
            Bot commands:
            !lookup - Lookup keys (if uncovered) |
            !keys - List uncovered keys |
            !task - Show next task |
            !uncover - Uncover more keys
            """
        await ctx.send(commands)

    @commands.command(name='keys')
    async def list_keys(self, ctx):
        keys += "Lookup uncovered keys by using the !lookup command"
        keys += " | " + self.state.list_uncovered_keys()
        await ctx.send(keys)

    @commands.command(name='task')
    async def next_task(self, ctx):
        task = self.state.next_task()
        await ctx.send(task)

    @commands.command(name='lookup')
    async def key_lookup(self, ctx, *args):
        translated = []
        for key in args:
            only_if_uncovered = not ctx.author.is_mod
            emote = self.state.get_emote_by_key(key, only_if_uncovered)
            if emote:
                translated.append(str(emote))
            else:
                translated.append(f"? = [{key}]")
        await ctx.send(" | ".join(translated))

    @commands.command(name='uncover')
    async def show_uncover(self, ctx, *args):
        donate = """
            Use channel points, bits or donations to uncover keys |
            50 bits to uncover a random key |
            100 bits uncover a specific key (put key as donation message)
            """
        try:
            if len(args) > 0 and ctx.author.is_mod:
                if args[0] == 'random':
                    uncovered = str(self.state.uncover_random_emote())
                else:
                    uncovered = " | ".join([str(obj) for obj in self.state.uncover_keys(args)])
                await ctx.send(f"Uncovered: {uncovered}")
            else:
                await ctx.send(donate)
        except (ValueError, IndexError, AttributeError):
            await ctx.send(donate)
            logger.exception()

    @commands.command(name='cover')
    async def cover_keys(self, ctx, *args):
        try:
            if len(args) > 0 and ctx.author.is_mod:
                covered = " | ".join([str(obj) for obj in self.state.cover_keys(args)])
                await ctx.send(f"Covered: {covered}")
        except (ValueError, IndexError, AttributeError):
            logger.exception()

    @commands.command(name='type')
    async def type_input(self, ctx, *args):
        try:
            if len(args) > 0 and (ctx.author.is_mod or 'vip' in ctx.author.badges.keys()):
                command = ' '.join(args)
                self.kbd_client.send_command(command)
                logger.debug("Executed %s", command)
                await ctx.send(f"Running: '{command}'")
        except (ValueError, IndexError, AttributeError):
            logger.exception()

    @commands.command(name='reload')
    async def reload_state(self, ctx):
        try:
            if ctx.author.is_mod:
                self.state.read_emotes()
                logger.info("Reloaded state")
                await ctx.send("Reloaded emotes in state")
        except AttributeError:
            pass

    @commands.command(name='enable')
    async def enable_feature(self, ctx, *args):
        try:
            if ctx.author.is_mod:
                if 'guess' in args:
                    logger.info("Enabling guess mode")
                    self.uncover_by_guess = True
                    await ctx.send("Users can now uncover by guessing emotes")
        except AttributeError:
            pass

    @commands.command(name='disable')
    async def disable_feature(self, ctx, *args):
        try:
            if ctx.author.is_mod:
                if 'guess' in args:
                    self.uncover_by_guess = False
                    logger.info("Disabling guess mode")
                    await ctx.send("Users can no longer uncover by guessing emotes")
        except AttributeError:
            pass
