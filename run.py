import json
import subprocess
import enum
import shlex
import argparse
import os

from github3 import login


class BumpAmount(enum.Enum):
    none = None
    patch = "patch"
    minor = "minor"
    major = "major"


class MergeMethod(enum.Enum):
    merge = "merge"
    squash = "squash"
    rebase = "rebase"


parser = argparse.ArgumentParser(prog="merge", description="Process some integers.")
parser.add_argument(
    "--bump",
    type=BumpAmount,
    default=BumpAmount.none,
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

    return parser.parse_args(split_command)


def run():
    github_event_path = os.environ["GITHUB_EVENT_PATH"]
    github_token = os.environ["INPUT_REPO-TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]
    bump_files = os.environ.get("INPUT_BUMP-FILES", ".").split(",")

    bump_commands = {
        None: None,
        BumpAmount.patch: os.environ.get("INPUT_BUMP-COMMAND-PATCH"),
        BumpAmount.minor: os.environ.get("INPUT_BUMP-COMMAND-MINOR"),
        BumpAmount.major: os.environ.get("INPUT_BUMP-COMMAND-MAJOR"),
    }

    with open(github_event_path, "rb") as f:
        github_event = json.load(f)

    user, repo = repository.split("/")
    issue_number = github_event["issue"]["number"]
    comment_body = github_event["comment"]["body"]

    print(command)
    command = parse_command(comment_body)

    try:
        bump_command = bump_commands.get(command.bump)
        print(bump_command)
        if not bump_command:
            bump_command = "poetry version minor"
        if bump_command:
            subprocess.call(shlex.split(bump_command))

            subprocess.call(
                shlex.split(
                    f"git config --global user.name 'Merge Manager (Github Action)'"
                )
            )
            subprocess.call(
                shlex.split(f"git config --global user.email 'actions@github.com'")
            )
            for file in bump_files:
                subprocess.call(shlex.split(f"git add {file}"))

            subprocess.call(shlex.split(f"git commit -m 'Bumping version'"))

            subprocess.call(shlex.split(f"git push -u origin HEAD"))
    except Exception as e:
        print(e)

    gh = login(token=github_token)
    pull_request = gh.pull_request(user, repo, issue_number)
    if pull_request.mergeable:
        pull_request.merge(merge_method=command.method.value)

    print(github_event)

    print(os.environ)


if __name__ == "__main__":
    run()
