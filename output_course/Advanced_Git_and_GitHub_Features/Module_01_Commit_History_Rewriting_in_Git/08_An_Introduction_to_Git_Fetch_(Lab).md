# 🎥 An Introduction to Git Fetch (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/531ef333-672c-433c-b7b2-e039bd394e69_9fc6d34a912d4047bea710c45e8ea40e_video19_6.mp4.mediaconvert/full/531ef333-672c-433c-b7b2-e039bd394e69_9fc6d34a912d4047bea710c45e8ea40e_video19_6_WEBM_540.webm?Expires=1793059200&Signature=huj0SzkAOepXBdl6WjNlTLYeWYwoh-xJ0SxuqFLUB5q-1Yb2~fxg~24TAGVbhe375pg3RsXy16GuBl8HOtaSBoZxj37onFEWk78L4CmhOflr8WMyeoorKm-k0jojKa602hPf5xGrcLRFvnPAbH3B3CcL~0XlhnUo6Dhn3cn3QV4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hey there, welcome. ​So in this lecture, I will discuss ​and work on an example ​that is related to the git fetch command. ​Now, the git fetch command, synchronizes origin master ​with whatever is on the remote repository. Now, what is origin master? ​So origin master is the local copy ​of the remote repository. ​So let's get going with an example. ​Now I have created this repository Deb ​fetch for you ​and let's check the contents of the working directory using LS. 
Play video starting at ::52 and follow transcript
0:52
​So we have multiple files over here and let's execute a git log ​command. So I'll retrieve an earlier command and just execute it. ​So you can see over here, we have three commits. ​The initial commit is setting up of the repository ​and then we have two commits related to index dot H TM L and I ​have tagged the commit messages with the word local as you can see over here. ​And our local repository has a remote counterpart or a remote repository. ​So if ​I execute the command ​git ​remote ​V, you can see our remote repository over here. So when I execute the command, ​git ​log ​one line, it is equivalent to git log ​one line and then master ​since master ​is my current branch. 
Play video starting at :1:50 and follow transcript
1:50
​So let's execute it. ​And if I want to check the log of the local copy of the remote repository, then I just ​need to execute the command ​git log ​oneline. ​And then origin ​master, ​origin ​master is a local copy of the remote repository origin. ​So let's execute this command press enter. ​And well, you can compare these two log output. One is this one ​and the other is this one. And you can see both our local repository ​master ​and ​local copy of the remote repository origin master are synced up. 
Play video starting at :2:40 and follow transcript
2:40
​They have this same number of commits ​and of course, ​the same commit ids. ​Now this origin ​is actually on the github. ​So let's get back to our browser and check the status of our remote repository. ​So here we are in the remote repository on the github, ​which is demo ​fetch ​and bro is the username. ​Now, if I click on this ​comets section here, you can see ​there are five comets. So let me click on this one. ​And well, over here, ​you can see the same three comets ​that were visible ​in our ​master ​and origin ​master ​in our local repository. However, it is pretty much visible ​that the remote is ahead ​of our local repository by two comets. 
Play video starting at :3:38 and follow transcript
3:38
​And so these are the two comets. ​So we need to update our local repository. ​And here comes the role of the git ​fetch ​command. So let's get back to a terminal. So let me clear the screen ​and let me re execute the git log command ​that checks the commit history for local copy of what ​remote repository, which is origin ​master press enter. ​So now I will execute the git ​fetch command. So git fetch ​now this is followed by origin ​and then master. 
Play video starting at :4:21 and follow transcript
4:21
​So origin ​is our remote reference ​and master is a branch on our remote repository. Now, since ​we have only a single remote repository, ​you can always omit this origin ​space master. ​And ​git fetch only ​will be good enough if you had more than ​one remote repositories, then of course, you need to mention the name of the remote ​explicitly. Now to reiterate fetch command, synchronizes origin ​master ​with whatever is on the remote repository. Origin ​master does not automatically reflect with whatever is on the remote repository. ​And hence, we need to execute the ​git fetch command. So let's execute it, press enter ​and here you go. 
Play video starting at :5:23 and follow transcript
5:23
​So git has updated with six objects, ​press them, unpack them from our remote repository demo fetch. ​And these are the commit hash ​involved. It updates from master on the remote repository ​to origin ​master, which is local copy of our remote repository. ​And now if I reexecute our earlier git log command, ​we are in a position to compare this ​three commit ​ids ​against these five ​ids. ​So these are the three commits which were already existing in origin ​master. And after executing ​git ​fetch, ​our origin ​master has been updated with these two commit ids. ​Now, when you synchronize using fetch command, it updates only origin ​master which is local copy of our remote repository. 
Play video starting at :6:29 and follow transcript
6:29
​It does not affect ​master ​or any non remote branches in our local repository in any way at all. ​So how do we get the updates that has been ​pulled down in our local copy of remote repository origin ​master to our local ​repository master. So ​there is a way and we have to manually do that, ​it does not happen automatically. ​So the way is to do a ​git merge. Now you're already acquainted with the git merge operation. ​So let's clear the screen. So let's now reexecute our ​Gitler command press enter. 
Play video starting at :7:17 and follow transcript
7:17
​So now you can see the head point ​to master ​at this commit ​ID ​and origin ​master is ahead of master by these two commits. ​So this is a classic scenario where we can do a fast forward merge of origin ​master ​and ​master. ​Now remember that origin ​master ​is a branch ​which is ​just like any other branch. Only difference ​is that this is a ​remote branch ​and a remote branch is visible using ​git branch with the R option. And of course, if you do a git branch, ​a, ​you can view both the local and remote branches. ​So let's do our merge operation. ​So we are in the master branch ​and we'll merge ​origin ​master with the master branch git ​merge, ​origin ​master press enter. 
Play video starting at :8:28 and follow transcript
8:28
​And here you go, ​we have a fast forward merge ​and let's ​re execute our ​git lock command. So let me retrieve an earlier command ​press enter. ​And here you go. Now, both master and origin ​master ​are at the same level as a result of our successful fast forward merge. ​So let me clear the screen. ​Now, there are a few important points that I would like to mention here. ​So do a fetch before you start your day's work. So when you sit at your terminal ​in the morning, ​you should always update origin ​master using your date fetch command ​so that you, ​you can see what work your other team members or collaborators have done. 
Play video starting at :9:19 and follow transcript
9:19
​Secondly, do a ​git fetch ​before you push to remote repository. It is always possible ​that some other team member of yours have made the ​same commit as yours or there might be some conflicting commits ​that you're going to push. ​So always do a gate ​fetch ​before you do a git push ​and finally execute the git fetch command as frequently as possible to stay in sync. ​Git ​fetch is a non destructive command ​and it updates the references only in origin ​master ​and does not affect any of the non remote branches in your local repository, ​including the master branch.
