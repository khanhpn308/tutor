# 🎥 Squashing Changes

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/Is_sezZGQSWk0fMbw9HP-A.processed/full/720p/index.mp4?Expires=1793059200&Signature=hx0jZy94iK857vKzGATqEFWJ3ZBxBXVE9Ov0npkDa6wyfVbQPIryupPjROMCk8uDBWaE3NJu8ilqosgMA314l0IUhmRn~lXSP~zR8RgIF2mwdoJB2q4pGbLRh2NS1b-IQDkU~k6UFl5UbtP1fSscML2CkkuQAuf~dCD66JhRSxE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:42 and follow transcript
0:01
As we've caught up before, you shouldn't rewrite history when the commits have been published. That's because someone else may have already synchronized that repo with those contents. This rule is waived with pull requests, since it's usually only you who have cloned your fork of the repository. So say the project maintainers ask us to create a single commit that includes both changes and a more detailed description than the one we submitted. We can do that by using the interactive version of the rebase command called rebase-i, as the parameter to the command will pass the master branch. So we'll call git rebase-i master.

Play video starting at ::1:25 and follow transcript
0:42
When we call an interactive rebase, a text editor opens with a list of all the selected commits from the oldest to the most recent. By changing the first word of each line, we can select what we want to do with the commits. The default action here is pick which takes the commits and rebases them against the branch we selected. This is what we do with git rebase in an earlier video when we called it without the dash i flag. But now we can change the action to something else. The comments in the file tells all the different commands we can use for our commits. For example, we can reword a commit message keeping the changes as they are but modifying the commit message.

Play video starting at ::2:18 and follow transcript
1:25
We can also edit the commit to add or remove changes from it. We have two options for combining commits, squash and fix up. In both cases, the contents of the selected commit are merged into the previous commit in the list. The difference is what happens with the commit messages. When we choose squash, the commit messages are added together and an editor opens up to let us make any necessary changes. When we choose fix up, the commit message for that commit is discarded. For our example, we want to use squash so that we can combine both commits but also modify the commit description. So let's change the pick command in the second line to squash it into the first one, then we'll save and exit the editor as usual.

Play video starting at ::3:07 and follow transcript
2:18
Once we've told git that we want to squash a commit unto the one before it, we're given another file to edit. In this case, it's the combined commit message. As usual, git shows us some helpful information in the comments including which files are modified and what commits are being combined. We want to improve the description by adding more info about our change. Let's add we're including an example use case. All right. Now that our commit contains the right information, we can save and exit as usual. Yes, our rebase worked.

Play video starting at ::3:48 and follow transcript
3:07
Let's check the output of git show to see the latest commit and the changes in it. Success, we got exactly what we wanted here, our two changes have been combined into one that contains the whole new file and the right commit message. Before we try to push this change to our repo, let's call git status to check the info that git gives us about the current state. Git tells us that our local branch has one commit, which is the rebase we just did. It also tells us that the origin/add-readme branch has two commits. These are the two commits we had already pushed to the repo.

Play video starting at ::4:42 and follow transcript
3:48
Let's look at the graph history of our commits by calling git log --graph --one line --all for all branches, and -4 for just the latest four commits. We can see that the two commits pushed to the origin/add-readme branch show up in a different path than the commit that's currently in our local add-readme branch. This is expected whenever we do a rebase because the old commits are in the remote repo and we have a different commit in our local repo. What do you think will happen when we call git push? Let's try that out. As we expected, git doesn't like us trying to push our change because it can't be fast-forwarded. But in this case, we don't want to create a merge.

Play video starting at ::5:22 and follow transcript
4:42
Instead, we want to replace the old commits with the new one. To do this, we will call git push -f to force git to push the current snapshot into the repo as is. This time, our push completed successfully. Git tells us here that we forced an update. Let's look once again our history graph by running git log -- graph --one line --all -4. This time, it's just one commit on top of master. The divergence is gone.

Play video starting at ::6:04 and follow transcript
5:22
Now let's look at the contents of the pull request. Success. We've managed to combine both are commits into one by using the interactive version of git rebase. Nice job in making it through these first videos. You now know how to create a pull request on GitHub, how to update a pull request, and squash changes. These tools are all super-helpful when using GitHub. Up next, you'll find a reference of the commands we used and links to where you find more information.

6:04
After that, there's a quick quiz to check that everything is making sense.
