FROM python:slim-latest

LABEL "com.github.actions.name"="release-manager"
LABEL "com.github.actions.description"="Perform a release based on the PR comments."
LABEL "com.github.actions.icon"="check-square"
LABEL "com.github.actions.color"="yellow"

# COPY requirements.txt
# RUN pip install -r requirements.txt

COPY "run.py" .
CMD [ "run.py" ]
