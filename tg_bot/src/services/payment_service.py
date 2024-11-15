import os
import yookassa
from yookassa import Payment
from uuid import uuid4

yookassa.Configuration.account_id = os.getenv("YOOKASSA_ACCOUNT_ID")
yookassa.Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


def create_payment(total_sum, chat_id):
    id_key = uuid4()
    payment = Payment.create({
        "amount": {
            "value": total_sum,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": os.getenv("BOT_URL")
        },
        "capture": True,
        'metadata': {
            "chat_id": chat_id
        },
        'description': "Оплата заказа",
    }, id_key)
    return payment.confirmation.confirmation_url, payment.id
