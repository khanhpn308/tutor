# 📖 Review: First steps with Git

This reading contains the code used in the instructional videos from [**First steps with Git**](https://www.coursera.org/learn/introduction-git-github/lecture/2xrXl/first-steps-with-git)**. **

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git config --global user.email "me@example.com" git config --global user.name "My name"``mkdir checks cd checks git init`

**Code output:**

Initialized empty Git repository in /home/user/checks/.git/

`ls -la`

**Code output:**

total 12

drwxrwxr-x 3 user user 4096 Jul 9 18:16 .

drwxr-xr-x 18 user user 4096 Jul 9 18:16 ..

drwxrwxr-x 7 user user 4096 Jul 9 18:16 .git

user@ubuntu:~/checks$ ls -l .git/

total 32

drwxrwxr-x 2 user user 4096 Jul 9 18:16 branches

-rw-rw-r-- 1 user user  92 Jul 9 18:16 config

-rw-rw-r-- 1 user user  73 Jul 9 18:16 description

-rw-rw-r-- 1 user user  23 Jul 9 18:16 HEAD

drwxrwxr-x 2 user user 4096 Jul 9 18:16 hooks

drwxrwxr-x 2 user user 4096 Jul 9 18:16 info

drwxrwxr-x 4 user user 4096 Jul 9 18:16 objects

drwxrwxr-x 4 user user 4096 Jul 9 18:16 refs

`ls -l`

**Code output:**

total 4

-rw-rw-r-- 1 user user 657 Jul 9 18:26 disk_usage.py

`ls -l .git/`

**Code output:**

total 32

drwxrwxr-x 2 user user 4096 Jul 9 18:16 branches

-rw-rw-r-- 1 user user  92 Jul 9 18:16 config

-rw-rw-r-- 1 user user  73 Jul 9 18:16 description

-rw-rw-r-- 1 user user  23 Jul 9 18:16 HEAD

drwxrwxr-x 2 user user 4096 Jul 9 18:16 hooks

drwxrwxr-x 2 user user 4096 Jul 9 18:16 info

drwxrwxr-x 4 user user 4096 Jul 9 18:16 objects

drwxrwxr-x 4 user user 4096 Jul 9 18:16 refs

`cp ../disk_usage.py . ls -l`

**Code output:**

total 4

-rw-rw-r-- 1 user user 657 Jul 9 18:26 disk_usage.py

`git add disk_usage.py git status`

**Code output:**

On branch master

No commits yet

Changes to be committed:

(use "git rm --cached <file>..." to unstage)

new file:  disk_usage.py

`git commit`

**Code output:**

GNU nano 3.2  /home/user/checks/.git/COMMIT_EDITMSG

# Please enter the commit message for your changes. Lines starting

# with '#' will be ignored, and an empty message aborts the commit.

#

# On branch master

#

# Initial commit

#

# Changes to be committed:

#  new file:  disk_usage.py
