from datetime import datetime
from typing import List
import pytz

from src.utils.character_data import load_character_data


def get_birthdays(character_json_path: str, month: int = 0, day: int = 0) -> List[str]:
    """
    获取指定日期生日的人的名字
    :param character_json_path: 统一角色 JSON 文件路径
    :param month: 月
    :param day: 日
    :return: 今天过生日的列表
    """
    if 1 <= month <= 12 and 1 <= day <= 31:
        date = datetime(2024, month, day)
    else:
        date = datetime.now().astimezone(pytz.timezone("Asia/Tokyo"))
    today = date.strftime("%-m-%-d")

    data = load_character_data(character_json_path)
    return sorted(
        character_name
        for character_name, info in data.items()
        if info.get("birthday") == today
    )
