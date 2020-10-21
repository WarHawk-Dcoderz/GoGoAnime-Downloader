import requests
from pySmartDL import SmartDL
import subprocess
import sys
import os
import time
import re
import string

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end].strip()
    except ValueError:
        return ""

def clear():
    if os.name in ('nt', 'dos'):
        subprocess.call("cls", shell=True)
    elif os.name in ('linux', 'osx', 'posix'):
        subprocess.call("clear", shell=True)
    else:
        print("\n") * 120

def download(download_link, location):
    obj = SmartDL(download_link, location, progress_bar=True)
    obj.start(blocking=False)

    while not obj.isFinished():
        clear()
        print("Speed: %s" % obj.get_speed(human=True))
        print("Downloading file to '%s'" % obj.get_dest())
        print("Already downloaded: %s" % obj.get_dl_size(human=True))
        print("Eta: %s" % obj.get_eta(human=True))
        print("Progress: %d%%" % (obj.get_progress() * 100))
        print("Progress bar: %s" % obj.get_progress_bar())
        print("Status: %s" % obj.get_status())
        print("\n" * 2 + "=" * 50 + "\n" * 2)
        time.sleep(0.5)

    if obj.isSuccessful():
        clear()
        print("downloaded file to '%s'" % obj.get_dest())
        print("download task took %ss" % obj.get_dl_time(human=True))
        print("File hashes:")
        print(" * MD5: %s" % obj.get_data_hash('md5'))
        print(" * SHA1: %s" % obj.get_data_hash('sha1'))
        print(" * SHA256: %s" % obj.get_data_hash('sha256'))
    else:
        clear()
        print("There were some errors:")
        for e in obj.get_errors():
            print(str(e))

def worker(request2, episode_quality, quality_list, location):
    url2 = find_between(request2.text,
                        '<li class="dowloads"><a href="',
                        '" target="_blank">')
    request3 = requests.get(url2)

    if episode_quality.upper() not in request3.text:
        quality_index = quality_list.index(episode_quality)
        episode_quality = quality_list[int(quality_index) - 1]

    regex = r"<div class=\"dowload\"><a\n                href=\"([^\"]+)\" download>Download\n            \(" + str(
        episode_quality).upper() + " - mp4\)<\/a><\/div>"

    download_link = find_between([x.group() for x in re.finditer(regex, request3.text, re.MULTILINE)][0],
                                 'href="',
                                 '"').replace('&amp;', '&').replace(';', '&').strip()

    location = str(location) + str('Episode ') + str(find_between(request3.text,
                                                'Episode',
                                                '</title>').strip()) + ' - ' + str(episode_quality).upper() + str('.mp4')

    download(download_link, location)

url = input("Enter URL of first episode: " )
try:
    request = requests.get(url)
    if request.status_code == 200:
        all_episode = input("Download all episodes? [y/n]: ").lower()
        
        if all_episode == 'n':
            first_episode = input("Enter episode to start with: ")
            last_episode = input("Enter episode to end with: ")
            
        episode_quality = input("Enter episode quality [HDP/360p/480p/720p/1080p]: ")
        quality_list = ['HDP', '360p', '480p', '720p', '1080p']
        
        if episode_quality not in quality_list:
            print("Invalid episode quality.")
            sys.exit()

        location = './' + string.capwords(find_between(url,
                                 'gogoanime.so/',
                                 '-episode').replace('-', ' ').strip()) + '/'
        if not os.path.exists(location):
            os.makedirs(location)

        url1 = url[:-1]
          
        if all_episode == 'y':
            episodes_count = 0
            download_episodes = True
            while download_episodes:
                episodes_count = episodes_count + 1
                request2 = requests.get(str(url1) + str(episodes_count))
                if '<h1 class="entry-title">404</h1>' not in request2.text:
                    worker(request2, episode_quality, quality_list, location)
                else:
                    break
        else:
            for episodes_count in range(int(first_episode), int(last_episode) + 1):
                request2 = requests.get(str(url1) + str(episodes_count))
                if '<h1 class="entry-title">404</h1>' not in request2.text:
                    worker(request2, episode_quality, quality_list, location)
                else:
                    break

        print('Episodes Downloaded:', episodes_count)

except Exception as e:
    print(e)
    sys.exit()