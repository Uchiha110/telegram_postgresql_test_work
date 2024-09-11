from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.dispatcher.router import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.fsm.context import FSMContext
from datetime import datetime
from dateutil.relativedelta import relativedelta

from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from states.start_state import Form
from database import (register_user, get_tariff_by_id, update_user_tariff,
                      get_topic_by_id, update_user_subscription_end, update_user_is_topic,
                      update_user_notification_enabled, get_notification_enabled_by_id, get_all_telegram_ids,
                      update_user_facts, get_facts_by_id)
from cfg.cfg import bot, PAYMENT_TOKEN, GIGA_CHAD_API_KEY

router = Router()
chat = GigaChat(credentials=GIGA_CHAD_API_KEY, verify_ssl_certs=False)


async def tariff_result(data):
    match str(data):
        case "1":
            return "Не имеет подписки"
        case "2":
            return "Стандарт"
        case "3":
            return "Премиум"


async def topic_result(data):
    match str(data):
        case "1":
            return "Тема не задана"
        case "2":
            return "Python"
        case "3":
            return "C++"
        case "4":
            return "Go"


async def notification_enabled_result(data):
    match data:
        case True:
            return "Включены"
        case False:
            return "Выключены"


async def get_facts_gigachad(language, count):
    messages = [
        SystemMessage(
            content="Твоя задача выводить интересные факты об языках программирования"
        )
    ]
    if language == "Python":
        messages.append(HumanMessage(content=f"Выведи {count} факта об {language}"))
    elif language == "C++":
        messages.append(HumanMessage(content=f"Выведи {count} факта об {language}"))
    elif language == "Go":
        messages.append(HumanMessage(content=f"Выведи {count} факта об {language}"))
    res = chat.invoke(messages)
    return res.content


async def enter_data_facts(tariff, language, telegram_id):
    language_ = ""
    match str(language):
        case "1":
            language_ = "none"
        case "2":
            language_ = "Python"
        case "3":
            language_ = "C++"
        case "4":
            language_ = "Go"

    # Определяем количество фактов на основе тарифа
    facts_count = 2 if tariff == "2" else 3 if tariff == "3" else 0

    if facts_count > 0:
        if language_ == "none":
            return "Если вы уже оформили подписку - выберите тему"
        else:
            facts = await get_facts_by_id(telegram_id=telegram_id)
            return facts
    else:
        return "У вас не оформлена подписка. Подпишитесь, чтобы получать факты."


async def update_morning_message():
    telegram_ids = await get_all_telegram_ids()
    for telegram_id in telegram_ids:
        language_ = ""
        tariff = await get_tariff_by_id(telegram_id)
        language = await get_topic_by_id(telegram_id)

        match str(language):
            case "1":
                language_ = "none"
            case "2":
                language_ = "Python"
            case "3":
                language_ = "C++"
            case "4":
                language_ = "Go"

        # Определяем количество фактов на основе тарифа
        facts_count = 2 if tariff == "2" else 3 if tariff == "3" else 0

        if facts_count > 0:
            if language_ == "none":
                pass
            else:
                facts = await get_facts_gigachad(language_, facts_count)
                await update_user_facts(telegram_id=telegram_id, new_facts=facts)
        else:
            pass


async def send_morning_message():
    telegram_ids = await get_all_telegram_ids()
    for telegram_id in telegram_ids:
        language_ = ""
        tariff = await get_tariff_by_id(telegram_id)
        language = await get_topic_by_id(telegram_id)

        match str(language):
            case "1":
                language_ = "none"
            case "2":
                language_ = "Python"
            case "3":
                language_ = "C++"
            case "4":
                language_ = "Go"

        # Определяем количество фактов на основе тарифа
        facts_count = 2 if tariff == "2" else 3 if tariff == "3" else 0

        if facts_count > 0:
            if language_ == "none":
                pass
            else:
                if get_notification_enabled_by_id(telegram_id=telegram_id):
                    await bot.send_message(chat_id=telegram_id, text=get_facts_by_id(telegram_id=telegram_id))
                else:
                    pass
        else:
            pass


