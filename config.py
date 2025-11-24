import os
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class BotConfig:
    bot_token: str
    admin_id: int
    username: str

#@dataclass
#class CardlinkSettings:
#    api_key: str
#    shop_id: str

@dataclass
class CryptoBotConfig:
    api_key: str
    url: str

@dataclass
class FragmentConfig:
    phone_number: str
    mnemonics: str
    api_key: str
    jwt_token: str

@dataclass
class VisualConfig:
    photo_file: FSInputFile

@dataclass
class RedisConfig:
    host: str
    port: int
    db_fsm: int
    db_data: int

@dataclass
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: int
    db: str

@dataclass
class LinkConfig:
    news_link: str
    support_link: str

@dataclass
class Config:
    bot: BotConfig
    visuals: VisualConfig
    cryptobot: CryptoBotConfig
 #   cardlink: CardlinkSettings
  #  fragment: FragmentConfig
    redis: RedisConfig
    db: DatabaseConfig
    links: LinkConfig


def load_config() -> Config:
    return Config(
        bot = BotConfig(
            bot_token= os.getenv("BOT_TOKEN"),
            admin_id=int(os.getenv("ADMIN_ID")),
            username=os.getenv("BOT_USERNAME")
        ),
        visuals = VisualConfig(
            photo_file = FSInputFile(path=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),"all_medias"), 'photo_bot.jpg'))
        ),
        redis= RedisConfig(
            host = os.getenv("REDIS_HOST"),
            port = int(os.getenv("REDIS_PORT")),
            db_fsm = int(os.getenv("REDIS_FSM_DB")),
            db_data = int(os.getenv("REDIS_DATA_DB"))
        ),
        db = DatabaseConfig(
            user = os.getenv("DB_USER"),
            host = os.getenv("DB_HOST"),
            password = os.getenv("DB_PASSWORD"),
            db = os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        ),
        links = LinkConfig(
            news_link=os.getenv("NEWS_LINK"),
            support_link=os.getenv("SUPPORT_LINK")
        ),
        cryptobot=CryptoBotConfig(
            api_key=os.getenv("CRYPTOBOT_TOKEN"),
            url=os.getenv("CRYPTOBOT_URL")
        ),
     #   cardlink=CardlinkSettings(
     #       api_key=os.getenv("CARDLINK_TOKEN"),
     #       shop_id=os.getenv("CARDLINK_SHOP_ID")
     #   )
       # fragment=FragmentConfig(
       #     api_key=os.getenv("FRAGMENT_API"),
       #     phone_number=os.getenv("FRAGMENT_PHONENUM"),
       #     mnemonics=os.getenv("FRAGMENT_MNEMONICS"),
       #     jwt_token=os.getenv("FRAGMENT_TOKEN"))
    )


