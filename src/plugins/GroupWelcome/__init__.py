import gc
import random
from asyncio import sleep
from nonebot.plugin import PluginMetadata
import json
from nonebot import get_plugin_config
from nonebot import get_driver, on_request, on_notice, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, \
    MessageSegment, Message, GroupMessageEvent
from .config import PluginConfig
__plugin_meta__ = PluginMetadata(
    name="KeyProphecy",
    description="",
    usage="",
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)

#superuser = int(list(get_driver().config.superusers)[0])

notice_handle = on_notice(priority=5, block=True)

def parseMessage(data):
    if data["type"] == "text":
        return [ MessageSegment.text("\n".join(data["content"])) ]
    elif data["type"] == "image":
        return [  MessageSegment.image(data["content"]) ]
    elif data["type"] == "node":
        msgs = []
        for msg in data["content"]:
            msgs += parseMessage(msg)
        return msgs
    else:
        return [ MessageSegment.text("欢迎新人！") ]


@notice_handle.handle()
async def GroupNewMember(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.user_id == event.self_id:
        return
    else:
        with open(config.welcome_json, 'r' ,encoding='utf-8') as f:
            data = json.load(f)
        if str(event.group_id) not in data:
            #await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.text(f"未发现相关群聊。{data} {event.group_id}"))
            await bot.send_group_msg(group_id=event.group_id, message=Message(
                MessageSegment.at(event.user_id) + MessageSegment.text(f" 欢迎新人！")))
            return
        # text = "\n".join(data[str(event.group_id)]["text"])
        msgs = parseMessage(data[str(event.group_id)])
        
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.at(event.user_id) + " " + msgs[0]))
        for msg in msgs[1:]:
            await bot.send_group_msg(group_id=event.group_id, message=msg)