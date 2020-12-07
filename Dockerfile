FROM        python:3

RUN         apt-get update && apt-get install --yes --no-install-recommends ffmpeg
RUN         pip3 install -U pip youtube-dl python-telegram-bot requests

WORKDIR     /workdir

COPY        pybot /workdir/pybot

CMD         ["python3", "-m", "pybot"]
