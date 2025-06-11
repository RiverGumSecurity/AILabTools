#!/usr/bin/env python

import argparse
import sqlite3
import hashlib
import pathlib
import re


class Chunker():

    def __init__(self, filename, overlap=0, regexp=r'.+',
                 sqlite_filename='logchunks.db', chunksize=1000):

        self.basedir = pathlib.Path().cwd() / ".data"
        if not self.basedir.is_dir():
            self.basedir.mkdir()

        self.filename = filename
        self.sqlite_filename = self.basedir / sqlite_filename
        self.overlap = overlap
        self.chunksize = chunksize
        self.rxp = re.compile(regexp)
        self.dbh = self.sqlconnect()
        self.run()

    def run(self):
        cur = self.dbh.cursor()
        with open(self.filename, 'rt') as fp:
            last_data = []
            data = ''
            for i, line in enumerate(fp):
                if not self.rxp.match(line):
                    continue
                elif i > 0 and not i % self.chunksize:
                    if self.overlap > 0:
                        data += '\n'.join(last_data[-self.overlap:])
                    print(f'[*] Log chunk #{i//1000:03d} with {len(data.split('\n'))} lines of log data inserted into SQL db')
                    sql = 'INSERT OR REPLACE INTO logchunks VALUES (?, ?, ?)'
                    sha256hash = hashlib.sha256(data.encode()).hexdigest()
                    cur.execute(sql, (i // 1000, sha256hash, data))
                    self.dbh.commit()
                    last_data = data.split('\n')
                    data = ''
                last_data.append(line[:-1])
                data += line

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
         help='number of log lines to overlap/keep from last round (default=20)')
    parser.add_argument(
        '-r', '--regexp', type=str,
        default=r'^\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}.+sshd',
        help='regular expression to match logging line (default=sshd)')
    parser.add_argument('log_filename', help='log file to chunk')
    args = parser.parse_args()
    Chunker(args.log_filename, overlap=args.overlap, regexp=args.regexp)
