import os
from typing import List

from src.utils.character_data import get_character_profile

class Character():
    def __init__(self, name: str):
        self.cha_name = name
        self.game_name: str
        self.aliases: List[str]
        self.birthday: str  # mm-dd
        self.img_path: List[str]
        self.cv: str
        self.staff: str
        self.like: str
        self.age: str
        self.tag: str
        
    def init(self, json_path: str, image_base_path: str) -> bool:
        try:
            profile = get_character_profile(self.cha_name, json_path)
        except Exception as e:
            return False

        if profile is None:
            return False

        self.cha_name = profile.name
        self.game_name = profile.game_name
        self.aliases = profile.aliases
        self.birthday = profile.birthday
        self.img_path = profile.configured_image_paths
        self.img_path = [ os.path.join(image_base_path, img) for img in self.img_path if os.path.isfile(os.path.join(image_base_path, img)) ]
        self.cv = profile.cv
        self.staff = profile.staff
        self.age = profile.age
        self.like = profile.like
        self.tag = profile.tag
        return True
