# 📖 Review: Fetching new changes

This reading contains the code used in the instructional videos from [**Fetching New Changes**](https://www.coursera.org/learn/introduction-git-github/lecture/vbWpa/fetching-new-changes)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd health-checks/ git remote show origin`

**Code output: **

* remote origin

Fetch URL: https://github.com/redquinoa/health-checks.git

Push URL: https://github.com/redquinoa/health-checks.git

HEAD branch: master

Remote branch:

master tracked

Local branch configured for 'git pull':

master merges with remote master

Local ref configured for 'git push':

master pushes to master (local out of date)

`git fetch`

**Code output:**

remote: Enumerating objects: 5, done.

remote: Counting objects: 100% (5/5), done.

remote: Compressing objects: 100% (4/4), done.

remote: Total 4 (delta 0), reused 4 (delta 0), pack-reused 0

Unpacking objects: 100% (4/4), done.

From https://github.com/redquinoa/health-checks

807cb50..b62dc2e master  -> origin/master

`git log origin/master`

**Code output:**

commit b62dc2eacfa820cd9a762adab9213305d1c8d344 (origin/master, origin/HEAD)

Author: Blue Kale <bluekale@example.com>

Date:  Mon Jan 6 14:32:45 2020 -0800

Add initial files for the checks

commit 807cb5037ccac5512ba583e782c35f4e114f8599 (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jan 6 14:09:41 2020 -800

Add one more line to README.md

commit 3d9f86c50b8651d41adabdaebd04530f4694efb5

Author: Red Quinoa <55592533+redquinoa@users.noreply.github.com>

Date:  Sat Sep 21 14:04:15 2019 -0700

Initial commit

`git status`

**Code output: **

On branch master

Your branch is behind 'origin/master' by 1 commit, and can be fast-forwarded.

(use "git pull" to update your local branch)

nothing to commit, working tree clean

`git merge origin/master`

**Code output: **

Updating 807cb50..b62dc2e

Fast-forward

all_checks.py | 18 ++++++++++++++++++

disk_usage.py | 24 ++++++++++++++++++++++++

2 files changed, 42 insertions(+)

create mode 100755 all_checks.py

create mode 100644 disk_usage.py

`git log`

**Code output:**

commit 1e0a1dfccf01183bfca7e30fb25f115889f95022 (HEAD -> master, origin/master, origin/HEAD)

commit b62dc2eacfa820cd9a762adab9213305d1c8d344 (HEAD -> master, origin/master, origin/HEAD)

Author: Blue Kale <bluekale@example.com>

Date:  Mon Jan 6 14:32:45 2020 -0800

Add initial files for the checks

commit 807cb5037ccac5512ba583e782c35f4e114f8599 (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jan 6 14:09:41 2020 -800

Add one more line to README.md

commit 3d9f86c50b8651d41adabdaebd04530f4694efb5

Author: Red Quinoa <55592533+redquinoa@users.noreply.github.com>

Date:  Sat Sep 21 14:04:15 2019 -0700
