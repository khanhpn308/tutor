# 📖 Review: Identifying a commit

This reading contains the code used in the instructional videos from [**Identifying a commit**](https://www.coursera.org/learn/introduction-git-github/lecture/WqddF/identifying-a-commit)**. **

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd checks git log -1`

**Code output:**

commit abb063210c1f011b0d6470a4c5f1d8f672edd3ef (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jul 15 22:20:45 2019 +0200

Add a gitignore file, ignoring .DS_STORE files

`git log -2`

**Code output:**

commit abb063210c1f011b0d6470a4c5f1d8f672edd3ef (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jul 15 22:20:45 2019 +0200

Add a gitignore file, ignoring .DS_STORE files

commit 7d7167b2db44abf8cf014230f9b9708786e41c2a

Author: My name <me@example.com>

Date:  Mon Jul 15 21:52:59 2019 +0200

New name for disk_usage.py

`git show 30e70712882267ca2dd749acfa02ea3aacfd0b24`

**Code output:**

Author: My name <me@example.com>

Date:  Mon Jul 15 21:52:59 2019 +0200

New name for disk_usage.py

diff --git a/disk_usage.py b/check_free_space.py

similarity index 100%

rename from disk_usage.py

rename to check_free_space.py

`git show 30`

**Code output:**

fatal: ambiguous argument '7d': unknown revision or path not in the working tree.

Use '--' to separate paths from revisions, like this:

'git <command> [<revision>...] -- [<file>...]'

`git show 30e7`

**Code output:**

commit 7d7167b2db44abf8cf014230f9b9708786e41c2a

Author: My name <me@example.com>

Date:  Mon Jul 15 21:52:59 2019 +0200

New name for disk_usage.py

diff --git a/disk_usage.py b/check_free_space.py

similarity index 100%

rename from disk_usage.py

rename to check_free_space.py

`git revert 30e7`

**Code output:**

Revert "New name for disk_usage.py"

Rollback reason: the previous name was actually better.

This reverts commit 7d7167b2db44abf8cf014230f9b9708786e41c2a.

# Please enter the commit message for your changes. Lines starting

# with '#' will be ignored, and an empty message aborts the commit.

#

# On branch master

# Changes to be committed:

#  renamed: check_free_space.py -> disk_usage.py

#

`git revert 7d71`

**Code output:**

[master 80b2dac] Revert "New name for disk_usage.py"

1 file changed, 0 insertions(+), 0 deletions(-)

rename check_free_space.py => disk_usage.py (100%)

`git show 7d1de19`

**Code output:**

commit 80b2dacef4b567196e61651064f03089c5e70b5e (HEAD -> master)

Author: My name <me@example.com>

Date:  Wed Jul 17 00:02:39 2019 +0200

Revert "New name for disk_usage.py"

Rollback reason: the previous name was actually better.

This reverts commit 7d7167b2db44abf8cf014230f9b9708786e41c2a.

diff --git a/check_free_space.py b/disk_usage.py

similarity index 100%

rename from check_free_space.py

rename to disk_usage.py
