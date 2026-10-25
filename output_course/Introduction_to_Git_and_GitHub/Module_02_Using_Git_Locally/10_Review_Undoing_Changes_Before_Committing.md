# 📖 Review: Undoing Changes Before Committing

This reading contains the code used in the instructional videos from [**Undoing changes before committing**](https://www.coursera.org/learn/introduction-git-github/lecture/LPJn7/undoing-changes-before-committing)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd scripts atom all_checks.py`

## File in video

`#!/usr/bin/env python3 import os import sys def main(): if check_reboot(): print("Pending Reboot.") sys.exit(1) print("Everything ok.") sys.exit(0) main() ``./all_checks.py `

**Code output:**

Traceback (most recent call last):

File "all_checks.py", line 14, in <module>

main()

File "all_checks.py", line 7, in main

if check_reboot():

NameError: name 'check_reboot' is not defined

`git status`

**Code output:**

On branch master

Changes not staged for commit:

(use "git add <file>..." to update what will be committed)

(use "git checkout -- <file>..." to discard changes in working directory)

modified:  all_checks.py

`git checkout all_checks.py git status `

**Code output:**

On branch master

nothing to commit, working tree clean

user@ubuntu:~/scripts$ ./all_checks.py

Everything ok.

`./all_checks.py `

**Code output:**

Everything ok.

`./all_checks.py > output.txt git add * git status`

**Code output:**

On branch master

Changes to be committed:

(use "git reset HEAD <file>..." to unstage)

new file:  output.txt

`git reset HEAD output.txt git status`

**Code output:**

On branch master

Untracked files:

(use "git add <file>..." to include in what will be committed)

Output.txt

`git commit -m "it should be os.path.exists"`
