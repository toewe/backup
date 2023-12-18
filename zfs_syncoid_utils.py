import subprocess
import datetime
month_to_int: dict = {'Jan': 1,
                      'Feb': 2,
                      'Mar': 3,
                      'Apr': 4,
                      'May': 5,
                      'Jun': 6,
                      'Jul': 7,
                      'Aug': 8,
                      'Sep': 9,
                      'Oct': 10,
                      'Nov': 11,
                      'Dec': 12,}

def get_pool_names() -> list[str]:
    pool_names_process: subprocess.CompletedProcess = subprocess.run(['zpool', 'list', '-H', '-o', 'name'], capture_output=True)
    if pool_names_process.returncode or pool_names_process.stderr:
        return ''
    pool_names: str = pool_names_process.stdout.decode().split('\n')[:-1]
    return pool_names

def get_pool_used_space(pool_name: str) -> str:
    free_space_process: subprocess.CompletedProcess = subprocess.run(['zpool', 'list', '-H', pool_name, '-o', 'cap'], capture_output=True)
    if free_space_process.returncode or free_space_process.stderr:
        return ''
    free_space: str = free_space_process.stdout.decode().strip()
    return free_space

def get_pool_status(pool_name: str) -> str:
    status_process: subprocess.CompletedProcess = subprocess.run(['zpool', 'status', pool_name], capture_output=True)
    if status_process.returncode or status_process.stderr:
        return ''
    status: str = status_process.stdout.decode()
    return status

def parse_scrub_state_and_date(status: str) -> tuple[str,  datetime.date] or tuple[None, None]:

    # return if argument is empty or not correct type
    if not status or type(status) != str:
        return (None, None)

    # get relevant line of status message
    scrub_line: str = status.split('scan: ')[-1].split('config:')[0].split('\n')[0]

    # initialize return variable
    scrub_state: str = 'invalid'

    # set string to divide scrub_line and find the date
    scrub_line_divider: str = 'on '

    if 'scan:' not in status:
        scrub_state: str = 'not performed yet'
        scrub_date = None
        return (scrub_state, scrub_date)
        

    # check for current scrub state, set scrub_state accordingly and change scrub_line_divider if necessary
    # scrub_state stays invalid if nothing matches, i.e. unknown state or wrong string was passed
    if 'scrub repaired' in scrub_line:
        scrub_state = 'finished'
    elif 'scrub canceled' in scrub_line:
        scrub_state = 'canceled'
    elif 'scrub paused' in scrub_line:
        scrub_state = 'paused'
        scrub_line_divider: str = 'since '
    elif 'scrub in progress' in scrub_line:
        scrub_state = 'running'
        scrub_line_divider: str = 'since '
    elif 'resilvered' in scrub_line:
        scrub_state = 'resilvered'
    elif 'resilver in progress' in scrub_line:
        scrub_state = 'resilver in progress'
        scrub_line_divider: str = 'since '


    # if known state was detected get date and return, otherwise return None
    if scrub_state != 'invalid':
        # divide scrub_line to get the date and split into list of strings
        scrub_date_list: list = list(filter(bool,scrub_line.split(scrub_line_divider)[-1].split(' ')))
        scrub_date: datetime.date = datetime.date(int(scrub_date_list[4]), month_to_int[scrub_date_list[1]], int(scrub_date_list[2]))    
        return (scrub_state, scrub_date)
    else:
        return (None, None)

def parse_pool_status(status: str, scrub_age_limit: int = 34) -> dict or None:
 
    # return if argument is empty or not correct type
    if not status:
        return None

    # initialize return variable
    status_dict: dict = {'state': '',
                         'scrub': '',
                         'scrub_date': '',
                         'io_errors': ''}
    
    # check state:
    # split status message to get the pool state
    state = status.split('state: ')[-1].split('\n')[0]
    if state != 'ONLINE':
        vdev_states = status.split('config:')[-1].split('errors')[0].strip()
        status_dict['state'] = f'POOL STATE: {state}\n{vdev_states.strip()}\n'
    
    # check scrub state and date
    (scrub_state, scrub_date) = parse_scrub_state_and_date(status)
    if scrub_state != 'finished' and scrub_state != 'not performed yet':
        scrub_segment: str = status.split('scan: ')[-1].split('config:')[0].strip()
        status_dict['scrub'] = f'SCRUB {scrub_state.upper()}:\n{scrub_segment}\n'
    elif scrub_state == 'not performed yet':
        status_dict['scrub'] = f'SCRUB {scrub_state.upper()}'
    if scrub_date is not None:
        now = datetime.date.today()
        delta_days: int = (now - scrub_date).days
        if delta_days > scrub_age_limit:
            status_dict['scrub_date'] = f'SCRUB DATE:\nLast scrub {delta_days} days old.\n'


    # check io errors:
    io_errors = status.split('errors: ')[-1].strip()
    if io_errors != 'No known data errors':
        status_dict['io_errors'] = f'IO ERRORS:\n{io_errors}\n'
    
    return status_dict

def parse_syncoid_log(dataset:str , log: str, known_datasets: dict[str,str] = None) -> tuple[list[tuple[str, str]], bool]:
    # init known_datasets as empty dict if not provided
    if known_datasets is None:
        known_datasets = {}
    
    
    return_datasets: list[tuple[str, str]] = []
    extra_log_entries: bool = False

    log = log.split('\n')
    i: int = 0

    while i < len(log):
        if 'NEWEST SNAPSHOT:' in log[i] and 'Sending incremental' in log[i+1]:
            dataset_from_log:str = log[i+1].split('@')[0].split(' ')[-1]
            if dataset_from_log in known_datasets.keys():
                dataset_from_log: str = known_datasets[dataset_from_log]
            size: str = log[i+1].split('(~')[-1].split(')')[0]
            return_datasets.append((dataset_from_log, size))
            i += 2
            continue
        elif 'NEWEST SNAPSHOT:' in log[i] and 'no snapshots on source newer than' in log[i+1]:
            return_datasets.append((f'some dataset in {dataset}', 'up to date'))
            i += 2
            continue
        elif 'NEWEST SNAPSHOT:' not in log[i] and 'Sending incremental' not in log[i] and log[i].strip() != '':
            extra_log_entries = True
            i += 1
            continue
        i += 1
    
    return return_datasets, extra_log_entries