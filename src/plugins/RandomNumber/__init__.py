import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot import require

from typing import List
from .config import PluginConfig
import pytz
from datetime import datetime
import os
import random


from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    GROUP,
    Message,
    MessageSegment,
)

__plugin_usage__ = f"""
1. 输入 “#r/roll/随机数 a” 获得[1, a]间的随机整数；
2. 输入 “#r/roll/随机数 a b”获得[a, b]间的随机整数。
"""


__plugin_meta__ = PluginMetadata(
    name="RandomNumber",
    description="",
    usage=__plugin_usage__,
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)

random_event = nonebot.on_command(
    "r", aliases={"roll", "随机数"}, priority=10, block=True
)


@random_event.handle()
async def random_event_handler(
    matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()
):
    def _isinteger(s: str) -> bool:
        if s.startswith("-"):
            return s[1:].isdigit()
        return s.isdigit()

    user_id = str(event.get_user_id())
    args: str = args.extract_plain_text()
    if not args:
        month, day = datetime.today().month, datetime.today().day
    else:
        args: List[str] = args.split()

        if len(args) > 2:
            await random_event.finish(
                MessageSegment.at(user_id) + f"使用方法：\n{__plugin_usage__}"
            )

        elif len(args) == 1:  # Query birthday by character name.
            if not _isinteger(args[0]):
                await random_event.finish(
                    MessageSegment.at(user_id) + f"使用方法：\n{__plugin_usage__}"
                )
            b = int(args[0])
            a = 1
        else:
            if not (_isinteger(args[0]) and _isinteger(args[1])):
                await random_event.finish(
                    MessageSegment.at(user_id) + f"使用方法：\n{__plugin_usage__}"
                )
            a, b = int(args[0]), int(args[1])

    c = random.randint(a, b)
    await random_event.finish(
        MessageSegment.at(user_id) + "\n" + f"{a}-{b}间的随机数为：{c}"
    )
