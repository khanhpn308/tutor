# 📖 Review: Rebasing your changes

This reading contains the code used in the instructional videos from [**Rebasing Your Changes**](https://www.coursera.org/learn/introduction-git-github/lecture/cEqbt/rebasing-your-changes)

##  Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git checkout master`

**Code output: **

Switched to branch 'master'

Your branch is up to date with 'origin/master'.

`git pull`

**Code output: **

Remote: Enumerating objects: 5, done.

Remote: Counting objects: 100% (5/5), done.

Remote: Total 3 (delta 1), reused 3 (delta 1), pack-reused 0

Unpacking objects: 10% (3/3), done.

From https://github.com/redquinoa/healthchecks

58351ff..0789f64 master -> origin/master

Updating 58351ff..0789f64

Fast-forward

README.md | 2 ++

1 file changed, 2 insertions(+)

`git log --graph --oneline --all`

**Code output: **

* 0789f64 (HEAD -> master, origin/master, origin/HEAD) Add reference to all_checks.py to README

| * cbee3f7 (origin/refactor, refactor) Allow printing more than one error message

| * 75bdd43 Iterate over a list of checks and messages to avoid code duplication

| * e914aee Create wrapper function for check_disk_full

|/

*  58351ff Merge branch 'master' of https://github.com/redquinoa/health-checks

|\

| * a2dc118 Reorder conditional to match parameter order

* | 03d23d0 Rename min_absolute to min_gb, use parameter names

|/

| * 4d99c56 (origin/experimental, experimental) Empty check_load function

|/

* 922d659 Add disk full check to all_checks.py

* b62dc2e Add initial files for the checks

* 807cb50 Add one more line to README.md

* 3d9f86c Initial commit

`git checkout refactor`

**Code output: **

Switched to branch 'refactor'

Your branch is up to date with 'origin/refactor'.

`git rebase master`

**Code output: **

First, rewinding head to replay your work on top of it...

Applying: Create wrapper function for check_disk_full

Applying: Iterate over a list of checks and messages to avoid code duplication

Applying: Allow printing more than one error message

`git log --graph --oneline`

**Code output: **

* f5813b1 (HEAD -> refactor) Allow printing more than one error message

* 18257a0 Iterate over a list of checks and messages to avoid code duplication

* e914aee Create wrapper function for check_disk_full

* 0789f64 (origin/master, origin/HEAD, master) Add reference to all_checks.py to README

*  58351ff Merge branch 'master' of https://github.com/redquinoa/health-checks

|\

| * a2dc118 Reorder conditional to match parameter order

* | 03d23d0 Rename min_absolute to min_gb, use parameter names

|/

* 922d659 Add disk full check to all_checks.py

* b62dc2e Add initial files for the checks

* 807cb50 Add one more line to README.md

* 3d9f86c Initial commit

`git checkout master`

**Code output: **

Switched to branch 'master'

Your branch is up to date with 'origin/master'.

`git merge refactor`

**Code output: **

Updating 0789f64..f5813b1

Fast-forward

all_checks.py | 24 +++++++++++++++++-----

1 file changed, 19 insertions(+), 5 deletions(-)

`git push --delete origin refactor`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

To https://github.com/redquinoa/health-checks.git

\- [deleted]  refactor

`git branch -d refactor`

**Code output: **

Deleted branch refactor (was f5813b1).

`git push`

**Code output: **

Enumerating objects: 11, done.

Counting objects: 100% (11/11), done.

Delta compression using up to 4 threads

Compressing objects: 100% (9/9), done.

Writing objects: 100% (9/9), 1.37 KiB | 1.37 MiB/s, done.

Total 9 (delta 3), reused 0 (delta 0)

remote: Resolving deltas: 100% (3/3), completed with 1 local object.

To https://github.com/red-quinoa/health-checks.git

0789f64..f5813b1 master -> master
