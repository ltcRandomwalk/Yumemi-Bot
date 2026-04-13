import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import CHARACTER_DATA_PATH, IMAGE_RESOURCE_DIR


@dataclass
class CharacterProfile:
    name: str
    raw: dict[str, Any]

    @property
    def game_name(self) -> str:
        return self.raw.get("game_name", "")

    @property
    def aliases(self) -> list[str]:
        return self.raw.get("aliases", [])

    @property
    def birthday(self) -> str:
        return self.raw.get("birthday", "")

    @property
    def cid(self) -> str:
        return self.raw.get("cid", "")

    @property
    def cv(self) -> str:
        return self.raw.get("cv", "")

    @property
    def staff(self) -> str:
        return self.raw.get("staff", "")

    @property
    def like(self) -> str:
        return self.raw.get("like", "")

    @property
    def age(self) -> str:
        return self.raw.get("age", "")

    @property
    def tag(self) -> str:
        return self.raw.get("tag", "")

    @property
    def configured_image_paths(self) -> list[str]:
        return self.raw.get("img_path", [])


@lru_cache(maxsize=4)
def load_character_data(json_path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    target_path = Path(json_path) if json_path else CHARACTER_DATA_PATH
    with open(target_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("character_data.json 顶层必须是对象")
    return data


def get_character_profile(
    name: str,
    json_path: str | Path | None = None,
) -> CharacterProfile | None:
    data = load_character_data(json_path)

    if name in data:
        return CharacterProfile(name=name, raw=data[name])

    lowered_name = name.lower()
    for character_name, info in data.items():
        for alias in info.get("aliases", []):
            if alias.lower() == lowered_name:
                return CharacterProfile(name=character_name, raw=info)

    return None


@lru_cache(maxsize=512)
def _list_character_images_cached(
    character_name: str,
    image_base_folder: str,
) -> tuple[str, ...]:
    base_dir = Path(image_base_folder)
    character_dir = base_dir / character_name
    if not character_dir.is_dir():
        return ()

    return tuple(sorted(str(path) for path in character_dir.iterdir() if path.is_file()))


def list_character_images(
    character_name: str,
    image_base_folder: str | Path | None = None,
) -> list[str]:
    base_dir = Path(image_base_folder) if image_base_folder else IMAGE_RESOURCE_DIR
    return list(_list_character_images_cached(character_name, str(base_dir)))
