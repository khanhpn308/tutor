# 🎥 First Steps with Git

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/B2r1wGpHSfipT4WOrPBT8g.processed/full/720p/index.mp4?Expires=1793059200&Signature=CyTIrQ1H2jfhvLisPeI63fPaa8~KLFQa-eZcFEGUM5E30kTwxB2QPVDneKhkpOF1AQRd5N5gvC-gSJIk07easZoUlExR~UAO2BRcUDYbXLLnqiJxl8uw9LEA4~hQ0zZGq4koYq4bV4WB6u23cRaAbxhq8lmvrvqZ~YeqS0swtYU_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::1:05 and follow transcript
0:01
When starting with Git, there are a bunch of concepts that we need to learn to understand how things are organized and how our files are tracked. Over the next few videos, we'll introduce some of the main Git concepts. If any of these seem confusing at first don't panic, we'll dive into all of them as we expand our Git knowledge. Let's start by setting some basic configuration. Remember when we said that a VCS tracks who made which changes, for this to work, we need to tell Git who we are. We can do this by using the Git config command and then setting the values of user.email and user.name to our email and our name like this.

Play video starting at ::1:47 and follow transcript
1:05
We use the dash dash global flag to state that we want to set this value for all git repositories that we'd use. We could also set different values for different repositories. With that done, there are two ways to start working with a git repository. We can create one from scratch using the git init command or we can use the git clone command to make a copy of a repository that already exists somewhere else. We'll talk about remote repositories later in the course. For now, let's start by creating a new directory and then a git repository inside that directory. So when we run git init we initialize an empty git repository in the current directory.

Play video starting at ::2:35 and follow transcript
1:47
The message that we get mentions a directory called. git. We can check that this directory exists using the ls-la command which lists files that start with a dot. We can also use the ls-l.git command to look inside of it and see the many different things it contains. This is called a Git directory. You can think of it as a database for your Git project that stores the changes and the change history. We can see it contains a bunch of different files and directories. We won't touch any of these files directly, we'll always interact with them through Git commands. So whenever you clone a repository, this git directory is copied to your computer. Whenever you run git init to create a new repository like we just did, a new git directory is initialized.

Play video starting at ::3:18 and follow transcript
2:35
The area outside the git directory is the working tree. The working tree is the current version of your project. You can think of it like a workbench or a sandbox where you perform all the modifications you want to your file. This working tree will contain all the files that are currently tracked by Git and any new files that we haven't yet added to the list of track files. Right now our working tree is empty. Let's change that by copying the disk usage that py file that we saw in an earlier video into our current directory. We now have a file and a working tree but it's currently untracked by Git. To make Git track our file, we'll add it to the project using the git add command passing the file that we want as a parameter.

Play video starting at ::4:00 and follow transcript
3:18
With that, we've added our file to the staging area. The staging area which is also known as the index is a file maintained by Git that contains all of the information about what files and changes are going to go into your next command. We can use the git status command to get some information about the current working tree and pending changes. Let's check that one out. We see that our new file is marked to be committed, this means that our change is currently in the staging area. To get it committed into the.git directory, we run the git commit command. Let's try that now.

Play video starting at ::4:40 and follow transcript
4:00
When we run this command, we tell Git that we want to save our changes. It opens a text editor where we can enter a commit message. If you want, you can change the editor used to your preferred editor. In our case, this computer has nano configured as a default editor. The texts that we get tells us that we need to write a commit message and that the change to be committed is the new file that we've added. We'll deep dive into commit messages later. For now, let's enter a simple description of what we did which was to add this one file and then exit the editor saving our commit message and with that we've created our first git commit.

4:40
Up next, we'll talk more about the life cycle of each track file in a git repository.
