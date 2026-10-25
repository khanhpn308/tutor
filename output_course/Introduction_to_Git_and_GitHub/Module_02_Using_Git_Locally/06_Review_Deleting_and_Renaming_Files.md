# 📖 Review: Deleting and Renaming Files

This reading contains the code used in the instructional videos from [**Deleting and Renaming FIles**](https://www.coursera.org/learn/introduction-git-github/lecture/3OT51/deleting-and-renaming-files)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd checks/ ls -l`

**Code output:**

total 8

-rw-rw-r-- 1 user user 659 Jul 9 19:28 disk_usage.py

-rw-rw-r-- 1 user user 659 Jul 15 21:43 processes.py

`git rm process.py`

**Code output:**

rm '[processes.py](http://processes.py)'

`ls -l `

**Code output:**

total 4

-rw-rw-r-- 1 user user 659 Jul 9 19:28 disk_usage.py

`git status`

**Code output:**

On branch master

Changes to be committed:

(use "git reset HEAD <file>..." to unstage)

deleted: [processes.py](http://processes.py)

`git commit -m 'Delete unneeded processes file'`

**Code output:**

[master 9939311] Delete unneeded processes file

1 file changed, 24 deletions(-)

delete mode 100644 processes.py

`git mv disk_usage.py check_free_space.py git status `

**Code output:**

On branch master

Changes to be committed:

(use "git reset HEAD <file>..." to unstage)

renamed: disk_usage.py -> check_free_space.py

`git commit -m 'New name for disk_usage.py'`

**Code output:**

[master 7d7167b] New name for disk_usage.py

1 file changed, 0 insertions(+), 0 deletions(-)

`echo .DS_STORE > gitignore ls -la`

**Code output:**

total 20

drwxrwxr-x 3 user user 4096 Jul 15 22:15 .

drwxr-xr-x 19 user user 4096 Jul 15 16:37 ..

-rw-rw-r-- 1 user user 659 Jul 9 19:28 check_free_space.py

drwxrwxr-x 8 user user 4096 Jul 15 21:52 .git

-rw-rw-r-- 1 user user  10 Jul 15 22:15 .gitignore

`git add .gitignore git commit -m 'Add a gitignore file, ignoring .DS_STORE files'`

**Code output:**

[master abb0632] Add a gitignore file, ignoring .DS_STORE files

1 file changed, 1 insertion(+)

create mode 100644 .gitignore
