import asyncio
import uvicorn

from config import config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from router.basic import router as router_basic
from router.shop import router as router_shop
from router.wheel import router as router_wheel

from bot.handler import commands, proof

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

bot = Bot(
    config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Список для хранения задач
tasks = []

def is_event_loop_running():
    try:
        loop = asyncio.get_event_loop()
        return loop.is_running()
    except RuntimeError:
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}",
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types()
    )

    try:
        yield
    except asyncio.CancelledError:
        print("Приложение завершает работу.")
    finally:
        await bot.session.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router_basic)
app.include_router(router_shop)
app.include_router(router_wheel)

dp.include_routers(
    commands.router,
    proof.router
)

@app.post(config.WEBHOOK_PATH)
async def webhooks(request: Request):
    update = Update.model_validate(
        await request.json(),
        context={'bot': bot}
    )
    await dp.feed_update(bot, update)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return True

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=config.APP_HOST,
        port=config.APP_PORT
    )