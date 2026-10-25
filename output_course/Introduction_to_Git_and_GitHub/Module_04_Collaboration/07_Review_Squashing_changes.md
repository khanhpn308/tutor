# 📖 Review: Squashing changes

This reading contains the code used in the instructional videos from [**Squashing Changes**](https://www.coursera.org/learn/introduction-git-github/lecture/6ODVl/squashing-changes)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`git rebase -i master``pick 736d754 Add a simple README file pick 01231b0 Add more information to the README (...)``pick 736d754 Add a simple README file squash 01231b0 Add more information to the README (...)``# This is a combination of 2 commits. # This is the 1st commit message: Add a simple README file # This is the commit message #2: Add more information to the README (...)``# This is a combination of 2 commits. # This is the 1st commit message: Add a simple README file including an example use case # This is the commit message #2: Add more information to the README (...)`

**Code output: **

git rebase -i master

[detached HEAD ae779e4] Add a simple README.md file including an example use case

Date: Tue Jan 7 09:47:17 2020 -0800

1 file changed, 9 insertions(+)

create mode 100644 README.md

Successfully rebased and updated refs/heads/add-readme.

`git show`

**Code output:**

commit ae779e430288b082a19062ed087c547e1051a981 (HEAD -> add-readme)

Author: My name <me@example.com>

Date:  Tue Jan 7 09:47:17 2020 -0800

Add a simple README file including an example use case

diff --git a/README.md b/README.md

new file mode 100644

index 0000000..5761a46

\--- /dev/null

+++ b/README.md

@@ -0,0 +1,9 @@

+Rearrange

+=========

+

+This module is used for rearranging names.

+Turns "LastName, FirstName" into "FirstName LastName"

+

+# Example

+

+Calling `rearrange_name("Turing, Alan")` will return `"Alan Turing"`

`git status`

**Code output:**

On branch add-readme

Your branch and 'origin/add-readme' have diverged,

and have 1 and 2 different commits each, respectively.

(use "git pull" to merge the remote branch into yours)

nothing to commit, working tree clean

`git log --graph --oneline --all -4`

**Code output:**

* ae779e4 (HEAD -> add-readme) Add a simple README.md file including an example use case

| * 01231b0 (origin/add-readme) Add more information to the README

| * 736d754 Add a simple README.md file

|/

* 367a127 (origin/master, origin/HEAD, master) Add tests for the rearrange module

`git push`

**Code output:**

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com': redquinoa

To https://github.com/redquinoa/rearrange.git

! [rejected] add-readme -> add-readme (non-fast-forward)

error: failed to push some refs to 'https://github.com/redquinoa/rearrange.git'

hint: Updates were rejected because the tip of your current branch is behind

hint: its remote counterpart. Integrate the remote changes (e.g.

hint: 'git pull ...') before pushing again.

hint: See the 'Note about fast-forwards' in 'git push --help' for details.

`git push -f`

**Code output:**

Enumerating objects: 4, done.

Counting objects: 100% (4/4), done.

Delta compression using up to 4 threads

Compressing objects: 100% (3/3), done.

Writing objects: 100% (3/3), 510 bytes | 510.00 KiB/s, done.

Total 3 (delta 0), reused 0 (delta 0)

To https://github.com/redquinoa/rearrange.git

\+ 01231b0...ae779e4 add-readme -> add-readme (forced update)

`git log --graph --oneline --all -4`

**Code output:**

* ae779e4 (HEAD -> add-readme, origin/add-readme) Add a simple README.md file including an example use case

* 367a127 (origin/master, origin/HEAD, master) Add tests for the rearrange module

* c89805e Add the rearrange module

* f4ddbc7 Initial commit
