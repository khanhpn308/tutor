# 🎥 Can we have multiple remotes in Git (LAB) Student Question #3: Can We Have Multiple Remotes in Git?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/9fee8b6c-d186-4d19-b635-b83eeb65b848_0a279714f037421baeaa99e3cfe4e090_video26_3.mp4.mediaconvert/full/9fee8b6c-d186-4d19-b635-b83eeb65b848_0a279714f037421baeaa99e3cfe4e090_video26_3_WEBM_540.webm?Expires=1793059200&Signature=KV3tZGLnhFY89kR6UkZ9dt1Xw14iA1CTwFcVda1XqLxB7XZ0riKuE8rsTicoHq9p7zGgXTD-i48DK-9PPdJrs92s-uxamPFGEqrCNZIdImUm5W2zWFEB13VkFDSGxKJMLMptog7kYcJCtuF9xC5SAAnRS9O14K4MRwqtBEXulOo_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hey, welcome to the lecture. So in this video, I'll address the question. ​Can we have multiple remotes in git? ​Now, ​this question actually means that whether git allows us ​to connect to multiple repositories hosted by different providers. ​For example, the same local repository can be synced ​or connected to, let's say github, ​bitbucket, GITLAB, etc ​bitbucket and GITLAB are providers which are similar to github. ​Note that git does not impose any limits on how ​many remote repositories can be connected to the local repository. ​In ​this video. 
Play video starting at ::46 and follow transcript
0:46
​We'll connect our local repository demo ​student solutions to bitbucket and gitlab. ​Now this local repository is already connected to ​github, ​rpo. ​So this is the demo student solution that I was talking off ​and ​let's check what are the remotes over here. So I'll run the command git ​remote ​dash ​V. ​So here you can see this is origin GH, actually it was origin by default and ​just to differentiate, I've added the suffix dash ​G ​which means GH means github. ​So I've renamed the origin from origin to origin ​GH. So it is thiss posit github.com, ​bro demos student solutions. So let's head over to the browser ​and I'll show you the github report that it is sent up to. 
Play video starting at :1:39 and follow transcript
1:39
​So here is the git ​repository and you can see ​bro, ​demo student solution. So, ​bro is a username and you can see all the artifacts over here. ​Now, let's head back to our bash terminal. Now, the goal is basically ​to connect to other repositories which are hosted ​on bitbucket and gitlab. ​So I'll start with Bitbucket first. ​So let's head over to the browser because we ​need to really create a blank repository over here. ​Now, if you are hearing the name Bitbucket for the first time, ​let's do a quick Google search. 
Play video starting at :2:15 and follow transcript
2:15
​So here we are in the Google and we'll do a quick Google search about Bitbucket. OK? ​And we press enter and here is Bitbucket. So on the right hand side, you can see ​it says Bitbucket is a web based version control repository ​hosting service owned by ​Atlassian for source code and development projects ​that use either Mercurial or git revision control system. ​Bitbucket offers both commercial plans and free accounts. ​So what you can do is you can create a free account on Bitbucket ​and then ​you can create a blank repository over here. ​So I'll not be going through creating a free account. 
Play video starting at :2:55 and follow transcript
2:55
​You can do that yourself and I'll just ​log in to my Bitbucket portal and create a blank repository. ​So I will head over to Bitbucket and here we are in the Bitbucket. ​So I'll create a blank repository pretty quick. ​So I have clicked on create repository ​and the repository name should be demo student Solutions. ​So let's head over to ​the ​terminal. Once again, I'll just copy the name of the repository. ​And here you go, I head back to the browser ​and this is demo student solution repository. 
Play video starting at :3:33 and follow transcript
3:33
​The access level, I'll change it to public. ​So basically I have ticked off the private repository, ​which means it is access level is public. ​So this is a blank repository. So not include a red me will not include a git ​ignore. So I'll click it. No, ​and we don't need that van settings will create a ​blank repository by clicking on the create repository button. ​So I need to select a project. That's what I see. 
Play video starting at :3:58 and follow transcript
3:58
​So I already have a project. So this is a bit ​bucket ​quick where you need to create a project and ​then you put the repository under the particular project. ​So I already have a project which is gets ​and tricks. So I'll select that and now I'll create the repository. ​So here the positive gets created and you have some helpful guidelines. ​So it says how you can add the remote to your local ​git terminal. ​So ​git remote add origin and then this entire URL. This is similar to what is in github, ​which I've already seen. 
Play video starting at :4:34 and follow transcript
4:34
​So I will head back to the bash terminal ​and here we'll paste this code. ​So here I changed the remote name because ​I don't want it to be origin, I want it to be origin ​B. So B is a short form, I'll add it for bitbucket. ​So get remote add origin ​B then this entire ​link or the URL to the blank reposit ray. ​So let's ​hit enter ​and here we go. ​So let's run the command git remote ​V once again and here you go. ​So I'll just reduce the font size. 
Play video starting at :5:17 and follow transcript
5:17
​So here, now we have a clear view. ​So origin ​G was that was existing, which is connected to the github ​and origin, ​which is the ​associated with ​bit ​pocket. ​So the remote has been added successfully. And let's try the same thing with ​gitlab. ​So if you have not heard of gitlab, so as I said before, ​GITLAB is a provider similar to github and ​bitbucket. So let's head back to our browser. ​So here we are in the browser and ​I just changed this search from bitbucket ​to ​gitlab. 
Play video starting at :5:55 and follow transcript
5:55
​So here you are in the GITLAB. On the right hand side, you can see what it says. ​GITLAB is a web based DevOps life cycle tool that provides a git repository manager, ​providing a wiki ​issue, tracking continuous integration and deployment pipeline features, ​blah blah blah. ​This software is created by Ukrainian developers Dimitry ​and it's a difficult name to pronounce. ​So I'll not attempt to do that. ​So this is what GITLAB is. ​So what I'll encourage you is to go to GITLAB and then you create a free account, ​right? 
Play video starting at :6:30 and follow transcript
6:30
​So I have already created a free account and I will go over to the tab. ​So here I'm logged in into my GITLAB account. ​So in GITLAB, a project is almost equivalent to repository, ​I use a word almost because basically a project is a superset of repository, ​which means apart from the repository, ​a project does contain some separate things. ​So in fact, if you create a project, you'll basically be creating a depository. ​So let's create a blank project. That's what our goal is. ​So the name should be demo student solution once again. 
Play video starting at :7:5 and follow transcript
7:05
​So I'll head back to bitbucket. I'll copy the name, ​demo student solutions. So here I have demo student solutions ​and ​I'll head over to Gitlab. ​So my project is demo student solution. ​So this is the project URL you can see over here. ​This is the project slug. It's almost similar to what was on github ​and pick pocket. 
Play video starting at :7:30 and follow transcript
7:30
​I don't need to add a project description, ​the access level. I'll keep it as public. I don't want to initialize with a rhythmic, ​I'll just keep it bare and blank. ​OK. ​So I think all is done ​and I'll hit create project. ​So here ​again, ​there is a helpful guidelines similar to one ​you create a blank repository on github. ​Pretty exhaustive. 
Play video starting at :7:55 and follow transcript
7:55
​So share is a command that I'm looking for. I'll simply copy it ​and head back to our bash terminal. ​So here in the bash terminal, I'll paste it. ​And as usual, ​we'll change the name to origin dash ​GITLAB. So ​GL, that is the acronym I'll use ​and let's hit enter ​and here you go. ​So we'll run the command git remote ​V once again. And we have three remotes ​origin ​G ​which is the original one connected to github, ​then origin ​GL, ​which is for ​gitlab and origin ​for bitbucket. So you're having three remotes. Now, this is not enough, ​we are able to see the three remotes, ​but we really need to see whether they are ​synced up and connected to the remote report. 
Play video starting at :8:47 and follow transcript
8:47
​Hence, we'll do a push ​and see whether the artifacts in the local report ​are pushed up to the remote deposit arrays. ​So let's do a push to origin ​BB and then origin ​GL. ​So I'll clear up the screen once again. ​So that was a Typo ​and here we are at the clean screen. ​So let's run the command now, get push ​an origin ​dash big bucket. So it's B ​and master ​hit. Enter. 
Play video starting at :9:25 and follow transcript
9:25
​There you go. ​So ​it has been pushed. It's pretty evident. ​So what we need to do right now is head over to the browser and see whether the remote ​is actually displaying the artifacts in the remote repository. ​So one thing to be noticed is that you ​might be prompted to enter the password if you're using ​Bitbucket connection for the first time. And so is the case with gitlab, ​but you've already done it, then it must be saved in your operating system, ​whichever operating system you're using, ​I'm using ​git ​bash ​terminal for windows. ​So let's head back to the browser. Now, here you're in the browser. 
Play video starting at :10:4 and follow transcript
10:04
​I'll head back to the bitbucket tab. ​I'll click, refresh ​and bingo, ​all the artifacts that you had been seeing on github ​are there. So let's check back github ​and you can see all the artifacts over here. ​And if you see ​the same in the bit bucket, so the push has been done, ​which means the remote has been added successfully and has been ​hooked up to the remote repository and the local repository successfully. ​OK? ​So let's go ahead and do the same with GITLAB. We'll head back to the bash terminal now ​and here we are. 
Play video starting at :10:38 and follow transcript
10:38
​So we'll run the command once again, only changing the remote name from B to GL. ​So its origin ​GL which is a remote connected to ​gitlab. ​So let's hit enter ​and here we are bingo. So the push has been done ​and I'm quite sure if we head over to the browser, ​things should look. OK? ​So let's head over to the browser ​and here we are in the GITLAB. Let me close this Google search ​and I'll refresh the page ​and ​Bingo. 
Play video starting at :11:12 and follow transcript
11:12
​So here we are, ​all the artifacts ​has been pushed up to the remote ​on GITLAB. ​OK? ​So that's it. ​So here we have demonstrated successfully ​that how to connect our local repository to multiple remote repositories. ​Here. ​The first step was we created the blank repositories with the same ​repository name on the different providers which are bitbucket and gitlab. ​And after that, ​we ​added the remote reference in the local repository by ​running the git remote ad and the respective URL. 
Play video starting at :11:53 and follow transcript
11:53
​Once that was done, ​then we had run the git push command with the respective origin names. So origin ​GL ​for GITLAB, origin ​B was the name we provided for the remote reference to bit pocket. ​So after the push, we refresh the browser and we could see ​the repositories populated with all the artifacts. ​So hope you enjoy the video, see you in the next video.
