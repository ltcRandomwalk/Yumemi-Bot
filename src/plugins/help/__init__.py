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
    #help / #帮助：显示本条信息
    #占卜：获取今日运势及今日 Key 社老婆
    #查询 [角色名]：优先查询本地角色资料，必要时补充 VNDB 信息；支持别名和模糊匹配
    #生日：查询今天过生日的角色
    #生日 [角色名]：查询指定角色的生日；支持别名和模糊匹配
    #生日 [月] [日]：查询某月某日过生日的角色
    #r / #roll / #随机数 a：获得 [1, a] 间的随机整数
    #r / #roll / #随机数 a b：获得 [a, b] 间的随机整数

补充说明：
    查询、生日等角色检索功能现已统一支持标准名、别名、大小写/空格归一和较自然的模糊匹配。
    占卜结果每天固定，图片发送速度和稳定性也做过一轮优化；如果偶尔网络拥堵，稍后再试即可。

其他功能：
    每日群聊总结：每天晚上，用大模型为当日的群聊内容进行总结
    Key 社生日推送：每日 0 点，推送当日过生日的 Key 社角色
    世界计划 / 啤酒烧烤相关：本 bot 已接入 haruki bot，可使用 haruki bot 的命令（不加前缀）。为避免打扰，请需要的群主或管理私信联系开发者开通此功能。使用文档：https://docs.haruki.seiunx.com/usage/

目前 bot 仍处于测试阶段，bug 反馈 / 功能建议联系：羽未（qq: 295259537）

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
    
