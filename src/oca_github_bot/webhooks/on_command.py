# Copyright (c) initOS GmbH 2019
# Distributed under the MIT License (http://opensource.org/licenses/MIT).

from .. import github
from ..commands import CommandError, parse_commands
from ..config import OCABOT_EXTRA_DOCUMENTATION, OCABOT_USAGE
from ..router import router


@router.register("issue_comment", action="created")
async def on_command(event, gh, *args, **kwargs):
    """On pull request review, tag if approved or ready to merge."""
    if not event.data["issue"].get("pull_request"):
        # ignore issue comments
        return
    org, repo = event.data["repository"]["full_name"].split("/")
    pr = event.data["issue"]["number"]
    username = event.data["comment"]["user"]["login"]
    text = event.data["comment"]["body"]

    try:
        for command in parse_commands(text):
            command.delay(org, repo, pr, username)
    except CommandError as e:
        with github.login() as gh:
            gh_pr = gh.pull_request(org, repo, pr)
            github.gh_call(
                gh_pr.create_comment,
                f"Hi @{username}. Your command failed:\n\n"
                f"``{str(e)}``.\n\n"
                f"{OCABOT_USAGE}\n\n"
                f"{OCABOT_EXTRA_DOCUMENTATION}",
            )
        raise
