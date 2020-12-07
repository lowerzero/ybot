FROM        python:3

RUN         apt-get update && apt-get install --yes --no-install-recommends ffmpeg
RUN         pip3 install -U pip pipenv

WORKDIR     /workdir

COPY        pybot /workdir/pybot
COPY        Pipfile /workdir/Pipfile

RUN         pipenv install

CMD         ["pipenv", "run", "python", "-m", "pybot"]