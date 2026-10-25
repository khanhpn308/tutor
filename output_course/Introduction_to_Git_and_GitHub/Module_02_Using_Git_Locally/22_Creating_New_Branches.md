# 🎥 Creating New Branches

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/hDjHFs0NT7maE4de8t_nWg.processed/full/720p/index.mp4?Expires=1793059200&Signature=ffuGNhKQ80NCf6D8HAXKbVtbHB8ywOa~3xOTiT2MxIJeD56TCldrvg8IV5DeUVI87v06Z4DE74ewN6kZopEGLknPxba93Oauib1E0lq4GLACqT9hQ-yuv1JgStaV1stne7op-xnB6JDl-tDOYVzERPYM~tKP-xIqU4TmNrXlx0w_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:43 and follow transcript
0:01
As branches are essential to how work is done in git, there's tons of different ways to work with them. We can use the git branch command to list, create, delete, and manipulate branches. Running git branch by itself will show you a list of all the branches in your repository. Let's try it out in our checks repo. Our list is looking pretty empty right now, but don't worry. Creating a branch is a snap. We do it by calling git branch with the name of the new branch. Let's create a new feature branch and then list the branches again with git branch. Our new branch was created based on the value of head.

Play video starting at ::1:26 and follow transcript
0:43
Remember that this might not necessarily be the master branch. The list we get shows that we're still on the master branch. We can tell because the current branch is indicated in the command's output with an asterisk in a different color. We'll look into other things that git branch lets us do with branches later on, but right now we want to switch to a new branch. To do that, we'll need to use the git checkout command. We saw earlier how we can use git checkout to restore a modified file back to the latest commit. Checking out branches is similar in that the working tree is updated to match the selected branch including both the files and the git history. If this seems a bit confusing at first, you're not alone.

Play video starting at ::2:06 and follow transcript
1:26
I also found it hard to wrap my head around it first. But rest assured that it will become clear after we use these commands for a while. It might help to remember that we use git checkout to check out the latest snapshot for both files and for branches. All right. Let's switch to our new feature branch by calling git checkout new feature, and then listing our branches once again. Before we were working on the master branch but now that we've changed to our new branch, the star has moved to a new feature. Creating a branch and switching to it immediately is a pretty common task.

Play video starting at ::3:02 and follow transcript
2:06
So common that git gives us a useful shortcut to create a new branch and to switch to it in a single command. We can use the git checkout -b new branch to do this. Take a look. See how the message says that we've switched to a new branch? Git created the new branch and switched to it in just one command. Super efficient. Now that we have our shiny new branch, let's create a new file in. We'll create a new Python3 file, that will include the usual shebang line and empty main function and a call to that function.

Play video starting at ::3:47 and follow transcript
3:02
This file is empty because it's only the beginning of our work. As it's in a separate branch, it's okay for it to not be finished yet. Let's save our file and commit it to the current branch now. We've added a commit in this branch and it's looking better. Let's check the last two entries in the log. We see the last two commits in this branch. Notice how next to the latest commit ID, git shows that this is where head is pointing to and that the branch is called even better feature.

3:47
Next to the previous commit, git shows that both the master and the new feature branches are pointing to that snapshot of the project. In this way, we can see that the even better feature branch is ahead of the master branch. With that, we've seen how we can create new branches and commit changes to them. You might say your knowledge of branches has grown. Up next, we'll learn even more things we can do to operate with branches. So stick around.
