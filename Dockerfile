FROM python:3.11-slim-bullseye

LABEL author "git-ogawa" \
    version "0.1.0"

COPY . /pylogcounter
RUN pip install --no-cache /pylogcounter && \
    rm -rf /pylogcounter

WORKDIR /work
ENTRYPOINT [ "pylogcounter" ]
CMD [ "" ]
