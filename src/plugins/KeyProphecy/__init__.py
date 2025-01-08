import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
from typing import List
import random
from datetime import datetime
import hashlib

from .config import PluginConfig
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    GROUP,
    Message,
    MessageSegment
)
from .prophecy import Prophecy
import json
import os
import random

__plugin_meta__ = PluginMetadata(
    name="KeyProphecy",
    description="",
    usage="",
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)

def get_lucky_discription(lucky_point):
    if lucky_point <= 10:
        return "大凶"
    elif lucky_point <= 20:
        return "凶"
    elif lucky_point <= 30:
        return "小凶"
    elif lucky_point <= 50:
        return "平"
    elif lucky_point <= 60:
        return "小吉"
    elif lucky_point <= 80:
        return "吉"
    elif lucky_point <= 99:
        return "大吉"
    else:
        return "头等奖！⭐️"

def get_image_list(image_base_folder: str, cha_name: str) -> List[str]:
    matching_files = []
    for root, dirs, files in os.walk(image_base_folder):
        for file in files:
            if cha_name in file:
                matching_files.append(os.path.join(root, file))
    
    return matching_files

prophecy_event = nonebot.on_command("今日运势", aliases={"抽签", "占卜", "key占卜"}, priority=8, block=True)

@prophecy_event.handle()
async def _(event: GroupMessageEvent):
    user_id = str(event.get_user_id())
    prophecier = Prophecy(user_id)
    heroine = prophecier.getHeroine()
    #heroine = "月宫亚由"
    lucky_point = prophecier.getLuckyPoint()
    dos, donts = prophecier.getDosDonts()
    lucky_thing = prophecier.getLuckyThing()
    
    image_path = ""
    game_name = "null"
    try:
        character_data = dict()
        with open(config.character_json_path, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
        
        if heroine in character_data:
            game_name = character_data[heroine]["game_name"]
            img_list = get_image_list(config.image_base_folder, heroine)
            today = datetime.now().strftime("%Y-%m-%d")
            random.seed( int(hashlib.md5(f"{user_id}_{today}".encode()).hexdigest(),16)%(2**32))
            image_path = random.choice(img_list)
            #print(image_path)
            if not os.path.isfile(image_path):
                image_path = ""
    except Exception as e:
        image_path = ""
    
    msg = MessageSegment.at(user_id)
    msg += MessageSegment.text(f" 你的今日运势值为{lucky_point}：{get_lucky_discription(lucky_point)}\n")
    msg += MessageSegment.text(f"🌟你今日的key社老婆为{game_name}中的{heroine}🌟")
    if image_path:
        msg += MessageSegment.image(image_path)
    msg += MessageSegment.text(f"✅宜: {dos[0]}、{dos[1]}、{dos[2]}\n")
    msg += MessageSegment.text(f"🈲忌: {donts[0]}、{donts[1]}、{donts[2]}\n")
    msg += MessageSegment.text(f"⭐占卜结果显示今天你会{lucky_thing}哦！")
    
    await prophecy_event.finish(msg)