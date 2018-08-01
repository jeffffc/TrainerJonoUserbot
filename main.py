import asyncio
import logging
import time

from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import User, PeerUser, PeerChannel

from constants import client, bot, OWNER, HK_DUKER, CMD_PREFIX, LAST_REGEX, BOT_HELP_REGEX
from game_tracker import GAME_BOTS
from utils import mention_markdown

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@client.on(events.NewMessage(from_users=[PeerUser(bot.ID) for bot in GAME_BOTS], chats=HK_DUKER))
async def message_handler(event: events.NewMessage.Event) -> None:
    for bot in GAME_BOTS:
        if bot.ID == event.sender_id:
            await bot.message_handler(event)
            break


@client.on(events.NewMessage(outgoing=True, pattern=fr"(?i){CMD_PREFIX}ping"))
async def ping(event: events.NewMessage.Event) -> None:
    t = time.time()
    msg = await event.edit(f"{event.raw_text}\nPong!")
    await msg.edit(f"{msg.raw_text} {round(time.time() - t, 3)}")


@client.on(events.NewMessage(outgoing=True, pattern=r":: .+"))
async def double_semicolon_handler(event: events.NewMessage.Event) -> None:
    await event.edit(f"```{event.raw_text[3:]}```", link_preview=False)


@client.on(events.NewMessage(outgoing=True, pattern=fr"(?i){CMD_PREFIX}md .+"))
async def markdown_handler(event: events.NewMessage.Event) -> None:
    await event.edit(event.raw_text[3:])


@client.on(events.NewMessage(outgoing=True, pattern=fr"(?i){CMD_PREFIX}eval ([\s\S]+)"))
async def owner_eval(event: events.NewMessage.Event) -> None:
    source = event.pattern_match.group(2)
    await event.edit(f"**Source:**\n`{source}`\n**Result:**\n`{eval(source)}`")


@client.on(events.NewMessage(outgoing=True, pattern=fr"(?i){CMD_PREFIX}exec ([\s\S]+)"))
async def owner_exec(event: events.NewMessage.Event) -> None:
    await exec(event.pattern_match.group(2))


@client.on(events.NewMessage(pattern=LAST_REGEX))
@client.on(events.MessageEdited(pattern=LAST_REGEX))
async def last(event: events.NewMessage.Event) -> None:
    nub = event.pattern_match.group(3)
    if nub.isdigit():
        nub = int(nub)
    try:
        entity = await client.get_entity(nub)
        assert isinstance(entity, User)
        msg = (await client.get_messages(event.input_chat, 1, from_user=entity))[0]
        await msg.reply("{}, this is the latest message of {} in this chat.".format(
            *map(mention_markdown, (await event.get_sender(), entity))))
    except ValueError:
        await event.reply("Failed to find entity.")
    except AssertionError:
        await event.reply("The entity is not a user.")
    except IndexError:
        await event.reply("This user has never sent a message here.")


@bot.on(events.ChatAction)
async def auto_leave(event: events.ChatAction.Event) -> None:
    if event.added_by:
        chat = PeerChannel(event.chat_id)
        if OWNER.id not in (p.id for p in await client.get_participants(chat, search="Trainer_Jono")):
            await bot(LeaveChannelRequest(chat))


@bot.on(events.NewMessage(pattern=BOT_HELP_REGEX, chats=HK_DUKER))
@bot.on(events.MessageEdited(pattern=BOT_HELP_REGEX, chats=HK_DUKER))
async def bot_help(event: events.NewMessage.Event) -> None:
    args = event.pattern_match.group(4)
    try:
        assert args
        args = args.lower()
        for game_bot in GAME_BOTS:
            if game_bot.HELP_REGEX.match(args):
                await event.respond(game_bot.HELP_MSG, link_preview=False)
                break
        else:
            raise AssertionError
    except AssertionError:
        event.reply("This is not a valid game.")


async def main():
    await asyncio.wait([c.run_until_disconnected() for c in (client, bot)])


if __name__ == "__main__":
    with client, bot:
        asyncio.get_event_loop().run_until_complete(main())
