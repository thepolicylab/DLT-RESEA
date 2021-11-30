import dataclasses
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

CONFIG_PREFIX = "DLT_"
_GLOBAL_CONFIG = None


@dataclass(frozen=True)
class Config:
    DATA_DIR: Optional[str] = None
    REFERENCE_PATH: Optional[str] = None
    INT420_LAYOUT: Optional[str] = None
    LEDGER_LAYOUT: Optional[str] = None
    REAEXT_LAYOUT: Optional[str] = None
    WAGE_LAYOUT: Optional[str] = None

    @classmethod
    def from_env(cls, **kwargs):
        # need to read in the .env file
        load_dotenv()
        for field in dataclasses.fields(Config):
            if field.name not in kwargs:
                name = f"{CONFIG_PREFIX}{field.name}"
                kwargs[field.name] = os.environ.get(name, f"{field} missing in .env")

        return cls(**kwargs)


def set_global_config(config: Optional[Config] = None):
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = config or Config.from_env()


def get_global_config() -> Config:
    if _GLOBAL_CONFIG is None:
        set_global_config()
    return _GLOBAL_CONFIG
