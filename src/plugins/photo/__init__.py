import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
import os

from .config import PluginConfig
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    GROUP,
    Message,
    MessageSegment
)

__plugin_meta__ = PluginMetadata(
    name="photo",
    description="",
    usage="",
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)

photo_event = nonebot.on_command("照片", aliases={"图片"}, priority=5, block=True)

@photo_event.handle()
async def _(event: GroupMessageEvent, args: Message=CommandArg()):
    message_id = event.message_id
    role_name = args.extract_plain_text()
    msg = MessageSegment.reply(message_id)
    
    if not role_name:
        msg += MessageSegment.text("请输入角色名！\n")
        await photo_event.finish(msg)
    
    photo_folder = os.path.join(config.image_base_folder, role_name)
    if not os.path.isdir(photo_folder):
        await photo_event.finish(msg + MessageSegment.text("没有找到这个角色的图片。"))

    image_files = sorted(
        os.path.join(photo_folder, file_name)
        for file_name in os.listdir(photo_folder)
        if os.path.isfile(os.path.join(photo_folder, file_name))
    )
    if not image_files:
        await photo_event.finish(msg + MessageSegment.text("这个角色的图片目录还是空的。"))

    photo_path = image_files[0]
    msg += MessageSegment.image(photo_path)
    
    await photo_event.finish(msg)
