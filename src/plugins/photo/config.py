from pydantic import BaseModel
from src.utils.paths import CHARACTER_DATA_PATH, IMAGE_RESOURCE_DIR


class PluginConfig(BaseModel):
    image_base_folder: str = str(IMAGE_RESOURCE_DIR)
    character_json_path: str = str(CHARACTER_DATA_PATH)
    photo_superusers: list[str] = []
