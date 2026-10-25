# 📖 Review: Anatomy of a commit message

This reading contains the code used in the instructional videos from [**Anatomy of a Commit Message**](https://www.coursera.org/learn/introduction-git-github/lecture/mhymc/anatomy-of-a-commit-message).

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cat example_commit.txt `

**Code output:**

Provide a good commit message example

The purpose of this commit is to provide an example of a hand-crafted,

artisanal commit message. The first line is a short, approximately 50-character

summary, followed by an empty line. The subsequent paragraphs are jam-packed

with descriptive information about the change, but each line is kept under 72

characters in length.

If even more information is needed to explain the change, more paragraphs can

be added after blank lines, with links to issues, tickets, or bugs. Remember

that future you will thank current you for your thoughtfulness and foresight!

# Please enter the commit message for your changes. Lines starting

# with '#' will be ignored, and an empty message aborts the commit.

#

# On branch master

#

# Changes to be committed:

# new file:  super_script.py

# new file:  cool_config.txt

#

`cd scripts git log`

**Code output:**

commit d8e139cc4f7dcd13b75cff67cfb68527e24c59c5 (HEAD -> master)

Author: My name <me@example.com>

Date:  Thu Jul 11 17:19:32 2019 +0200

Add a check_reboot function

commit 6cfc29966acda8213fcd8ac2735b31f3fdbc6c53

Author: My name <me@example.com>

Date:  Thu Jul 11 12:08:46 2019 +0200

Create and empty all_checks.py
