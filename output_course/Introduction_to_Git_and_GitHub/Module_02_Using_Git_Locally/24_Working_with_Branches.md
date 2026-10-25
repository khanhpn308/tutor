# 🎥 Working with Branches

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/FhPdo8ZOS66FQOVJzFapNA.processed/full/720p/index.mp4?Expires=1793059200&Signature=JRP20tKM4Ewu8yiIA-2EDzti-LB22nxHwTFXIzraM~qDen6R8kwiJe3L4ukfoNLUTPAn8Dug5jj3z6mWFsclf4Yq~twpUBJ-AhrABB-2wLT84vZdAnXN3xQs2rzzFKZett~ao01gO1rWgfQw9VM~nttTriTAdc7JQ4iMZi2TgZA_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:42 and follow transcript
0:01
In our last video, we created a new branch different than the master branch and added a commit to it. Let's check out the current status of our repo by calling git status and ls dash l. So we see that we're on a clean working tree in the even better feature branch, and that a new free memory py file is in our working tree. Let's now change back to the master branch using git checkout master and then lists the latest two commits there. When we switch to a different branch using git checkout, under the hood, git changes where head is pointing.

Play video starting at ::1:30 and follow transcript
0:42
Thanks to this checkout, head went from pointing to the latest commit in the even better feature branch to the most recent commit of the master branch. The commit from even better feature doesn't show up at all, and the latest snapshot is the second entry we've seen before. Remember that when we switch branches, git will also change files in our working directory or working tree to whatever snapshot head is currently pointing at. Let's look at the current contents of our directory. Free memory py isn't there. This demonstrates that when we switch branches in git, the working directory and commit history will be changed to reflect the snapshot of our project in that branch. When we check out a new branch and commit on it, those changes will be added to the history of that branch.

Play video starting at ::2:12 and follow transcript
1:30
Since free memory py was committed on another branch, it doesn't show up in the history or working directory of the master branch. One thing to note after all this back and forth, is that each branch is just a pointer to a specific commit in a series of snapshots. It's very easy to create new branches because there isn't any data that needs to be copied around. When we switch to another branch, we check out a different commit and git updates both head and the contents of our working directory. Head floats around with us. It's like a free spirit. What a head trip. Okay. We've now seen how to create and switch between branches. So what if we want to delete a branch that we don't need anymore?

Play video starting at ::2:55 and follow transcript
2:12
We can do that by using git branch dash d. Let's first list the current branches in our repo and then get rid of the new feature branch by calling git branch dash d new-feature. Just like that, our branch was trimmed. We can check with another call to git branch that is not there anymore. If there are changes in the branch we want to delete that haven't been merged back into the master branch, git will let us know with an error. Hopefully, git also gives us the command to run if we were sure that we wanted to delete the branch, even if it has unmerged changes.

2:55
But we won't do that just yet. We actually want to merge those changes back into the repo first. How do we do that? It's all coming up in our next video.
