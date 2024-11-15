from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from src.services.pagination_service import Paginator


class ProductsCallBack(CallbackData, prefix="products"):
    subcategory: str | None = None
    page: int = 1
    product_id: int | None = None


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"
    if paginator.has_next():
        btns["След. ▶"] = "next"
    return btns


def get_callback_btns(*, btns, sizes):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


def get_products_kb(*, subcategory: int, page: int, paginator, product_id: int, sizes: tuple[int] = (2, 1)):
    pagination_btns = pages(paginator)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Купить 💵', callback_data=f"add_to_cart_{product_id}"))
    keyboard.adjust(*sizes)
    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text, callback_data=ProductsCallBack(subcategory=subcategory,
                                                                                      page=page + 1).pack()))
        if menu_name == "previous":
            row.append(InlineKeyboardButton(text=text, callback_data=ProductsCallBack(subcategory=subcategory,
                                                                                      page=page - 1).pack()))

    return keyboard.row(*row).as_markup()
