import asyncio
import telegram


MESSAGE_CHAR_LIMIT = 4096
CHAT_ID_PRIVATE = 571775064
CHAT_ID_BACKUP_GROUP = -651876374

BOT_TOKEN: dict = {'onsite': '5562358842:AAEhGUm4Bw6RJD4ItT6aop5nPR1XyJXyxX0',
                   'offsite': '5484868873:AAFSw0_ceTr51OT7k2OHCzgrpc7qvc6h9bs'}

def init_bot(token: str) -> telegram.Bot:
    return telegram.Bot(token)

async def read_updates(bot: telegram.Bot):
    async with bot:
        return (await bot.get_updates())

async def send_message(bot: telegram.Bot, text: str, chat_id: int):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)

def split_message_at_char_limit(msg: str, char_limit: int = MESSAGE_CHAR_LIMIT) -> list[str]:

    return_list: list[str] = []

    for i in range(len(msg)//char_limit + 1):
        return_list.append(msg[i*char_limit:(i+1)*char_limit])

    return return_list