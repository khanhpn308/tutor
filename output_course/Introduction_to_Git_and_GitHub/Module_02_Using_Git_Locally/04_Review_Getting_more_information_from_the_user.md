# 📖 Review: Getting more information from the user

This reading contains the code used in the instructional videos from [**Getting More Information About Our Changes**](https://www.coursera.org/learn/introduction-git-github/lecture/KLQkB/getting-more-information-about-our-changes)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git log -p`

**Code output:**

commit 033f27a8196987d61c4fd42930f2148b23434a03 (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jul 15 14:39:18 2019 +0200

Call check_reboot from main, exit with 1 on error

diff --git a/all_checks.py b/all_checks.py

index 340f1f7..710266a 100644

\--- a/all_checks.py

+++ b/all_checks.py

@@ -1,12 +1,15 @@

#!/usr/bin/env python3

import os

+import sys

def check_reboot():

"""Returns True if the computer has a pending reboot."""

return os.path.exists("/run/reboot-required")

(...)

`git log`

**Code output:**

commit 033f27a8196987d61c4fd42930f2148b23434a03 (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jul 15 14:39:18 2019 +0200

Call check_reboot from main, exit with 1 on error

commit **cc1acbf10fdea6cc07ebf827697666b6a35b0f36**

Author: My name <me@example.com>

Date:  Thu Jul 11 17:19:32 2019 +0200

Add a check_reboot function

(...)

user@ubuntu:~/scripts$ git show cc1acbf10fdea6cc07ebf827697666b6a35b0f36

commit cc1acbf10fdea6cc07ebf827697666b6a35b0f36

Author: My name <me@example.com>

Date:  Thu Jul 11 17:19:32 2019 +0200

Add a check_reboot function

diff --git a/all_checks.py b/all_checks.py

index c0d03b3..340f1f7 100644

\--- a/all_checks.py

+++ b/all_checks.py

@@ -1,5 +1,11 @@

#!/usr/bin/env python3

+import os

+

+def check_reboot():

+ """Returns True if the computer has a pending reboot."""

+ return os.path.exists("/run/reboot-required")

+

def main():

Pass

`git log --stat`

**Code output:**

commit 033f27a8196987d61c4fd42930f2148b23434a03 (HEAD -> master)

Author: My name <me@example.com>

Date:  Mon Jul 15 14:39:18 2019 +0200

Call check_reboot from main, exit with 1 on error

all_checks.py | 5 ++++-

1 file changed, 4 insertions(+), 1 deletion(-)

(...)

`atom all_checks.py`

## File in video

`#!/usr/bin/env python3 import os import sys def check_reboot(): """Returns True if the computer has a pending reboot.""" return os.path.exists("/run/reboot-required") def main(): if check_reboot(): print("Pending Reboot.") sys.exit(1) print("Everything ok.") sys.exit(0) main() ``git diff`

**Code output:**

diff --git a/all_checks.py b/all_checks.py

index 710266a..fdc4476 100644

\--- a/all_checks.py

+++ b/all_checks.py

@@ -12,4 +12,7 @@ def main():

print("Pending Reboot.")

sys.exit(1)

+ print("Everything ok.")

+ sys.exit(0)

+

main()

`git add -p`

**Code output:**

diff --git a/all_checks.py b/all_checks.py

index 710266a..fdc4476 100644

\--- a/all_checks.py

+++ b/all_checks.py

@@ -12,4 +12,7 @@ def main():

print("Pending Reboot.")

sys.exit(1)

+ print("Everything ok.")

+ sys.exit(0)

+

main()

Stage this hunk [y,n,q,a,d,e,?]? y

user@ubuntu:~/scripts$

`git diff git diff --staged `

**Code output:**

diff --git a/all_checks.py b/all_checks.py

index 710266a..fdc4476 100644

\--- a/all_checks.py

+++ b/all_checks.py

@@ -12,4 +12,7 @@ def main():

print("Pending Reboot.")

sys.exit(1)

+ print("Everything ok.")

+ sys.exit(0)

+

main()

`git commit -m 'Add a message when everything is ok'`

**Code output:**

[master 49d610b] Add a message when everything is ok

1 file changed, 3 insertions(+)
