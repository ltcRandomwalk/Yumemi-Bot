import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from typing import List

import pytz
from datetime import datetime
import os

from .config import Config
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    GROUP,
    Message,
    MessageSegment
)


__plugin_usage__ = f"""

"""


__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage=__plugin_usage__,
    config=Config,
)

config = get_plugin_config(Config)


help_event = nonebot.on_command("help", aliases={"帮助"}, priority=8, block=True)


@help_event.handle()
async def birthday_event_handler(matcher: Matcher, event: GroupMessageEvent, args: Message=CommandArg()):
    help_msg = """命令全集：
    #help/#帮助：显示本条信息
    #占卜：获取今日运势及Key社老婆（每人每天的占卜结果都是相同的，不要刷屏哦）
    #查询 [角色名]：调用vndb API，查询Key社角色信息
    #生日 [角色名]：查询角色的生日
    #生日 [月] [日]：查询某月某日过生日的角色
    #r/roll/随机数 a：获得[1, a]间的随机整数
    #r/roll/随机数 a b：获得[a, b]间的随机整数
    
其他功能：
    每日群聊总结：每天晚上，用大模型为当日的群聊内容进行总结
    Key社生日推送：每日0点，推送当日过生日的Key社角色
    世界计划/啤酒烧烤功能相关：本bot已接入haruki bot，可使用haruki bot的命令（不加前缀）。为避免造成打扰，请需要的群主或管理私信联系开发者开通此功能。使用文档：https://docs.haruki.seiunx.com/usage/
    
目前bot仍处于测试阶段，bug反馈/功能建议联系：羽未（qq: 295259537）

开发者最近比较忙，暂时不处理新入群请求
    """
    
    help_node =[]
    
    help_node.append(
            MessageSegment.node_custom(
                user_id=os.getenv("QQ_NUMBER"),
                nickname=os.getenv("QQ_ID"),
                content=help_msg,
            )
        )
    # birth_node = MessageSegment.node_custom(user_id="2544412429", nickname="星野梦美", content= msg_list)
    # for msg in msg_list: 
    #     await birthday_event.send(msg)
    await help_event.finish(help_node)
    
