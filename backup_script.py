import os
import shutil
import subprocess
import zfs_syncoid_utils as zsu
import telegram_utils as tu
import json
import datetime
import asyncio
from time import sleep

location: str = 'offsite'

########################
# Update datasets.json #
########################

datasets_json_updated: bool = False
# nextcloud link to datasets
datasets_share_link: str = 'https://nc.home.arpa/s/GiwSS48Ys2z8XX9/download/datasets.json'

if os.path.exists('dataset.json'):
    shutil.move('datasets.json', 'datasets_old.json')

wget_process = subprocess.run(['wget', '--no-check-certificate', datasets_share_link])

if not os.path.exists('dataset.json'):
    shutil.copy2('datasets_old.json', 'datasets.json')
else:
    datasets_json_updated = True


####################
# SYNCOID COMMANDS #
####################

# variables for syncoid command
syncoid_command: str = 'syncoid'
syncoid_user: str = 'syncoid'
source_host: str = 'pve.home.arpa'
ssh_port: int = 2425
sendoptions: str = 'w'
destination_root_pool: str = 'backup'


# DEPRECATED
# list of datasets tuples of (source, destination)
# root_datasets: list[tuple[str, str]] = [('rpool/data', 'rpool_data'),
#                                         ('nc-disk', 'nc_disk'),
#                                         ('shelf/data', 'shelf_data'),
#                                         ('shelf/disks', 'shelf_disks')]

#todo
########################
# UPDATE DATASETS.JSON #
########################
# curl_process = subprocess.run(['curl', '-k', datasets_share_link, '>>', 'datasets_update.json'], capture_output=True)
# if curl_process.returncode != 0:
#     datasets_updated = False
# elif


# load datasets to sync
with open('datasets.json', 'r') as f:
    json_datasets = json.loads(f.read())

# intializing datasets to copy and parsing json file:
root_datasets = {}
known_datasets = {}
for json_dataset in json_datasets['datasets']:
    root_datasets[json_dataset['source']] = json_dataset['destination']
    for known_dataset_path, known_dataset_name in zip(json_dataset['known_datasets'].keys(), json_dataset['known_datasets'].values()):
        known_datasets[known_dataset_path] = known_dataset_name


syncoid_logs: dict[str, tuple[str, str]] = {}
# iterating over datasets and invoking syncoid command
for source_root_dataset, destination_root_dataset in root_datasets:
    syncoid_process = subprocess.run([syncoid_command,
                                      f'--sendoptions={sendoptions}',
                                      '--no-privilege-elevation',
                                      '--no-sync-snap',
                                      '--skip-parent',
                                      '-r', 
                                      '--sshport',
                                      f'{ssh_port}',
                                      f'{syncoid_user}@{source_host}:{source_root_dataset}',
                                      f'{destination_root_pool}/{destination_root_dataset}'
                                     ],
                                     capture_output=True,
                                    )

    syncoid_logs[destination_root_dataset] = (syncoid_process.stdout.decode(), syncoid_process.stderr.decode())


#####################
# PARSE SYNCOID LOG #
#####################

parsed_datasets: dict[str, tuple[list[tuple[str, str]], str, str]] = {}

for destination_root_dataset in syncoid_logs:
    partial_parsed_datasets, extra_log_entries_present = zsu.parse_syncoid_log(destination_root_dataset, syncoid_logs[destination_root_dataset][0], known_datasets)
    if extra_log_entries_present:
        extra_stdout = syncoid_logs[destination_root_dataset][0]
    else:
        extra_stdout = ''
    parsed_datasets[destination_root_dataset] = (partial_parsed_datasets, extra_stdout, syncoid_logs[destination_root_dataset][1])

##########################
# CREATE SYNCOID MESSAGE #
##########################

