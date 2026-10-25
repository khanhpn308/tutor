# 📖 Review: Another Rebasing example

This reading contains the code used in the instructional videos from [**Another rebasing example**](https://www.coursera.org/learn/introduction-git-github/lecture/jipZ8/another-rebasing-example)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`atom all_checks.py (...) import socket (...) def check_root_full(): """Returns True if the root partition is full, False otherwise.""" return check_disk_full(disk="/", min_gb=2, min_percent=10) def check_no_network(): """Returns True if it fails to resolve Google's URL, False otherwise.""" try: socket.gethostbyname("www.google.com") return False except: return True def main(): checks = [ (check_reboot, "Pending Reboot."), (check_root_full, "Root partition full"), (check_no_network, "No working network."), ] (...)``git commit -a -m 'Add a simple network connectivity check'`

**Code output:**

[master aa8da6f] Add a simple network connectivity check

1 file changed, 10 insertions(+), 1 deletion(-)

`git fetch`

**Code output:**

remote: Enumerating objects: 6, done.

remote: Counting objects: 100% (6/6), done.

remote: Compressing objects: 100% (4/4), done.

remote: Total 5 (delta 1), reused 5 (delta 1), pack-reused 0

Unpacking objects: 100% (5/5), done.

From https://github.com/redquinoa/health-checks

f5813b1...d8c8fcd master  -> origin/master

`git rebase origin/master`

**Code output:**

First, rewinding head to replay your work on top of it...

Applying: Add a simple network connectivity check

Using index info to reconstruct a base tree...

A  all_checks.py

Falling back to patching base and 3-way merge...

Auto-merging health_checks.py

CONFLICT (content): Merge conflict in health_checks.py

error: Failed to merge in the changes.

Patch failed at 0001 Add a simple network connectivity check

hint: Use 'git am --show-current-patch' to see the failed patch

Resolve all conflicts manually, mark them as resolved with

"git add/rm <conflicted_files>", then run "git rebase --continue".

You can instead skip this commit: run "git rebase --skip".

To abort and get back to the state before "git rebase", run "git rebase --abort".

`atom health_checks.py (...) <<<<<<< HEAD:health_checks.py def check_cpu_constrained(): """Returns True if the cpu is having too much usage, False otherwise.""" return psutil.cpu_percent(1) > 75 def main(): checks = [ (check_reboot, "Pending Reboot."), (check_root_full, "Root partition full"), (check_cpu_constrained, "CPU load too high."), ] everything_ok = True ======= def check_no_network(): """Returns True if it fails to resolve Google's URL, False otherwise.""" try: socket.gethostbyname("google.com") return False except: return True >>>>>>> Add a simple network connectivity check:all_checks.py def main(): checks = [ (check_reboot, "Pending Reboot."), (check_root_full, "Root partition full"), <<<<<<< HEAD:health_checks.py (check_cpu_constrained, "CPU load too high."), ======= (check_no_network, "No working network."), >>>>>>> Add a simple network connectivity check:all_checks.py ] (...) ``(...) def check_cpu_constrained(): """Returns True if the cpu is having too much usage, False otherwise.""" return psutil.cpu_percent(1) > 75 def main(): checks = [ (check_reboot, "Pending Reboot."), (check_root_full, "Root partition full"), (check_cpu_constrained, "CPU load too high."), ] everything_ok = True def check_no_network(): """Returns True if it fails to resolve Google's URL, False otherwise.""" try: socket.gethostbyname("google.com") return False except: return True def main(): checks = [ (check_reboot, "Pending Reboot."), (check_root_full, "Root partition full"), (check_cpu_constrained, "CPU load too high."), (check_no_network, "No working network."), ] (...) ``./health_checks.py `

**Code output:**

Traceback (most recent call last:

File ".health_checks.py", line 61, in <module>

main()

File ".health_checks.py", line 49, in main

If check():

File ".health_checks.py", line 30, in check_cpu_constrained

Return psutil.cpu_percent(1) >75

NameError: name ‘psutil’ is not defined

`atom health_checks.py import os import shutil import sys import socket import psutil (...)``./health_checks.py `

**Code output:**

Everything ok.

`git add health_checks.py git rebase --continue`

**Code output:**

Applying: Add a simple network connectivity check

`git log --graph --oneline`

**Code output:**

* 160b5f3 (HEAD -> master) Add a simple network connectivity check

* b52b7a2 (origin/master, origin/HEAD) Add cpu_constrained check

* 9fc7275 Rename all_checks.py to health_checks.py

* f5813b1 Allow printing more than one error message

* 18257a0 Iterate over a list of checks and messages to avoid code duplication

* 5d2e3eb Create wrapper function for check_disk_full

* 0789f64 Add reference to all_checks.py to README

*  58351ff Merge branch 'master' of https://github.com/redquinoa/health-checks

|\

| * a2dc118 Reorder conditional to match parameter order

* | 03d23d0 Rename min_absolute to min_gb, use parameter names

|/

* 922d659 Add disk full check to all_checks.py

* b62dc2e Add initial files for the checks

* 807cb50 Add one more line to README.md

* 3d9f86c Initial commit

`git push`

**Code output:**

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

Enumerating objects: 5, done.

Counting objects: 100% (5/5), done.

Delta compression using up to 4 threads

Compressing objects: 100% (3/3), done.

Writing objects: 100% (3/3), 501 bytes | 501.00 KiB/s, done.

Total 3 (delta 2), reused 0 (delta 0)

remote: Resolving deltas: 100% (2/2), completed with 2 local objects.

To https://github.com/redquinoa/health-checks.git

b52b7a2..160b5f3 master -> master
