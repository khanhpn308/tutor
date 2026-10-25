# 🎥 Student Question #1: Can We Rename the Remote Repository Reference?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/87da9746-fccc-41e1-a9fb-9dca33284aa7_8596801f9ca548c185b8a150547552e5_video26_1.mp4.mediaconvert/full/87da9746-fccc-41e1-a9fb-9dca33284aa7_8596801f9ca548c185b8a150547552e5_video26_1_WEBM_540.webm?Expires=1793059200&Signature=TTyk0RJAjHfQCR6DVYnn1mbgbSUsaK91uKjGVyEKUS15UxWKBOafGSZa-oKRRMTPExAIwCqqeo1hYhzv8helhZ7b-C6QdDW12v7SeF5erwsOCh61ZyAwspXvVFzy5Y2UUVMqBDQBDqtKAnd1h1x92HoK~Fx6-WrSrZmXnL4nII0_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hey, welcome to the lecture. ​So here in this lecture, we are now in the repository Demo Student Solutions, ​as you can see. ​So the question that we will address here is ​can we have different name for a remote repository? ​Yes, sure, we can ​rename an existing remote. ​So I have created this repository Demo Student Solutions to address ​this particular questions from ​the different students ​so that they understand things better. ​So ​let's check this repository a bit and let's see where we are. ​So we are in this particular directory ​users HPP ​PC first ​get fast demo Student solutions. 
Play video starting at :1: and follow transcript
1:00
​OK. So let's get going. ​So let's see what are the artifacts are in the depository, Ls ​LRT. ​So you can see these are all the standard files we have been ​using so far in this course. So these are the artifacts over there. ​However, we will not be dealing with the artifacts in this ​a particular lecture. So basically, I'll clear the screen. 
Play video starting at :1:26 and follow transcript
1:26
​So basically, I will start demonstrating how to rename a remote repository. ​So let's check what are the remote or what is the remote that is existing? Now? ​Of course, there can be multiple remotes in a repository. ​So the remote is get a remote. ​So you can see origin is the name of the remote reference for the remote repository. ​And you can see the full path over here. OK. 
Play video starting at :1:57 and follow transcript
1:57
​So ​now if you want a short output from git, ​you can of course run this command which is git remote instead of the vs ​version, which is git remote ​V. ​So now we'll just rename this remote from origin to something else. ​Let's consider my new remote as the name of ​the new remote that will change from origin. ​So the command is git ​remote ​and then rename, this is the subcommand ​and then we'll be having ​the existing remote name. Of course, that is origin ​and we'll be renaming it to my new remote. ​OK, ​let's run this command and see what happens, ​get return silently ​and we need to really verify what happened after running this command. ​So run the command again, get remote. 
Play video starting at :2:56 and follow transcript
2:56
​And we see bingo, ​the new name of the remote reference is my new remote instead of the origin. ​And of course, if you want to change back to the old name, you can even do that. ​So it will be command will be git remote, rename my new remote and origin. ​So that's it. You can see that we can very easily rename a remote in git. ​Now, the question is, ​can there be any errors? ​Yes, you might face certain errors when you try to rename ​the remote repository. 
Play video starting at :3:34 and follow transcript
3:34
​So what are the type of errors? So the first type of error message might be, ​could not rename config section remote old name to remote new name, ​which you can see. ​I have got it displayed in front of the screen. ​Now, ​this error means that the old remote name you typed doesn't exist. ​And these simple errors can happen. ​You can check which remote currently exists with the git remote ​V command or simply the git ​remote command. ​The second type of error which might happen or the ​second error message which you might get is remote. 
Play video starting at :4:17 and follow transcript
4:17
​The new remote name ​already exist. So this two you can see displayed on the screen. ​So this error means that the remote name you want to ​use already exist when I say already you want to use. ​So basically, we are trying to rename ​the remote to a name that is already existing. ​So if you try to rename a remote, which is origin to origin naturally, ​you'll get this error message. ​Now to solve this, you either use a different remote name, ​so or ​you rename the original remote. ​So ​that's all for this lecture. I hope you enjoyed it. See you in the next video.
