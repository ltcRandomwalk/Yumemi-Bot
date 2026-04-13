import random
from datetime import datetime
from .config import PluginConfig
from typing import List
import hashlib
from nonebot import get_plugin_config


class Prophecy():
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.variant_seed = f"{self.user_id}_{self.today}"
    
    def seed(self, s):
        return int(hashlib.md5(s.encode()).hexdigest(),16)%(2**32)
        
    def getLuckyPoint(self) -> int:
        random.seed(self.seed(f"lukcypoint_{self.variant_seed}"))
        return random.randint(0, 100)
        
    def getHeroine(self) -> str:
        random.seed(self.seed(f"heroine_{self.variant_seed}"))
        config = get_plugin_config(PluginConfig)
        heroines: List[str]
        with open(config.heroine_path, 'r', encoding='utf-8') as f:
            heroines = [ s.strip() for s in f.readlines() ]
        return random.choice(heroines)
    
    def getDosDonts(self) -> (List[str], List[str]):
        random.seed(self.seed(f"should_do_{self.variant_seed}"))
        config = get_plugin_config(PluginConfig)
        dos: List[str]
        with open(config.littlethings_path, 'r', encoding='utf-8') as f:
            dos = [ s.strip() for s in f.readlines() ]
        samples = random.sample(dos, 6)
        return (samples[:3], samples[3:])
    
    def getLuckyThing(self) -> str:
        random.seed(self.seed(f"lucky_{self.variant_seed}"))
        config = get_plugin_config(PluginConfig)
        with open(config.luckythings_path, 'r', encoding='utf-8') as f:
            lucky_things = [ s.strip() for s in f.readlines() ]
        return random.choice(lucky_things)
    
