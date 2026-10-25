# 📖 Review: Practical Application of diff and patch

This reading contains the code used in the instructional videos from [**Practical application of diff and patch**](https://www.coursera.org/learn/introduction-git-github/lecture/IkuqC/practical-application-of-diff-and-patch).

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cp disk_usage.py disk_usage_original.py cp disk_usage.py disk_usage_fixed.py `

## **File with code**

`#!/usr/bin/env python3 import shutil def check_disk_usage(disk, min_absolute, min_percent): """Returns True if there is enough free disk space, false otherwise.""" du = shutil.disk_usage(disk) # Calculate the percentage of free space percent_free = 100 * du.free / du.total # Calculate how many free gigabytes gigabytes_free = du.free / 2**30 if percent_free < min_percent or gigabytes_free < min_absolute: return False return True # Check for at least 2 GB and 10% free if not check_disk_usage("/", 2*2**30, 10): print("ERROR: Not enough disk space") return 1 print("Everything ok") return 0 `

`./disk_usage_fixed.py #this throws an error `

**Code output:**

File "./disk_usage_fixed.py", line 19

return 1

^

SyntaxError: 'return' outside function

## File with code

The instructor adds import sys at the beginning, then change return 1 to sys.exit(1) and return 0**** to sys.exit(0).

`#!/usr/bin/env python3 import shutil import sys def check_disk_usage(disk, min_absolute, min_percent): """Returns True if there is enough free disk space, false otherwise.""" du = shutil.disk_usage(disk) # Calculate the percentage of free space percent_free = 100 * du.free / du.total # Calculate how many free gigabytes gigabytes_free = du.free / 2**30 if percent_free < min_percent or gigabytes_free < min_absolute: return False return True # Check for at least 2 GB and 10% free if not check_disk_usage("/", 2*2**30, 10): print("ERROR: Not enough disk space") sys.exit(1) print("Everything ok") sys.exit(0)``./disk_usage_fixed.py`

**Code output:**

ERROR: Not enough disk space

## File with code

Instructor changed change check_disk_usage("/", 2*2**30, 10)**** in previous file to check_disk_usage("/", 2, 10).

`#!/usr/bin/env python3 import shutil import sys def check_disk_usage(disk, min_absolute, min_percent): """Returns True if there is enough free disk space, false otherwise.""" du = shutil.disk_usage(disk) # Calculate the percentage of free space percent_free = 100 * du.free / du.total # Calculate how many free gigabytes gigabytes_free = du.free / 2**30 if percent_free < min_percent or gigabytes_free < min_absolute: return False return True # Check for at least 2 GB and 10% free if not check_disk_usage("/", 2, 10): print("ERROR: Not enough disk space") sys.exit(1) print("Everything ok") sys.exit(0)``./disk_usage_fixed.py `

**Code output:**

Everything ok

`diff -u disk_usage_original.py disk_usage_fixed.py > disk_usage.diff cat disk_usage.diff `

**Code output:**

\--- disk_usage_original.py 2019-06-22 15:13:38.591579963 -0700

+++ disk_usage_fixed.py 2019-06-22 15:41:35.013023839 -0700

@@ -1,6 +1,7 @@

#!/usr/bin/env python3

import shutil

+import sys

def check_disk_usage(disk, min_absolute, min_percent):

"""Returns True if there is enough free disk space, false otherwise."""

@@ -14,9 +15,9 @@

return True

# Check for at least 2 GB and 10% free

-if not check_disk_usage("/", 2*2**30, 10):

+if not check_disk_usage("/", 2, 10):

print("ERROR: Not enough disk space")

- return 1

+ sys.exit(1)

print("Everything ok")

-return 0

+sys.exit(0)

`patch disk_usage.py < disk_usage.diff patching file disk_usage.py`

**Code output:**

patching file disk_usage.py

`./disk_usage.py `

**Code output:**

Everything ok
