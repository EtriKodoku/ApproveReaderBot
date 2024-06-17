import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from settings import settings

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()


@dp.message(CommandStart)
async def send_welcome(message: types.Message):
    await message.answer("Welcome! This bot handles join requests for a channel.")
    await message.answer(f"ID of this chat is {message.chat.id}")


@dp.chat_join_request()
async def handle_chat_join_request(message: types.ChatJoinRequest):
    time = datetime.datetime.now()
    user = message.from_user
    user_id = user.id
    chat_id = message.chat.id
    print(
        f"{time}: Request {user_id} {user.username if user.username is not None else user.firstname}"
    )
    if chat_id == settings.JOING_CHANNEL_ID:
        try:
            member = await bot.get_chat_member(
                chat_id=settings.CHECK_CHANNEL_ID, user_id=user_id
            )
            # If the user is a member of the check channel, approve the request
            if member.status in ["member", "administrator", "creator"]:
                await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
                if settings.LOG_CHAT_ID is not None:
                    await bot.send_message(
                        settings.LOG_CHAT_ID,
                        f"User {chat_member_update.from_user.full_name} has been approved.",
                    )
            else:
                await bot.send_message(
                    text=f"Щоб увійти, вам потрібно спочатку доєднатись до головного каналу\n{settings.LINK}",
                    chat_id=user_id,
                )
        except Exception as e:
            print(e)
            # Decline the request if there's an error (e.g., user is not found in the check channel)
            await bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
            if settings.LOG_CHAT_ID is not None:
                await bot.send_message(
                    settings.LOG_CHAT_ID,
                    f"Occured error. User {chat_member_update.from_user.full_name} has been declined.",
                )


@dp.chat_member()
async def handle_chat_member_update(chat_member_update: types.ChatMemberUpdated):
    if (
        chat_member_update.old_chat_member.status in ["member", "administrator"]
        and chat_member_update.new_chat_member.status == "left"
    ):

        time = datetime.datetime.now()
        user = chat_member_update.from_user
        user_id = user.id
        chat_id = chat_member_update.chat.id
        if settings.LOG_CHAT_ID is not None:
            await bot.send_message(
                settings.LOG_CHAT_ID,
                f"User {chat_member_update.from_user.full_name} has left the chat.",
            )
        with open("banned.txt", "a") as ban:
            ban.write(
                f"{time} {user_id} {user.username if user.username is not None else user.firstname}\n"
            )
        await bot.ban_chat_member(
            chat_id=settings.JOING_CHANNEL_ID,
            user_id=user_id,
            until_date=time + datetime.timedelta(seconds=30),
        )
        await bot.unban_chat_member(chat_id=settings.JOING_CHANNEL_ID, user_id=user_id)
        await bot.send_message(
            chat_id=user_id,
            text=f"Нам сумно, що ви покидаєте нашу родину🥺. Ви завжди можете повернутись за цим посиланням: {settings.LINK}",
        )


if __name__ == "__main__":
    print("Bot started")
    asyncio.run(dp.start_polling(bot))