async def start_commands(dp):
    @dp.message(Command(commands=["start"]))
    async def start(message: types.Message, state: FSMContext) -> None:
        user_registered = await register_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        if user_registered:
            msg = f"Привет, {message.from_user.first_name}! Вы успешно зарегистрированы!"
        else:
            msg = f"С возвращением, {message.from_user.first_name}!"

        # Кнопки "Тарифы" и "Начать"
        keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Тарифы", callback_data="tariffs_1")],
            [InlineKeyboardButton(text="Начать", callback_data="start__")]
        ])

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        message__ = await message.answer(msg, reply_markup=keyboard__)
        await state.update_data(delete_message=message__.message_id)

        await state.update_data(telegram_id=message.from_user.id)
        await state.update_data(username=message.from_user.username)
        await state.update_data(user_first_name=message.from_user.first_name)
        await state.update_data(user_last_name=message.from_user.last_name)

        await state.set_state(Form.START_DEAFAULT)

    @dp.callback_query(F.data == "tariffs_1")
    async def tariffs(callback: types.CallbackQuery, state: FSMContext) -> None:
        await state.set_state(Form.START_TARIFFS_1)

        data_delete_message = await state.get_data()
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=data_delete_message.get("delete_message")
        )

        msg = ("Стандарт - Получение 2 факта в день, на 1 тему, стоимость - 100р\n"
               "Премиум - Получение 3 факта в день, на 1 тему, стоимость - 500р")

        keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Стандарт", callback_data="standart__")],
            [InlineKeyboardButton(text="Премиум", callback_data="premium__")],
            [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
        ])

        message__ = await callback.message.answer(msg, reply_markup=keyboard__)
        await state.update_data(delete_message=message__.message_id)

    @dp.callback_query(Form.START_DEAFAULT, F.data == "start__")
    async def start(callback: types.CallbackQuery, state: FSMContext) -> None:
        await state.set_state(Form.START_START__)

        data = await state.get_data()
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=data.get("delete_message")
        )

        msg = (f"💫 Добро пожаловать, {callback.from_user.first_name}!\n"
               f"Рад приветствовать тебя в твоём собственном личном кабинете!\n"
               f"Информация о тарифе: {await tariff_result(await get_tariff_by_id(data.get('telegram_id')))}\n"
               f"Тема фактов: {await topic_result(await get_topic_by_id(data.get('telegram_id')))}\n"
               f"Ежедневные уведомленя: {await notification_enabled_result(await get_notification_enabled_by_id(data.get('telegram_id')))}\n"
               f"Последние факты:\n\n{await enter_data_facts(tariff=await get_tariff_by_id(telegram_id=data.get('telegram_id')), language=await get_topic_by_id(data.get('telegram_id')), telegram_id=data.get('telegram_id'))}")

        keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Тарифы", callback_data="tariffs_1")],
            [InlineKeyboardButton(text="Добавить тему", callback_data="add_topic")],
            [InlineKeyboardButton(text="Обновить факты", callback_data="refresh_facts")],
            [InlineKeyboardButton(text="Ежедневные уведомления", callback_data="every_day_message")],
            [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
        ])

        message__ = await callback.message.answer(msg, reply_markup=keyboard__)
        await state.update_data(delete_message=message__.message_id)

    @dp.callback_query(Form.START_START__, F.data == "refresh_facts")
    async def refresh_facts(callback: types.CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=data.get("delete_message")
        )

        msg = "Вы хотите обновить факты?"

        keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Обновить факты", callback_data="refresh")],
            [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
        ])

        await callback.message.answer(msg, reply_markup=keyboard__)

    @dp.callback_query(Form.START_START__, F.data == "refresh")
    async def refresh(message: types.Message) -> None:
        msg = "Факты успешно обновленны!"

        await update_morning_message()
        await message.answer(msg)

    @dp.callback_query(Form.START_START__, F.data == "every_day_message")
    async def every_day_message(callback: types.CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=data.get("delete_message")
        )

        if await get_topic_by_id(data.get('telegram_id')) == "1":
            msg = "Вы не можете пользоваться данной функцией бота, так-как вы не имеете платную подписку"

            keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
            ])

            await callback.message.answer(msg, reply_markup=keyboard__)
        else:
            msg = "Вы хотите включить или выключить функцию ежедневного уведомления от бота?"

            keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Включить", callback_data="on_every_day_message")],
                [InlineKeyboardButton(text="Выключить", callback_data="off_every_day_message")],
                [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
            ])

            await callback.message.answer(msg, reply_markup=keyboard__)

    @dp.callback_query(Form.START_START__, F.data == "on_every_day_message")
    async def on_every_day_message(message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = "Уведомления от бота были включены"

        await update_user_notification_enabled(telegram_id=data.get("telegram_id"), new_notification_enabled=True)
        await message.answer(msg)

    @dp.callback_query(Form.START_START__, F.data == "off_every_day_message")
    async def off_every_day_message(message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = "Уведомления от бота были отключены"

        await update_user_notification_enabled(telegram_id=data.get("telegram_id"), new_notification_enabled=False)
        await message.answer(msg)

    @dp.callback_query(Form.START_START__, F.data == "add_topic")
    async def add_topic(callback: types.CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=data.get("delete_message")
        )

        if await get_tariff_by_id(data.get('telegram_id')) == "1":
            msg = "Вы не можете пользоваться данной функцией бота, так-как вы не имеете платную подписку"

            keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
            ])

            await callback.message.answer(msg, reply_markup=keyboard__)
        else:
            msg = "Выберете тему из представленных ниже"

            keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Python", callback_data="python")],
                [InlineKeyboardButton(text="C++", callback_data="cpp")],
                [InlineKeyboardButton(text="Go", callback_data="go")],
                [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")]
            ])

            await callback.message.answer(msg, reply_markup=keyboard__)

    @dp.callback_query(F.data == "python")
    async def add_topic_python(message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = "Тема изменина на: Python"

        await update_user_is_topic(telegram_id=data.get("telegram_id"), new_is_topic="2")
        await message.answer(msg)

    @dp.callback_query(F.data == "cpp")
    async def add_topic_cpp(message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = "Тема изменина на: C++"

        await update_user_is_topic(telegram_id=data.get("telegram_id"), new_is_topic="3")
        await message.answer(msg)

    @dp.callback_query(F.data == "go")
    async def add_topic_cpp(message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = "Тема изменина на: Go"

        await update_user_is_topic(telegram_id=data.get("telegram_id"), new_is_topic="4")
        await message.answer(msg)

    @dp.callback_query(F.data == "go_to_back__1")
    async def go_to_back__1(callback: types.CallbackQuery, state: FSMContext) -> None:
        await state.set_state(Form.START_DEAFAULT)
        data = await state.get_data()

        user_registered = await register_user(
            telegram_id=data.get('telegram_id'),
            username=data.get('username'),
            first_name=data.get('user_first_name'),
            last_name=data.get('user_last_name')
        )

        data = await state.get_data()

        if user_registered:
            msg = f"Привет, {data.get('user_first_name')}! Вы успешно зарегистрированы!"
        else:
            msg = f"С возвращением, {data.get('user_first_name')}!"

        # Кнопки "Тарифы" и "Начать"
        keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Тарифы", callback_data="tariffs_1")],
            [InlineKeyboardButton(text="Начать", callback_data="start__")]
        ])

        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

        message__ = await callback.message.answer(msg, reply_markup=keyboard__)
        await state.update_data(delete_message=message__.message_id)

    # Платежи

    # Обработчик для кнопки оплаты тарифа "Стандарт"
    @router.callback_query(Form.START_TARIFFS_1, F.data == "standart__")
    async def send_invoice(callback: types.CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()

        # Данные о товаре (тарифе)
        title = "Тариф 'Стандарт'"
        description = "Получение 2 факта в день, на 1 тему"
        payload = "standart_tariff_payment"  # уникальный идентификатор платежа
        currency = "RUB"  # Валюта
        prices = [LabeledPrice(label="Тариф 'Стандарт'", amount=10000)]  # amount в копейках (100 рублей)

        # Отправляем счет пользователю через Telegram
        invoice_message = await bot.send_invoice(
            chat_id=data.get("telegram_id"),
            title=title,
            description=description,
            payload=payload,
            provider_token=PAYMENT_TOKEN,  # Тестовый токен ЮKassa
            currency=currency,
            prices=prices,
        )

        await state.update_data(delete_invoice_message=invoice_message.message_id)

    # Обработчик для кнопки оплаты тарифа "Премиум"
    @router.callback_query(Form.START_TARIFFS_1, F.data == "premium__")
    async def send_invoice(callback: types.CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()

        # Данные о товаре (тарифе)
        title = "Тариф 'Премиум'"
        description = "Получение 3 факта в день, на 1 тему"
        payload = "premium_tariff_payment"  # уникальный идентификатор платежа
        currency = "RUB"  # Валюта
        prices = [LabeledPrice(label="Тариф 'Премиум'", amount=50000)]  # amount в копейках (500 рублей)

        # Отправляем счет пользователю через Telegram
        invoice_message = await bot.send_invoice(
            chat_id=data.get("telegram_id"),
            title=title,
            description=description,
            payload=payload,
            provider_token=PAYMENT_TOKEN,  # Тестовый токен ЮKassa
            currency=currency,
            prices=prices,
        )

        await state.update_data(delete_invoice_message=invoice_message.message_id)

    @router.pre_checkout_query()
    async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        print("pre_checkout_query confirmed")

    @router.message(F.successful_payment)
    async def successful_payment(message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=data.get("delete_message")
        )
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=data.get("delete_invoice_message")
        )

        sp_ = message.successful_payment
        total_amount = sp_.total_amount / 100  # Преобразуем копейки в рубли
        payload = sp_.invoice_payload  # Уникальный идентификатор платежа
        tariff_ = ""
        tariff_num = ""

        current_date = datetime.now()
        new_subscription_end = current_date + relativedelta(months=1)

        match payload:
            case "standart_tariff_payment":
                tariff_ = "Стандарт"
                tariff_num = "2"
            case "premium_tariff_payment":
                tariff_ = "Премиум"
                tariff_num = "3"

        msg = f"Спасибо за оплату {total_amount} рублей! Ваша подписка по тарифу {tariff_} активирована."

        keyboard__ = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться назад", callback_data="go_to_back__1")],
        ])

        await update_user_tariff(telegram_id=data.get('telegram_id'), new_tariff_value=tariff_num)
        await update_user_subscription_end(telegram_id=data.get('telegram_id'),
                                           new_subscription_end=new_subscription_end)
        await update_morning_message()
        await message.answer(msg, reply_markup=keyboard__)
