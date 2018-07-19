import os
import re

from telethon import TelegramClient, sync  # importing sync so no need async def run until complete loop blah blah blah
from telethon.tl.types import PeerUser, PeerChannel

from utils import mention_markdown

# Private constants
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
PHONE_NUMBER = os.environ["PHONE_NUMBER"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

client = TelegramClient("Trainer_Jono", API_ID, API_HASH).start(phone=PHONE_NUMBER)
bot = TelegramClient("DukerCupBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

client.get_dialogs()

# Not too secret constants
JS_MENTION = mention_markdown((client.get_entity(PeerUser(190726372))))

HK_DUKER_ID = -1001295361187  # Real HK Duker
# HK_DUKER_ID = -1001282856749  # Duker Admin
# HK_DUKER_ID = -1001141544515  # On9 Admin

HK_DUKER = PeerChannel(HK_DUKER_ID)
GROUP_LINK = "t.me/hkduker"

CMD_PREFIX = "(/|!|\?|\.|#)"
USERNAME_NOT_EXIST_MSG = re.compile(r'^No user has "(.*)" as username$')
