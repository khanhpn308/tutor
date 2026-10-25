# 📖 Review: Tracking issues

This reading contains the code used in the instructional videos from [**Tracking Issues**](https://www.coursera.org/learn/introduction-git-github/lecture/s59zR/tracking-issues)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd health-checks/ atom README.md # health-checks This repo will be populated with lots of fancy checks. Currently the main script is health_checks.py This script will print "Everything ok" if all checks pass, or the corresponding error messages if some checks fail.``git commit -a Update README to use the new name of the script Also add more information about how this works. Closes #1 (...)`

**Code output: **

[master 8981efe] Update README to use the new name of the script

1 file changed, 4 insertions(+), 1 deletion(-)

`git push`

**Code output:**

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

Enumerating objects: 5, done.

Counting objects: 100% (5/5), done.

Delta compression using up to 2 threads

Compressing objects: 100% (3/3), done.

Writing objects: 100% (3/3), 564 bytes | 564.00 KiB/s, done.

Total 3 (delta 0), reused 0 (delta 0)

To https://github.com/redquinoa/health-checks.git

160b5f3..8981efe master -> master
