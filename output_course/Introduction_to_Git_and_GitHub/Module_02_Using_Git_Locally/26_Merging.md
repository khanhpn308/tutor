# 🎥 Merging

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/2bP2SKt0Sy2Gl5DMLh2AZQ.processed/full/720p/index.mp4?Expires=1793059200&Signature=Y~hFxl3q6a3CVjNFp8BstSlRcSLgtj~ae3J2DUp80YmDbop~0ozKIV2c~1-eV364Bf4H8nNVlSKx35IJjI9V7c~mvqUQytzhSdgy~YTpHB3j07S5LknE~mzjhZNTVHppc~BkFibsJg3oDTVrZZeBT4Tw0zwHaGu71mcaoXCPztc_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:41 and follow transcript
0:01
A typical workflow for managing branches in Git is to create a separate branch for developing any new features or changes. Once the new feature is in good shape, we merge the separate branch back into the main trunk of code. Merging is the term that git uses for combining branch data and history together. We'll use the Git merge command, which lets us take the independent snapshots and history of one git branch and tangle them into another. Let's try this out with our example branch from the last video. First, we'll check that we're in the master branch, and then we'll call git merge even better feature to merge the even better feature branch into the master branch.

Play video starting at ::1:28 and follow transcript
0:41
Now we've brought the master branch up to speed, which we can see by looking at the git log. As we're on the master branch head points at Master, we can see the even better feature and master branches are now both pointing at the same commit. Git uses two different algorithms to perform a merge, fast forward and threeway merge. The merge we just performed is an example of a fast forward merge. This kind of merge occurs when all the commits in the checked out branch are also in the branch that's being merged. If this is the case, we can say that the commit history of both branches doesn't diverge. In these cases, all git has to do is update the pointers of the branches to the same commit, and no actual merging needs to take place.

Play video starting at ::2:10 and follow transcript
1:28
On the other hand, a 3 way merge is performed when the history of the merging branches has diverged in some way. And there isn't a nice linear path to combine them via fast forwarding. This happens when a commit is made on one branch after the point when both branches split. In our case, this could have happened if we made a commit on the master branch after creating the other branches. When this occurs, git will tie the branch histories together with a new commit and merge the snapshots at the two branch tips with the most recent common ancestor, the commit, before the divergence. To do this successfully, git tries to figure out how to combine both snapshots.

2:10
If the changes were made in different files or in different parts of the same file, git will take both changes and put them together in the result. If instead, the changes were made on the same part of the same file, git won't know how to merge those changes, and the attempt will result in a merge conflict. This sounds scary, but don't panic, git doesn't quit. We'll solve those conflicts in our next video.
