# 📖 Review: Merging

This reading contains the code used in the instructional videos from [**Merging**](https://www.coursera.org/learn/introduction-git-github/lecture/InLJQ/merging)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git branch`

**Code output: **

Even-better-feature

* master

`git merge even-better-feature `

**Code output: **

Updating 7d1de19..4361880

Fast-forward

free-memory.py | 6 ++++++

1 file changed, 6 insertions (+)

Create mode 100644 free_memory.py

`git log`

**Code output: **

Switched to branch 'master'

commit 436188012f633b773eb6034fc02051e34da05134 (HEAD -> master, even-better-feature)

Author: My name <me@example.com>

Date:  Mon Jan 6 09:47:07 2020 -0800

Add an empty free_memory.py

commit 7d7167b2db44abf8cf014230f9b9708786e41c2a

Author: My name <me@example.com>

Date:  Mon Jan 6 09:15:58 2020 -0800

Revert "New name for disk_usage.py"

Rollback reason: the previous name was actually better :)

This reverts commit 7d7167b2db44abf8cf014230f9b9708786e41c2a.

(...)
