# 🎥 Merge Conflicts

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/aNZ38xkeQIuBJncY6MpK0w.processed/full/720p/index.mp4?Expires=1793059200&Signature=YLY0ammbyf5kWtbKiSnNajApZjj~f61ZC2m8p7wEQP2dxiIC2F1U46UKlyHPwKl2MxcwCw8nZlfJSwNlX7YW7XALmxeIWHx6iPGScG-2WyFtYTOvLRarsc6uvKSVRdTF3z1bczn~VL0MRN6xTrrXDoKS2leanCm6nXH7XNdp5ck_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:46 and follow transcript
0:01
From time to time, we might find that both the branches we're trying to merge have edits to the same part of the same file. This will result in something called a merge conflict. Normally, Git can automatically merge files for us. But when we have a merge conflict, it will need a little help to figure out what to do. To see how this would look, let's edit the free_memory.py file in the master branch and replace the pass statement with a comment about what the main function should do.

Play video starting at ::1:26 and follow transcript
0:46
Cool, we made the change so let's save it and commit it back to our master branch. Next, Let's check out the even-better-feature branch and make a change in the same place. In this case, we will replace the call to pass with a call to print, saying that everything is okay.

Play video starting at ::2:08 and follow transcript
1:26
Now, we'll save this other change and commit it to this branch. We are primed for chaos with our file all setup for a merge conflict. Let's check out the master branch again and try to merge the even-better-feature back into it. Git tells us it tried to automatically merge the two versions of the free memory file, but it didn't know how to do it. We can use Git's status to get more information about what's going on.

Play video starting at ::3:03 and follow transcript
2:08
As usual, git status gives us a lot of additional information. It tells us that we have files that are currently unmerged, and that we need to fix the conflicts or abort the merge if we decide it was a mistake. It also tells us that we need to run Git add on each unmerged file to mark that the conflicts have been resolved. Let's get to work. To fix the conflict, let's open up free_memory.py in our text editor. Thankfully, Git has added some information to our files to tell us which parts of the code are conflicting. The unmerged content of the file at head, remember, in this case, head points to master, is the docstring stating what the main function should do. The unmerged content of the file in the even-better-feature branch is the call to the print function.

Play video starting at ::3:52 and follow transcript
3:03
It's up to us to decide which one to keep or if we should change the contents of the file altogether. In this case, we'll keep both statements and delete the merger markers. Now that we've fixed the conflict, we'll mark it as resolved by running git add on the file, and then call the git status to see how our merge is doing.

Play video starting at ::4:41 and follow transcript
3:52
See how Git now tells us that all conflicts have been resolved. Woo-hoo, we just need to call git commit to wrap up the merge. The comments that git commit shows us look different than other commits. That's because this is a merge and Git tells us so. It also tells us which file had conflicts which have now been resolved. The commit already has a description saying that it's merging the other branch. This description was automatically created when we called the git merge command. But we can add onto this description if we want. For example, we can say that we're keeping the lines from both branches, and then just save and exit as usual.

Play video starting at ::5:22 and follow transcript
4:41
The merge conflict is resolved. To see what the commit history looks like now, we'll use a couple of handy options to the git log command; --graph for seeing the commits as a graph, and --oneline to only see one line per commit. This format helps us better understand the history of our commits and how merges have occurred. We can see the new commit that was added and also the two separate commits that we merged. One coming from the master branch and the other coming from the even-better-feature branch. We can also see that master is pointing to the merge commit but even-better-feature is still pointing to the previous one.

Play video starting at ::6:07 and follow transcript
5:22
In our example, resolving the conflict was straightforward and easy. But in the real world, this won't always be the case. Merge conflicts can sometimes be tricky, complicated, and spread across multiple files. If you want to throw the merge away and start over, you can use the git merge --abort command as an escape hatch. This will stop the merge and reset the files in your working tree back to the previous commit before the merge ever happened. So by now you know how to create, delete, and switch between branches in Git. You've also seen that each branch represents a pointer to a commit in a sequence of independent snapshots. You know how to merge these commits back into the main trunk by using the git merge command. Amazing work.

6:07
Seriously, this isn't easy stuff. Up next, you'll find a cheat sheet summarizing all of these branching techniques followed by a quiz to consolidate these concepts.
