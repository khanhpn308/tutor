# 📖 Review: The typical pull request workflow on GitHub

This reading contains the code used in the instructional videos from [**The Typical Pull Request Workflow on GitHub**](https://www.coursera.org/learn/introduction-git-github/lecture/8mpDb/the-typical-pull-request-workflow-on-github)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git clone https://github.com/redquinoa/rearrange.git`

**Code output: **

Cloning into 'rearrange'...

remote: Enumerating objects: 9, done.

remote: Counting objects: 100% (9/9), done.

remote: Compressing objects: 100% (7/7), done.

remote: Total 9 (delta 1), reused 9 (delta 1), pack-reused 0

Unpacking objects: 100% (9/9), done.

`cd rearrange ls -l`

**Code output: **

total 20

-rw-rw-r-- 1 user user 11357 Jan 7 09:42 LICENSE

-rw-rw-r-- 1 user user  211 Jan 7 09:42 rearrange.py

-rw-rw-r-- 1 user user  762 Jan 7 09:42 rearrange_test.py

`git log`

**Code output: **

commit 367a127672c40a163a6f05ad930f2b0b857dc961 (HEAD -> master, origin/master, origin/HEAD)

Author: Blue Kale <bluekale@example.com>

Date:  Mon Jul 29 21:21:53 2019 +0200

Add tests for the rearrange module

commit c89805e52a1afa143c503f946cc5ead0fdd20255

Author: Blue Kale <bluekale@example.com>

Date:  Mon Jul 29 21:20:57 2019 +0200

Add the rearrange module

commit f4ddbc7a0ca3ac83a7e9ce7030e774b58e5dda42

Author: Blue Kale <53440916+blue-kale@users.noreply.github.com>

Date:  Mon Jul 29 16:07:42 2019 -0300

Initial commit

`git checkout -b add-readme`

**Code output: **

Switched to a new branch 'add-readme'

`git atom README.md Rearrange ========= This module is used for rearranging names. ``git add README.md git commit -m 'Add a simple README.md file'`

**Code output: **

[master 736d754] Add a simple README.md file

1 file changed, 4 insertions(+)

create mode 100644 README.md

`git push -u origin add-readme`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

Enumerating objects: 4, done.

Counting objects: 100% (4/4), done.

Delta compression using up to 4 threads

Compressing objects: 100% (3/3), done.

Writing objects: 100% (3/3), 400 bytes | 400.00 KiB/s, done.

Total 3 (delta 0), reused 0 (delta 0)

remote:

remote: Create a pull request for 'add-readme' on GitHub by visiting:

remote: https://github.com/redquinoa/rearrange/pull/new/add-readme

remote:

To https://github.com/redquinoa/rearrange.git

* [new branch] add-readme -> add-readme

Branch 'add-readme' set up to track remote branch 'add-readme' from 'origin'.
