from pydantic import BaseModel
from src.utils.paths import IMAGE_RESOURCE_DIR

class PluginConfig(BaseModel):
    image_base_folder: str = str(IMAGE_RESOURCE_DIR)
