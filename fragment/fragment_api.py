import aiohttp
import aiogram
from sqlalchemy.orm import with_parent

from config import load_config
from logs.logging_bot import logger

config = load_config()

URL_fragment = "https://api.fragment-api.com/v1"

"""async def fragment_authentication():
    try:
        headers={
            'Content-Type': "application/json",
            'Accept': "application/json"
        }
        data={
            "api_key":config.fragment.api_key,
            "phone_number": config.fragment.phone_number,
            "version": "W5",
            "mnemonics":config.fragment.mnemonics.split()
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{URL_fragment}/v1/auth/authenticate/",
                                    headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    authentication_token = result.get("token", "error")
                    return authentication_token
    except Exception as e:
        logger.error(e)

"""
async def buy_stars(username: str, amount: int):
    try:
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
                else:
                    data = {
                        "status": response.status,
                        "error":result["errors"][0]["error"],
                        "code":result["errors"][0]["code"]
                    }
                return data

    except Exception as e:
        logger.info("Ошибка покупки звёзд ")


async def buy_premium(username: str, month: int):
    try:
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
                else:
                    data = {
                        "status": response.status,
                        "error":result["errors"][0]["error"],
                        "code":result["errors"][0]["code"]
                    }
                return data

    except Exception as e:
        logger.info("Ошибка покупки звёзд")


async def check_order(order_id):
    try:
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
        pass

async def check_balance():
    try:
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
        pass
"""import aiohttp
from typing import Optional, Any
import asyncio


class FragmentAPI:
    def __init__(
            self,
            token: str,
            base_url: str = "https://api.fragment-api.com/v1/",
            auth_scheme: Optional[str] = "JWT",
            user_agent: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.auth_scheme = auth_scheme
        self.user_agent = user_agent or "Mozilla/5.0 (compatible; FragmentAPI/1.0)"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.token:
            if self.auth_scheme:
                headers["Authorization"] = f"{self.auth_scheme} {self.token}"
            else:
                headers["Authorization"] = f"{self.token}"

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with self.session.request(method, url, **kwargs) as resp:
            text = await resp.text()
            content_type = resp.headers.get("Content-Type", "")
            if resp.status >= 400:
                return {
                    "ok": False,
                    "status": resp.status,
                    "content_type": content_type,
                    "text": text,
                    "url": url,
                }
            try:
                data = await resp.json()
                return {"ok": True, "status": resp.status, "data": data}
            except aiohttp.ContentTypeError:
                return {
                    "ok": False,
                    "status": resp.status,
                    "content_type": content_type,
                    "text": text,
                    "url": url,
                }

    async def buy_stars(
            self,
            username: str,
            quantity: int,
            show_sender: bool = False,
            webhook_url: Optional[str] = None,
    ) -> dict[str, Any]:
        if quantity < 50:
            raise ValueError("quantity must be >= 50")

        payload = {"username": username, "quantity": quantity}
        if show_sender:
            payload["show_sender"] = True
        if webhook_url:
            payload["webhook_url"] = webhook_url

        return await self._request("POST", "/order/stars/", json=payload)

    async def gift_premium(
            self,
            username: str,
            months: int,
            show_sender: bool = False,
            webhook_url: Optional[str] = None,
    ) -> dict[str, Any]:
        if months not in (3, 6, 12):
            raise ValueError("months must be 3, 6, or 12")

        payload = {"username": username, "months": months}
        if show_sender:
            payload["show_sender"] = True
        if webhook_url:
            payload["webhook_url"] = webhook_url

        return await self._request("POST", "/order/premium/", json=payload)

    async def CheckOrder(self, order_id: str) -> dict[str, Any]:
        response = await self._request("GET", f"/order/{order_id}/")

        if not response.get("ok"):
            content_type = response.get("content_type", "")
            text = response.get("text", "")

            if content_type.startswith("text/html"):
                return {
                    "ok": False,
                    "status": response.get("status"),
                    "data": None,
                    "error": "Server Error (HTML response instead of JSON)",
                    "url": response.get("url"),
                }

            return {
                "ok": False,
                "status": response.get("status"),
                "data": None,
                "error": text or "Unknown error",
                "url": response.get("url"),
            }
        return {
            "ok": True,
            "status": response["status"],
            "data": response.get("data"),
            "error": None,
        }

    async def GetUserInfo(self, username: str) -> dict[str, Any]:
        path = f"/misc/user/{username}/"
        response = await self._request("GET", path)

        if not response.get("ok"):
            return {
                "ok": False,
                "status": response.get("status"),
                "data": None,
                "error": response.get("text")
            }

        return {
            "ok": True,
            "status": response["status"],
            "data": response.get("data"),
            "error": None
        }"""