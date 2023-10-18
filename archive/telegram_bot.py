import asyncio
import telegram

# async def main():
#     onsite_lsiuefgb_bot = telegram.Bot('5562358842:AAEhGUm4Bw6RJD4ItT6aop5nPR1XyJXyxX0')
#     print('pause')
#     async with onsite_lsiuefgb_bot:
#         print(await onsite_lsiuefgb_bot.get_me())

CHAT_ID_PRIVATE = 571775064
CHAT_ID_BACKUP_GROUP = -651876374

async def send_message_to_group(bot: telegram.Bot, message: str):
    # with open('/home/syncoid/backup_log.txt', 'r') as log_file:
    #     backup_msg = 'BACKUP EXECUTED - LOG:\n\n'
    #     for line in log_file.readlines():
    #         backup_msg += line

    #     print(backup_msg)
    # with open('/home/syncoid/backup_error.txt', 'r') as error_file:
    #     for line in error_file.readlines():
	#         error_msg += line

    onsite_bot = telegram.Bot('5562358842:AAEhGUm4Bw6RJD4ItT6aop5nPR1XyJXyxX0')
#    offsite_bot = telegram.Bot('5484868873:AAFSw0_ceTr51OT7k2OHCzgrpc7qvc6h9bs')

#    print('ONSITE:\n')
#    for update_object in await read_updates(onsite_bot):
#        print(update_object)
#        print()

#    print('OFFSITE:\n')
#    for update_object in await read_updates(offsite_bot):
#        print(update_object)
#        print()

#    await send_message(onsite_bot, text='Private Chat with OnsiteBot', chat_id=CHAT_ID_PRIVATE)
#    await send_message(offsite_bot, text='Private Chat with OffsiteBot', chat_id=CHAT_ID_PRIVATE)
    await send_message(onsite_bot, text=backup_msg, chat_id=CHAT_ID_BACKUP_GROUP)

    await send_message(onsite_bot, text=error_msg, chat_id=CHAT_ID_BACKUP_GROUP)

#    await send_message(offsite_bot, text='Group Chat from OffsiteBot', chat_id=CHAT_ID_BACKUP_GROUP)

async def read_updates(bot):
    async with bot:
        return (await bot.get_updates())

async def send_message(bot, text, chat_id):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)

if __name__ == '__main__':
    asyncio.run(main())
