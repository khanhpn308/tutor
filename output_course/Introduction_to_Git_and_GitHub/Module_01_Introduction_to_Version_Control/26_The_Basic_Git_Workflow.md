# 🎥 The Basic Git Workflow

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/mkLIK-PeRZa8pqzDOHT20Q.processed/full/720p/index.mp4?Expires=1793059200&Signature=ZE0SM50i8cRI4Db0visyft-JlnBZvYrwUeF2xznDlAsSfZv19vXt2GJFgNmBqg-de6OCnVloHG9aqq62--~cn~FEJd17ulHcrdS6DeAhkL0gEN4BR0Kfn5s02-PCNs9A4zEpv65O3I6CeYAEQiNeTj8DOi3cwQI9VSRlbMg11u4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:43 and follow transcript
0:01
In earlier videos, we discussed some of the basic concepts involved in working with Git. We saw that each repository will have a Git directory, a working tree, and a staging area. And we called out that files can be in three different states, modified, staged, and committed. Let's review these concepts one more time by looking at the normal workflow when operating with Git on a day to day basis. First, all the files we want to manage with Git must be a part of a Git repository. We initialize a new repository by running the git init command in any file system directory. For example, let's use the mkdir command to create a directory called scripts, and then change into it and initialize an empty Git repository init.

Play video starting at ::1:33 and follow transcript
0:43
Our shiny new Git repository can now be used to track changes to files inside of it. But before jumping into that, let's check out our current configuration by using the git config -l command. There's a bunch of info in there, and we won't cover all of it. For now, pay special attention to the user.email and the user.name lines, which we touched on briefly in an earlier video. This information will appear in public commit logs if you use a shared repository. For privacy reasons, you might want to use different identities when dealing with your private work and when submitting code to public repositories. We'll include more details about changing this information in our next reading. Okay, our repo is ready to work, but it's currently empty.

Play video starting at ::2:17 and follow transcript
1:33
Let's create a file in it, we'll start with a basic skeleton for a Python script, which will help us demonstrate the Git workflow. As with any Python script, we'll start with the shebang line. For now, we'll add an empty main function, which we'll fill in later. And at the end, we'll just call this main function. All right, we've created our file. This is a script that we'll want to execute, so let's make it executable. And then let's check the status of our repo using git status command. As we called out before, when we create a new file in a repository, it starts off as untracked.

Play video starting at ::3:00 and follow transcript
2:17
We can make all kinds of changes to the file, but until we tell Git to track it, Git won't do anything with an untracked file. Do you remember what command we have to use to make Git track our file? That's right, we need to call the git add command. This command will immediately move a new file from untracked to stage status. And as we'll see later, it will also change a file in the modified state to staged state. Remember that when a file is staged, it means it's been added to the staging area and it's ready to be committed to the Git repository.

Play video starting at ::3:46 and follow transcript
3:00
To initiate a commit of staged files, we issue the git commit command. When we do this, Git will only commit the changes that have been added to the staging area, untracked files or modified files that weren't staged will be ignored. Calling git commit with no parameters will launch a text editor, this will open whatever has been set as your default editor. If the default editor is not the one you'd like to use, there are a bunch of ways to change it. We'll include more info about changing the default editor in the next reading. For now, let's edit our message with Nano, which is the current default for this computer. We'll say that our change is creating an empty all_checks.py file, then save and exit. Voila!

Play video starting at ::4:46 and follow transcript
3:46
We've just recorded a snapshot of the code in our project, which is stored in the Git directory. Remember that every time we commit changes, we take another snapshot, which is annotated with a commit message that we can review later. Okay, that's how we add new files, but usually we'll modify existing ones. So let's add a bit more content to our script to see that in action. We'll add a function called check_reboot, that will check if the computer is pending a reboot. To do that, we'll check if the run/reboot-required file exists.

Play video starting at ::5:28 and follow transcript
4:46
This is a file that's created on our computer when some software requires a reboot. And of course, since we're using os.path.exists, we need to add import os to our script. All right, we've added a function to our file. Let's check the current status using git status again. Our file's modified, but not staged. To stage our changes, we need to call git add once again.

Play video starting at ::6:08 and follow transcript
5:28
Okay, our changes are now staged. What do we need to do next? You got it, we have to call git commit to store those changes to the Git directory. This time, we'll use the other way of setting the commit message. We'll call git commit -m, and then pass the commit message that we want to use. So in this case, we'll say that we've added the check_reboot function. With that, we've demonstrated the basic Git workflow. We make changes to our files, stage them with git add, and commit them with git commit. Are you starting to feel more comfortable with this process, and see how it fits within the rest of your tasks?

6:08
If there's anything that's not totally clear yet, remember, that the only way to get familiar with these concepts is practice. Feel free to try these examples out on your computer as we go along, until you get comfortable with these commands. Up next we'll talk more about how to write useful commit messages.
