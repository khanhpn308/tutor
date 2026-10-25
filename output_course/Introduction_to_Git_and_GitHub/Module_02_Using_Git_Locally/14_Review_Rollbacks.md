# 📖 Review: Rollbacks

This reading contains the code used in the instructional videos from [**Rollbacks**](https://www.coursera.org/learn/introduction-git-github/lecture/21kjM/rollbacks)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd scripts atom all_checks.py `

## File in video

`#!/usr/bin/env python3 import os import sys def check_reboot(): """Returns True if the computer has a pending reboot.""" return os.path.exists("/run/reboot-required") def main(): if check_reboot(): print("Pending Reboot.") sys.exit(1) if disk_full(): print("Disk Full.") sys.exit(1) print("Everything ok.") sys.exit(0) main() ``git commit -a -m 'Add call to disk_full function'`

**Code output:**

[master ec61497] Add call to disk_full function

1 file changed, 4 insertions(+)

`./all_checks.py `

**Code output:**

Traceback (most recent call last):

File "./all_checks.py", line 22, in <module>

main()

File "./all_checks.py", line 15, in main

if disk_full():

NameError: name 'disk_full' is not defined

`git revert HEAD`

**Code output:**

Revert "Add call to disk_full function"

Reason for rollback: The disk_full function is undefined.

This reverts commit ec614976e1665b40134d2c01921f9b0fbf89d1e2.

# Please enter the commit message for your changes. Lines starting

# with '#' will be ignored, and an empty message aborts the commit.

#

# On branch master

# Changes to be committed:

#  modified:  all_checks.py

#

# Untracked files:

#  output.txt

#

`git revert HEAD`

**Code output:**

[master 91c4968] Revert "Add call to disk_full function"

1 file changed, 4 deletions(-)

`git log -p -2`

**Code output:**

commit 91c4968ebd80de900d71b9bc3f332f53149ac57d (HEAD -> master)

Author: My name <me@example.com>

Date:  Tue Jul 16 21:43:18 2019 +0200

Revert "Add call to disk_full function"

Reason for rollback: The disk_full function is undefined.

This reverts commit ec614976e1665b40134d2c01921f9b0fbf89d1e2.

diff --git a/all_checks.py b/all_checks.py

index 21da366..fdc4476 100755

\--- a/all_checks.py

+++ b/all_checks.py

@@ -12,10 +12,6 @@ def main():

print("Pending Reboot.")

sys.exit(1)

- if disk_full():

- print("Disk Full.")

- sys.exit(1)

-

print("Everything ok.")

sys.exit(0)
