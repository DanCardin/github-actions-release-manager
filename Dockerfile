FROM python:3-slim

ENV PATH="/root/.poetry/bin:${PATH}"

RUN apt-get update \
    && apt-get install curl git -y \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/1.0.0/get-poetry.py | python \
    && poetry config virtualenvs.create false

COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "run.py" ]
