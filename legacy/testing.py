import zfs_syncoid_utils as zsu

known_datasets = {'rpool/data/basevol-1002-disk-0': 'nc-template',
                  'rpool/data/subvol-102-disk-1': 'docker',
                  'rpool/data/vm-100-disk-0': 'vm_home_assistant', 
                  'rpool/data/vm-100-disk-1': 'vm_home_assistant_data',
                  'nc-disk/subvol-101-disk-0': 'nc-old',
                  'nc-disk/subvol-103-disk-0': 'nextcloud',
                  'shelf/disks/dummy1': 'shelf_dummy',
                  'shelf/data/archive': 'shelf_archive', 
                  'shelf/data/audio': 'shelf_audio',
                  'shelf/data/backups': 'shelf_backups',
                  'shelf/data/images': 'shelf_images',
                  'shelf/data/photo': 'shelf_photo',
                  'shelf/data/photo/a7iii': 'shelf_photo_a7iii',
                  'shelf/data/photo/a7s': 'shelf_photo_a7s',
                  'shelf/data/photo/analog': 'shelf_photo_analog',
                  'shelf/data/photo/phone_backup': 'shelf_photo_phone_backup'}
syncoid_logs = {'rpool_data':['''NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental rpool/data/basevol-1002-disk-0@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 28 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental rpool/data/subvol-102-disk-1@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 83.6 MB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental rpool/data/vm-100-disk-0@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 28 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental rpool/data/vm-100-disk-1@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 28 KB):''',''],
'nc-disk':['''NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental nc-disk/subvol-101-disk-0@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 28 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:58_hourly
Sending incremental nc-disk/subvol-103-disk-0@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:58_hourly (~ 255.7 MB):''',''],
'shelf_disks':['''NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:58_hourly
Sending incremental shelf/disks/dummy1@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:58_hourly (~ 20 KB):''','Error in this dataset'],
'shelf_data':['''NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental shelf/data/archive@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 14 KB):
Here is something unusal.
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental shelf/data/audio@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 14 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental shelf/data/backups@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 6 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental shelf/data/images@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 14 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:58_hourly
Sending incremental shelf/data/photo@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:58_hourly (~ 6 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:58_hourly
Sending incremental shelf/data/photo/a7iii@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:58_hourly (~ 14 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:58_hourly
Sending incremental shelf/data/photo/a7s@autosnap_2023-08-07_11:07:44_daily ... autosnap_2023-08-10_13:00:58_hourly (~ 6 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental shelf/data/photo/analog@autosnap_2023-08-07_11:07:43_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 6 KB):
NEWEST SNAPSHOT: autosnap_2023-08-10_13:00:59_hourly
Sending incremental shelf/data/photo/phone_backup@autosnap_2023-08-07_11:07:44_daily ... autosnap_2023-08-10_13:00:59_hourly (~ 6 KB):''','']}

pool_msg = '''  pool: rpool
 state: ONLINE
  scan: scrub paused since Tue Sep 26 06:36:39 2023
	scrub started on Fri Sep  1 00:04:32 2023
	0B scanned, 0B issued, 39.9G total
	0B repaired, 0.00% done
config:

	NAME                                               STATE     READ WRITE CKSUM
	rpool                                              ONLINE       0     0     0
	  nvme-eui.e8238fa6bf530001001b444a46344fac-part3  ONLINE       0     0     0

errors: No known data errors
'''

#pool_names: list = zsu.get_pool_names()

pool_names = ['rpool', 'nc-disk', 'shelf']
pool_free_space_dummies: dict = {'rpool': '73%', 'nc-disk': '20%', 'shelf': '45%'}
pool_status_dummies: dict = {'nc-disk': '''  pool: nc-disk
 state: ONLINE
  scan: scrub repaired 0B in 00:07:31 with 0 errors on Fri Sep  1 08:38:32 2023
config:

	NAME                                                 STATE     READ WRITE CKSUM
	nc-disk                                              ONLINE       0     0     0
	  nvme-Samsung_SSD_970_EVO_Plus_2TB_S4J4NX0RA52323D  ONLINE       0     0     0

errors: No known data errors
''',
'rpool': '''  pool: rpool
 state: ONLINE
  scan: scrub canceled 0B in 00:00:50 with 0 errors on Wed Aug 15 13:28:09 2023
config:

	NAME                                               STATE     READ WRITE CKSUM
	rpool                                              ONLINE       0     0     0
	  nvme-eui.e8238fa6bf530001001b444a46344fac-part3  ONLINE       0     0     0

errors: No known data errors
''',
'shelf': '''  pool: shelf
 state: ONLINE
  scan: scrub repaired 0B in 00:35:44 with 0 errors on Fri Aug  1 08:40:35 2023
config:

	NAME                                      STATE     READ WRITE CKSUM
	shelf                                     OFFLINE       0     0     0
	  mirror-0                                OFFLINE       0     0     0
	    374391f3-93bc-41ef-bf40-54d2055140f9  OFFLINE       0     0     0
	    a4de6c72-6bfc-4954-a706-06127442483d  OFFLINE       0     0     0
	  mirror-1                                ONLINE       0     0     0
	    873c6f0e-5c16-4705-a9cc-be2344f512a8  ONLINE       0     0     0
	    e9476262-2fc2-42ba-90e2-9abbd3017eb7  ONLINE       0     0     0

errors: No known data errors
'''}
pool_statuses: dict = {}
for pool in pool_names:
    pool_statuses[pool] = (pool_free_space_dummies[pool], zsu.parse_pool_status(pool_status_dummies[pool]))

##############################
# CREATE POOL STATUS MESSAGE #
##############################

pool_msg: str = 'Pool Status:\n'

for pool in pool_statuses:
    pool_msg += f'{pool}: {pool_statuses[pool][0]} used\n'
    if any(pool_statuses[pool][1].values()):
        for status_type in pool_statuses[pool][1]:
            pool_msg += pool_statuses[pool][1][status_type]
    else:
        pool_msg += 'Status OK\n'
    pool_msg += '\n'

pool_msg.strip()

print(pool_msg)


