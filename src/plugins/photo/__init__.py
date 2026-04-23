import os
import random
import re

import nonebot
from nonebot import get_driver, get_plugin_config, logger
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageSegment,
)
from nonebot.adapters.onebot.v11.exception import ActionFailed, ApiNotAvailable, NetworkError
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from src.utils.character_data import (
    CharacterProfile,
    get_character_profile,
    get_character_profile_from_text,
    list_character_images,
    normalize_lookup_text,
    warmup_character_resource_cache,
)

from .config import PluginConfig

__plugin_meta__ = PluginMetadata(
    name="photo",
    description="管理员本地图库随机返图",
    usage="管理员使用：#图片 角色名",
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)
global_superusers = {str(user_id) for user_id in get_driver().config.superusers}
photo_superusers = {str(user_id) for user_id in config.photo_superusers}
allowed_users = photo_superusers or global_superusers
PHOTO_SEND_TIMEOUT = 45.0
PHOTO_MAX_COUNT = 9

warmup_stats = warmup_character_resource_cache(
    json_path=config.character_json_path,
    image_base_folder=config.image_base_folder,
)
logger.info(
    "Photo resource cache warmed up: "
    f"{int(warmup_stats['image_character_count'])} image folders, "
    f"{warmup_stats['total_ms']} ms total"
)


def is_probable_napcat_send_timeout(error: ActionFailed) -> bool:
    return getattr(error, "retcode", None) == 1200 and "Timeout:" in str(error)


def format_title_line(query: str, standard_name: str, matched_name: str | None, game_name: str) -> str:
    normalized_query = normalize_lookup_text(query)
    normalized_standard_name = normalize_lookup_text(standard_name)
    normalized_matched_name = normalize_lookup_text(matched_name or "")

    title = f"{game_name} - {standard_name}" if game_name else standard_name
    if not matched_name:
        return title
    if normalized_query == normalized_standard_name:
        return title
    if normalized_matched_name and normalized_query == normalized_matched_name and matched_name != standard_name:
        return f"{title}（{matched_name}）"
    if matched_name != standard_name:
        return f"{title}（{query} -> {matched_name}）"
    return f"{title}（{query}）"


def extract_count(raw_text: str) -> tuple[int, str]:
    count = 1
    text = raw_text
    match = re.search(r"(?<!\d)(\d{1,2})\s*(?:张|个|幅|p|P)?(?!\d)", raw_text)
    if match:
        count = max(1, min(int(match.group(1)), PHOTO_MAX_COUNT))
        text = (raw_text[: match.start()] + " " + raw_text[match.end() :]).strip()
    return count, text


def normalize_query_text(raw_text: str) -> str:
    text = raw_text.strip()
    fillers = [
        "给我",
        "给梦美",
        "来点",
        "来张",
        "来一张",
        "想要",
        "想看",
        "让我看看",
        "我想看",
        "我想要",
        "今天想看",
        "今天想要",
        "发我",
        "发张",
        "发点",
        "整点",
        "看看",
        "照片",
        "图片",
        "涩图",
        "色图",
        "老婆",
        "的",
    ]
    for filler in fillers:
        text = text.replace(filler, " ")
    text = re.sub(r"[，。！？、,.!?；;:：~～/\\\\]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def choose_display_query(raw_query: str, normalized_query: str, profile: CharacterProfile) -> str:
    for candidate in [profile.name, profile.matched_name, *profile.aliases]:
        if not candidate:
            continue
        if normalize_lookup_text(candidate) in normalize_lookup_text(raw_query):
            return candidate
    if normalized_query:
        return normalized_query
    return raw_query.strip()


def resolve_profile(raw_query: str) -> tuple[CharacterProfile | None, str]:
    profile = get_character_profile_from_text(raw_query, config.character_json_path)
    if profile is not None:
        return profile, choose_display_query(raw_query, raw_query.strip(), profile)

    normalized_query = normalize_query_text(raw_query)
    if normalized_query:
        direct_profile = get_character_profile(normalized_query, config.character_json_path)
        if direct_profile is not None:
            return direct_profile, normalized_query

        fuzzy_profile = get_character_profile_from_text(normalized_query, config.character_json_path)
        if fuzzy_profile is not None:
            return fuzzy_profile, choose_display_query(raw_query, normalized_query, fuzzy_profile)

    return None, normalized_query


def pick_random_images(image_files: list[str], count: int) -> list[str]:
    if count <= 1:
        return [random.choice(image_files)]
    if count <= len(image_files):
        return random.sample(image_files, count)
    return [random.choice(image_files) for _ in range(count)]


photo_event = nonebot.on_command(
    "照片",
    aliases={"图片", "涩图", "色图", "来张图", "来张照片", "老婆", "涩涩"},
    priority=5,
    block=True,
)


@photo_event.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = str(event.get_user_id())
    message_id = event.message_id
    raw_query = args.extract_plain_text().strip()

    if user_id not in allowed_users:
        return

    msg = MessageSegment.reply(message_id)

    if not raw_query:
        msg += MessageSegment.text(
            "梦美还不知道你想看谁哦。试试：#图片 观铃、#涩图 kamio，或者 #色图 我想看 2 张观铃。"
        )
        await photo_event.finish(msg)

    count, query_without_count = extract_count(raw_query)
    profile, display_query = resolve_profile(query_without_count)
    if profile is None:
        await photo_event.finish(msg + MessageSegment.text("梦美没有在本地图库里找到对应角色。"))

    image_files = list_character_images(profile.name, config.image_base_folder)
    if not image_files:
        await photo_event.finish(msg + MessageSegment.text(f"梦美这里暂时还没有 {profile.name} 的图片。"))

    picked_images = pick_random_images(image_files, count)
    missing_images = [image_path for image_path in picked_images if not os.path.isfile(image_path)]
    if missing_images:
        await photo_event.finish(msg + MessageSegment.text("梦美翻到了一条失效的图片记录，等我整理一下图库。"))

    title_line = format_title_line(display_query, profile.name, profile.matched_name, profile.game_name)
    if count > 1:
        title_line += f" × {count}"
    msg += MessageSegment.text(f"{title_line}\n")
    for image_path in picked_images:
        msg += MessageSegment.image(image_path)

    try:
        await photo_event.finish(msg, _timeout=PHOTO_SEND_TIMEOUT)
    except ActionFailed as e:
        if is_probable_napcat_send_timeout(e):
            logger.warning(
                "Photo send likely succeeded but NapCat timed out while waiting for ack; "
                f"suppressing retry/log spam. user_id={user_id}, character={profile.name}, count={count}, error={repr(e)}"
            )
            return
        raise
    except (ApiNotAvailable, NetworkError) as e:
        logger.warning(
            "Photo send failed after a single attempt; not retrying. "
            f"user_id={user_id}, character={profile.name}, count={count}, error={repr(e)}"
        )
        return
