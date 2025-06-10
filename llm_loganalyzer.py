#!/usr/bin/env python

import argparse
import sqlite3
import os
import sys
import openai
import time
import pathlib
from datetime import datetime


class LLMLogChunker():

    def __init__(self, prompt, model="gpt-4.1-mini", temp=0.3, prev=False,
                 max_tokens=8192, skip=0, sqlite_filename='logchunks.db',
                 final=False, response_prefix='llm_response'):

        self.basedir = pathlib.Path().cwd() / ".data"
        if not self.basedir.is_dir():
            self.basedir.mkdir()

        openai.api_key = os.getenv("OPENAI_API_KEY")

        # grab prompt
        with open(prompt, 'rt') as fp:
            prompt_content = fp.read()
            self.prompt, self.final_prompt = prompt_content.split('[FINAL_SUMMARY_PROMPT]')
            _, self.prompt = self.prompt.split('[LOG_CHUNK_PROMPT]')

        self.model = model
        self.temp = temp
        self.prev = prev
        self.skip = skip
        self.max_tokens = max_tokens
        self.response_prefix = self.basedir / response_prefix
        self.sqlite_filename = self.basedir / sqlite_filename
        self.dbh = self.sqlconnect()
        self.prev_response = ''
        print(f'[*] LLM Log Analyzer using model [{self.model}]')
        if final:
            self.summarize()
        else:
            self.run()

    def run(self):
        sql = 'SELECT id, datachunk FROM logchunks'
        cur = self.dbh.cursor()
        try:
            cur.execute(sql)
        except sqlite3.OperationalError as e:
            print(f'[-] ERROR: {e} - You need to run log_chunker.py first!')
            sys.exit(1)
        rows = cur.fetchall()
        for i, r in enumerate(rows):
            if i < self.skip:
                continue
            newprompt = f'''\
{self.prompt}

# INPUT

## IncidentID: {datetime.now().strftime("%Y%d%m-%H%M%S")}
## LogChunkID: {r[0]}/{len(rows)}
## LoggingData
{r[1]}
'''
            resp = self.llmquery(newprompt)
            if resp['success']:
                self.prev_response = resp['response']
                filename = f'{self.response_prefix}_{i:002d}.txt'
                with open(filename, 'wt') as fp:
                    print(f'[+] Writing #{i:002d} LLM response to [{filename}]')
                    fp.write(self.prev_response)
            else:
                print(f'[-] ERROR: {resp}')
                sys.exit(0)

    def summarize(self):
        summaries = '# START OF SUMMARIES\n'
        for f in pathlib.Path('.').glob(f'{self.response_prefix}_*.txt'):
            summaries += f'## Summary from filename: {f}\n'
            with open(f, 'rt') as fp:
                summaries += fp.read() + '\n\n'
        summaries += '# END OF SUMMARIES\n'
        prompt = self.final_prompt.format(summaries)
        resp = self.llmquery(prompt)
        if resp['success']:
            print(resp['response'])

    def sqlconnect(self):
        dbh = sqlite3.connect(self.sqlite_filename)
        return dbh

    def llmquery(self, prompt):
        try:
            client = openai.Client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temp,
                max_tokens=self.max_tokens
            )
            return {
                "success": True, "response": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except openai.APIError as e:
            return { "success": False, "error": f"OpenAI API error: {e}", "error_type": "api_error" }
        except openai.RateLimitError as e:
            return { "success": False, "error": f"Rate limit exceeded: {e}", "error_type": "rate_limit" }
        except openai.AuthenticationError as e:
            return { "success": False, "error": f"Authentication failed: {e}", "error_type": "auth_error" }
        except Exception as e:
            return { "success": False, "error": f"Unexpected error: {e}", "error_type": "unknown" }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
---------------------------------------------
  Version 1.0.1, Author: Joff Thyer
  Copyright (c) 2025 River Gum Security LLC
---------------------------------------------''')
    parser.add_argument(
        '-p', action='store_true', default=False,
        help='Print previous/interim LLM responses')
    parser.add_argument(
        '-m', '--model', default='gpt-4o-mini',
        help='OpenAI model to use')
    parser.add_argument(
        '-t', '--temp', type=float, default=0.3,
        help='model temperature setting (default:0.3)')
    parser.add_argument(
        '-mt', '--maxtokens', default=8192,
        help='max tokens (default:8192)')
    parser.add_argument(
        '-s', '--skip', type=int, default=0,
        help='number of log chunks to skip forward to')
    parser.add_argument(
        '-f', '--final', action='store_true', default=False,
        help='produce final summary only')
    parser.add_argument(
        'prompt',
        help='file containing prompt template text')
    args = parser.parse_args()
    LLMLogChunker(
        args.prompt,
        model=args.model, temp=args.temp,
        max_tokens=args.maxtokens,
        prev=args.p, skip=args.skip, final=args.final)
