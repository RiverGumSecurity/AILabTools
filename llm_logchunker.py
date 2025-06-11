#!/usr/bin/env python

import argparse
import sqlite3
import hashlib
import pathlib
import json
import re


class Chunker():

    def __init__(self, filename, overlap=0, regexp=r'.+', jsonmode=False,
                 sqlite_filename='logchunks.db', chunksize=1024):

        self.basedir = pathlib.Path().cwd() / ".data"
        if not self.basedir.is_dir():
            self.basedir.mkdir()

        self.filename = filename
        self.sqlite_filename = self.basedir / sqlite_filename
        self.overlap = overlap
        self.chunksize = chunksize
        self.rxp = re.compile(regexp)

        print(f'[*] LogChunker: SQL database filename = [{self.sqlite_filename}]')
        self.dbh = self.sqlconnect()
        if jsonmode:
            self.chunksize = self.chunksize / 16
            self.parse_json()
        else:
            self.run()

    def run(self):
        cur = self.dbh.cursor()
        total_lines = 0
        chunks = 0
        with open(self.filename, 'rt') as fp:
            last_data = []
            data = ''
            for i, line in enumerate(fp):
                if not self.rxp.match(line):
                    continue
                elif i > 0 and not i % self.chunksize:
                    if self.overlap > 0:
                        data += '\n'.join(last_data[-self.overlap:])
                    sql = 'INSERT OR REPLACE INTO logchunks VALUES (?, ?, ?)'
                    sha256hash = hashlib.sha256(data.encode()).hexdigest()
                    cur.execute(sql, (i // self.chunksize, sha256hash, data))
                    self.dbh.commit()
                    last_data = data.split('\n')
                    chunks += 1
                    data = ''
                last_data.append(line[:-1])
                total_lines += 1
                data += line
        if data:
            sql = 'INSERT OR REPLACE INTO logchunks VALUES (?, ?, ?)'
            sha256hash = hashlib.sha256(data.encode()).hexdigest()
            cur.execute(sql, (i // self.chunksize, sha256hash, data))
            self.dbh.commit()
            chunks += 1
        print(f'[+] Inserted {chunks} chunks consisting of {total_lines} lines of log data into SQL database')

    def parse_json(self):
        cur = self.dbh.cursor()
        chunks = total_lines = 0
        with open(self.filename, 'rt') as fp:
            data = json.load(fp)
        print(f'[+] {self.filename} has {len(data)} JSON records')
        new_data = []
        for i, line in enumerate(data):
            if i > 0 and not i % self.chunksize:
                data_chunk = str(new_data)
                sql = 'INSERT OR REPLACE INTO logchunks VALUES (?, ?, ?)'
                sha256hash = hashlib.sha256(data_chunk.encode()).hexdigest()
                cur.execute(sql, (i // self.chunksize, sha256hash, data_chunk))
                self.dbh.commit()
                new_data = []
                chunks += 1
            new_data.append(line)
            total_lines += 1
        if len(new_data) > 0:
            data_chunk = str(new_data)
            sql = 'INSERT OR REPLACE INTO logchunks VALUES (?, ?, ?)'
            sha256hash = hashlib.sha256(data_chunk.encode()).hexdigest()
            cur.execute(sql, (i // self.chunksize, sha256hash, data_chunk))
            self.dbh.commit()
            chunks += 1
        print(f'[+] Inserted {chunks} chunks consisting of {total_lines} lines of log data into SQL database')

    def sqlconnect(self):
        dbh = sqlite3.connect(self.sqlite_filename)
        sql = '''\
CREATE TABLE IF NOT EXISTS logchunks (
    id INTEGER PRIMARY KEY,
    sha256hash TEXT,
    datachunk BLOB
);'''
        cur = dbh.cursor()
        cur.execute(sql)
        print('[+] Deleting all data in logchunks table')
        cur.execute('DELETE FROM logchunks')
        dbh.commit()
        return dbh


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
---------------------------------------------
  Version 1.0.1, Author: Joff Thyer
  Copyright (c) 2025 River Gum Security LLC
---------------------------------------------''')
    parser.add_argument(
        '-o', '--overlap', type=int, default=20,
        help='number of log recs to overlap/keep (default=20)')
    parser.add_argument(
        '-j', '--json', action='store_true', default=False,
        help='JSON parsing mode')
    parser.add_argument(
        '-cs', '--chunksize', type=int, default=1024,
        help='chunking size factor')
    parser.add_argument(
        '-r', '--regexp', type=str,
        default=r'^\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}.+sshd',
        help='regular expression to match logging line (default=sshd)')
    parser.add_argument('log_filename', help='log file to chunk')
    args = parser.parse_args()
    Chunker(
        args.log_filename,
        overlap=args.overlap,
        regexp=args.regexp,
        jsonmode=args.json,
        chunksize=args.chunksize)
