# 🎥 Amending Commits

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/dDdJ6GvATJGrMiAJ6HmbdQ.processed/full/720p/index.mp4?Expires=1793059200&Signature=LrlLMTs9uIhpPCP2qi1MMYOnaxsJkYq3ejNBSKn4g2CWDYRcUCNq8NTjyCfgqSVnGRSpWgv26t4yd4uzpu9jzZCa20RyAAn0WmmY0FEulxzLJKLvTUWmNeZT6RGLQJUuqTawA4Q9yRNWUfKWPdmDYkBqYep2osdRk4jcIw9lGws_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:46 and follow transcript
0:01
In general, we try to make sure our commits include all the right changes and descriptions. But we're all human and we make mistakes. It's not uncommon for developers and IT specialists to realize that there is an error in a recent commit, which is why it's important to know how to take action and fix it. Let's say you just finished committing your latest batch of work, but you've forgotten to add a file that belongs to the same change. You'll want to update the commit to include that change. Or maybe the files were correct, but you realize that your commit message just wasn't descriptive enough. So you want to fix the description to add a link to the bug that you're solving with that commit. What can you do? We can solve problems like these using the --amend option of the git commit command.

Play video starting at ::1:26 and follow transcript
0:46
When we run git commit --amend, git will take whatever is currently in our staging area and run the git commit workflow to overwrite the previous commit. Let's see this in an example. We'll go to our scripts directory and create two new files using the touch command. Then list the contents of the directory using ls at our Python script and commit it saying that we've added two files. As you can see, the message printed by git says that only one file was added.

Play video starting at ::2:36 and follow transcript
1:26
Our commit message said that we added two files, but we forgot to add one of them. Ouch. Don't panic. We can fix it. We'll start by adding the missing file and then amending our commit. We called git commit --amend and an editor opened up showing the commit message and the stats about the commit that we're working with. The list of added files for this commit now includes both files that we wanted to add. Yay. Now that the files have been added, we can also improve our initial commit message which was a bit too short. We'll keep the existing description as the first sentence of our commit, and then add a line of description about the intended purpose of each file.

Play video starting at ::3:16 and follow transcript
2:36
With that, our commit is ready to be amended. Let's save the new description as usual. We've amended our previous commit to include both files and a better message. You could also just update the message of the previous commit by running the git commit --amend command with no changes in the staging area. An important heads up. While git --amend is okay for fixing up local commits, you shouldn't use it on public commits. Meaning, those that have been pushed to a public or shared repository. This is because using --amend rewrites the git history removing the previous commit and replacing it with the amended one.

3:16
This can lead to some confusing situations when working with other people and should definitely be avoided. So remember, fixing up a local commit with amend is great and you can push it to a shared repository after you fixed it. But you should avoid amending commits that have already been made public. If this sounds confusing now, don't worry. We'll mention it again when we talk about collaborating with others through shared repositories. We've covered how to fix staged and unstaged changes, and how to fix a commit that was incomplete. Up next, we'll talk about what to do if you come across a bad commit that needs to be completely reverted.
