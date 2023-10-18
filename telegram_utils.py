import asyncio
import telegram


CHAT_ID_PRIVATE = 571775064
CHAT_ID_BACKUP_GROUP = -651876374

bot_token: dict = {'onsite': '5562358842:AAEhGUm4Bw6RJD4ItT6aop5nPR1XyJXyxX0',
                   'offsite': '5484868873:AAFSw0_ceTr51OT7k2OHCzgrpc7qvc6h9bs'}

def init_bot(token: str) -> telegram.Bot:
    return telegram.Bot(token)

async def read_updates(bot):
    async with bot:
        return (await bot.get_updates())

async def send_message(bot, text, chat_id):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)
