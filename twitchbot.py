# twitchhacks.online
# "Twitch Hacks Online"
# 2020 - Frank Godo

import json
import logging
from state import State
from vbox_srv import VirtualBoxSrv, KEYBOARD_KEYS
from twitchio.ext import commands
from settings import BOT_NICK, CHANNEL_NAME, CHANNEL_ID, IRC_TOKEN, CLIENT_ID, CLIENT_SECRET, CLIENT_TOKEN,\
    API_TOKEN, SUBSCRIPTIONS, MAX_FREEBIES

logger = logging.getLogger(__name__)
SPECIAL_KEYS = ' | '.join([x for x in KEYBOARD_KEYS if len(x) > 1])


class TwitchBot(commands.Bot):
    def __init__(self):
        self.state = State(CLIENT_ID, CHANNEL_ID)
        self.box = VirtualBoxSrv()
        super().__init__(irc_token=IRC_TOKEN,
                         nick=BOT_NICK,
                         client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         api_token=API_TOKEN,
                         prefix='!',
                         initial_channels=[CHANNEL_NAME])
        logger.info("TwitchBot initialized!")

    async def event_ready(self):
        print(f'Ready | {self.nick}')
        self.listener = await self.pubsub_subscribe(CLIENT_TOKEN, *SUBSCRIPTIONS)

    async def event_raw_pubsub(self, data):
        if data.get('type') == 'RESPONSE':
            if data.get('error'):
                logger.error("Failed to subscribe to %s", SUBSCRIPTIONS)
            else:
                logger.info("Subscribed to %s", SUBSCRIPTIONS)
                channel = self.get_channel(CHANNEL_NAME)
                await channel.send('Bot initialized! Type !help to learn how to interact with me')
        elif data.get('type') == 'PONG':
            pass
        elif data.get('type') == 'MESSAGE':
            try:
                topic = data.get('data').get('topic')
                message = json.loads(data.get('data').get('message'))
                if topic == f'channel-points-channel-v1.{CHANNEL_ID}' and message.get('type') == 'reward-redeemed':
                    redemption = message.get('data').get('redemption')
                    user = redemption.get('user').get('display_name')
                    reward = redemption.get('reward').get('title')
                    logger.info(f'{user} redeemed {reward}')
                    channel = self.get_channel(CHANNEL_NAME)
                    if reward == 'Get the hot seat!':
                        # Award the hotseat for 5 minutes
                        self.state.hotseat(user, expire=True)
                        await channel.send(
                            f"{user} is now in the hotseat, and has exclusive control for the next 5 minutes"
                        )
                    elif reward == 'Hints':
                        # Ask Agent Random for a hint
                        await channel.send(f'Hints will be supplied by {CHANNEL_NAME}')
                elif topic == f'channel-bits-events-v2.{CHANNEL_ID}':
                    username = message.get('data').get('user_name')
                    amount = message.get('data').get('bits_used')
                    logger.info(f'{username} cheered {amount}')
                elif topic == f'channel-subscribe-events-v1.{CHANNEL_ID}':
                    username = message.get('display_name')
                    amount = message.get('cumulative_months')
                    gift = message.get('is_gift')
                    logger.info(f'{username} has subscribed for {amount} months')
                    if not gift:
                        channel = self.get_channel(CHANNEL_NAME)
                        if amount == 1:
                            await channel.send(
                                f'{username} is a new subscriber. Thank you!'
                            )
                        else:
                            await channel.send(
                                f'{username} has been subscribed for a total of {amount} months. Thank you!'
                            )
                elif topic == f'chat_moderator_actions.{CHANNEL_ID}':
                    action = message.get('data').get('moderation_action')
                    username = message.get('data').get('created_by')
                    args = message.get('data').get('args')
                    logger.info(f'{username} moderated {action}: {args}')
            except (ValueError, KeyError):
                logger.exception("Unable to parse pubsub message")
        else:
            print(data)

    async def event_message(self, message):
        logger.debug("Received message: %s", message.content)
        await self.handle_commands(message)

    async def can_interact(self, ctx):
        name = ctx.author.name
        hotseat = self.state.get_hotseat()
        if ctx.author.is_mod:
            return True
        elif self.state.is_rejected(name):
            return False
        elif hotseat and hotseat != name and not self.state.is_hotseat_expired():
            await ctx.send(f"Can't interact while {hotseat} is in the hotseat!")
            return False
        elif self.state.is_allowed(name):
            return True
        elif self.state.is_follower(name):
            return True
        else:
            following = await self.get_follow(ctx.author.id, CHANNEL_ID)
            if following:
                self.state.add_follower(name)
                return True
            freebies = self.state.update_noob(name)
            if freebies < MAX_FREEBIES:
                return True
            else:
                await ctx.send(f"{name}: please follow the channel to continue interacting")
                return False

# Information commands
    @commands.command(name='help')
    async def show_help(self, ctx):
        help_text = """
            Use !t[ype] 'your text' to type text |
            Use !e[xecute] 'your command' to execute commands (enter at end of line) |
            Use !p[ress] [key(s)] to send special key commands (lists keys if no parameters) |
            Use !release to release stuck modifier keys
            """
        await ctx.send(help_text)

    @commands.command(name='objective', aliases=['obj', 'what'])
    async def show_objective(self, ctx):
        objective_text = """
            Find flags in order to escalate privileges. Flags are 64char hexadecimal strings.
            """
        await ctx.send(objective_text)

    @commands.command(name='source', aliases=['github', 'gh'])
    async def show_source(self, ctx):
        source_text = """
            The source for this bot is here: https://github.com/godoppl/twitchhacksonline
            """
        await ctx.send(source_text)

