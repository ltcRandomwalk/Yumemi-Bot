from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    white_list: List[int] = [
        398227078,
        737574359,
        496642207,
        221436683,
        612308690,
        264271679,
        1026440181,
        961707929,
        608533421
    ]
