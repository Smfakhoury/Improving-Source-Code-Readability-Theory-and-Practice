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
import sys
import shutil
import patch

from pathlib import Path


def get_project_name() -> str:
    # The last to parts of the url (owner name and repository name) form the project name.
    return '-'.join(commit['url'].split('/')[-2:])


def process_file():
    if file_json['status'] == "renamed":
        print(f"Row {row} of oracle.csv skipped, because the file was only renamed.")
    else:
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
        print(f"Row {row} of oracle.csv processed.")


def get_next_commit_page() -> bool:
    # Use pagination, because with to many files it does not work without it.
    # At about 120 files they are still listed in the json, but the patch is missing.

    # Use 100 files per page -- maximum as mentioned in the documentation:
    # https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#get-a-commit
    files_per_page = 100
    if page > 0 and len(commit_json[page - 1]['files']) < files_per_page:
        # The previous page was not a full page. So there was not enough files in the commit
        # left to list there. This implies it was the last page of the commit.
        print(f"ERROR: File, from row {row} in oracle.csv, could not be found in the commit.",
              file=sys.stderr)
        return False
    else:
        if page >= len(commit_json):
            commit_json.append(requests.get(link, headers=requestHeaders,
                                            params={"page": page, "per_page": files_per_page})
                               .json())
        if 'message' in commit_json[page] and commit_json[page]['message'] == "Not Found":
            print(f"ERROR: Commit, from row {row} in oracle.csv, not found.",
                  file=sys.stderr)
            return False
        else:
            # When there are no files anymore, the last page was already processed.
            return len(commit_json[page]['files']) > 0


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
        row = 0
        oracle_reader = csv.DictReader(oracle, delimiter=',', quotechar='"')
        row += 1
        print(f"Row {row} (header) of oracle.csv processed.")
        previous_link = None
        commit_json: list = []
        for commit in oracle_reader:
            row += 1
            link = f"{commit['url']}/commits/{commit['sha']}"
            # For commits with more files, make only one request for the commit,
            # to reduce calls to GitHub API to a minimum, to avoid reaching the rate limit
            # of 5000 requests per hour for authenticated users.
            if previous_link != link:
                commit_json.clear()
                previous_link = link
            page = 0
            found = False
            while not found and get_next_commit_page():
                for file_json in commit_json[page]['files']:
                    found = file_json['filename'] == commit['filepath']
                    if found:
                        process_file()
                        break
                page += 1
