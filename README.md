# Github Actions release manager

Atomically merge version-bumped releases to your repo upon a trigger comment from a user
with permission to merge a PR.

```
Performs a bump/merge on a pull request

optional arguments:
  --bump BUMP          The kind of version bump to perform, values: patch, minor,
                       major
  -D, --delete-branch  Whether to delete the branch after performing the merge
  --method METHOD      The kind of merge to perform, values: merge, squash, rebase (default: merge)
```

Suppose a scenario where your package is at version 1.0.0, and you're accepting a bugfix
which you want to automatically release.

Comment on the PR like `/merge --bump patch -D `.
