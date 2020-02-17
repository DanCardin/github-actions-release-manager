#! /usr/bin/env python3
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
import subprocess  # nosec
import enum
import shlex
import argparse
import os
import logging

import github3


log = logging.getLogger(__name__)


class BumpAmount(enum.Enum):
    patch = "patch"
    minor = "minor"
    major = "major"

    @classmethod
    def parse(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            log.warning("Unhandled bump amount: %s", value)
            return


class MergeMethod(enum.Enum):
    merge = "merge"
    squash = "squash"
    rebase = "rebase"

    @classmethod
    def parse(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            log.warning("Unhandled merge method: %s", value)
            return


class AuthorAssociation(enum.Enum):
    none = "NONE"
    collaborator = "COLLABORATOR"
    owner = "OWNER"

    @classmethod
    def parse(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            log.warning("Unhandled author association: %s", value)
            return cls.none


@dataclass
class Issue:
    user: str
    repo: str
    number: str


@dataclass
class CommandContext:
    event: Dict[str, Any]
    issue: Issue
    token: str
    bump_files: str
    bump_command: Optional[BumpAmount]
    command: argparse.Namespace

    @classmethod
    def from_env(cls, parser, env=os.environ):
        github_event_path = os.environ["GITHUB_EVENT_PATH"]
        with open(github_event_path, "rb") as f:
            event = json.load(f)

        fq_repo = os.environ["GITHUB_REPOSITORY"]
        user, repo = fq_repo.split("/")
        issue_number = event["issue"]["number"]
        issue = Issue(user=user, repo=repo, number=issue_number)

        bump_files = cls.extract_bump_files(env)
        command = cls.extract_command(parser, event["comment"]["body"])
        bump_command = cls.extract_bump_command(command, env)

        return cls(
            event=event,
            issue=issue,
            token=os.environ.get("INPUT_REPO-TOKEN"),
            bump_files=bump_files,
            bump_command=bump_command,
            command=command,
        )

    @property
    def has_permission(self) -> bool:
        author_association = AuthorAssociation.parse(
            self.event["comment"]["author_association"]
        )
        return author_association in {
            AuthorAssociation.owner,
            AuthorAssociation.collaborator,
        }

    @staticmethod
    def extract_bump_files(env):
        raw_bump_files = os.environ.get("INPUT_BUMP-FILES")
        if not raw_bump_files:
            raw_bump_files = "."
        return raw_bump_files.split(",")

    @staticmethod
    def extract_bump_command(command, env):
        if not command:
            return

        default_base = env.get("INPUT_BUMP-COMMAND-BASE")

        bump_commands = {}
        for variant in BumpAmount:
            bump_command = env.get(
                "INPUT_BUMP-COMMAND-{}".format(variant.value.upper())
            )
            if not bump_command and default_base:
                bump_command = " ".join([default_base, variant.value])

            bump_commands[variant] = bump_command

        return bump_commands.get(command.bump)

    @staticmethod
    def extract_command(parser, raw_command):
        split_command = shlex.split(raw_command)
        if split_command[0] != "/merge":
            return

        split_command = split_command[1:]

        print(split_command)
        return parser.parse_args(split_command)

    def bump_version(self):
        commands = [
            self.bump_command,
            "git config --global user.name 'Release Manager (Github Action)'",
            "git config --global user.email 'actions@github.com'",
            *(f"git add {bump_file}" for bump_file in self.bump_files),
            "git commit -m 'Bumping version'",
            "git push -e origin HEAD",
        ]

        for command in commands:
            subprocess.call(shlex.split(command))  # nosec

    def merge(self):
        if not self.command.method:
            return

        client = github3.login(token=self.token)
        if not client:
            return

        pull_request = client.pull_request(
            self.issue.user, self.issue.repo, self.issue.number
        )
        if not pull_request.mergeable:
            return

        pull_request.merge(merge_method=self.command.method.value)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="merge", description="Performs a bump/merge on a pull request"
    )
    parser.add_argument(
        "--bump",
        type=BumpAmount.parse,
        default=None,
        help="The kind of version bump to perform, values: patch, minor, major",
    )
    parser.add_argument(
        "-D",
        "--delete-branch",
        action="store_true",
        help="Whether to delete the branch after performing the merge",
    )
    parser.add_argument(
        "--method",
        type=MergeMethod.parse,
        default=MergeMethod.merge,
        help="The kind of merge to perform, values: merge, squash, rebase",
    )
    return parser


def run():
    logging.basicConfig()

    parser = create_parser()
    context = CommandContext.from_env(parser, os.environ)

    if not context.has_permission:
        log.info("User does not have permission to merge, stopping.")
        return

    if not context.command:
        log.info("Comment was not a merge command, stopping.")
        return

    if context.bump_command:
        context.bump_version()

    context.merge()


if __name__ == "__main__":
    run()
