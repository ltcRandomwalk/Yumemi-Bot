import json
import re
import time
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


@lru_cache(maxsize=4)
def load_image_index(
    image_base_folder: str | Path | None = None,
) -> dict[str, tuple[str, ...]]:
    base_dir = Path(image_base_folder) if image_base_folder else IMAGE_RESOURCE_DIR
    index: dict[str, tuple[str, ...]] = {}
    if not base_dir.is_dir():
        return index

    for character_dir in sorted(path for path in base_dir.iterdir() if path.is_dir()):
        index[character_dir.name] = tuple(
            sorted(str(path) for path in character_dir.iterdir() if path.is_file())
        )
    return index


def warmup_character_resource_cache(
    json_path: str | Path | None = None,
    image_base_folder: str | Path | None = None,
) -> dict[str, float]:
    started_at = time.perf_counter()
    character_data = load_character_data(json_path)
    character_data_loaded_at = time.perf_counter()
    image_index = load_image_index(image_base_folder)
    image_index_loaded_at = time.perf_counter()
    return {
        "character_count": float(len(character_data)),
        "image_character_count": float(len(image_index)),
        "character_data_ms": round((character_data_loaded_at - started_at) * 1000, 3),
        "image_index_ms": round((image_index_loaded_at - character_data_loaded_at) * 1000, 3),
        "total_ms": round((image_index_loaded_at - started_at) * 1000, 3),
    }


