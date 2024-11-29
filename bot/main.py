import os
import asyncio
import logging
from dotenv import load_dotenv
from celery import shared_task
from celery.schedules import crontab
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, StateFilter, Command

from utils import get_tokens, update_access_and_refresh_tokens, get_revenue_by_manager
from db_helper import db_helper
import crud


load_dotenv(override=True)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

amocrm_bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher()

class AuthState(StatesGroup):
    client_id = State()
    secret_key = State()
    redirect_url = State()
    subdomain = State()
    auth_code = State()


class SetReportTimeState(StatesGroup):
    set_time = State()


@dispatcher.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в бот, для получения ежедневной статистики по прадажам менеджеров с платформы amocrm" \
                         "Для начала работы создайте приватную интеграцию, согласно примеру из документации: https://www.amocrm.ru/developers/content/oauth/step-by-step" \
                         "После создания интеграции, используйте команду бота /auth и введите необходимые данные приватной интеграции.")


@dispatcher.message(StateFilter(None), Command('auth'))
async def auth(message: types.Message, state: FSMContext):
    await message.answer("Введите ID интеграции:")
    await state.set_state(AuthState.client_id)


@dispatcher.message(StateFilter(AuthState.client_id))
async def set_client_id(message: types.Message, state: FSMContext):
    await state.update_data(client_id=message.text)
    await message.answer("Введите секретный ключ:")
    await state.set_state(AuthState.secret_key)


@dispatcher.message(StateFilter(AuthState.secret_key))
async def set_secret_key(message: types.Message, state: FSMContext):
    await state.update_data(secret_key=message.text)
    await message.answer("Введите URL для перенаправления, указанный при создании интеграции:")
    await state.set_state(AuthState.redirect_url)


@dispatcher.message(StateFilter(AuthState.redirect_url))
async def set_secret_key(message: types.Message, state: FSMContext):
    await state.update_data(redirect_url=message.text)
    await message.answer("Введите Ваш субдомен:")
    await state.set_state(AuthState.subdomain)


@dispatcher.message(StateFilter(AuthState.subdomain))
async def set_subdomain(message: types.Message, state: FSMContext):
    await state.update_data(subdomain=message.text)
    await message.answer("Введите код авторизации:")
    await state.set_state(AuthState.auth_code)


@dispatcher.message(StateFilter(AuthState.auth_code))
async def set_auth_code(message: types.Message, state: FSMContext):
    await state.update_data(auth_code=message.text)
    data = await state.get_data()
    session = db_helper.get_scoped_session()
    credentials = await crud.set_user_credentials(chat_id=message.chat.id, client_id=data.get("client_id"), 
                                                  secret_key=data.get("secret_key"), redirect_url=data.get("redirect_url"), 
                                                  subdomain=data.get("subdomain"), auth_code=data.get("auth_code"),
                                                  session=session)
    response = get_tokens(credentials)
    if response.status_code != 200:
        await message.answer(response.text)
    else:
        tokens = response.json()
        await crud.set_user_tokens(message.chat.id, tokens["access_token"], tokens["refresh_token"], session)
        await message.answer(f"Авторизация прошла успешно! Каждый день в {os.getenv('REPORT_HOUR')}-{os.getenv('REPORT_MINUTE')} будет приходить отчёт с выручкой по каждому менеджеру.")
    await state.clear()


@shared_task
def send_report_message():
    session = db_helper.get_scoped_session()
    loop = asyncio.get_event_loop()
    credentials = loop.run_until_complete(crud.get_user_credentials(session))
    if credentials is not None:
        tokens = loop.run_until_complete(crud.get_user_tokens(session))
        response = update_access_and_refresh_tokens(credentials, tokens.refresh_token)
        if response.status_code != 200:
            amocrm_bot.send_message(chat_id=credentials.chat_id, text=response.text)
        else:
            data = response.json()
            loop.run_until_complete(crud.set_user_tokens(credentials.chat_id, data["access_token"], data["refresh_token"], session))
            message = get_revenue_by_manager(credentials.subdomain, data["access_token"])
            loop.run_until_complete(amocrm_bot.send_message(chat_id=credentials.chat_id, text=message))  


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dispatcher.start_polling(amocrm_bot)


if __name__ == "__main__":
    asyncio.run(main())

