from pydantic import BaseModel
from src.utils.paths import CHARACTER_DATA_PATH

class PluginConfig(BaseModel):
    character_json_path: str = str(CHARACTER_DATA_PATH)
