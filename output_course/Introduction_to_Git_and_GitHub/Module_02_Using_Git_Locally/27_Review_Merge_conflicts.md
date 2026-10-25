# 📖 Review: Merge conflicts

This reading contains the code used in the instructional videos from [**Merge Conflicts**](https://www.coursera.org/learn/introduction-git-github/lecture/96VdS/merge-conflicts)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`atom free_memory.py #!/usr/bin/env python3 def main(): """Checks if there's enough free memory in the computer.""" main()``git commit -a -m 'Add comment to main()'`

**Code output: **

[master fe2fc5b] Add comment to main()

1 file changed, 2 insertions(+), 2 deletions(-)

`git checkout even-better-feature `

**Code output:**

Switched to branch 'even-better-feature'

`atom free_memory.py #!/usr/bin/env python3 def main(): print("Everything ok.") main()`

`git commit -a -m 'Print everything ok'`

**Code output: **

[even-better-feature 6a6de99] Print everything ok

1 file changed, 2 insertions(+), 2 deletions(-)

`git checkout master`

**Code output: **

Switched to branch 'master'

`git merge even-better-feature `

**Code output: **

Auto-merging free_memory.py

CONFLICT (content): Merge conflict in free_memory.py

Automatic merge failed; fix conflicts and then commit the result.

`git status`

**Code output: **

On branch master

You have unmerged paths.

(fix conflicts and run "git commit")

(use "git merge --abort" to abort the merge)

Unmerged paths:

(use "git add <file>..." to mark resolution)

both modified:  free_memory.py

no changes added to commit (use "git add" and/or "git commit -a")

`atom free_memory.py #!/usr/bin/env python3 def main(): <<<<<<< HEAD """Checks if there's enough free memory in the computer.""" ======= print("Everything ok.") >>>>>>> even-better-feature main() ``#!/usr/bin/env python3 def main(): """Checks if there's enough free memory in the computer.""" print("Everything ok.") main()``git add free_memory.py git status`

**Code output: **

On branch master

All conflicts fixed but you are still merging.

(use "git commit" to conclude merge)

Changes to be committed:

modified:  free_memory.py

`git commit`

**Code output: **

Merge branch 'even-better-feature'

Kept lines from both branches

# Conflicts:

#  free_memory.py

#

# It looks like you may be committing a merge.

# If this is not correct, please remove the file

#  .git/MERGE_HEAD

# and try again.

# Please enter the commit message for your changes. Lines starting

# with '#' will be ignored, and an empty message aborts the commit.

#

# On branch master

# All conflicts fixed but you are still merging.

#

# Changes to be committed:

#  modified:  free_memory.py

`git log --graph --oneline`

**Code output: **

*  8cb5e62 (HEAD -> master) Merge branch 'even-better-feature'

|\

| * ca6de99 (even-better-feature) Print everything ok

* | fe2fc5b Add comment to main()

|/

* 4361880 Add an empty free_memory.py

* 7d1de19 Revert "New name for disk_usage.py"

* bb9bd78 Add a gitignore file, ignoring .DS_STORE files

* 30e7071 New name for disk_usage.py

* 0d5a271 Delete unneeded processes file

* 5aada26 Adding file to delete it later

* cfb2b8e Add periods to the end of sentences.

* 21e6a1a Add new disk_usage check.
