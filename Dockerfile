FROM python:3-slim

ENV PATH="/root/.poetry/bin:${PATH}"
LABEL "com.github.actions.name"="release-manager"
LABEL "com.github.actions.description"="Perform a release based on the PR comments."
LABEL "com.github.actions.icon"="check-square"
LABEL "com.github.actions.color"="yellow"

RUN apt-get update \
    && apt-get install curl -y \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/1.0.0/get-poetry.py | python \
    && poetry config virtualenvs.create false

COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "run.py" ]
