from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_DIR = PROJECT_ROOT / "resource"
IMAGE_RESOURCE_DIR = RESOURCE_DIR / "images"
CHARACTER_DATA_PATH = RESOURCE_DIR / "character_data.json"

PLUGINS_DIR = PROJECT_ROOT / "src" / "plugins"
KEY_PROPHECY_RESOURCE_DIR = PLUGINS_DIR / "KeyProphecy" / "resource"
GROUP_WELCOME_DATA_DIR = PLUGINS_DIR / "GroupWelcome" / "data"
BIRTHDAY_DATA_DIR = PLUGINS_DIR / "birthday" / "data"
