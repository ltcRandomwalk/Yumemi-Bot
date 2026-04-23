from pydantic import BaseModel
from src.utils.paths import CHARACTER_DATA_PATH, IMAGE_RESOURCE_DIR

class PluginConfig(BaseModel):
    character_json_path: str = str(CHARACTER_DATA_PATH)
    image_base_folder: str = str(IMAGE_RESOURCE_DIR)
