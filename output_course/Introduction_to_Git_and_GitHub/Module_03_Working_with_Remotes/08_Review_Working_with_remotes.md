# 📖 Review: Working with remotes

This reading contains the code used in the instructional videos from [**Working with remotes**](https://www.coursera.org/learn/introduction-git-github/lecture/udUgl/working-with-remotes)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cd health-checks/ git remote -v`

**Code output: **

origin https://github.com/redquinoa/health-checks.git (fetch)

origin https://github.com/redquinoa/health-checks.git (push)

`git remote show origin`

**Code output: **

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com':

* remote origin

Fetch URL: https://github.com/redquinoa/health-checks.git

Push URL: https://github.com/redquinoa/health-checks.git

HEAD branch: master

Remote branch:

master tracked

Local branch configured for 'git pull':

master merges with remote master

Local ref configured for 'git push':

master pushes to master (up to date)

`git branch -r`

**Code output:**

origin/HEAD -> origin/master

origin/master

`git status`

**Code output: **

On branch master

Your branch is up to date with 'origin/master'.

nothing to commit, working tree clean
