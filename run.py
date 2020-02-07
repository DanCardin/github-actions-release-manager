import json
import enum
import shlex
import argparse
import os

from github3 import login


class BumpAmount(enum.Enum):
    patch = "patch"
    minor = "minor"


class MergeMethod(enum.Enum):
    merge = "merge"
    squash = "squash"
    rebase = "rebase"


parser = argparse.ArgumentParser(prog="merge", description="Process some integers.")
parser.add_argument(
    "--bump",
    type=BumpAmount,
    default=BumpAmount.minor,
    help="an integer for the accumulator",
)
parser.add_argument(
    "-D",
    "--delete-branch",
    action="store_true",
    help="sum the integers (default: find the max)",
)
parser.add_argument(
    "--method",
    type=MergeMethod,
    default=MergeMethod.merge,
    help="sum the integers (default: find the max)",
)


def parse_command(command):
    if not command.startswith("/merge "):
        return

    split_command = shlex.split(command)
    split_command = split_command[1:]

    args = parser.parse_args(split_command)


def run():
    github_event_path = os.environ["GITHUB_EVENT_PATH"]
    github_token = os.environ["INPUT_REPO-TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]

    with open(github_event_path, "rb") as f:
        github_event = json.load(f)

    user, repo = repository.split("/")
    issue_number = github_event["issue"]["number"]
    comment_body = github_event["comment"]["body"]

    command = parse_command(comment_body)

    gh = login(token=github_token)
    pull_request = gh.pull_request(user, repo, issue_number)
    if pull_request.mergeable:
        pull_request.merge(merge_method=command)

    print(github_event)

    print()
    print()

    print(os.environ)


if __name__ == "__main__":
    run()
