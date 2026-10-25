# 📖 Review: The Basic Git Workflow

This reading contains the code used in the instructional videos from [**The basic Git Workflow**](https://www.coursera.org/learn/introduction-git-github/lecture/p5zYm/the-basic-git-workflow)**.**

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`mkdir scripts cd scripts git init`

**Code output:**

Initialized empty Git repository in /home/user/scripts/.git/

`git config -l`

**Code output:**

user.email=me@example.com

user.name=My name

core.repositoryformatversion=0

core.filemode=true

core.bare=false

core.logallrefupdates=true

## File with code

`#!/usr/bin/env python3 def main(): pass main() ``chmod +x all_checks.py git status`

**Code output:**

On branch master

No commits yet

Untracked files:

(use "git add <file>..." to include in what will be committed)

all_checks.py

nothing added to commit but untracked files present (use "git add" to track)

`git add all_checks.py git commit`

## File with code

`Create an empty all_checks. # Please enter the commit message for your changes. Lines starting # with '#' will be ignored, and an empty message aborts the commit. # # On branch master # # Initial commit # # Changes to be committed: # new file: all_checks.py # `

## File with code

`#!/usr/bin/env python3 import os def check_reboot(): """Returns True if the computer has a pending reboot.""" return os.path.exists("/run/reboot-required") def main(): pass main() ``git status`

On branch master

Changes not staged for commit:

(use "git add <file>..." to update what will be committed)

(use "git checkout -- <file>..." to discard changes in working directory)

modified:  all_checks.py

no changes added to commit (use "git add" and/or "git commit -a")

`git add all_checks.py git status`

**Code output:**

On branch master

Changes to be committed:

(use "git reset HEAD <file>..." to unstage)

modified:  all_checks.py

`git commit -m 'Add a check_reboot function'`

**Code output:**

[master d8e139c] Add a check_reboot function

1 file changed, 6 insertions(+)
