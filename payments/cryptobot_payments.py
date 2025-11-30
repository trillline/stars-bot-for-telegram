import asyncio
import aiohttp
import uuid
import time
from typing import Dict, Any, Optional
from config import load_config
from logs.logging_bot import logger

config = load_config()
base_url = config.cryptobot.url
api_key = config.cryptobot.api_key

async def create_invoice(amount: float, description: str) -> Dict[str, Any]:
    try:
        headers = {
            "Crypto-Pay-API-Token": api_key,
            "Content-Type": "application/json"
        }

        invoice_id = f"cryptobot_{uuid.uuid4().hex[:12]}"

        data = {
            "fiat": "RUB",
            "amount": str(amount),
            "accepted_assets": "USDT,TON,BTC,ETH",
            "currency_type": "fiat",
            "description": description,
            "payload": invoice_id,
            "expires_in": 600
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{base_url}/createInvoice",
                    headers=headers,
                    json=data
            ) as response:

                if response.status == 200:
                    result = await response.json()

                    if result.get("ok"):
                        invoice_data = result.get("result", {})

                        real_invoice_id = invoice_data.get("invoice_id")

                        return {
                            "success": True,
                            "invoice_id": str(real_invoice_id) if real_invoice_id else invoice_id,
                            "payload": invoice_id,
                            "payment_url": invoice_data.get("pay_url", ""),
                            "amount": amount

                        }
                    else:
                        error_info = result.get("error", {})
                        error_name = error_info.get("name", "Unknown error")
                        logger.error(f"Ошибка API CryptoBot: {result}")
                        return {
                            "success": False,
                            "error": f"Ошибка CryptoBot: {error_name}"
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка создания счета CryptoBot: {error_text}")
                    return {
                        "success": False,
                        "error": f"Ошибка API CryptoBot: {response.status}"
                    }

    except Exception as e:
        logger.error(f"Исключение при создании счета CryptoBot: {e}")
        return {
            "success": False,
            "error": "Ошибка соединения с API CryptoBot"
        }


async def get_current_rate(from_asset: str, to_asset: str) -> Optional[float]:
    try:
        rates_result = await get_exchange_rates()

        if not rates_result["success"]:
            return None

        rates = rates_result["rates"]

        for rate in rates:
            if (rate.get("source") == from_asset and
                    rate.get("target") == to_asset and
                    rate.get("is_valid", False)):
                return float(rate.get("rate", 0))

        return None

    except Exception as e:
        logger.error(f"Ошибка получения курса {from_asset}->{to_asset}: {e}")
        return None


async def convert_rub_to_crypto(rub_amount: float, target_asset: str) -> float:
    try:
        rates_result = await get_exchange_rates()

        if not rates_result["success"]:
            logger.error(f"Не удалось получить курсы из CryptoBot API: {rates_result.get('error')}")
            return None

        rates = rates_result["rates"]

        crypto_to_rub_rate = None

        for rate in rates:
            source = rate.get("source", "")
            target = rate.get("target", "")
            rate_value = float(rate.get("rate", 0))
            is_valid = rate.get("is_valid", False)

            if source == target_asset and target == "RUB" and rate_value > 0 and is_valid:
                crypto_to_rub_rate = rate_value
                logger.info(f"Найден актуальный курс {target_asset} -> RUB: {rate_value}")
                break

        if crypto_to_rub_rate is None:
            logger.error(f"Не найден актуальный курс {target_asset} -> RUB в CryptoBot API")
            return None

        crypto_amount = rub_amount / crypto_to_rub_rate

        precision_map = {"BTC": 8, "ETH": 6, "USDT": 2, "USDC": 2, "TON": 4, "SOL": 6, "BNB": 4, "TRX": 2, "LTC": 6,
                         "DOGE": 4}

        precision = precision_map.get(target_asset, 4)
        crypto_amount = round(crypto_amount, precision)

        logger.info(
            f"Конвертация через CryptoBot API: {rub_amount} RUB = {crypto_amount} {target_asset} (курс: 1 {target_asset} = {crypto_to_rub_rate} RUB)")
        return crypto_amount

    except Exception as e:
        logger.error(f"Ошибка конвертации RUB -> {target_asset} через CryptoBot API: {e}")
        return None


async def get_invoice_info(invoice_id: str) -> Dict[str, Any]:
    try:
        headers = {
            "Crypto-Pay-API-Token": api_key,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            if invoice_id.isdigit():
                async with session.get(f"{base_url}/getInvoice", headers=headers,
                                       params={"invoice_id": invoice_id}) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            invoice = result.get("result", {})
                            status = invoice.get("status")
                            amount = invoice.get("amount", '0')
                            return {"success": True, "status": "pending" if status == "active" else status,
                                    "invoice_data": invoice, "amount":amount}

            async with session.get(f"{base_url}/getInvoices", headers=headers,
                                   params={"count": 100}) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        invoices = result.get("result", {}).get("items", [])
                        for invoice in invoices:
                            if str(invoice.get("invoice_id")) == invoice_id or (
                                    invoice.get("payload", "").startswith("cryptobot_") and invoice.get(
                                "payload") == invoice_id):
                                status = invoice.get("status")
                                amount = invoice.get("amount", '0')
                                return {"success": True, "status": "pending" if status == "active" else status,
                                        "invoice_data": invoice, "amount":amount}
                        return {"success": True, "status": "pending"}
                    else:
                        return {"success": False, "error": result.get("error", {}).get("name", "Unknown error")}
                else:
                    return {"success": False, "error": f"Ошибка проверки статуса: {response.status}"}

    except Exception as e:
        logger.error(f"Ошибка проверки статуса CryptoBot: {e}")
        return {"success": False, "error": "Ошибка соединения с API"}


async def get_exchange_rates(force_refresh: bool = False) -> Dict[str, Any]:

    try:
        headers = {
            "Crypto-Pay-API-Token": api_key,
            "Content-Type": "application/json"
        }

        logger.info("Запрашиваем актуальные курсы валют из CryptoBot API")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{base_url}/getExchangeRates",
                    headers=headers
            ) as response:

                if response.status == 200:
                    result = await response.json()

                    if result.get("ok"):
                        rates = result.get("result", [])

                        valid_rates = [rate for rate in rates if rate.get("is_valid", False)]

                        logger.info(f"Получено {len(valid_rates)} актуальных курсов валют")
                        return {
                            "success": True,
                            "rates": valid_rates
                        }
                    else:
                        error_info = result.get("error", {})
                        error_name = error_info.get("name", "Unknown error")
                        logger.error(f"Ошибка API при получении курсов: {error_name}")
                        return {
                            "success": False,
                            "error": error_name
                        }
                else:
                    logger.error(f"HTTP ошибка при получении курсов: {response.status}")
                    return {
                        "success": False,
                        "error": f"Ошибка API: {response.status}"
                    }

    except Exception as e:
        logger.error(f"Исключение при получении курсов валют: {e}")
        return {
            "success": False,
            "error": "Ошибка соединения с API"
        }