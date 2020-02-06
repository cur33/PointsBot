import os
import os.path
import pprint
import zipfile

import dateutil.parser
import requests
import simplejson as json

### Globals ###

API_ENDPOINT = 'https://api.github.com'

REPO_OWNER = 'cur33'
REPO_NAME = 'PointsBot'
BRANCH_NAME = 'master'

VERSION_FILE = 'version.json'
ZIP_FILE = 'pointsbot.zip'

### API Call Functions ###


def get_commit_info():
    url = (f'{API_ENDPOINT}/repos/{REPO_OWNER}/{REPO_NAME}/branches/'
           f'{BRANCH_NAME}')
    resp = requests.get(url)
    return resp.json()


def download_archive():
    # :ref omitted to default to master branch
    # To change this behavior, add /:ref to end of url
    url = f'{API_ENDPOINT}/repos/{REPO_OWNER}/{REPO_NAME}/zipball'
    resp = requests.get(url)
    return resp.content


### Data Functions ###


def parse_version_info(commit_info):
    '''Return the relevant fields from the commit json data.'''
    commit_date = commit_info['commit']['commit']['committer']['date']
    return {
        'branch name': commit_info['name'],
        'commit sha': commit_info['commit']['sha'],
        'commit date': dateutil.parser.isoparse(commit_date),
    }


def is_same_branch(ver1, ver2):
    '''Return True if the branch names are identical, False otherwise.'''
    return ver1['branch name'] == ver2['branch name']


def is_newer_commit(ver1, ver2):
    '''Return True if ver1 represents a newer commit than ver2.'''
    return (ver1['commit sha'] != ver2['commit sha']
            and ver1['commit date'] > ver2['commit date'])


### Debug Functions ###


def debug(cur_version_info, rem_version_info):
    print('#' * 80)
    print('Current version info:')
    pprint.pprint(cur_version_info)
    print('#' * 80)
    print('Remove version info:')
    pprint.pprint(rem_version_info)
    print('#' * 80)


### Main ###

if __name__ == '__main__':
    # Get info about repo status via Github API JSON response
    rem_version_data = get_commit_info()

    should_download = False

    if not os.path.exists(VERSION_FILE):
        print(f"Version file not found: '{VERSION_FILE}'")
        should_download = True
    else:
        with open(VERSION_FILE) as f:
            cur_version_data = json.load(f)
        cur_version_info = parse_version_info(cur_version_data)
        rem_version_info = parse_version_info(rem_version_data)

        if not is_same_branch(rem_version_info, cur_version_info):
            print('Name of remote release branch has changed from '
                  f"'{cur_version_info['branch name']}' to "
                  f"'{rem_version_info['branch name']}'")

        if not is_newer_commit(rem_version_info, cur_version_info):
            print('There is a newer version of the bot available')
        else:
            print('The bot is up-to-date')

        answer = input('Download? (y/n) ')
        if answer.startswith('y'):
            should_download = True

    if should_download:
        zipdata = download_archive()
        with open(ZIP_FILE, 'wb') as f:
            f.write(zipdata)
        print(f'ZIP archive written to {ZIP_FILE}')

        answer = input('Update? (y/n) ')
        if answer.startswith('y'):
            if os.path.exists(VERSION_FILE):
                dname, fname = os.path.split(VERSION_FILE)
                backup_path = os.path.join(dname, f'old.{fname}')
                os.rename(VERSION_FILE, backup_path)
                print(f"Current version info saved to '{backup_path}'")

            with open(VERSION_FILE, 'w') as f:
                json.dump(rem_version_data, f)
            print(f"New version info saved to '{VERSION_FILE}'")

            # TODO unzip and update
