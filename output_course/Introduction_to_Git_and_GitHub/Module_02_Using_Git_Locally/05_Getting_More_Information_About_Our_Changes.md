# 🎥 Getting More Information About Our Changes

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/ihrh1pUVQDqQf58_bAXVGg.processed/full/720p/index.mp4?Expires=1793059200&Signature=NLZBbTbMNUjRXkAutswd~qaVTC3OwRUaRT5447kOJ3bFlVN-xmyweVaGATaiWRRc8QWRFGwns3KCPS69LDAe-G6Tp249zQoz7bW3vK-Miy9jdRd-d06TAs2v6eIU5oAc~pRWTAjsMY-q8imgO9fqoMxAMhtbLQkRBNVHYHSdItw_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:41 and follow transcript
0:01
We've seen how git log shows us the list of commits made in the current Git repository. By default, it prints the commit message, the author, and the date of the change. This is useful, but if we're combing through a history of changes in a repo to try and find what caused the latest outage, we'll probably also need to look at the actual lines that changed in each commit. To do this with git log, we can use the -p flag. The p comes from patch, because using this flag gives us the patch that was created. Let's try it out. The format is equivalent to the diff-u output that we saw on an earlier video.

Play video starting at ::1:23 and follow transcript
0:41
It shows added lines with plusses and remove lines with dashes. Because the amount of text is now longer than what fits on your screen, Git automatically uses a paging tool that allows us to scroll using page up, page down, and the arrow keys. We still have one commit below the other, but now each commit takes up a different amount of space, depending on how many lines were added or removed in that commit. Using this option, we can quickly see what changes were made to the files in our repository. This can be especially useful if we're trying to track down a change that recently broke our tools. If we don't want to scroll down until we find the commit that we're actually interested in, another option is to use the git show command.

Play video starting at ::2:03 and follow transcript
1:23
This command takes a commit ID as a parameter, and will display the information about the commit and the associated patch. We'll talk more about commit IDs in a later video. But for now, remember that this is an identifier that we see next to the word commit in the log. Let's check this out by first listing the current commits in the repo and then calling git show for the second commit in the list. First, I'm going to exit out by pressing q.

Play video starting at ::2:47 and follow transcript
2:03
We've shown how we can use git log for listing commits, and git log -p for showing the associated patches. Another interesting flag for git log is the --stat flag. This will cause git log to show some stats about the changes in the commit, like which files were changed and how many lines were added or removed. Let's try it with our repo. There are a bunch of other options to git log, so we won't cover them all. You can always use the reference documentation or the manual pages to find out more. And as we called up before, you don't need to memorize any of this, you'll learn the different commands and flags by using them.

Play video starting at ::3:32 and follow transcript
2:47
The important thing to remember is that all the information is stored in the repository and you have it at your fingertips when you need it. You're welcome. Now, what about changes that haven't been committed yet? Until now, whenever we've made changes to our files, we've either added them to the staging area with git add and committed them with git commit, or committed them directly using git commit -a. This works fine, but it means we have to know exactly which changes we've made. Sometimes it can take a while until we're ready to commit. We call these commitment issues. Just kidding. But imagine you've been working on adding a new complex feature to a script and it requires thorough testing.

Play video starting at ::4:16 and follow transcript
3:32
Before committing it, you need to make sure that it works correctly. Check that all the test cases are covered and so on and so on. So while doing this you find bugs in your code that you need to fix. It's only natural that by the time you get to the commit step you don't really remember everything you changed. To help us keep track, git gives us the git diff command. Let's make a new change to our script and then try this command out. We'll add another message to the user to say that everything is okay when the check is successful and then exit with 0 instead of 1.

Play video starting at ::5:01 and follow transcript
4:16
Okay, we've made the change. Let's now save it and check out what git diff shows us. Again, this format is equivalent to the diff -u output that we saw in an earlier video. In this case, we see that the only change is the extra lines that we've added. If our change was bigger and included several files, we could pass a file by parameter to see the differences relevant to that specific file instead of all the files at the same time. Something else we can do to review changes before adding them is to use the -p flag with the git add command.

Play video starting at ::5:54 and follow transcript
5:01
When we use this flag, git will show us the change being added and ask us if we want to stage it or not. This way we can detect if there's any changes that we don't want to commit. Let's try that one out. We've staged our change and it's now ready to be committed. If we call git diff again, it won't show any differences, since git diff shows only unstaged changes by default. Instead, we can call git diff -- staged to see the changes that are staged but not committed. With this command, we can see the actual stage changes before we call git commit. Let's commit these changes now so that they aren't pending anymore. We'll say that we've added a message when everything's okay.

5:54
Nice, and with that, we've learned a bunch of different ways to get more information about our changes. We've covered a lot of ground, so take the time to review and practice these commands if they don't make sense yet. Up next, we'll look into what happens when we want to delete or rename files in our repository. It's time to do a little housekeeping.
