# 📖 Review: Updating an Existing Pull Request

This reading contains the code used in the instructional videos from [**Updating an Existing Pull Request**](https://www.coursera.org/learn/introduction-git-github/lecture/aRZ95/updating-an-existing-pull-request)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`atom README.md Rearrange ========= This module is used for rearranging names. Turns "LastName,FirstName" into "Firstname LastName" # Example Calling `rearrange_name("Turing, Alan")` will return `"Alan Turing"```git commit -a -m 'Add more information to the README'`

**Code output: **

[add-readme 01231b0] Add more information to the README

1 file changed, 5 insertions(+)

`git push`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com': redquinoa

Enumerating objects: 5, done.

Counting objects: 100% (5/5), done.

Delta compression using up to 4 threads

Compressing objects: 100% (3/3), done.

Writing objects: 100% (3/3), 407 bytes | 407.00 KiB/s, done.

Total 3 (delta 1), reused 0 (delta 0)

remote: Resolving deltas: 100% (1/1), completed with 1 local object.

To https://github.com/redquinoa/rearrange.git

736d754..01231b0 add-readme -> add-readme
