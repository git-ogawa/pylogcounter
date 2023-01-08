FROM python:3.11-slim-bullseye

LABEL author "git-ogawa" \
    version "0.1.0"

COPY . /logcounter
RUN pip install --no-cache /logcounter && \
    rm -rf /logcounter

WORKDIR /work
ENTRYPOINT [ "logcounter" ]
CMD [ "" ]
