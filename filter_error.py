import os
import json
import time
import socket

# get the current server name and private ip
hostname = socket.gethostname()
private_ip = socket.gethostbyname(hostname)

# get the directory of the log files
log_dir = 'C://zzinfo//errorLog//'

# get the current time
now_time = time.strftime('%Y%m%d%H', time.localtime(time.time()))

# get the log file name
log_file_name = now_time + '.log'

# get the log file path
log_file_path = os.path.join(log_dir, log_file_name)

# read the log file
with open(log_file_path, 'r', encoding='gb18030') as f:
    lines = f.readlines()

# get the line number of errorno=-
errorno_index = [i for i, line in enumerate(lines) if 'errorno=-' in line]

# get the content of errorno=-
errorno_content = []
for index in errorno_index:
    errorno_content.append(lines[index-2:index+2])

# write the content to json
errorno_json = []
for content in errorno_content:
    errorno_json.append({
        'hostname': hostname,
        'private_ip': private_ip,
        'errorno_content': content
    })

# write the json log to fiter_error.log
with open('fiter_error.log', 'w') as f:
    for json_content in errorno_json:
        f.write(json.dumps(json_content, ensure_ascii=False))
        f.write('\n')
