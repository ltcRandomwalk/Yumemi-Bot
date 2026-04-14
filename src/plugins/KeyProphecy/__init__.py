import nonebot
from nonebot import get_driver, get_plugin_config, logger
from nonebot.plugin import PluginMetadata
from typing import List
import random
from datetime import datetime
import hashlib
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11.exception import ActionFailed, ApiNotAvailable, NetworkError

from .config import PluginConfig
from src.utils.character_data import (
    get_character_profile,
    get_character_profile_from_text,
    list_character_images,
    warmup_character_resource_cache,
)
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageSegment
)
from nonebot.params import CommandArg
from .prophecy import Prophecy
import os

__plugin_meta__ = PluginMetadata(
    name="KeyProphecy",
    description="",
    usage="",
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)
superusers = {str(user_id) for user_id in get_driver().config.superusers}
PROPHECY_SEND_TIMEOUT = 45.0
PROPHECY_ERROR_MESSAGE = "占卜时出了点小故障，请再试一次……"

warmup_stats = warmup_character_resource_cache(config.character_json_path, config.image_base_folder)
logger.info(
    "KeyProphecy resource cache warmed up: "
    f"{int(warmup_stats['character_count'])} characters, "
    f"{int(warmup_stats['image_character_count'])} image folders, "
    f"{warmup_stats['total_ms']} ms total"
)


def is_probable_napcat_send_timeout(error: ActionFailed) -> bool:
    return getattr(error, "retcode", None) == 1200 and "Timeout:" in str(error)


def pick_prophecy_image(user_id: str, heroine: str, image_paths: List[str]) -> str:
    if not image_paths:
        return ""

    today = datetime.now().strftime("%Y-%m-%d")
    seed = int(hashlib.md5(f"{user_id}_{today}_{heroine}_image".encode()).hexdigest(), 16) % (2**32)
    random.seed(seed)
    return random.choice(image_paths)

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
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = str(event.get_user_id())

    try:
        prophecier = Prophecy(user_id)
        heroine = prophecier.getHeroine()
        forced_name = args.extract_plain_text().strip()
        if user_id in superusers and forced_name:
            forced_profile = get_character_profile_from_text(forced_name, config.character_json_path)
            if forced_profile is not None:
                heroine = forced_profile.name

        lucky_point = prophecier.getLuckyPoint()
        dos, donts = prophecier.getDosDonts()
        lucky_thing = prophecier.getLuckyThing()

        image_path = ""
        game_name = "null"
        profile = get_character_profile(heroine, config.character_json_path)
        if profile is not None:
            heroine = profile.name
            game_name = profile.game_name
            image_list = list_character_images(heroine, config.image_base_folder)
            if image_list:
                image_path = pick_prophecy_image(user_id, heroine, image_list)

            if image_path and not os.path.isfile(image_path):
                image_path = ""

        msg = MessageSegment.at(user_id)
        msg += MessageSegment.text(f" 你的今日运势值为{lucky_point}：{get_lucky_discription(lucky_point)}\n")
        msg += MessageSegment.text(f"🌟你今日的key社老婆为{game_name}中的{heroine}🌟")
        if image_path:
            msg += MessageSegment.image(image_path)
        msg += MessageSegment.text(f"✅宜: {dos[0]}、{dos[1]}、{dos[2]}\n")
        msg += MessageSegment.text(f"🈲忌: {donts[0]}、{donts[1]}、{donts[2]}\n")
        msg += MessageSegment.text(f"⭐占卜结果显示今天你会{lucky_thing}哦！")
    except Exception as e:
        logger.exception(f"KeyProphecy failed before sending message: user_id={user_id}, error={repr(e)}")
        await prophecy_event.finish(PROPHECY_ERROR_MESSAGE, _timeout=10.0)

    try:
        await prophecy_event.finish(msg, _timeout=PROPHECY_SEND_TIMEOUT)
    except FinishedException:
        return
    except ActionFailed as e:
        if is_probable_napcat_send_timeout(e):
            logger.warning(
                "KeyProphecy send likely succeeded but NapCat timed out while waiting for ack; "
                f"suppressing retry/log spam. user_id={user_id}, heroine={heroine}, timeout={PROPHECY_SEND_TIMEOUT}, error={repr(e)}"
            )
            return
        raise
    except (ApiNotAvailable, NetworkError) as e:
        logger.warning(
            "KeyProphecy send failed after a single attempt; not retrying. "
            f"user_id={user_id}, heroine={heroine}, timeout={PROPHECY_SEND_TIMEOUT}, error={repr(e)}"
        )
        return
