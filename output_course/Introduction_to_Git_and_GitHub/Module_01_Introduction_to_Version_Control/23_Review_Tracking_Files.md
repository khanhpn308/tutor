# 📖 Review: Tracking Files

This reading contains the code used in the instructional videos from [**Tracking Files**](https://www.coursera.org/learn/introduction-git-github/lecture/CO6OR/tracking-files)**.**

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd checks ls -l`

**Code output:**

total 4

-rw-r--r-- 1 user user 657 Jul 9 12:52 disk_usage.py

user@ubuntu:~/checks$ git status

On branch master

nothing to commit, working tree clean

`git status`

**Code output:**

On branch master

nothing to commit, working on clean tree

`atom disk_usage.py git status`

**Code output:**

On branch master

Changes to be committed:

(use "git restore --staged <file>..." to unstage)

modified:  disk_usage.py

`git commit -m 'Add periods to the end of sentences.'`

**Code output:**

[master ae8d19c] Add periods to the end of sentences.

1 file changed, 2 insertions(+), 2 deletions(-)

`git status`

**Code output:**

On branch master

nothing to commit, working tree clean
