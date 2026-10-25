# 📖 Review: Basic interaction with GitHub

This reading contains the code used in the instructional videos from [**Basic interaction with GitHub**](https://www.coursera.org/learn/introduction-git-github/lecture/4Fl6n/basic-interaction-with-github)**. **

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written, allow you to practice running it, and can be used as a reference to refer back to.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git clone https://github.com/redquinoa/health-checks.git `

**Code output: **

Cloning into 'health-checks'...

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

remote: Enumerating objects: 3, done.

remote: Counting objects: 100% (3/3), done.

remote: Compressing objects: 100% (2/2), done.

remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0

Unpacking objects: 100% (3/3), done.

`cd health-checks/ ls -l`

**Code output: **

total 4

-rw-rw-r-- 1 user user 62 Jan 6 14:06 README.md

`atom README.md # health-checks Scripts that check the health of my computers This repo will be populated with lots of fancy checks. ``git commit -a -m "Add one more line to README.md"`

**Code output:**

[master 807cb50] Add one more line to README.md

1 file changed, 2 insertions(+)

`git push`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

Enumerating objects: 5, done.

Counting objects: 100% (5/5), done.

Delta compression using up to 4 threads

Compressing objects: 100% (2/2), done.

Writing objects: 100% (3/3), 347 bytes | 347.00 KiB/s, done.

Total 3 (delta 0), reused 0 (delta 0)

To https://github.com/redquinoa/health-checks.git

3d9f86c..807cb50 master -> master

`git config --global credential.helper cache``git pull`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

Already up to date.

`git pull`

**Code output: **

Already up to date.
