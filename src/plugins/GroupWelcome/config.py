from pydantic import BaseModel
from src.utils.paths import GROUP_WELCOME_DATA_DIR

class PluginConfig(BaseModel):
    welcome_json: str = str(GROUP_WELCOME_DATA_DIR / "data.json")
