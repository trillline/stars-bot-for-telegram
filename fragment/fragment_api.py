import aiohttp
import aiogram
from sqlalchemy.orm import with_parent

from config import load_config
from logs.logging_bot import logger

config = load_config()

URL_fragment = "https://api.fragment-api.com/v1" # Основной URL Fragment-api

async def buy_stars(username: str, amount: int):
    try:
        logger.info(f"Заказ через fragment на {amount} звёзд для @{username}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"JWT {config.fragment.jwt_token}"
        }
        payload = {
            "username": username,
            "quantity": amount,
            "show_sender": True

        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{URL_fragment}/order/stars/", headers=headers, json=payload) as response:
                result = await response.json()
                if response.status == 200:
                    data = {
                        "status": response.status,
                        "success": result.get("success"),
                        "id": result.get("id")
                    }
                    logger.info(f"Статус 200 для @{username}")
                else:
                    data = {
                        "status": response.status,
                        "error":result["errors"][0]["error"],
                        "code":result["errors"][0]["code"]
                    }
                    logger.info(f"Статус {response.status} для @{username}")
                return data

    except Exception as e:
        logger.error(f"Ошибка покупки звёзд для {username}: {e}")


async def buy_premium(username: str, month: int):
    try:
        logger.info(f"Заказ через fragment {month} мес прем для @{username}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"JWT {config.fragment.jwt_token}"
        }
        payload = {
            "username": username,
            "months": month,
            "show_sender": True

        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{URL_fragment}/order/premium/", headers=headers, json=payload) as response:
                result = await response.json()
                if response.status == 200:
                    data = {
                        "status": response.status,
                        "success": result.get("success"),
                        "id": result.get("id")
                    }
                    logger.info(f"Статус 200 для @{username}")
                else:
                    data = {
                        "status": response.status,
                        "error":result["errors"][0]["error"],
                        "code":result["errors"][0]["code"]
                    }
                    logger.info(f"Статус {response.status} для @{username}")
                return data

    except Exception as e:

        logger.error(f"Ошибка покупки премиума для @{username}: {e}")


async def check_order(order_id):
    try:
        logger.info(f"Проверка заказа {order_id} на fragment")
        headers ={
            "Accept": "application/json",
            "Authorization": f"JWT {config.fragment.jwt_token}"
        }
        body = {
            "id": order_id
        }
        async with aiohttp.ClientSession as session:
            async with session.get(url=f"{URL_fragment}/order/{order_id}/", headers=headers, json=body) as response:
                result = await response.json()
                if response.status == 200:
                    data = {"status":response.status,
                            "success":result.get("success", False),
                            "ref_id": result.get("ref_id", None),
                            }
                else:
                    data = {
                        "status":response.status,
                        "error": result["errors"][0]["error"],
                        "code": result["errors"][0]["code"]
                    }
                return data
    except Exception as e:
        logger.error(f"ОШИБКА проверки заказа {order_id} на fragment: {e}")

async def check_balance():
    try:
        logger.info("Проверяем баланс Fragment")
        headers = {
            "Accept": "application/json",
            "Authorization": f"JWT {config.fragment.jwt_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{URL_fragment}/misc/wallet/", headers=headers) as response:
                result = await response.json()
                if response.status == 200:
                    balance = result.get("balance")
                    return {"status":200, "balance":balance}
                else:
                    return{"status":response.status, "error":result["errors"][0]["error"], "code":result["errors"][0]["code"]}
    except Exception as e:
        logger.error(f"Ошибка проверки баланса fragment: {e}")