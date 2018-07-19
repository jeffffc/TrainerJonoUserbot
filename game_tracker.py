import re
from typing import List, Dict, Optional

from telethon import events
from telethon.tl.types import User, PeerUser, MessageEntityBold, MessageEntityTextUrl, MessageEntityMentionName

from constants import client, bot, JS_MENTION, HK_DUKER, GROUP_LINK, USERNAME_NOT_EXIST_MSG
from utils import strip_list, mention_markdown


class BaseGameBot:
    ID: int = 0
    END_MSG: str = ""
    GROUP_LINK: str = GROUP_LINK
    HELP_REGEX = re.compile("")
    HELP_MSG: str = ""

    @staticmethod
    async def message_handler(event: events.NewMessage.Event) -> None:
        pass

    @staticmethod
    def reset_game() -> None:
        pass

    @staticmethod
    async def end_handler(event: events.NewMessage.Event) -> None:
        pass


class SixNimmtBot(BaseGameBot):
    ID = 567333815
    PLACE_SYMBOL_LIST = ["🥇", "🥈", "🥉", "4⃣", "5⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    PLACE_MSG = re.compile(r"^▃▄▅▇(.*)▇▅▄▃")
    PLACE_NO_AFK_MSG = re.compile(r"^【.*】食撚咗 \d{1,3} 個牛頭！$")
    PLACE_AFK_MSG = re.compile(r"^豬西【.*】有幾晚訓撚著咗，見佢咁訓得，我送多 (\d{1,2}) 個牛頭比佢啦，"
                               "加埋本身嗰 \d{1,3} 個牛頭，總共食撚咗 \d{1,3} 個牛頭！$")
    END_MSG = "個驚完撚咗喇！肚餓嘅，咪再㩒 /startgame 叫多D懵西入離食牛lo，牛閪豐富嘅鐵質呀！"
    place_list: List[List[int]] = [[] for _ in range(10)]
    afk_list1: List[int] = []
    afk_list2: List[int] = []
    HELP_REGEX = re.compile(r"(?i)@?(six|6)\s*nimmt|(誰是)?牛")
    HELP_MSG = "\n".join([s[4:] for s in f"""    [誰是牛頭王](@sixnimmtbot)計分方法

    參與並完成游戲(AFK*除外):
        1-6人: +1🔅
        7-9人: +2🔅
        10 人: +3🔅

    排名(AFK*除外):
        +(在場玩家數目 - 玩家排名* + 1)🔅

    AFK*玩家:
        收到3-6個瞓覺獎勵牛頭: +0🔅
        收到9個或以上瞓覺獎勵牛頭: -5🔅及一次警告

    *AFK是指玩家收到3個或以上瞓覺獎勵牛頭
    ^排名為SixNimmtBot顯示之排名，可並列


    以[此局](t.me/hkduker/887406)為例:
        有7位玩家，因此無AFK嘅玩家顯獲得2參與分。

        第1名 🌞🧜🏼‍♂️ -> 2+7-1+1 = +9🔅
        第2名 JS -> 2+7-2+1 = +8🔅
        第2名 利狗 -> 2+7-2+1 = +8🔅
        第3名 SiuTsz -> 2+7-3+1 = +7🔅
        第3名 Dinar -> 2+7-3+1 = +7🔅
        第4名 陰蜂怒號 -> 3 × 瞓覺獎勵牛頭 = +0🔅
        第5名 小炸鷄 -> 2+7-5+1 = +5🔅
    """.split("\n")])

    @staticmethod
    async def message_handler(event: events.NewMessage.Event) -> None:
        text = event.raw_text
        if SixNimmtBot.PLACE_MSG.match(text):
            await SixNimmtBot.place_handler(event)
        elif text == SixNimmtBot.END_MSG and any(
                (*SixNimmtBot.place_list, SixNimmtBot.afk_list1, SixNimmtBot.afk_list2)):  # exclude not enough players
            await SixNimmtBot.end_handler(event)

    @staticmethod
    def reset_game() -> None:
        SixNimmtBot.place_list, SixNimmtBot.afk_list1, SixNimmtBot.afk_list2 = [[] for _ in range(10)], [], []

    @staticmethod
    async def place_handler(event: events.NewMessage.Event) -> None:
        text = event.raw_text
        user_ids = [e[0].user_id for e in event.get_entities_text(MessageEntityMentionName)]
        if "\n" * 3 in text:  # The message contains 2 places, deal them one by one
            li = text.split("\n\n\n")
            n = li[0].count("\n")
            SixNimmtBot.place_handler2(li[0], user_ids[:n])
            SixNimmtBot.place_handler2(li[1], user_ids[n:])
        else:
            SixNimmtBot.place_handler2(text, user_ids)

    @staticmethod
    def place_handler2(text: str, user_ids: List[int]) -> None:
        symbol = SixNimmtBot.PLACE_MSG.match(text.split("\n")[0]).group(1)
        no_afk_list, afk_list, afk_warn_list = [], [], []
        for line_count, text in enumerate(text.split("\n")[1:]):
            if SixNimmtBot.PLACE_NO_AFK_MSG.match(text):
                no_afk_list.append(user_ids[line_count])
            elif SixNimmtBot.PLACE_AFK_MSG.match(text):
                bulls = int(SixNimmtBot.PLACE_AFK_MSG.match(text).group(1))
                uids = user_ids[line_count]
                (no_afk_list.append(uids) if bulls < 6 else
                 afk_list.append(uids) if bulls < 9 else afk_warn_list.append(uids))
        SixNimmtBot.place_list[SixNimmtBot.PLACE_SYMBOL_LIST.index(symbol)].extend(no_afk_list)
        SixNimmtBot.afk_list1.extend(afk_list)
        SixNimmtBot.afk_list2.extend(afk_warn_list)

    @staticmethod
    async def end_handler(event: events.NewMessage.Event) -> None:
        player_count = (sum([sum([1 for _ in t]) for t in SixNimmtBot.place_list]) + len(SixNimmtBot.afk_list1) +
                        len(SixNimmtBot.afk_list2))  # also score for #1
        base_score = 1 if player_count < 7 else 2 if player_count < 10 else 3
        to_send = f"呢場誰是牛頭王玩完咗啦。\n\n呢局有{player_count}個玩家，你哋每人(AFK除外)至少會獲得{base_score}參與分。"
        if any(SixNimmtBot.place_list):
            to_send += f"\n\n各玩家分數(AFK除外):"
            for rank, players in enumerate(strip_list(SixNimmtBot.place_list)):
                for user_id in players:
                    player = await client.get_entity(PeerUser(user_id))
                    to_send += f"\n{mention_markdown(player)}:  {base_score + player_count - rank}分"
        for afk_list in SixNimmtBot.afk_list1, SixNimmtBot.afk_list2:
            if afk_list:
                to_send += f"\n\n獲得{'3-6' if afk_list is SixNimmtBot.afk_list1 else '9+'}個瞓教獎勵牛頭(AFK)嘅玩家:"
                for user_id in afk_list:
                    player = await client.get_entity(PeerUser(user_id))
                    to_send += (f"\n{mention_markdown(player)}: "
                                f"{'0分' if afk_list is SixNimmtBot.afk_list1 else '-5分 & 警告'}")
        to_send += "\n\n#DC2 #DC2SixNimmt"
        if SixNimmtBot.afk_list2:
            to_send += " #DC2AFKWarn"
        to_send += "\n"
        for rank in SixNimmtBot.place_list:
            for user_id in rank:
                to_send += f"\n#DCP{user_id}"
        to_send += "".join([f"\n#DC2P{user_id}" for user_id in (*SixNimmtBot.afk_list1, *SixNimmtBot.afk_list2)])
        await bot.send_message(HK_DUKER, to_send)
        SixNimmtBot.reset_game()


class ThirtyOneBot(BaseGameBot):
    ID = 402171524
    JOIN_START_MSG = "有一場新嘅遊戲開始喇，快啲撳下面個制一齊玩啦！\n\n注意：呢個 Bot 仲係 Beta 版本！\n\n官方 Channel: @ApeDev"
    START_MSG = "開波喇開波喇！！！\n\n玩家名單：\n"
    AFK_MSG = re.compile(".* 好似連續瞓足兩回合，好啦咁你慢慢瞓啦，下鋪再見你啦拜拜。")
    END_MSG = re.compile("完～！\n .* 做咗今次嘅大贏家！ 🏆\n/startgame 開過新一場？$")
    AFK_END_MERGED_MSG = re.compile("^.* 好似連續瞓足兩回合，好啦咁你慢慢瞓啦，下鋪再見你啦拜拜。\n\n"
                                    "完～！\n .* 做咗今次嘅大贏家！ 🏆\n/startgame 開過新一場？$")
    ERROR_MSG = ("，本bot計唔到分數。請用 `@admin` 回覆呢個訊息通知{0}處理，{0}請你自行計返呢局分數。".format(JS_MENTION) +
                 f"\n\n#DC2 #DC2ThirtyOne #DC2Manual\n[訊息]({GROUP_LINK}/""{})")
    players: List[User] = []
    afk_players_ids: List[int] = []
    HELP_REGEX = re.compile(r"(?i)@?(Thirty[-\s]?One|31|三十一)")

    @staticmethod
    async def message_handler(event: events.NewMessage.Event) -> None:
        text = event.raw_text
        if text == ThirtyOneBot.JOIN_START_MSG:
            await ThirtyOneBot.join_start_handler(event)
        elif text.startswith(ThirtyOneBot.START_MSG):
            await ThirtyOneBot.start_handler(event)
        elif ThirtyOneBot.players:  # Avoid processing msgs from game where player has no username
            if ThirtyOneBot.AFK_MSG.search(text):
                await ThirtyOneBot.afk_handler(event)
            if ThirtyOneBot.END_MSG.search(text):
                await ThirtyOneBot.end_handler(event)

    @staticmethod
    def reset_game() -> None:
        ThirtyOneBot.players, ThirtyOneBot.afk_players_ids = [], []

    @staticmethod
    async def join_start_handler(event: events.NewMessage.Event) -> None:
        ThirtyOneBot.reset_game()  # double confirm game is rest although unnecessary
        buttons = await event.get_buttons()
        url = buttons[0][0].url
        await bot.send_message(HK_DUKER, f"唔該你地set返個username先[加入呢局31]({url})，完game前亦唔好改username，"
                                         "否則我計唔到呢局分數。", link_preview=False)

    @staticmethod
    async def error_handler(event: events.NewMessage.Event, error_type: str) -> None:
        if error_type == "start_no_username":  # No username
            nubs = event.get_entities_text(MessageEntityBold)
            msg = f"{', '.join([f'**{e[1]}**' for e in nubs])} 唔set username入31點"
        else:  # Username changed
            msg = f"{error_type} 入局後轉左username"
        await bot.send_message(HK_DUKER, f"{msg}{ThirtyOneBot.ERROR_MSG.format(event.id)}", link_preview=False)
        ThirtyOneBot.reset_game()  # Not going to process the game any further in case of error

    @staticmethod
    async def start_handler(event: events.NewMessage.Event) -> None:
        if event.get_entities_text(MessageEntityBold):  # Bold means no username
            await ThirtyOneBot.error_handler(event, "start_no_username")
            return
        try:
            ThirtyOneBot.players = [await client.get_entity(e[0].url) for e in
                                    event.get_entities_text(MessageEntityTextUrl)]
        except ValueError as e:
            match = USERNAME_NOT_EXIST_MSG.match(str(e))
            if match:
                await ThirtyOneBot.error_handler(event, f"@{match.group(1)}")
            else:
                raise

    @staticmethod
    async def afk_handler(event: events.NewMessage.Event) -> None:
        afk_player_username = event.get_entities_text(MessageEntityTextUrl)[0][0].url[13:]  # [13:] gets username
        [ThirtyOneBot.afk_players_ids.append(p.id) for p in ThirtyOneBot.players if p.username == afk_player_username]

    @staticmethod
    def nobody_won_merged_msg_check(event: events.NewMessage.Event) -> bool:
        url = event.get_entities_text(MessageEntityTextUrl)[-1][0]
        if event.raw_text[url.offset + url.length:] == " 做咗今次嘅大贏家！ 🏆\n/startgame 開過新一場？":
            return False  # If the text after the last entity is that string, a player won
        return True

    @staticmethod
    async def end_handler(event: events.NewMessage.Event) -> None:
        try:
            urls = event.get_entities_text(MessageEntityTextUrl)
            if "\n\n" in event.raw_text:
                if ThirtyOneBot.nobody_won_merged_msg_check(event):
                    await ThirtyOneBot.end_handler2(None)
                else:
                    await ThirtyOneBot.end_handler2(await client.get_entity(urls[-1][0].url))
            else:
                await ThirtyOneBot.end_handler2(await client.get_entity(urls[0][0].url))
        except ValueError as e:
            match = USERNAME_NOT_EXIST_MSG.match(str(e))
            if match:
                await ThirtyOneBot.error_handler(event, f"@{match.group(1)}")
            else:
                raise

    @staticmethod
    async def end_handler2(winner: Optional[User]) -> None:
        base_score = 1 if len(ThirtyOneBot.players) < 5 else len(ThirtyOneBot.players) - 3
        to_send = (f"呢場31點玩完咗啦。\n\n呢局有{len(ThirtyOneBot.players)}個玩家，"
                   f"你哋每人(AFK除外)至少會獲得{base_score}參與分。")
        to_send += "\n\n" + (f"勝出玩家:\n{mention_markdown(winner)}: +{base_score + 2}分" if winner
                             else f"各位玩家一樣咁廢，Super！無人贏！")
        if winner:
            remaining_players = [p for p in ThirtyOneBot.players if
                                 p.id != winner.id and p.id not in ThirtyOneBot.afk_players_ids]
        else:
            remaining_players = [p for p in ThirtyOneBot.players if p.id not in ThirtyOneBot.afk_players_ids]
        afk_players = [p for p in ThirtyOneBot.players if p.id in ThirtyOneBot.afk_players_ids]
        for players in remaining_players, afk_players:
            if players:
                to_send += "\n\n" + (f"{'其餘' if winner else '參與'}玩家:" if players is remaining_players
                                     else "AFK而比踢出游戲嘅玩家:")
                score = 0
                if players is remaining_players:
                    score = base_score if winner else base_score + 1
                for player in players:
                    to_send += f"\n{mention_markdown(player)}: +{score}分"
        to_send += "\n\n#DC2 #DC2ThirtyOne\n"
        to_send += "".join([f"\n#DC2P{user_id}" for user_id in [p.id for p in ThirtyOneBot.players]])
        await bot.send_message(HK_DUKER, to_send)
        ThirtyOneBot.reset_game()


class WerewolfBot(BaseGameBot):
    ID = 198626752  # HK Duker uses beta bot
    END_MSG = "\n/startgame 開個『正常版（淫賤版）』\n/startchaos 開個『混亂版（淫賤版）』"
    AFK_MSGS = [re.compile(text + "\n") for text in (r"【(.*)】有票又唔撚投，連續兩日都係咁，唔得閒就咪撚玩啦！受死啦【\1】！",
                                                     r"大膽刁民，【(.*)】竟敢連續兩日唔投票？人嚟，拖【\1】出去斬！")]
    afk_messages: Dict[int, str] = {}
    HELP_REGEX = re.compile(r"(?i)@?(Werewolf|WW|狼)")

    @classmethod
    async def message_handler(cls, event: events.NewMessage.Event) -> None:
        text = event.raw_text
        if any([msg.search(text) for msg in cls.AFK_MSGS]):
            await cls.afk_handler(event)
        elif text.endswith(cls.END_MSG):
            await cls.end_handler(event)

    @classmethod
    def reset_game(cls) -> None:
        cls.afk_messages = {}

    @classmethod
    async def afk_handler(cls, event: events.NewMessage.Event) -> None:
        entities = event.get_entities_text(MessageEntityMentionName)[:-2:3]  # exclude lynch res (2 mentions, sep)
        for user_id in [e[0].user_id for e in entities]:
            cls.afk_messages[user_id] = f"{cls.GROUP_LINK}/{event.id}"  # save msg link for end handler

    @classmethod
    async def end_handler(cls, event: events.NewMessage.Event) -> None:
        entities = event.get_entities_text(MessageEntityMentionName)
        players = [await client.get_entity(PeerUser(e[0].user_id)) for e in entities]
        res = tuple(zip(players, [True if line == "贏" else False for line in
                                  [line[-1] for line in event.raw_text.split("\n\n")[0].split("\n")[1:]]]))
        results = {"won": [p[0] for p in res if p[1]], "lost": [p[0] for p in res if not p[1]]}
        base_score = 1 if len(players) < 8 else 2 if len(players) < 11 else 3
        to_send = f"呢場狼人玩完咗啦。\n\n呢局有{len(players)}個玩家，你哋每人至少會獲得{base_score}參與分。"
        for result in "won", "lost":
            if results[result]:
                to_send += f"\n\n{'勝出' if result == 'won' else '其餘' if results['won'] else '參與'}玩家:"
                for player in results[result]:
                    to_send += f"\n{mention_markdown(player)}: +{base_score + (2 if result == 'won' else 0)}分"
                    if player.id in cls.afk_messages:
                        to_send += f" [AFK]({cls.afk_messages[player.id]})"
        to_send += (f"\n\n由於狼人計分制度複雜，以及本bot難以辨認大愛同Betrayal等行爲，{JS_MENTION}稍後可能會修改本局玩家"
                    "分數甚至警告違規玩家。\n\n#DC2 #DC2Werewolf #DC2Manual\n")
        to_send += "".join([f"\n#DC2P{e[0].user_id}" for e in entities])
        await bot.send_message(HK_DUKER, to_send)
        cls.reset_game()


class WerewolfBotWWAchHK(WerewolfBot):
    ID = 175844556  # WWAchHK uses normal bot
    GROUP_LINK = "t.me/wwachhk"
    HELP_REGEX = re.compile("@?(ww|werewolf|狼)\s*ach")

    @classmethod
    async def end_handler(cls, event: events.NewMessage.Event) -> None:
        entities = event.get_entities_text(MessageEntityMentionName)
        players = [await client.get_entity(PeerUser(e[0].user_id)) for e in entities]
        members = [await client.get_participants(HK_DUKER)]
        participating_members = [p for p in players if p.id in [m.id for m in members]]
        if not participating_members:
            return
        to_send = f"呢場[狼人Achv]({cls.GROUP_LINK}/{event.id})玩完咗啦。\n\n你哋每人會獲得2參與分。"


class CriminalDanceBot(BaseGameBot):
    ID = 430952419
    END_MSG = "\n\n\n剩落嚟嘅牌有："
    afk_messages: Dict[int, str] = {}
    HELP_REGEX = re.compile(r"(?i)@?(Criminal\s?Dance|cd|犯人在跳舞)")

    @staticmethod
    def reset_game():
        pass

    @staticmethod
    async def message_handler(event: events.NewMessage.Event):
        if CriminalDanceBot.END_MSG in event.raw_text:
            await CriminalDanceBot.end_handler(event)

    @staticmethod
    async def end_handler(event: events.NewMessage.Event):
        players = [mention_markdown(await client.get_entity(PeerUser(p[0].url)))
                   if isinstance(p[0], MessageEntityTextUrl)
                   else f"**{p[1]}**" for p in [e for e in event.get_entities_text()
                                                if isinstance(e[0], (MessageEntityBold, MessageEntityTextUrl))]]
        base_score = 1 if len(players) < 6 else 1
        res = tuple(zip(players, [True if line[-1] == "贏" else False
                                  for line in event.raw_text.split("\n\n\n")[0].split("\n")]))
        results = {"won": [p[0] for p in res if p[1]], "lost": [p[0] for p in res if not p[1]]}
        to_send = f"呢場狼人玩完咗啦。\n\n呢局有{len(players)}個玩家，你哋每人至少會獲得{base_score}參與分。"


GAME_BOTS = (SixNimmtBot, ThirtyOneBot, WerewolfBot)