# Action commands
    @commands.command(name='type', aliases=['t'])
    async def type_input(self, ctx, *args):
        if not args:
            return
        try:
            if await self.can_interact(ctx):
                prefix = ctx.message.content.split(' ')[0]
                command = ctx.message.content[len(prefix)+1:]
                if self.box.type(command) is not False:
                    logger.debug("Typing %s", command)
                    await ctx.send(f"Typing: '{command}'"[:500])
                else:
                    await ctx.send("Instance is not running, attempting to restart it...")
                    self.box.launch()
        except (ValueError, IndexError, AttributeError) as e:
            logger.exception(e)

    @commands.command(name='execute', aliases=['e'])
    async def execute_line(self, ctx, *args):
        try:
            if await self.can_interact(ctx):
                if args:
                    prefix = ctx.message.content.split(' ')[0]
                    command = ctx.message.content[len(prefix)+1:]
                    if self.box.type(command) is not False:
                        self.box.send('enter')
                        logger.debug("Executing %s", command)
                        await ctx.send(f"Executing: '{command}'"[:500])
                    else:
                        await ctx.send("Instance is not running, attempting to restart it...")
                        self.box.launch()
                else:
                    command = self.box.send('enter')
                    if command is not None:
                        logger.debug("Pressing %s", command)
                        await ctx.send("Pressing 'ENTER'")

        except (ValueError, IndexError, AttributeError) as e:
            logger.exception(e)

    @commands.command(name='press', aliases=['p'])
    async def press_keys(self, ctx, *args):
        try:
            if await self.can_interact(ctx):
                if len(args) > 0:
                    command = self.box.send(*args)
                    if command is not None:
                        logger.debug("Pressing %s", command)
                        await ctx.send(f"Pressing keys: '{command}'")
                    else:
                        await ctx.send("Instance is not running, attempting to restart it...")
                        self.box.launch()
                else:
                    await ctx.send(f"Special keys: {SPECIAL_KEYS}")
        except (ValueError, IndexError, AttributeError) as e:
            logger.exception(e)

    @commands.command(name='release')
    async def release_keys(self, ctx, *args):
        if self.box.release():
            await ctx.send('Released all modifier keys')
        else:
            await ctx.send("Instance is not running, interaction is disabled")

# User handling
    @commands.command(name='hotseat', aliases=['hs'])
    async def hotseat_user(self, ctx, *args):
        if not ctx.author.is_mod:
            return
        if len(args) > 0:
            self.state.hotseat(args[0])
            await ctx.send(f"{args[0]} is now in the hotseat, and is the only one that can interact with the machine")
        else:
            self.state.hotseat(None)
            await ctx.send("Hotseat is empty, anyone with the permission can interact")

    @commands.command(name='allow')
    async def allow_user(self, ctx, *args):
        if not ctx.author.is_mod:
            return
        added = []
        for user in args:
            if not self.state.is_allowed(user):
                self.state.add_allowed(user)
                logger.info('Added %s to allowed list', user)
                added.append(user)
        if added:
            added_users = ', '.join(added)
            await ctx.send(f"Added users: {added_users}")
        else:
            await ctx.send("No users could be added!")

    @commands.command(name='remove')
    async def remove_user(self, ctx, *args):
        if not ctx.author.is_mod:
            return
        removed = []
        for user in args:
            self.state.remove_user(user)
            removed.append(user)
        if removed:
            removed_users = ', '.join(removed)
            await ctx.send(f"Removed users from all lists: {removed_users}")
        else:
            await ctx.send("No users could be removed!")

    @commands.command(name='reject')
    async def reject_user(self, ctx, *args):
        if not ctx.author.is_mod:
            return
        added = []
        for user in args:
            if not self.state.is_rejected(user):
                self.state.add_rejected(user)
                logger.info('Added %s to rejected list', user)
                added.append(user)
        if added:
            added_users = ', '.join(added)
            await ctx.send(f"Added users: {added_users}")
        else:
            await ctx.send("No users could be added!")

# Virtualbox control
    @commands.command(name='stop')
    async def shut_down(self, ctx, *args):
        try:
            if args and ctx.author.is_mod:
                if args[0] == 'restore':
                    self.box.shut_down(restore=True)
                    await ctx.send("Most recent snapshot has been restored")
                if args[0] == 'halt':
                    self.box.shut_down()
                    await ctx.send("System is now in 'powered off' state")
            else:
                if ctx.author.name.lower() in [CHANNEL_NAME, BOT_NICK]:
                    self.box.shut_down(save=True)
                    await ctx.send("System is now in 'saved' state")
        except (ValueError, IndexError, AttributeError) as e:
            logger.exception(e)

    @commands.command(name='snap')
    async def snapshot(self, ctx, *args):
        if ctx.author.is_mod:
            self.box.snapshot(ctx.author.name)
            await ctx.send("Snapshot created")