syncoid_msg_prefix_error_template: str = 'ERROR!\n'
syncoid_msg_prefix_attention_template: str = 'ATTENTION!\n'
syncoid_msg_prefix: str = ''
syncoid_msg: str = f'{location.capitalize()} Backup:\n'
for destination_root_dataset in parsed_datasets:
    # set prefix if additional stdout or stderr detected
    if parsed_datasets[destination_root_dataset][1] and syncoid_msg_prefix != syncoid_msg_prefix_error_template:
        syncoid_msg_prefix = syncoid_msg_prefix_attention_template
    if parsed_datasets[destination_root_dataset][2]:
        syncoid_msg_prefix = syncoid_msg_prefix_error_template
    

    syncoid_msg += f'--- {destination_root_dataset} ---\n'
    # find max len dataset
    for dataset in parsed_datasets[destination_root_dataset][0]:
        syncoid_msg += f'{dataset[0]}: {dataset[1]}\n'

    if parsed_datasets[destination_root_dataset][1]:
        syncoid_msg += f'\nLOG of {destination_root_dataset}:\n{parsed_datasets[destination_root_dataset][1]}\n'
    if parsed_datasets[destination_root_dataset][2]:
        syncoid_msg += f'\nERROR LOG of {destination_root_dataset}:\n{parsed_datasets[destination_root_dataset][2]}\n'

    syncoid_msg += '\n'

# if prefix was set during msg generation, prepend to message:
if syncoid_msg_prefix:
    syncoid_msg = syncoid_msg_prefix + syncoid_msg

print(syncoid_msg)

###############################
# COLLECT LOCAL POOL STATUSES #
###############################

pool_names: str = zsu.get_pool_names()

pool_statuses: dict = {}
for pool in pool_names:
    pool_statuses[pool] = (zsu.get_pool_used_space(pool), zsu.parse_pool_status(zsu.get_pool_status(pool)))

###############################
# CREATE POOL STATUS MESSAGES #
###############################

pool_msg: str = f'{location.capitalize()} Pool Status:\n'

for pool in pool_statuses:
    pool_msg += f'{pool}:\n'
    pool_msg += f'- {pool_statuses[pool][0]} used\n'
    if any(pool_statuses[pool][1].values()):
        for status_type in pool_statuses[pool][1]:
            pool_msg += f'- {pool_statuses[pool][1][status_type]}'
    else:
        pool_msg += '- Status OK\n'

############
# TELEGRAM #
############

# init telegram bot
telegram_bot = tu.telegram.Bot(tu.BOT_TOKEN[location])

### syncoid message
# check if message length is too long
if len(syncoid_msg) < tu.MESSAGE_CHAR_LIMIT:
    syncoid_messages: list[str] = [syncoid_msg]
else:
    syncoid_messages: list[str] = tu.split_message_at_char_limit(syncoid_msg)

# send list of messages
for message in syncoid_messages:
    asyncio.run(tu.send_message(telegram_bot, message, chat_id=tu.CHAT_ID_BACKUP_GROUP))
    sleep(4)

### pool message
# check if message length is too long
if len(syncoid_msg) < tu.MESSAGE_CHAR_LIMIT:
    syncoid_messages: list[str] = [syncoid_msg]
else:
    syncoid_messages: list[str] = tu.split_message_at_char_limit(syncoid_msg)

# send list of messages
for message in syncoid_messages:
    asyncio.run(tu.send_message(telegram_bot, message, chat_id=tu.CHAT_ID_BACKUP_GROUP))
    sleep(4)

asyncio.run(tu.send_message(telegram_bot, pool_msg, chat_id=tu.CHAT_ID_BACKUP_GROUP))

#########
# SCRUB #
#########

pool_names: str = zsu.get_pool_names()

pool_scrub_states: dict = {}
for pool in pool_names:
    pool_scrub_states[pool] = zsu.parse_scrub_state_and_date(zsu.get_pool_status(pool))

now = datetime.date.today()
for pool in pool_scrub_states:
    if pool_scrub_states[pool][1] == None:
        continue
    if 'in progress' in pool_scrub_states[pool][0]:
        continue 
    delta_days: int = (now - pool_scrub_states[pool][1]).days
    if delta_days > 34:
        
        scrub_message: str = f'Starting SCRUB for {pool}.'
        asyncio.run(tu.send_message(telegram_bot, scrub_message, chat_id=tu.CHAT_ID_BACKUP_GROUP))
        subprocess.run(['zpool', 'scrub','-w', pool])

        pool_status = zsu.get_pool_status(pool)
        scrub_message = f'Finished SCRUB for {pool}:\n'
        if any(pool_statuses[pool][1].values()):
            for status_type in pool_statuses[pool][1]:
                scrub_message += f'- {pool_statuses[pool][1][status_type]}'
        else:
            scrub_message += '- Status OK\n'
        asyncio.run(tu.send_message(telegram_bot, scrub_message, chat_id=tu.CHAT_ID_BACKUP_GROUP))
