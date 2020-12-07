import os
import shutil
import threading

from pybot import set_status, SEND_QUEUE, send_photo, PUBLIC_CHANNEL, send_audio


class Sender(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.message_id = None
        self.chat_id = None
        self.media = []
        self.thumb = None
        self.base_path = None
        self.title = None

        self.keep_running = True

    def set_status(self, status):
        set_status(self.message_id,
                   self.chat_id,
                   status)

    def run(self):
        print('Sender thread started')
        while self.keep_running:
            task = SEND_QUEUE.get()

            if task == 'kill':
                self.keep_running = False
                return

            self.media = task['media']
            self.chat_id = task['chat_id']
            self.message_id = task['message_id']
            self.thumb = task['thumb']
            self.base_path = task['base_path']
            self.title = task['title']

            self.set_status('sending picture')

            with open(self.thumb, 'rb') as fh:
                send_photo(PUBLIC_CHANNEL, fh)

            self.set_status('sending media')

            if len(self.media) > 1:
                for n, m in enumerate(self.media):
                    with open(m, 'rb') as fh:
                        print(f'sending {m}')
                        send_audio(PUBLIC_CHANNEL, fh, f'[{n + 1}/{len(self.media)}] {self.title}')
            else:
                send_audio(PUBLIC_CHANNEL, fh, self.title)

            if os.path.exists(self.base_path):
                shutil.rmtree(self.base_path)

            self.set_status('Done ✅')
