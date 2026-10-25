# 🎥 Fetching New Changes

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/UW8SS0o5RWW3G_E_NZMn6w.processed/full/720p/index.mp4?Expires=1793059200&Signature=VFYDCAcO-nzQkAbkLUVWMJ8oCAWNH8Adwm8Nqa3-D5ge6~81irBzSm6PrPZkFcKJ2vFvrqB0GNzap9pFgW22TryGd7tkhnORRiQg3vnPIzHXqq~14Ik7lYRZXNeFNuBIpIhDC-Geu1Vnxi2chuxNyJaEKNV0RABom7~795jkSno_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:53 and follow transcript
0:01
While we were learning about remotes, our colleague Blue Kale added some files to our repo. We could always use the GitHub website to browse the changes that were submitted. But we want to learn how to do it by interacting through the command line because you might need to do it this way at your job, and it'll work the same no matter which platform you use to interact with Git. So first, let's look at the output of the Git remote show origin command. Check out how it says that the local branches are out of date. This happens when there were commits done to the repo that aren't yet reflected locally. Git doesn't keep remote and local branches in sync automatically, it waits until we execute commands to move data around when we're ready. To sync the data, we use the git fetch command.

Play video starting at ::1:35 and follow transcript
0:53
This command copies the commits done in the remote repository to the remote branches, so we can see what other people have committed. Let's call it now and see what happens. Fetched content is downloaded to the remote branches on our repository. So it's not automatically mirrored to our local branches. We can run git checkout on these branches to see the working tree, and we can run git log to see the commit history. Let's look at the current commits in the remote repo by running git log origin/master. Looking at this output, we can see that the remote origin/branch is pointing to the latest commit.

Play video starting at ::2:17 and follow transcript
1:35
While the local master branch is pointing to the previous commit we made earlier on. Let's see what happens if we run git status now. Git status helpfully tells us that there's a commit that we don't have in our branch. It does this by letting us know our branches behind their remote origin/master branch. If we want to integrate the branches into our master branch, we can perform a merge operation, which merges the origin/master branch into our local master branch. To do that, we'll call git merge origin/master. Great. We've merged the changes of the master branch of the remote repository into our local branch.

Play video starting at ::3:03 and follow transcript
2:17
See how Git tells us that the code was integrated using fast-forward? It also shows that two files were added, all checks and disk_usage.py. If we look at the log output on our branch now, we should see the new commit. We see that now our master branch is up to date with the remote origin/master branch. With that, we've updated our branch to the latest changes. We can use git fetch like this to review the changes that happen in the remote repository. If we're happy with them, we can use git merge to integrate them into the local branch. Fetching commits from a remote repository and merging them into your local repository is such a common operation in Git that there's a handy command to let us do it all in one action.

3:03
We'll check that out in our next video.
