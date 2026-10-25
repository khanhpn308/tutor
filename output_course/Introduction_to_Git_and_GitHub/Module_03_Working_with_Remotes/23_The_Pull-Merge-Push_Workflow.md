# 🎥 The Pull-Merge-Push Workflow

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/jZ_60l02TtaOEQJ8AI3oXg.processed/full/720p/index.mp4?Expires=1793059200&Signature=djJynu3E6ieyz9cNNz5BGegVq97ypXYgzppd4OitkvIuRwSO7QdS6rtDK9yQLkh2rLcq7VJalBy0-2P8E6s06yXMDxjzQTSKnfGEx9a8QaLqH2aJI7jteVlhUEHfip3FOJ8Cij1n3eIsC4JJneTM6UMst8U9~4mDP6W5JOt3luM_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:43 and follow transcript
0:01
We've now looked at the details of fetching and pulling data from a remote repositories without any local changes. We saw earlier how we can use the git push command to send our changes to the remote repo. But what if when we go to push our changes, there are new changes to the remote repo? To find out, let's start by making a change to our all checks py script. Remember way back to the beginning of the course, when we fixed the bug in the function that checks the disk space? The one that was doing gigabyte conversion twice? Part of the reason why our code was so buggy, was that we were passing numbers around without saying what those numbers were for.

Play video starting at ::1:31 and follow transcript
0:43
We could have made our code clearer by renaming our min absolute parameter to min GB, so that it's obvious that the function expects gigabytes. With that, we've clarified the code of the function. Another way we can make the code invocation clearer, we can use the name of the parameters in the call to the function, like this.

Play video starting at ::2:12 and follow transcript
1:31
By using the names of the parameters, our invocation is clear, and we can even alter the order of the values and our code would still work. All right, we've made the change. Let's stage it and commit it as usual. We'll first use git add -p to look at the changes we made and accept them. Then we'll create a commit message to show that we've renamed min absolute to min GB, and that we're using parameter names for the invocation. We've made our change, staged it, and committed it.

Play video starting at ::3:02 and follow transcript
2:12
We should be ready to push into the remote repo, except now we have a collaborator also making changes. Let's see what happens when we try running git push. And it failed. Can you work out what went wrong here? There are a few hints. When we tried to push, Git rejected our change, that's because the remote repository contains changes that we don't have in our local branch that Git can't fast-forward. Maybe you remember when we talked about Git's merging algorithms? As usual, Git gives us some helpful information along with the error message, especially the part about integrating remote changes with git pull. This means we need to sync our local remote branch with the remote repository before we can push.

Play video starting at ::3:52 and follow transcript
3:02
We learned earlier that we can do this with git pull. Let's do this now. Git tried to automatically merge the local and remote changes to all_checks.py, but found a conflict. Let's first look at the tree of commits on all branches as represented by git log --graph --oneline --all. This graph shows us the different commits and positions in the tree. We can see the master branch, the origin/master branch, and the experimental branch. The graph indicates that our current commit and the commit in the origin/master branch share a common ancestor, but they don't follow one another. This means that we'll need to do a three-way merge.

Play video starting at ::4:35 and follow transcript
3:52
To do this, let's look at the actual changes in that commit by running git log -p origin/master. So our colleague decided to reorder the conditional clauses in the function to match the order that the parameters are passed to the function. They happen to change in the same line that we changed when we renamed the min_gb variable, which caused the conflict that Git couldn't resolve. Let's fix it by editing the file to remove the conflict. So first, let me exit with Q.

Play video starting at ::5:19 and follow transcript
4:35
We see that the problem occurred in the conditional. On the first line, we see our change, where min_absolute was renamed to min_gb. In the second line, we see the old variable names, with the checks done in a different order. We need to decide what to do to this. For example, we can keep the new order, but use min_gb. One thing to notice is that Git will try to do all possible automatic merges and only leave manual conflicts for us to resolve when the automatic merge fails. In this case, we can see that the other changes we made were merged successfully without intervention.

Play video starting at ::6:04 and follow transcript
5:19
Only the change that happened in the same line of the file needed our input. We fixed the conflict here, and the file is short enough that we can very quickly check that there are no other conflicts. For larger files, it might make sense to search for the conflict markers, greater than, greater, greater than, in the whole file. This lets us check that there are no unresolved conflicts left. Nice, now that we fixed the conflict, you can finish the merge. Do you remember how to do it? We need to add the all_checks.py file, and then call git commit to finish the merge. But first, we're going to save and close.

Play video starting at ::6:49 and follow transcript
6:04
The editor message shows that it's performing a merge of the remote branch with the local branch. We can add extra information to this message. For example, we can say that we fixed the conditional in the check disk usage function to use the new variable name and the new order. Our merge is finally ready, we can try pushing to the remote again. Yes, after fixing the conflict, we were able to push our work to the remote repo. Let's look at the commit history of the master branch now, by calling git log --graph --oneline.

Play video starting at ::7:33 and follow transcript
6:49
We see that the latest commit is the merge, followed by the two commits that caused the merge conflict, which are on split paths in our graph. As we called out before, when Git needs to do a three-way merge, we end up with a separate commit for merging the branches back into the main tree. Now we know how to successfully complete a pull, merge, and push cycle, even when it means doing some manual merges. This was a complex exercise, and it's okay if some things still seem a bit scary. We all felt panic the first time we encountered a merge conflict. But don't worry, it gets easier with practice. To practice dealing with merge conflicts, you want to have two copies of your repository in separate directories, then try editing the same lines of the same files.

7:33
You can follow along with the examples shown here, or come up with your own. Up next, we'll talk about using branches with a remote repositories.
