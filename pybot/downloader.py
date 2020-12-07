import os
import shutil
import threading

import requests
import youtube_dl
from youtube_dl.utils import ExtractorError, DownloadError

from pybot import set_status, WORKDIR, TCD_QUEUE


class Downloader(threading.Thread):
    def __init__(self, message_id, chat_id, url, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.chat_id = chat_id
        self.message_id = message_id
        self.url = url.split(' ')[-1]

        self.download_progress = 0

    def set_status(self, status):
        set_status(self.message_id,
                   self.chat_id,
                   status)

    def hook(self, update):
        if '_percent_str' not in update:
            return

        percent_main = int(int(update['_percent_str'].split('.')[0].strip()) / 10)

        if int(percent_main) > self.download_progress:
            self.download_progress = int(percent_main)
            self.set_status(f'{update["status"]} ⏳ {self.download_progress * 10} %')

    def run(self):

        for running_thread in threading.enumerate():
            if isinstance(running_thread,
                          Downloader) and running_thread.url == self.url and self.ident != running_thread.ident:
                print("already running")
                return False
        try:
            video_info = youtube_dl.YoutubeDL().extract_info(self.url, download=False)
        except (ExtractorError, DownloadError) as e:
            set_status(self.message_id,
                       self.chat_id,
                       f'{self.url} not a valid youtube url')

            return False

        no_video_formats = [x for x in video_info['formats'] if x['vcodec'] == 'none']

        selected_format = None

        # format id 140
        for x in no_video_formats:
            if x['format_id'] == '140':
                selected_format = x

        if selected_format is None:
            self.set_status('error: no format found')
            return

        file_basepath = f'{WORKDIR}/media/{video_info["id"]}'

        ydl_opts = {
            'format': selected_format['format_id'],
            'outtmpl': f'{file_basepath}/src.{selected_format["ext"]}',
            'forceid': True,
            'restrictfilenames': True
        }

        if os.path.exists(file_basepath):
            shutil.rmtree(file_basepath)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.cache.remove()
            ydl.add_progress_hook(self.hook)
            ydl.download([self.url])

        self.set_status('downloaded')

        # download thumbnail
        thumb_url = video_info['thumbnails'][-1]['url']
        with open(f'{file_basepath}/thumbnail.jpg', 'wb') as fh:
            rsp = requests.get(thumb_url)
            fh.write(rsp.content)

        self.set_status('await transcoding')

        TCD_QUEUE.put({
            'src': f'{file_basepath}/src.{selected_format["ext"]}',
            'dest': f'{file_basepath}/dest.mp3',
            'thumb': f'{file_basepath}/thumbnail.jpg',
            'chat_id': self.chat_id,
            'message_id': self.message_id,
            'base_path': file_basepath,
            'title': video_info['title']
        })
