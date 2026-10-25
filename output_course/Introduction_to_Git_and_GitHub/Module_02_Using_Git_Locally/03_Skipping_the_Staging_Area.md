# 🎥 Skipping the Staging Area

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/eRc6G_8gQFuNgXGkVj6KwA.processed/full/720p/index.mp4?Expires=1793059200&Signature=XLMLvlOF-OkrpMlTaKM4UkkBr6jtxnXwL8PVyk1AebPiMGc4WL-~TQTI7h0Vb0Wf4HQt8qYVrlx3qx0mczwDkpwJ3uNfYuFeGHRRzU0FSdTIdY~yJRTb9vTY~kiMNu46X0R17GHJhnBTp4jR8B83IqkMD1dehRTVNeLm671H~As_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:45 and follow transcript
0:01
When we covered the basic Git workflow, we called out that the process is usually to make changes, stage them, and then commit them. The separate step between staging and committing allows us to stage several changes in one commit. But if we already know that the current changes are the ones that we want to commit, we can skip the staging step and go directly to the commit. No dress rehearsals. We do this by using the dash a-flag to the git commit command. This flag automatically stages every file that's tracked and modified before doing the commit letting it skip the git add step. At first, you might think that git commit dash a is just a shortcut for git add followed by git commit but that's not exactly true.

Play video starting at ::1:26 and follow transcript
0:45
Git commit -a doesn't work on new files because those are untracked. Instead, git commit -a is a shortcut to stage any changes to tracked files and commit them in one step. If the modified file has never been committed to the repo, we'll still need to use git add to track it first. So let's make a change to our example script from an earlier video and try out this new flag. We'll now modify our main function and make it call the check reboot function that we wrote before. If a reboot is pending, we'll print a message and then exit our program with an exit status of one.

Play video starting at ::2:13 and follow transcript
1:26
Since we're using the sys module, we'll need to import it. All right. Now that we've made the change, we're ready to try out the new -a flag. We'll also use the -m flag to add the commit message directly. This time, we'll say that we're calling check underscore reboot and exiting with one on the error condition. Success. These shortcuts are useful when making small changes that we know we'll want to commit directly without keeping them in the staging area and having to write long and complex descriptions.

Play video starting at ::2:53 and follow transcript
2:13
Keep in mind that when you use the -m shortcut, you can only write short messages and can't use the best practices regarding commit descriptions that we talked about earlier. So it's best reserved for truly small changes that don't require extra context or explanation, short and sweet. Heads up, when you use the -a shortcut, you skip the staging area. Meaning, you can't add any other changes before creating the commit. So you need to be sure that you've already included everything you want to include in that commit. In the end, using a shortcut like -a is just like using the regular commit workflow. The commit will show up in the log along with the message just as usual.

Play video starting at ::3:35 and follow transcript
2:53
Let's check that out. See how our latest commit was added to the top of the list of commits and notice how the head indicator has now moved to the latest commit. You might be wondering, what is this head and where is it heading? We'll keep coming across it. So let's clarify. Git uses the head alias to represent the currently checked out snapshot of your project. This lets you know what the contents of your working directory should be. In this case, the current snapshot is the latest commit in the project. We'll soon learn about branches. In that case, head can be a commit in a different branch of the project.

Play video starting at ::4:15 and follow transcript
3:35
We can even use git to go back in time and have head representing old commit from before the latest changes were applied. In all cases, head is used to indicate what the currently checked out snapshot is. This is how git marks your place in the project. Think about it as a bookmark that you can use to keep track of where you are. Even if you have multiple books to read, the bookmark allows you to pick up right where you left off. When you run git commands like diff, branch, or status, git will use the head bookmark as a basis for whatever operation it's performing. We'll see Head used when we learn how to undo things and perform rollbacks. We'll talk more about branches in later videos.

4:15
As a shortcut, it's generally easy to think of head as a pointer to the current branch, although it can be more powerful than that. Next, we'll dig into how we can get more information about our changes, both before and after we commit them.
