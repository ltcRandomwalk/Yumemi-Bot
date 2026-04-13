import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from typing import List
import random
from datetime import datetime
import hashlib
from nonebot.exception import FinishedException
import traceback

from .config import PluginConfig
from src.utils.character_data import get_character_profile, list_character_images
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageSegment
)
from .prophecy import Prophecy
import os

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
    img_list: List[str] = []
    try:
        profile = get_character_profile(heroine, config.character_json_path)
        if profile is not None:
            heroine = profile.name
            game_name = profile.game_name
            img_list = list_character_images(heroine, config.image_base_folder)
            today = datetime.now().strftime("%Y-%m-%d")
            random.seed(int(hashlib.md5(f"{user_id}_{today}".encode()).hexdigest(), 16) % (2**32))
            if img_list:
                image_path = random.choice(img_list)
            
            if not os.path.isfile(image_path):
                image_path = ""
    except Exception as e:
        image_path = ""
    error_count = 0
    while True:
        try:
            msg = MessageSegment.at(user_id)
            msg += MessageSegment.text(f" 你的今日运势值为{lucky_point}：{get_lucky_discription(lucky_point)}\n")
            msg += MessageSegment.text(f"🌟你今日的key社老婆为{game_name}中的{heroine}🌟")
            
            if image_path:
                msg += MessageSegment.image(image_path)
            msg += MessageSegment.text(f"✅宜: {dos[0]}、{dos[1]}、{dos[2]}\n")
            msg += MessageSegment.text(f"🈲忌: {donts[0]}、{donts[1]}、{donts[2]}\n")
            msg += MessageSegment.text(f"⭐占卜结果显示今天你会{lucky_thing}哦！")
            
            await prophecy_event.finish(msg)
            break
        except FinishedException as f:
            return
        except Exception as e:
            error_info = traceback.format_exc()
            error_info = ""
            await prophecy_event.send(f"占卜时出了点小故障，再来一次……")
            if not img_list:
                break
            img_index = img_list.index(image_path)
            img_index = (img_index + 1) % len(img_list)
            image_path = img_list[img_index]
            error_count += 1
            if error_count == 5:
                break
        
