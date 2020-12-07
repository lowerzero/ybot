from pybot import TCD_QUEUE, SEND_QUEUE
from pybot.bot import start_listener
from pybot.sender import Sender
from pybot.transcoder import Transcoder

if __name__ == '__main__':
    Transcoder().start()
    Sender().start()

    start_listener()

    TCD_QUEUE.put('kill')
    SEND_QUEUE.put('kill')