def normalize_lookup_text(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def _contains_candidate_in_normalized_text(
    normalized_text: str,
    normalized_candidate: str,
) -> bool:
    if not normalized_candidate:
        return False
    if re.fullmatch(r"[a-z0-9]+", normalized_candidate):
        pattern = rf"(?<![a-z0-9]){re.escape(normalized_candidate)}(?![a-z0-9])"
        return re.search(pattern, normalized_text) is not None
    return normalized_candidate in normalized_text


def _contains_candidate_in_text(text: str, candidate: str) -> bool:
    if not candidate:
        return False
    if re.fullmatch(r"[A-Za-z0-9]+", candidate):
        pattern = rf"(?<![A-Za-z0-9]){re.escape(candidate.lower())}(?![A-Za-z0-9])"
        return re.search(pattern, text.lower()) is not None
    return candidate in text


def _is_valid_substring_candidate(
    normalized_text: str,
    substring: str,
    start: int,
    end: int,
) -> bool:
    if not substring:
        return False
    if not re.fullmatch(r"[a-z0-9]+", substring):
        return True

    left_char = normalized_text[start - 1] if start > 0 else ""
    right_char = normalized_text[end] if end < len(normalized_text) else ""
    return not re.fullmatch(r"[a-z0-9]", left_char) and not re.fullmatch(r"[a-z0-9]", right_char)


def _candidate_sort_key(
    priority: int,
    candidate: str,
    character_name: str,
    candidate_index: int,
) -> tuple[int, int, int, int, str, str]:
    normalized_candidate = normalize_lookup_text(candidate)
    return (
        priority,
        0 if candidate_index == 0 else 1,
        -len(normalized_candidate),
        len(candidate),
        character_name,
        candidate,
    )


def _build_profile(
    data: dict[str, dict[str, Any]],
    character_name: str,
    matched_name: str,
) -> CharacterProfile:
    return CharacterProfile(name=character_name, raw=data[character_name], matched_name=matched_name)


def _search_character_candidate_match(
    query: str,
    data: dict[str, dict[str, Any]],
) -> tuple[tuple[int, int, int, int, str, str], str, str] | None:
    normalized_query = normalize_lookup_text(query)
    if not normalized_query:
        return None

    best_match: tuple[tuple[int, int, int, int, str, str], str, str] | None = None

    for character_name, info in data.items():
        candidates = [character_name, *info.get("aliases", [])]
        for candidate_index, candidate in enumerate(candidates):
            normalized_candidate = normalize_lookup_text(candidate)
            if not normalized_candidate:
                continue

            priority: int | None = None
            if candidate_index == 0 and candidate == query:
                priority = 0
            elif candidate_index > 0 and candidate == query:
                priority = 1
            elif candidate_index == 0 and normalized_candidate == normalized_query:
                priority = 2
            elif candidate_index > 0 and normalized_candidate == normalized_query:
                priority = 3
            elif candidate_index == 0 and normalized_candidate.startswith(normalized_query):
                priority = 4
            elif candidate_index > 0 and normalized_candidate.startswith(normalized_query):
                priority = 5
            elif candidate_index == 0 and normalized_query in normalized_candidate:
                priority = 6
            elif candidate_index > 0 and normalized_query in normalized_candidate:
                priority = 7

            if priority is None:
                continue

            sort_key = _candidate_sort_key(priority, candidate, character_name, candidate_index)
            if best_match is None or sort_key < best_match[0]:
                best_match = (sort_key, character_name, candidate)

    return best_match


def _search_character_candidates(
    query: str,
    data: dict[str, dict[str, Any]],
) -> CharacterProfile | None:
    best_match = _search_character_candidate_match(query, data)
    if best_match is None:
        return None
    _, character_name, matched_name = best_match
    return _build_profile(data, character_name, matched_name)


def get_character_profile(
    name: str,
    json_path: str | Path | None = None,
) -> CharacterProfile | None:
    data = load_character_data(json_path)
    return _search_character_candidates(name, data)


def get_character_profile_from_text(
    text: str,
    json_path: str | Path | None = None,
) -> CharacterProfile | None:
    data = load_character_data(json_path)

    direct_match = _search_character_candidate_match(text, data)
    if direct_match is not None:
        _, character_name, matched_name = direct_match
        return _build_profile(data, character_name, matched_name)

    normalized_text = normalize_lookup_text(text)
    if not normalized_text:
        return None

    contained_match: tuple[tuple[int, int, int, int, str, str], str, str] | None = None
    for character_name, info in data.items():
        candidates = [character_name, *info.get("aliases", [])]
        for candidate_index, candidate in enumerate(candidates):
            if not candidate:
                continue
            normalized_candidate = normalize_lookup_text(candidate)
            if not normalized_candidate:
                continue

            priority: int | None = None
            if _contains_candidate_in_text(text, candidate):
                priority = 0 if candidate_index == 0 else 1
            elif _contains_candidate_in_normalized_text(normalized_text, normalized_candidate):
                priority = 2 if candidate_index == 0 else 3

            if priority is None:
                continue

            sort_key = _candidate_sort_key(priority, candidate, character_name, candidate_index)
            candidate_match = (sort_key, character_name, candidate)
            if contained_match is None or candidate_match[0] < contained_match[0]:
                contained_match = candidate_match

    if contained_match is not None:
        _, character_name, matched_name = contained_match
        return _build_profile(data, character_name, matched_name)

    seen_substrings: set[str] = set()
    min_length = 2
    text_length = len(normalized_text)
    best_substring_match: tuple[
        tuple[int, int, tuple[int, int, int, int, str, str]],
        str,
        str,
    ] | None = None

    for substring_length in range(text_length, min_length - 1, -1):
        for start in range(0, text_length - substring_length + 1):
            substring = normalized_text[start : start + substring_length]
            if substring in seen_substrings:
                continue
            seen_substrings.add(substring)
            if not _is_valid_substring_candidate(
                normalized_text,
                substring,
                start,
                start + substring_length,
            ):
                continue
            substring_match = _search_character_candidate_match(substring, data)
            if substring_match is None:
                continue
            match_sort_key, character_name, matched_name = substring_match
            candidate_key = (
                match_sort_key[0],
                -substring_length,
                match_sort_key,
            )
            if best_substring_match is None or candidate_key < best_substring_match[0]:
                best_substring_match = (candidate_key, character_name, matched_name)

    if best_substring_match is not None:
        _, character_name, matched_name = best_substring_match
        return _build_profile(data, character_name, matched_name)

    return None


@lru_cache(maxsize=512)
def _list_character_images_cached(
    character_name: str,
    image_base_folder: str,
) -> tuple[str, ...]:
    return load_image_index(image_base_folder).get(character_name, ())


def list_character_images(
    character_name: str,
    image_base_folder: str | Path | None = None,
) -> list[str]:
    base_dir = Path(image_base_folder) if image_base_folder else IMAGE_RESOURCE_DIR
    return list(_list_character_images_cached(character_name, str(base_dir)))
