# 📖 Review: How to use code reviews

This reading contains the code used in the instructional videos from [**How to use Code Reviews in GitHub**](https://www.coursera.org/learn/introduction-git-github/lecture/QH52K/how-to-use-code-reviews-in-github)

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`atom README.md Rearrange ========= This module is used for rearranging names. Turns "LastName, FirstName" into "FirstName LastName". ## Examples * Calling `rearrange_name("Turing, Alan")` will return `"Alan Turing"` * Calling `rearrange_name("Hopper, Grace M.")` will return `"Grace M. Hopper"` * Calling `rearrange_name("Voltaire")` will return `"Voltaire"```git commit -a --amend`

**Code output: **

[add-readme 55e32ed] Add a simple README.md file including an example use case

Date: Tue Jan 7 09:47:17 2020 -0800

1 file changed, 11 insertions(+)

Create mode 100644 README.md

`git status`

**Code output:**

On branch add-readme

Your branch and ‘origin/add-readme’ have diverged,

And have 1 and 1 different commits, respectively

(use “git pull” to merge the remote branch into yours)

Nothing to commit, working tree clean

`git push -f`

**Code output:**

Username for 'https://github.com': redquinoa

Password for 'https://redquinoa@github.com': redquinoa

numerating objects: 4, done.

Counting objects: 100% (4/4), done.

Delta compression using up to 4 threads

Compressing objects: 100% (3/3), done.

Writing objects: 100% (3/3), 553 bytes | 553.00 KiB/s, done.

Total 3 (delta 0), reused 0 (delta 0)

To https://github.com/redquinoa/rearrange.git

\+ ae779e4...55e32ed master -> master (forced update)
