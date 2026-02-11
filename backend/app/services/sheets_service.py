"""
Синхронизация заказов в Google Sheets.
Используется gspread с сервисным аккаунтом.
"""

import json
import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from app.config import get_settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "ID",
    "Тип клиента",
    "ФИО",
    "Телефон",
    "Адрес",
    "Район",
    "ЖВ",
    "ЛВ",
    "Всего",
    "Дата доставки",
    "Статус",
    "Дата создания",
    "Оператор",
]


def get_sheets_client():
    settings = get_settings()
    if not settings.GOOGLE_SHEETS_CREDENTIALS:
        logger.warning("Google Sheets credentials не настроены")
        return None

    try:
        creds_dict = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Ошибка подключения к Google Sheets: {e}")
        return None


def sync_order_to_sheet(order_data: dict) -> bool:
    """
    Синхронизировать заказ в Google Sheets.
    order_data — словарь с данными заказа.
    """
    settings = get_settings()
    if not settings.GOOGLE_SHEET_ID:
        logger.warning("Google Sheet ID не настроен")
        return False

    client = get_sheets_client()
    if not client:
        return False

    try:
        sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
        worksheet = sheet.sheet1

        # Проверить заголовки
        existing = worksheet.row_values(1)
        if not existing:
            worksheet.append_row(HEADERS)

        # Найти строку с этим ID или добавить новую
        order_id = str(order_data.get("id", ""))
        cell = None
        try:
            cell = worksheet.find(order_id, in_column=1)
        except gspread.exceptions.CellNotFound:
            pass

        row = [
            order_data.get("id", ""),
            order_data.get("client_type", ""),
            order_data.get("name", ""),
            order_data.get("phone", ""),
            order_data.get("address", ""),
            order_data.get("district", ""),
            order_data.get("jv_qty", 0),
            order_data.get("lv_qty", 0),
            order_data.get("total_qty", 0),
            str(order_data.get("delivery_date", "")),
            order_data.get("status", ""),
            str(order_data.get("created_at", "")),
            order_data.get("operator", ""),
        ]

        if cell:
            worksheet.update(f"A{cell.row}:M{cell.row}", [row])
        else:
            worksheet.append_row(row)

        return True

    except Exception as e:
        logger.error(f"Ошибка синхронизации с Google Sheets: {e}")
        return False


def prepare_order_data(order, user=None, address=None, operator=None) -> dict:
    """Подготовить данные заказа для Google Sheets."""
    is_new = "Новый" if user and not user.phone else "Постоянный"

    addr_str = ""
    district = ""
    if address:
        addr_str = f"{address.city}, {address.district}, {address.street}, {address.house}"
        district = address.district

    return {
        "id": order.id,
        "client_type": is_new,
        "name": user.name if user else "",
        "phone": user.phone if user else "",
        "address": addr_str,
        "district": district,
        "jv_qty": order.jv_qty,
        "lv_qty": order.lv_qty,
        "total_qty": order.total_qty,
        "delivery_date": order.delivery_date,
        "status": order.status.value if hasattr(order.status, "value") else order.status,
        "created_at": order.created_at,
        "operator": operator.name if operator else "",
    }
