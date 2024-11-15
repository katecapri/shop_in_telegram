from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputMediaPhoto, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sys
import traceback

from src.tg_bot.filters.chat_types import ChatTypeFilter
from src.tg_bot.kbds.inline import ProductsCallBack, get_callback_btns, get_products_kb
from src.tg_bot.kbds.reply import get_keyboard

from src.database.repository import Repository
from src.services.pagination_service import Paginator
from src.services.payment_service import create_payment
from src.services.order_service import add_order_in_orders_table
from src.services.log_service import save_log_file

logger = logging.getLogger('app')
user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


class RegistrationStep(StatesGroup):
    name = State()
    phone = State()

class AddProductToCartStep(StatesGroup):
    product_id = State()
    qty = State()
    confirm = State()

class CreateOrderStep(StatesGroup):
    address = State()

class FAQStep(StatesGroup):
    question = State()

# Регистрация пользователя или выдача главного меню
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        repository = Repository(session)
        chat_id = message.chat.id
        user = await repository.get_user_by_chat_id(chat_id)
        if not user:
            await message.reply("Как к Вам можно обращаться?")
            await state.set_state(RegistrationStep.name)
        else:
            main_menu_kb = get_keyboard(['Каталог', 'Корзина', 'FAQ'], placeholder="Что вас интересует?", sizes=(3,))
            await message.reply("Что вас интересует?", reply_markup=main_menu_kb)
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.message(RegistrationStep.name, F.text)
async def ask_phone(message: types.Message, state: FSMContext):
    try:
        user_name = message.text
        await state.update_data(name=user_name)
        request_phone_kb = get_keyboard(['Поделиться телефоном'],
                                        placeholder=f"{user_name}, предоставьте, пожалуйста, Ваш номер телефона",
                                        request_contact=1, sizes=(1,))
        await message.reply("Предоставьте свой номер телефона", reply_markup=request_phone_kb)
        await state.set_state(RegistrationStep.phone)
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.message(RegistrationStep.phone, F.contact)
async def register_user(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        phone_number = message.contact.phone_number.replace('+', '')
        if phone_number.startswith('7'):
            phone_number = '8' + phone_number[1:]
        chat_id = message.chat.id
        data = await state.get_data()
        repository = Repository(session)
        await repository.create_user(chat_id, data["name"], phone_number)
        await state.clear()
        await message.answer('Вы успешно зарегистрированы. Теперь можете перейти к выбору товаров.', 
                             reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.message(F.text == "Каталог")
async def get_main_categories(message: types.Message, session: AsyncSession):
    try:
        repository = Repository(session)
        main_categories = await repository.get_main_categories()
        if main_categories:
            number_of_2 = int(round(len(main_categories) / 2, 0))
            sizes = [2 for _ in range(number_of_2)]
            btns = {cat.name: f"subcategories_{cat.id}" for cat in main_categories}
            main_categories_kb = get_callback_btns(btns=btns, sizes=tuple(sizes))
            await message.answer("Выберите категорию товара: ", reply_markup=main_categories_kb)
        else:
            await message.answer("На данный момент не заведено ни одной категории.")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.callback_query(F.data.startswith("subcategories_"))
async def get_subcategories(callback: types.CallbackQuery, session: AsyncSession):
    try:
        main_category_id = callback.data.split("_")[-1]
        repository = Repository(session)
        subcategories = await repository.get_subcategories_by_category_id(main_category_id)
        if subcategories:
            number_of_2 = int(round(len(subcategories) / 2, 0))
            sizes = [2 for _ in range(number_of_2)]
            btns = {subcat.name: ProductsCallBack(subcategory=str(subcat.id), page=1).pack()
                    for subcat in subcategories}
            subcategories_kb = get_callback_btns(btns=btns, sizes=tuple(sizes))
            await callback.message.answer("Выберите подкатегорию товара: ", reply_markup=subcategories_kb)
        else:
            await callback.message.answer("На данный момент не заведено подкатегорий для выбранной. "
                                          "Просверьте другие разделы.")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.callback_query(ProductsCallBack.filter())
async def get_product(callback: types.CallbackQuery, callback_data: ProductsCallBack, session: AsyncSession):
    try:
        repository = Repository(session)
        products = await repository.get_products_for_subcategory(callback_data.subcategory)
        if products:
            paginator = Paginator(products, page=callback_data.page)
            product = paginator.get_page()[0]
            reply_markup = get_products_kb(subcategory=callback_data.subcategory, page=callback_data.page,
                                           paginator=paginator, product_id=product.id)
            image = FSInputFile(path=f"/application/src/media/images/{product.photo}")
            description = f"{callback_data.page}/{len(products)}: {product.name} \n" \
                          f"{product.description} \n" \
                          f"{product.price} руб."
            if not callback.message.photo:
                await callback.message.answer_photo(photo=image, caption=description, reply_markup=reply_markup)
            else:
                await callback.message.edit_media(InputMediaPhoto(media=image, caption=description),
                                                  reply_markup=reply_markup)
            await callback.answer()
        else:
            await callback.message.answer("В выбранной категории пока что нет товаров.")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    try:
        product_id = callback.data.split("_")[-1]
        await state.set_state(AddProductToCartStep.qty)
        await state.update_data(product_id=product_id)
        await callback.message.answer("Введите количество:")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.message(AddProductToCartStep.qty, F.text)
async def add_to_cart_get_qty(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        try:
            await state.update_data(qty=int(message.text))
        except:
            await message.reply("Введите корректное количество товара")
            return

        await state.set_state(AddProductToCartStep.confirm)

        repository = Repository(session)
        cart_product = await state.get_data()
        product = await repository.get_product_by_id( cart_product["product_id"])
        btns = {
            "Подтверждаю": "confirm_add_product",
            "Изменить количество": "change_qty_add_product",
            "Отмена": "cancel_add_product"
        }
        subcategories_kb = get_callback_btns(btns=btns, sizes=(3,))
        await message.answer(f"Подтвердите добавление товара {product.name} в количестве "
                             f"{cart_product['qty']} шт в корзину.", reply_markup=subcategories_kb)
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.callback_query(AddProductToCartStep.confirm, F.data == "confirm_add_product")
async def confirm_add_to_cart(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        repository = Repository(session)
        chat_id = callback.message.chat.id
        user = await repository.get_user_by_chat_id(chat_id)
        cart_product = await state.get_data()
        await repository.add_product_to_cart(user.id, cart_product["product_id"], cart_product["qty"])
        await callback.message.answer("Товар добавлен в корзину")
        await state.clear()
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.callback_query(AddProductToCartStep.confirm, F.data == "change_qty_add_product")
async def change_qty_add_product(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(AddProductToCartStep.qty)
        await callback.message.answer("Введите количество:")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.callback_query(AddProductToCartStep.confirm, F.data == "cancel_add_product")
async def cancel_add_product(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.answer("Добавление товара в корзину отменено.")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.message(F.text == "Корзина")
async def get_user_cart(message: types.Message, session: AsyncSession):
    try:
        repository = Repository(session)
        chat_id = message.chat.id
        user = await repository.get_user_by_chat_id(chat_id)
        cart_products = await repository.get_cart_products_for_user(user.id)
        if not cart_products:
            await message.reply("Ваша корзина пуста. Можете выбрать товары в каталоге.")
            return
        for cart_product in cart_products:
            product = await repository.get_product_by_id(cart_product.product_id)
            image = FSInputFile(path=f"/application/src/media/images/{product.photo}")
            reply_markup = get_callback_btns(
                btns={f"Удалить {product.name}": f"delete_from_cart_{str(cart_product.id)}"}, sizes=(1,))
            await message.answer_photo(photo=image, caption=f"{product.name}: {cart_product.count} шт",
                                       reply_markup=reply_markup)
        await message.answer("Желаете оформить заказ?",
                             reply_markup=get_callback_btns(btns={f"Оформить заказ": f"create_order"}, sizes=(1,)))
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.callback_query(F.data.startswith("delete_from_cart_"))
async def delete_product_from_cart(callback: types.CallbackQuery, session: AsyncSession):
    try:
        cart_product_id = callback.data.split("_")[-1]
        repository = Repository(session)
        cart_product = await repository.get_cart_product_by_id(cart_product_id)
        product = await repository.get_product_by_id(cart_product.product_id)
        await repository.delete_cart_product_by_id(cart_product_id)
        await callback.message.answer(f"Товар {product.name} удален из корзины.")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.callback_query(F.data.startswith("create_order"))
async def create_order(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(CreateOrderStep.address)
        await callback.message.answer("Введите адрес для доставки:")
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.message(CreateOrderStep.address, F.text)
async def get_address_to_create_order(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        address = message.text
        chat_id = message.chat.id
        repository = Repository(session)
        user = await repository.get_user_by_chat_id(chat_id)
        cart_products = await repository.get_cart_products_for_user(user.id)
        user_order = ""
        total_sum = 0
        for cart_product in cart_products:
            product = await repository.get_product_by_id(cart_product.product_id)
            product_cost = float(product.price) * int(cart_product.count)
            user_order += f"{product.name}: {cart_product.count} шт за {product_cost} руб. \n"
            total_sum += product_cost
        if user_order:
            add_order_in_orders_table(user, address, total_sum, user_order)
            await message.answer(f"Ваш заказ: \n {user_order}"
                                 f"Для оплаты перейдите по ссылке. Менеджер свяжется с вами после оплаты заказа.")
            # payment_url, payment_id = create_payment(total_sum, chat_id)
            # await message.answer(f"{payment_url} {payment_id}")
            await repository.delete_cart_for_user(user.id)
        else:
            await message.answer("Ваша корзина пуста. Выберите что-нибудь в каталоге")
        await state.clear()
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)


@user_private_router.message(F.text == "FAQ")
async def faq_start(message: types.Message, session: AsyncSession, state: FSMContext):
    try:
        await message.answer("Введите интересующий Вас вопрос.")
        await state.set_state(FAQStep.question)
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.message(FAQStep.question, F.text)
async def get_faq_questions(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        words = message.text.split(' ')
        repository = Repository(session)
        result = dict()
        for word in words:
            word_results = await repository.get_faq_by_question_word(word)
            for word_result in word_results:
                if word_result.question not in result:
                    result[word_result.question] = f"faq_question_{word_result.id}"
        if not result:
            all_faq_questions = await repository.get_all_faq_questions()
            for faq_question in all_faq_questions:
                result[faq_question.question] = f"faq_question_{faq_question.id}"

        if not result:
            await message.answer("В данный момент раздел не заполнен. "
                                 "Попробуйте уточнить позже или обратитесь к менеджеру.")
        else:
            reply_markup = get_callback_btns(btns=result, sizes=tuple([1 for _ in range(len(list(result.keys())))]))
            await message.answer(f"Выберите вопрос из списка.", reply_markup=reply_markup)
        await state.clear()
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)

@user_private_router.callback_query(F.data.startswith("faq_question"))
async def get_faq_answer(callback: types.CallbackQuery, session: AsyncSession):
    try:
        faq_question_id = callback.data.split("_")[-1]
        repository = Repository(session)
        faq_question = await repository.get_faq_question_by_id(faq_question_id)
        await callback.message.answer(faq_question.answer)
    except Exception as e:
        logger.error(e, exc_info=True)
        save_log_file(traceback.format_exc(), sys._getframe().f_code.co_name)
