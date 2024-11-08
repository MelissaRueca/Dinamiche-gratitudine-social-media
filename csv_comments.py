'''
Decodifica e estrazione file zst dei commenti
Impostare subreddit di interesse
Salvataggio in file csv (colonne a scelta)
'''


import zstandard
import os
import json
import sys
from datetime import datetime
import logging.handlers
import pandas as pd

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
    chunk = reader.read(chunk_size)
    bytes_read += chunk_size
    if previous_chunk is not None:
        chunk = previous_chunk + chunk
    try:
        return chunk.decode()
    except UnicodeDecodeError:
        if bytes_read > max_window_size:
            raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
        log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
        return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
    with open(file_name, 'rb') as file_handle:
        buffer = ''
        reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
        while True:
            chunk = read_and_decode(reader, 2**27, (2**29) * 2)

            if not chunk:
                break
            lines = (buffer + chunk).split("\n")

            for line in lines[:-1]:
                yield line, file_handle.tell()

            buffer = lines[-1]
        reader.close()

if __name__ == "__main__":
    file_path = "C:\\Users\\HP\\OneDrive\\Desktop\\Tirocinio\\reddit\\comments\\RC_2023-06.zst"
    file_size = os.stat(file_path).st_size
    file_lines = 0
    file_bytes_processed = 0
    created = None
    field = "subreddit"
    value = "wallstreetbets"
    bad_lines = 0
    
    data_frame = pd.DataFrame(columns=['author', 'author_fullname', 'body', 'created_utc', 'id','parent_id', 'subreddit', 'subreddit_id'])
    
    for line, file_bytes_processed in read_lines_zst(file_path):
        try:
            obj = json.loads(line)
            if obj[field] == "offmychest":
                created = datetime.utcfromtimestamp(int(obj['created_utc']))
                obj_id_sistemato = obj['body'].replace('\n', '').replace('\r', '')
                riga = {'author': obj['author'], 'author_fullname': obj['author_fullname'],'body': obj_id_sistemato, 'created_utc': obj['created_utc'], 'id': obj['id'], 'parent_id': obj['parent_id'], 'subreddit': obj['subreddit'], 'subreddit_id': obj['subreddit_id']}
                data_frame = pd.concat([data_frame, pd.DataFrame([riga])], ignore_index=True)
        except (KeyError, json.JSONDecodeError) as err:
            bad_lines += 1
        file_lines += 1
        if file_lines % 100000 == 0:
            log.info(f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {file_lines:,} lines processed, {bad_lines:,} bad lines, {file_bytes_processed:,} bytes processed, {(file_bytes_processed / file_size) * 100:.0f}% completed")

    log.info(f"Complete : {file_lines:,} lines processed, {bad_lines:,} bad lines")
    data_frame.to_csv('C:\\Users\\HP\\OneDrive\\Desktop\\Tirocinio\\RC_2023-06_offmychest.csv', index=False, header=True)