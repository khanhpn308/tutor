# 📖 Review: The Pull-Merge-Push Workflow

This reading contains the code used in the instructional videos from [**The Pull-Merge-Push Workflow**](https://www.coursera.org/learn/introduction-git-github/lecture/n3GnN/the-pull-merge-push-workflow)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`atom all_checks.py #!/usr/binenv python3 (...) def check_disk_full(disk, min_gb, min_percent): """Returns True if there isn't enough disk space, False otherwise.""" du = shutil.disk_usage(disk) # Calculate the percentage of free space percent_free = 100 * du.free / du.total # Calculate how many free gigabytes gigabytes_free = du.free / 2**30 if percent_free < min_percent or gigabytes_free < min_gb: return True return False def main(): if check_reboot(): print("Pending Reboot.") sys_exit(1) if check_disk_full(disk="/", min_gb=2, min_percent=10): print("Disk full.") sys.exit(1) print("Everything ok") sys.exit(0) main()``git add -p`

**Code output: **

diff --git a/all_checks.py b/all_checks.py

index e46cdae..a40047c 100755

\--- a/all_checks.py

+++ b/all_checks.py

@@ -8,14 +8,14 @@ def check_reboot():

"""Returns True if the computer has a pending reboot."""

return os.path.exists("/run/reboot-required")

-def check_disk_full(disk, min_absolute, min_percent):

+def check_disk_full(disk, min_gb, min_percent):

"""Returns True if there isn't enough disk space, False otherwise."""

du = shutil.disk_usage(disk)

# Calculate the percentage of free space

percent_free = 100 * du.free / du.total

# Calculate how many free gigabytes

gigabytes_free = du.free / 2**30

- if percent_free < min_percent or gigabytes_free < min_absolute:

+ if percent_free < min_percent or gigabytes_free < min_gb:

return True

return False

Stage this hunk [y,n,q,a,d,j,J,g,/,s,e,?]? y

@@ -27,7 +27,7 @@ def main():

if check_reboot():

print("Pending Reboot.")

sys.exit(1)

- if check_disk_full("/", 2, 10):

+ if check_disk_full(disk="/", min_gb=2, min_percent=10):

print("Disk full.")

sys.exit(1)

Stage this hunk [y,n,q,a,d,K,g,/,e,?]? y

`git commit -m 'Rename min_absolute to min_gb, use parameter names'`

**Code output: **

[master 03923d0] Rename min_absolute to min_gb, use parameter names

1 file changed, 3 insertions(+), 3 deletions(-)

`git push`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

To https://github.com/redquinoa/health-checks.git

! [rejected] master -> master (fetch first)

error: failed to push some refs to 'https://github.com/redquinoa/health-checks.git'

hint: Updates were rejected because the remote contains work that you do

hint: not have locally. This is usually caused by another repository pushing

hint: to the same ref. You may want to first integrate the remote changes

hint: (e.g., 'git pull ...') before pushing again.

hint: See the 'Note about fast-forwards' in 'git push --help' for details.

`git pull`

**Code output: **

remote: Enumerating objects: 5, done.

remote: Counting objects: 100% (5/5), done.

remote: Compressing objects: 100% (2/2), done.

remote: Total 3 (delta 1), reused 3 (delta 1), pack-reused 0

Unpacking objects: 100% (3/3), done.

From https://github.com/red-quinoa/health-checks

92d659..a2dc118 master  -> origin/master

Auto-merging all_checks.py

CONFLICT (content): Merge conflict in all_checks.py

Automatic merge failed; fix conflicts and then commit the result.

`git log --graph --oneline --all`

**Code output: **

* 03d23d0 Rename min_absolute to min_gb, use parameter names

| * 42dc118 (origin/master, origin/HEAD) reorder conditional to match parameter order

|/

| * 4d99c56 (origin/experimental, experimental) Empty check_load function

|/

* 922d659 Add disk full check to all_checks.py

* b62dc2e Add initial files for the checks

* 807cb50 Add one more line to README.md

* 3d9f86c Initial commit

`git log -p origin/master`

**Code output: **

commit a2dc1181e5cccf36fec30d6eeefbe569a13883de (origin/master, origin/HEAD)

Author: Blue Kale <bluekale@example.com>

Date:  Mon Jan 6 14:52:23 2020 -0800

Reorder conditional to match parameter order

diff --git a/all_checks.py b/all_checks.py

index e46cdae..6dda356 100755

\--- a/all_checks.py

+++ b/all_checks.py

@@ -15,7 +15,7 @@ def check_disk_full(disk, min_absolute, min_percent):

percent_free = 100 * du.free / du.total

# Calculate how many free gigabytes

gigabytes_free = du.free / 2**30

- if percent_free < min_percent or gigabytes_free < min_absolute:

+ if gigabytes_free < min_absolute or percent_free < min_percent:

return True

return False

commit 922d65950b5325109525a24b71d8df8a46412d04 (HEAD -> master, origin/master, origin/HEAD)

Author: Blue Kale <bluekale@example.com>

Date:  Mon Jan 6 14:42:44 2020 -0800

Add disk full check to all_checks.py

diff –git a/all_checks.py b/all_checks.py

`atom all_checks.py #!/usr/binenv python3 (...) def check_disk_full(disk, min_gb, min_percent): """Returns True if there isn't enough disk space, False otherwise.""" du = shutil.disk_usage(disk) # Calculate the percentage of free space percent_free = 100 * du.free / du.total # Calculate how many free gigabytes gigabytes_free = du.free / 2**30 <<<<<<< HEAD if percent_free < min_percent or gigabytes_free < min_gb: ======= if gigabytes_free < min_absolute or percent_free < min_percent: >>>>>>> a2dc1181e5cccf36fec30d6eeefbe569a13883de return True return False (...)``(...) def check_disk_full(disk, min_gb, min_percent): """Returns True if there isn't enough disk space, False otherwise.""" du = shutil.disk_usage(disk) # Calculate the percentage of free space percent_free = 100 * du.free / du.total # Calculate how many free gigabytes gigabytes_free = du.free / 2**30 if gigabytes_free < min_gb or percent_free < min_percent: return True return False (...)``git add all_checks.py git commit`

**Code output: **

Merge branch 'master' of https://github.com/redquinoa/health-checks

Fixed check_disk_usage conditional to use the new order and new variable name.

# Conflicts:

#  all_checks.py

#

(...)

`git push`

**Code output: **

Enumerating objects: 10, done.

Counting objects: 100% (10/10), done.

Delta compression using up to 2 threads

Compressing objects: 100% (6/6), done.

Writing objects: 100% (6/6), 877 bytes | 877.00 KiB/s, done.

Total 6 (delta 2), reused 0 (delta 0)

remote: Resolving deltas: 100% (2/2), completed with 1 local object.

To https://github.com/redquinoa/health-checks.git

a2dc118..58351ff master -> master

`git log --graph --oneline`

**Code output: **

* 58351ff (Head -> master, origin/master, origin/HEAD) Merge branch ‘master’ of https://github.com/redquinoa/health-checks.git

|\

| * 42dc118 (origin/master, origin/HEAD) reorder conditional to match parameter order

* | 03d23d0 Rename min_absolute to min_gb, use parameter names

|/

| * 4d99c56 (origin/experimental, experimental) Empty check_load function

|/

* 922d659 Add disk full check to all_checks.py

* b62dc2e Add initial files for the checks

* 807cb50 Add one more line to README.md

* 3d9f86c Initial commit
