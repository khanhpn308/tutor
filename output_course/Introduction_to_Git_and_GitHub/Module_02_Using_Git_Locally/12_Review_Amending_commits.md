# 📖 Review: Amending commits

This reading contains the code used in the instructional videos from [**Amending commits**](https://www.coursera.org/learn/introduction-git-github/lecture/nT1S2/amending-commits)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd scripts/ touch auto-update.py touch gather-information.sh ls -l `

**Code output:**

total 8

-rwxrwxr-x 1 user user 319 Jul 16 17:56 all_checks.py

-rw-rw-r-- 1 user user  0 Jul 16 20:19 auto-update.py

-rw-rw-r-- 1 user user  0 Jul 16 20:19 gather-information.sh

-rw-rw-r-- 1 user user 15 Jul 16 18:03 output.txt

user@ubuntu:~/scripts$ git add auto-update.py

user@ubuntu:~/scripts$ git commit -m 'Add two new scripts'

[master 9c78761] Add two new scripts

1 file changed, 0 insertions(+), 0 deletions(-)

create mode 100644 [auto-update.py](http://auto-update.py)

`git add auto-update.py git commit -m 'Add two new scripts'`

**Code output:**

# Please enter the commit message for your changes. Lines starting

# with '#' will be ignored, and an empty message aborts the commit.

#

# Date: Tue Jul 16 20:20:24 2019 +0200

#

# On branch master

# Changes to be committed:

#  new file:  auto-update.py

#  new file:  gather-information.sh

#

# Untracked files:

#  output.txt

#

`git add gather-information.sh git commit --amend `

## File in video

`Add two new scripts. # Please enter the commit message for your changes. Line starting #with '#' will be ignored, and an empty message aborts the commit. # #Date: Mon Jan 6 08:28:17 2020 -0800 # # On branch master # Changes to be committed: # new file: auto-update.py # new file: gather-information.sh # # Untracked files: # output.txt`

## File in video

`Add two new scripts. gather-information.sh will collect information in case of errors. auto-update.py will run daily to update computers automatically. # Please enter the commit message for your changes. Line starting #with '#' will be ignored, and an empty message aborts the commit. # #Date: Mon Jan 6 08:28:17 2020 -0800 # # On branch master # Changes to be committed: # new file: auto-update.py # new file: gather-information.sh # # Untracked files: # output.txt`
