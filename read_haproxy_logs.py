import os
import gzip
import re
from datetime import datetime, timedelta

def read_and_count(file_path):
    # Initialize counters
    v1_chain_counter = 0
    v1_history_counter = 0
    v2_history_counter = 0
    atomicassets_counter = 0
    
    # Existing regex pattern
    pattern1 = re.compile(r' \d+/\d+/\d+/\d+/\d+ 200 \d+ - - [\-\+]+ \d+/\d+/\d+/\d+/\d+ \d+/\d+ \"(POST|GET) /v([12])/([a-zA-Z]+)/.* HTTP/1\.\d+\"')
    
    # New regex pattern for /atomicassets/
    pattern2 = re.compile(r' \d+/\d+/\d+/\d+/\d+ 200 \d+ - - [\-\+]+ \d+/\d+/\d+/\d+/\d+ \d+/\d+ \"(POST|GET) /atomicassets/.* HTTP/1\.\d+\"')

    
    # Check if the file is gzipped
    if file_path.endswith('.gz'):
        f = gzip.open(file_path, 'rt')
    else:
        f = open(file_path, 'r')
        
    # Loop over lines
    for line in f:
        match1 = pattern1.search(line)
        if match1:
            version = match1.group(2)
            request_type = match1.group(3)
            
            if version == '1' and request_type == 'chain':
                v1_chain_counter += 1
            elif version == '1' and request_type == 'history':
                v1_history_counter += 1
            elif version == '2' and request_type == 'history':
                v2_history_counter += 1
        
        match2 = pattern2.search(line)
        if match2:
            atomicassets_counter += 1
                
    f.close()
    
    return v1_chain_counter, v1_history_counter, v2_history_counter, atomicassets_counter


def main():
    # Initialize counters
    total_v1_chain = 0
    total_v1_history = 0
    total_v2_history = 0
    total_atomicassets = 0

    log_dir = '/var/log/'
    current_date = datetime.now()

    # Loop through the last 7 days of log files
    for i in range(8):  # 0 is today, 1 is yesterday, etc.
        date_suffix = current_date - timedelta(days=i)
        log_file = f"{log_dir}haproxy.log"
        
        if i != 0:
            log_file += f".{i}.gz"
        
        if os.path.exists(log_file):
            v1_chain, v1_history, v2_history, atomicassets = read_and_count(log_file)
            total_v1_chain += v1_chain
            total_v1_history += v1_history
            total_v2_history += v2_history
            total_atomicassets += atomicassets
            print(f"Processed {log_file}")

    print(f"Total successful /v1/chain requests: {total_v1_chain}")
    print(f"Total successful /v1/history requests: {total_v1_history}")
    print(f"Total successful /v2/history requests: {total_v2_history}")
    print(f"Total successful /atomicassets/ requests: {total_atomicassets}")


if __name__ == '__main__':
    main()
