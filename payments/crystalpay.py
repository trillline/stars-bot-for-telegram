import aiohttp
from config import load_config


config=load_config()
base_url = config.crystalpay.url

async def create_invoice(amount: float, sender_user_id: int, recipient_username: str, product: str, amount_prod: int):
    try:
        body = {
            "auth_login":config.crystalpay.login,
            "auth_secret":config.crystalpay.secret,
            "amount": int(amount),
            "type": "purchase",
            "lifetime": 15,
            "redirect_url": f"https://t.me/{config.bot.username}",
            "callback_url": f"{config.links.webhook_url}/crystalpay/invoice/",
            "extra":f"{sender_user_id}_{recipient_username}_{product}_{amount_prod}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{base_url}/invoice/create/", json=body) as response:
                result = await response.json()
                if response.status == 200:
                    if not result.get("error"):
                        invoice_url = result.get("url")
                        invoice_id = result.get("id")
                        return {"status":200,"error": False,"payment_url":invoice_url, "invoice_id":invoice_id}
                    else:
                        errors = result.get("errors")
                        return {"status":200, "error": True, "errors": errors}
                else:
                    return{"status":response.status, "error": result.get('error', "error"), "errors": result.get("errors", "errors")}

    except Exception as e:
        pass