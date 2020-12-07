import os
import subprocess
import threading

from pybot import set_status, TCD_QUEUE, SEND_QUEUE, FILESIZE_LIMIT, FFMPEG_THREADS


class Transcoder(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.progress = 0
        self.duration = 0
        self.duration_str = ''

        self.src_file = None
        self.dest_file = None

        self.message_id = None
        self.chat_id = None
        self.thumb = None
        self.base_path = None
        self.title = None

        self.keep_running = True

    def set_status(self, status):
        set_status(self.message_id,
                   self.chat_id,
                   status)

    def run(self):
        print('Transcoder thread started')
        while self.keep_running:
            task = TCD_QUEUE.get()

            if task == 'kill':
                self.keep_running = False
                return

            self.progress = 0
            self.duration = 0

            self.src_file = task['src']
            self.dest_file = task['dest']
            self.chat_id = task['chat_id']
            self.message_id = task['message_id']
            self.thumb = task['thumb']
            self.base_path = task['base_path']
            self.title = task['title']

            self.transcode()

    def transcode(self):
        tcd_process = subprocess.Popen(['ffmpeg',
                                        '-threads',
                                        f'{FFMPEG_THREADS}',
                                        '-y',
                                        '-hide_banner',
                                        '-i',
                                        self.src_file,
                                        self.dest_file],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True,
                                       encoding='utf-8')

        self.set_status(f'transcoding {self.duration_str} ⏳')

        for line in tcd_process.stdout:
            clean_line = line.strip()

            if clean_line.startswith('Duration'):
                self.duration_str = clean_line.split(',')[0].split(' ')[-1].split('.')[0]
                dp_hour, dp_min, dp_sec = self.duration_str.split(':')
                self.duration = int(dp_hour) * 60 * 60 + int(dp_min) * 60 + int(dp_sec)
                print(f'Duration {self.duration_str} ({self.duration})')

            if clean_line.startswith('size='):
                tp1 = clean_line.split('=')[2].split(' ')[0].split('.')[0]
                tp_hour, tp_min, tp_sec = tp1.split(':')
                tp_seconds = int(tp_hour) * 60 * 60 + int(tp_min) * 60 + int(tp_sec)

                transcoded = (tp_seconds / (self.duration / 100) / 10)

                if int(transcoded) > self.progress:
                    self.progress = int(transcoded)

                    print(f'Time {tp1} {self.progress * 10} %')

                    self.set_status(f'transcoding {self.duration_str} ⏳ {self.progress * 10} %')

        tcd_process.wait()

        self.set_status('transcoded')

        media = [self.dest_file]

        original_filesize = os.path.getsize(self.dest_file)
        if original_filesize > FILESIZE_LIMIT:
            print(f'original size {original_filesize}')

            segments = int(original_filesize / FILESIZE_LIMIT) + 1
            print(f'segments {segments}')
            print(f'full duration {self.duration}')

            segment_duration = int(self.duration / segments) + 10
            print(f'segment duration {segment_duration}')

            split_process = subprocess.Popen(["ffmpeg",
                                              "-threads",
                                              f"{FFMPEG_THREADS}",
                                              "-y",
                                              "-hide_banner",
                                              "-i",
                                              self.dest_file,
                                              "-c",
                                              "copy",
                                              "-f",
                                              "segment",
                                              "-segment_time",
                                              f'{segment_duration}',
                                              f'{self.base_path}/part-%d.mp3'],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT,
                                             universal_newlines=True,
                                             encoding='utf-8')
            split_process.wait()
            media = [f'{self.base_path}/part-{x}.mp3' for x in range(segments)]

        SEND_QUEUE.put({
            'thumb': self.thumb,
            'media': media,
            'message_id': self.message_id,
            'chat_id': self.chat_id,
            'base_path': self.base_path,
            'title': self.title
        })
