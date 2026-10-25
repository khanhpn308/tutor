# 🎥 Git Stash: Creating a Branch from a Stash (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/51f3c59d-1c02-491c-961a-cb18dbe5c93b_d0a14ecfd7534f4c8cb6faec852725a4_video22_3.mp4.mediaconvert/full/51f3c59d-1c02-491c-961a-cb18dbe5c93b_d0a14ecfd7534f4c8cb6faec852725a4_video22_3_WEBM_540.webm?Expires=1793059200&Signature=AwOxYXhQsji-lyK-twIvlSmmtaIbtp3ufAOWbIbFhpegqVlX9H1Kx1edbNjWaYcp3kTFeMT2x9bpoc7cLhJ-C3wuol-hZpCrI-8kDrTxqaQk2RUv9YxhO6z3j-itDXUsDd3mDMbYHhHKwK7fQEelWF98wWIUXVh4QHVyecLfNrg_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So, in this lecture, I'll talk about how to apply stash to a particular branch. ​So suppose you have changed quite a number of files and then ​you have stashed away all those changes on the master branch. ​Now, for reasons whatsoever, ​you have decided that you want to move all those saved changes ​in the stash to a different branch. ​So you can always do that using ​git stash branch command. ​So let's see how it works with a working example. ​So in continuation with the earlier lecture, ​I will continue working with the demo stash repository. 
Play video starting at ::57 and follow transcript
0:57
​So let's check the contents of the directory ​and let's see whether we ​any pending stash or not. So our stash ​is empty. ​Let's clear the screen and let's modify the file index dot HTM. ​Let's modify the title here. So our title will be Stash Branch ​demo. ​So that's a simple change. ​We'll quit and say now I'll modify ​the 404 dot ht ​and also ​add it to the index. 
Play video starting at :1:33 and follow transcript
1:33
​So let's modify the font family over here. ​So it'ss ​now ​and I'll modify it to times ​new ​Roman. ​So that's a simple change for this particular file ​will save and quit. ​And also I'll add 404 ​HTML to the index as well. ​So from the custom bash ​prompt, you can see there is both star and plus and this indicates ​we have modification in the working directory as well ​as changes have been added to the staging area. ​If you wish, ​you can either execute the git status, command ​or git status with ​option S option S stands for abbreviated information press enter. ​So you can see here, index dot HTML is in modified state ​and 404 HTML have been added to the index. 
Play video starting at :2:30 and follow transcript
2:30
​Now, let's create a new file and let's name it new ​file two ​TXT ​press enter. ​We'll just add a very simple line over here. This is the ​second ​new file ​in ​our stash ​example. ​Let's save and quit. ​Let's execute the git status command once again. ​And you can see we have three types of change. ​We have added the change to staging area for 400 4h tm ​L index dot HTML is a modified stage in the working directory ​and we have an untracked file which is new ​file two dot ​txt ​and of course, these two are tracked files. 
Play video starting at :3:15 and follow transcript
3:15
​Let's clear the screen. ​And if we execute the gate status with ​there is option for abbreviated information, ​then you can see ​we have three types of changes here. ​Now let's clear the screen ​and let's stash away our changes. ​So let's execute the command gates, ​stash option U Now we're using the option U because of the fact ​that we have both tracked and untracked file involved in our changes. ​So the option you will enable to stash both ​the changes for tracked as well as untracked file. ​Remember, ​get stash without any option ​works by default only for tract files, press enter ​and here you go. Our stash is created ​and we can confirm this by using the git stash list ​command and we have a single stash on the Stack. 
Play video starting at :4:21 and follow transcript
4:21
​Now let's consider a scenario that for certain important reason, ​I need to ​move away all the changes made ​in the master branch to a new branch. ​So this kind of situation often does arise during our daily workflow. ​So in order to ​move all the changes to a different branch, ​we need to execute the command git stash branch ​and let's ​name the new branch to which we want to move all our changes ​as ​branch press enter. ​And here you go. So very carefully. ​Now notice the response of the gate gate does ​several important things in one go for executing this command ​git stash ​branch demo branch. ​So the first thing ​git does, it creates a new branch ​demo branch as you can see the prompt appropriately changes to signify that. 
Play video starting at :5:26 and follow transcript
5:26
​And not only it creates a new branch, ​it also switches to the new branch demo branch ​after that git applies the stash. ​And due to application of the stash, we are able to see the ​changes that we made in our working directory. And finally, ​after application of stash ​git has dropped the stash as well as you can see down below. ​So to summarize ​the command ​git stash branch demo branch does four things in one go. ​It creates a branch, ​then it switches to the new branch. It applies the stash ​and finally it drops the stash as well. ​So let's clear the screen. 
Play video starting at :6:16 and follow transcript
6:16
​Now, if you execute the command git stash list, ​you'll see there is an empty stash since git doesn't provide ​any response. So let's add our changes to the staging area using git ​add ​dot command. ​So all the changes have been added to the staging area. As you can see. ​Now let's commit our changes git ​commit. ​A ​that will be an express commit. Our simple commit message is three files changed ​and will in short mention the name of the file ​index ​404 ​and new file two codes, close press enter, commit is done. 
Play video starting at :6:59 and follow transcript
6:59
​And now that the changes have been committed will check out master ​and ​will also merge the demo branch. So ​get merge demo branch ​press enter ​and we have a successful fast forward merge over here as you can see. ​And now that our branch has been merged, we don't need it any further. ​So we can remove the branch using git branch, ​D ​demo ​branch. ​So the branch is deleted. ​And let's now execute the command git log ​oneline ​decorate ​graph and ​all. ​So you can see the head points to master ​and the demo branch has been deleted. 
Play video starting at :7:46 and follow transcript
7:46
​If we check all the branches using kit branch, ​it will list all our local branches ​still have the hotfix branch. ​So you can remove the hotfix branch using git branch att ​and ​git branch, ​hotfix will delete this branch. ​So well, the changes in the hotfix branch is yet to be merged. Hence, ​git doesn't allow us to delete it. ​However, it is quite possible to delete a branch even without ​merging. As you can see using the dash ​uppercase ​D option. ​Now, since this branch was created for demonstration, ​there is really no need to merge your changes. 
Play video starting at :8:25 and follow transcript
8:25
​Let force delete the hot fix branch using uppercase D option press enter ​and our branch is deleted. ​Let's clear the screen ​and let's re execute our ​git log command with online decorate graph and all options press enter. ​Now we have a pretty much flat commit history as you can see over here ​and all the branches have been deleted and head wars to ​this commit ID. So with this, we conclude this lecture.
