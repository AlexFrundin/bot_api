import pyppeteer as pr
from tempfile import NamedTemporaryFile
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from config import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class ScreenshotUrlState(StatesGroup):
    url = State()


@dp.message_handler(commands=['start'])
async def go_start(message: types.Message):
    await message.reply('Слушаюсь и повинуюсь')


@dp.message_handler(commands=['help'])
async def go_help(message: types.Message):
    await message.reply('Дай мне ссылку сайта и я сделаю его скриншот! Используй для этого команду /go')


@dp.message_handler(commands=['go'])
async def go_url(message: types.Message):
    await ScreenshotUrlState.url.set()
    await message.reply("Введи урл")


@dp.message_handler(state=ScreenshotUrlState.url)
async def process_url(message: types.Message, state: FSMContext):
    #Добавить проверку валидности введенных строки
    url = message.text
    viewport = {"width": 1920, "height": 1080}

    browser = await pr.launch()
    page = await browser.newPage()
    
    await page.goto(url)
    await page.setViewport(viewport=viewport)

    with NamedTemporaryFile() as fp:
        await page.screenshot(path=fp.name, type='jpeg', _quality=100, fullPage=True)
        await message.reply_photo(fp.name)

    await state.finish()
    await browser.close()

if __name__ == '__main__':
    executor.start_polling(dp)
