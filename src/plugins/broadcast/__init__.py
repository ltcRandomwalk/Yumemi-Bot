import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
import pytz
from openai import AzureOpenAI
import openai
from openai import OpenAI
import os
from nonebot import require
import nonebot_plugin_session
from nonebot_plugin_session import extract_session, SessionIdType
require("nonebot_plugin_chatrecorder")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_chatrecorder import get_message_records, get_messages_plain_text
from datetime import datetime, timedelta
from nonebot.exception import FinishedException
from anthropic import Anthropic
from nonebot.permission import SUPERUSER
from nonebot.params import ArgPlainText
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    GROUP,
    Message,
    MessageSegment
)

__plugin_meta__ = PluginMetadata(
    name="broadcast",
    description="",
    usage="",
)

#chat_event = nonebot.on_command("总结", priority=10, block=True)
test_event = nonebot.on_command("超管测试", permission=SUPERUSER)
broadcast_event = nonebot.on_command("广播", permission=SUPERUSER)
get_group_list_event = nonebot.on_command("获取群列表", permission=SUPERUSER)

@test_event.handle()
async def test_handler(bot: Bot, event: GroupMessageEvent, args: Message=CommandArg()):
    await test_event.finish("测试成功")

@get_group_list_event.handle()
async def get_group_list_handler(bot: Bot):
    group_list = await  bot.get_group_list()
    group_info = "group_id\tgroup_name\tmember_count\tmax_member_count\n"
    for group in group_list:
        group_id = group['group_id']
        group_name = group['group_name']
        member_count = group['member_count']
        max_member_count = group['max_member_count']
        group_info += f"{group_id}\t{group_name}\t{member_count}\t{max_member_count}\n"
    await get_group_list_event.finish(group_info)

@broadcast_event.got("content", prompt="请输入广播内容，输入“取消”结束广播")
async def broadcast_handler(bot: Bot, content: str = ArgPlainText()):
    if content == "取消":
        await broadcast_event.finish("广播已取消")
    group_list = await bot.get_group_list()
    group_id_list = [ info['group_id'] for info in group_list ]
    total_num = len(group_id_list)
    error_list = []
    for group_id in group_id_list:
        try:
            await bot.send_group_msg(group_id=group_id, message=content)
        except Exception as e:
            error_list.append(group_id)
            continue
    await broadcast_event.send(f"发送失败群聊：{error_list}")

