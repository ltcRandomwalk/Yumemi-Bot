import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import CHARACTER_DATA_PATH, IMAGE_RESOURCE_DIR


@dataclass
class CharacterProfile:
    name: str
    raw: dict[str, Any]
    matched_name: str | None = None

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


def normalize_lookup_text(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def get_character_profile(
    name: str,
    json_path: str | Path | None = None,
) -> CharacterProfile | None:
    data = load_character_data(json_path)

    if name in data:
        return CharacterProfile(name=name, raw=data[name], matched_name=name)

    lowered_name = name.lower()
    for character_name, info in data.items():
        for alias in info.get("aliases", []):
            if alias.lower() == lowered_name:
                return CharacterProfile(name=character_name, raw=info, matched_name=alias)

    normalized_name = normalize_lookup_text(name)
    if not normalized_name:
        return None

    exact_matches: list[tuple[int, int, str, str]] = []
    prefix_matches: list[tuple[int, int, str, str]] = []
    partial_matches: list[tuple[int, int, str, str]] = []

    for character_name, info in data.items():
        candidates = [character_name, *info.get("aliases", [])]
        best_match: tuple[int, int, str, str] | None = None
        for index, candidate in enumerate(candidates):
            normalized_candidate = normalize_lookup_text(candidate)
            if not normalized_candidate:
                continue

            match_score: tuple[int, int, str, str] | None = None
            if normalized_candidate == normalized_name:
                match_score = (index, len(normalized_candidate), character_name, candidate)
                exact_matches.append(match_score)
                best_match = match_score
                break
            if normalized_candidate.startswith(normalized_name):
                match_score = (index, len(normalized_candidate), character_name, candidate)
                if best_match is None or match_score < best_match:
                    best_match = match_score
            elif normalized_name in normalized_candidate:
                match_score = (index, len(normalized_candidate), character_name, candidate)
                if best_match is None or match_score < best_match:
                    best_match = match_score

        if best_match is None:
            continue
        if any(normalize_lookup_text(candidate) == normalized_name for candidate in candidates):
            continue
        normalized_character_name = normalize_lookup_text(character_name)
        if normalized_character_name.startswith(normalized_name):
            prefix_matches.append(best_match)
        else:
            partial_matches.append(best_match)

    if exact_matches:
        best_match = min(exact_matches)
        best_name = best_match[2]
        return CharacterProfile(name=best_name, raw=data[best_name], matched_name=best_match[3])
    if prefix_matches:
        best_match = min(prefix_matches)
        best_name = best_match[2]
        return CharacterProfile(name=best_name, raw=data[best_name], matched_name=best_match[3])
    if partial_matches:
        best_match = min(partial_matches)
        best_name = best_match[2]
        return CharacterProfile(name=best_name, raw=data[best_name], matched_name=best_match[3])

    return None


def get_character_profile_from_text(
    text: str,
    json_path: str | Path | None = None,
) -> CharacterProfile | None:
    profile = get_character_profile(text, json_path)
    if profile is not None:
        return profile

    normalized_text = normalize_lookup_text(text)
    if not normalized_text:
        return None

    seen_substrings: set[str] = set()
    min_length = 2
    text_length = len(normalized_text)

    for substring_length in range(text_length, min_length - 1, -1):
        for start in range(0, text_length - substring_length + 1):
            substring = normalized_text[start : start + substring_length]
            if substring in seen_substrings:
                continue
            seen_substrings.add(substring)
            profile = get_character_profile(substring, json_path)
            if profile is not None:
                return profile

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
