from typing import List, Any, Union

from telethon.tl.types import User, Chat, Channel
from telethon.utils import get_display_name


def strip_list(li: List[Any]) -> List[Any]:
    while li and not li[-1]:
        del li[-1]
    return li


def flatten_matrix(li: List[List[Any]]) -> List[Any]:
    return [e for elem in li for e in elem]


def mention_markdown(user: User) -> str:
    return f"[{get_display_name(user)}](tg://user?id={user.id})"
