# 📖 Review: Working with branches

This reading contains the code used in the instructional videos from [**Working with branches**](https://www.coursera.org/learn/introduction-git-github/lecture/UHBEa/working-with-branches)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd checks git status`

**Code output:**

On branch even-better-feature

nothing to commit, working tree clean

`ls -l`

**Code output:**

total 8

-rw-rw-r-- 1 user user 659 Jul 17 00:02 disk_usage.py

-rw-rw-r-- 1 user user 53 Jul 17 15:33 free_memory.py

`git checkout master git log -2 `

**Code output:**

Switched to branch 'master'

user@ubuntu:~/checks$ git log -2

commit 80b2dacef4b567196e61651064f03089c5e70b5e (HEAD -> master, new-feature)

Author: My name <me@example.com>

Date:  Wed Jul 17 00:02:39 2019 +0200

Revert "New name for disk_usage.py"

Rollback reason: the previous name was actually better.

This reverts commit 7d7167b2db44abf8cf014230f9b9708786e41c2a.

commit abb063210c1f011b0d6470a4c5f1d8f672edd3ef

Author: My name <me@example.com>

Date:  Mon Jul 15 22:20:45 2019 +0200

Add a gitignore file, ignoring .DS_STORE files

`ls -l`

**Code output:**

total 4

-rw-rw-r-- 1 user user 659 Jul 17 00:02 disk_usage.py

`git branch`

**Code output:**

even-better-feature

* master

new-feature

`git branch -d new-feature `

**Code output:**

Deleted branch new-feature (was 80b2dac).

`git branch`

**Code output:**

even-better-feature

* master

`git branch -d even-better-feature `

**Code output:**

error: The branch 'even-better-feature' is not fully merged.

If you are sure you want to delete it, run 'git branch -D even-better-feature'.
