from pydantic import BaseModel
from src.utils.paths import CHARACTER_DATA_PATH, IMAGE_RESOURCE_DIR, KEY_PROPHECY_RESOURCE_DIR

class PluginConfig(BaseModel):
    heroine_path: str = str(KEY_PROPHECY_RESOURCE_DIR / "heroine.txt")
    littlethings_path: str = str(KEY_PROPHECY_RESOURCE_DIR / "littlethings.txt")
    luckythings_path: str = str(KEY_PROPHECY_RESOURCE_DIR / "luckythings.txt")
    character_json_path: str = str(CHARACTER_DATA_PATH)
    image_base_folder: str = str(IMAGE_RESOURCE_DIR)
