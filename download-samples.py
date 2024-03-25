#!/usr/bin/python3

# The MIT License (MIT)
#
# Copyright © 2024 Michael Baumgartner, <Michael-Baumgartner@posteo.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import csv
import requests
import os
import shutil
import patch

from pathlib import Path


def get_project_name() -> str:
    # The last to parts of the url (owner name and repository name) form the project name.
    return '-'.join(commit['url'].split('/')[-2:])


def process_file():
    # Download files to the same directory as they are mentioned in the other csv files.
    # For example in column 'after_path' in the change-distiller.csv
    base_path = Path(os.path.join("source-file-samples", get_project_name(), commit['sha'], commit['filename']))
    base_path.mkdir(parents=True, exist_ok=True)

    after_path = base_path.joinpath("after")
    after_path.mkdir(exist_ok=True)
    with open(after_path.joinpath(commit['filename']), mode="wb") as after_file:
        link_after_file = file_json['raw_url']
        after_file.write(requests.get(link_after_file).content)

    before_path = base_path.joinpath("before")
    before_path.mkdir(exist_ok=True)
    shutil.copy(after_path.joinpath(commit['filename']), before_path)
    patch_str = f"--- a/{commit['filename']}\n+++ b/{commit['filename']}\n{file_json['patch']}\n"
    file_patch = patch.fromstring(patch_str.encode())
    file_patch.revert(root=before_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("github_api_token", type=str,
                        help="Token for the GitHub API, so that the rate limit "
                             "for anonymous access does not stop the download. "
                             "Create a token with at least the right to read public repositories here: "
                             "https://github.com/settings/tokens")
    args = parser.parse_args()
    requestHeaders = {"X-GitHub-Api-Version": "2022-11-28",
                      "Authorization": f"Bearer {args.github_api_token}"}
    with open('oracle.csv', newline='') as oracle:
        oracle_reader = csv.DictReader(oracle, delimiter=',', quotechar='"')
        for commit in oracle_reader:
            link = f"{commit['url']}/commits/{commit['sha']}"
            commit_json = requests.get(link, headers=requestHeaders).json()
            for file_json in commit_json['files']:
                if file_json['filename'] == commit['filepath']:
                    process_file()
                    break
            break
