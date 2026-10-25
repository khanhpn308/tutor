# 🎥 Git Rebase Implementation Setup (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/7c4317cf-7138-49ac-ab62-931e5a13ca97_6c6cb24494a841d7ab805102d6b2c11f_video19_3.mp4.mediaconvert/full/7c4317cf-7138-49ac-ab62-931e5a13ca97_6c6cb24494a841d7ab805102d6b2c11f_video19_3_WEBM_540.webm?Expires=1793059200&Signature=TlIbyL5WizFzI1Cnhgz0Tj8kp6mv0Ut9WV4Z1WgL3OsrGOY2h8B53DYC7Jd8f0ybyuwDEuLPeI3C-NOF6bZy2VKe1565VLple5Qql~DeXwNLZaAP2QTTqjGmoY3XJ8l4VdGQBOuRKch2SttU3qhUazCMlgJNiTguyZKo50XGNYI_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So in this lecture, we'll be working on setting up an example for our ​git rebase demonstration. ​So actual demonstration will be in the next lecture. In ​this lecture, we'll set up our example. ​OK. So I have created a demo rebase repository as you can see over here. ​And if I check the log, I can see only a single commit as you can see ​over here, let's clear the screen and we are in the master branch. 
Play video starting at ::44 and follow transcript
0:44
​So let's check the contents of the directory. So we have several files over here. ​So I'll start building up the commit history ​and first, I'll modify the humans dot ​TXT. ​So in this section, I'll change the name first over here. So I'll just add by name Bsh ​Roy ​and that's it. ​Press escape key, colon ​WQ to quit ​and save. ​So since all these files in the repository are already tracked, ​considering the fact that I have made a commit of all the files, ​I'll just do an express commit using git ​commit. 
Play video starting at :1:21 and follow transcript
1:21
​A ​and for each commit, I will label with the name of the branch. So this is master branch ​and then the action I took which is added name ​and the name of the file that I have changed. ​So that's humans ​dot ​TXT codes, close press enter and the comment is done. ​So I'll just make another simple commit in the humans dot ​TXT. ​So over here under this section team, I'll just add the name of the team. ​So the team is white pick software and ​the rule can be software ​development ​and I'll add the Twitter handle over here. ​So the Twitter handle is at ​white ​soft ​and that's it. Press escape colon ​WQ to create and save ​and we make a simple commit. 
Play video starting at :2:19 and follow transcript
2:19
​So just to retrieve an earlier commit message ​and I will simply modify it. ​So the action we take is added team information ​and the file is humans dot ​TXT press enter key and the commit is done. So let's clear the screen ​now we'll create a branch using git checkout ​B ​and we'll create a feature branch. ​Let's ​assume that we are working on a very important feature ​and we name the branch, top feature, press enter. ​And we have not only created the branch but ​also we have current branch as top feature. ​So we'll just modify the file index dot HTML twice. ​So this is the first change that you're making, press I ​to insert and we'll just modify the title over here. 
Play video starting at :3:16 and follow transcript
3:16
​So let the name of the title be ​Reba ​demo. ​So demo short for demonstration press S ​KP colon ​WQ to quit and save now, we need to commit it. So I retrieve the earlier commit message ​and we modify this message suitably. ​So the branch is top feature now. ​So the action we took is modified title ​and the file is index dot HTML. So that forms the simple commit message, press enter ​and the commit is done. ​We'll just add one with change. 
Play video starting at :3:55 and follow transcript
3:55
​Let's scroll down. ​And we are right now in this paragraph as you can see over here. ​So we'll just add a simple change over here. ​Press I ​to insert and we add a simple line which is latest browser ​version ​recommended. ​So that's it. Press escape, colon ​WQ to quit and save. ​And we'll just covet it. 
Play video starting at :4:24 and follow transcript
4:24
​He can retrieve an earlier commit message ​and we simply ​modify the commit message to suit our needs. ​So the action he took his ​browser upgrade ​recommendation. ​So that's our simple commit message. Press enter ​and commit is done ​and we switch back to master branch using git checkout ​master press enter. ​So let's do an LS to check the contents of the directory. ​So I'll make two more changes in this file. ​404 dot HTML. ​So this is the first change in this file, ​press I ​to insert ​and I just modify the title over here. 
Play video starting at :5:9 and follow transcript
5:09
​So you just add 404 error ​page not found. ​That's it. Press ​SK colon ​WQ to quit and save and let's do our commit. ​So I retrieve an earlier commit message for ​the master branch and modify it suitably. ​So the branch is master ​and we add our action which is modified title ​and the file is 404 ​dot HTML. Press enter and the commit is done ​and let's make our last commit. ​So VM 404 dot HTML, ​press I ​to insert and we just ​change the font family over here. 
Play video starting at :5:55 and follow transcript
5:55
​So let's ​have times new Roman instead of Sanserif ​press ​SK colon ​WQ to quit and save. ​And let's do an express commit once again. ​So the file remains 404 ​HTML ​and it changes to modified ​font family press enter ​and the commit is done. So let's check our ​git log after all the necessary changes we have done. ​So I retrieve an earlier git log command ​which we executed earlier. ​And here it is, let's press enter ​and here you go. So here are the three commits related to the master branch. 
Play video starting at :6:38 and follow transcript
6:38
​So this is the first one which I created earlier ​when I set up the repository. And these are the two comets we created right now. ​Then I created our branch over here as you can see in the graph. ​And these are the two comets I made ​in the top Fisher branch as you can see over here. ​And lastly, we switched back to master and created those two comets over here. ​So that's the ​glog ​comet history
