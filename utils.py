from typing import List, Any, Union

from telethon.tl.types import User, Chat, Channel
from telethon.utils import get_display_name


def strip_list(li: List[Any]) -> List[Any]:
    while li and not li[-1]:
        del li[-1]
    return li


def mention_markdown(entity: Union[User, Chat, Channel]) -> str:
    return f"[{get_display_name(entity)}](tg://user?id={entity.id})"
