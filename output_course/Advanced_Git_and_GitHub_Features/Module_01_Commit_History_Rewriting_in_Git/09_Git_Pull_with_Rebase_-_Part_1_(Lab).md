# 🎥 Git Pull with Rebase - Part 1 (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/20c324f7-9c11-4c7e-9e71-8d1ae3c73e75_c1f1dffd81e84a95a250fd76d07bfd2c_video19_7.mp4.mediaconvert/full/20c324f7-9c11-4c7e-9e71-8d1ae3c73e75_c1f1dffd81e84a95a250fd76d07bfd2c_video19_7_WEBM_540.webm?Expires=1793059200&Signature=gD4ZCeCAdxnumlxHVnFeQ8cqvQVqsyZ4tbcx-ddOe5lypsVWvXJsdjo~wsuzKpSN0-bAQnhQ5bWCHLJnaCqQjb4SgWcjSdWOw0GsHstm8oC74tK~qqdhjBqCeXfWy51HMYP4xmAh2z0kHATKkLYzOjJK3srF3acCS1AKMwoCWDI_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::9 and follow transcript
0:09
​Hi, welcome. So in this lecture, I'll talk about the difference between doing a ​git pull versus ​git pull with rebase. ​So we need to understand certain basic concepts before ​we actually go ahead with examples on this topic. ​So to understand this, you first need to understand ​that your local ​git ​maintains not only your local repository, but it also maintains ​a local copy of the ​remote repository. Now, ​git ​fetch ​brings your local copy of the remote repository ​up to date. For example, if your remote repository is github, ​you may want to fetch any changes made in the remote repository ​to your local copy of the remote repository. ​This will allow you to perform operations such as diff ​or merge ​git pull. On the other hand, will bring down the changes in the remote repository ​to where you keep your own code. 
Play video starting at :1:25 and follow transcript
1:25
​Typically, git pool will do a ​git ​fetch first to bring the local copy of the remote repository ​up to date ​and then it will merge the changes into your own code repository. ​So git pool does a git fetch to pull down data ​from the specified remote ​and then calls git merge to join the changes received ​with your current branch's work. However, ​that may not always be, be the best case, you can also rebase the changes in ​and that may end up being a lot cleaner. This can be done simply by tacking on ​the dash ​dash ​rebase option ​when you pull like so ​get pull ​rebase ​and then the remote name. ​So remote name can be for example, origin ​and then ​the branch name, ​so the branch name can master. ​So I missed an L here. So it's good ​pull. 
Play video starting at :2:42 and follow transcript
2:42
​So why is this useful? ​Sometimes it's easier not to merge in the upstream content. And it's better ​just to reapply your work ​on top of the incoming changes. ​For long term changes, it is probably best to do a merge. ​But for smaller change sets ​history will stay cleaner ​with the rebase. OK? So now that I have explained thoroughly ​the basic concepts behind pool with rebase, ​I'll start working on the actual example. 
Play video starting at :3:21 and follow transcript
3:21
​So I'll demonstrate the example basically in three steps. ​So first, I'll set up the commit history ​so that we have the basis for working on the example. ​In the second step, I will demonstrate how to do a ​git pull without rebase. ​And what are the consequences of doing the same? ​And in the last step or the third step, ​I'll show actually ​how to do a pool with rebase and consequences of doing the same. ​So I've created a repository ​which is demo pool rebase ​and I have several artifacts within this directory. ​If I check the git ​log, ​I have a single commit ​wherein I just committed all the files to set up the repository. OK. 
Play video starting at :4:13 and follow transcript
4:13
​Let me clear the screen. ​So I'll create a remote repository and set ​up the connection with my local repository, ​which is demo ​Pool ​rebase. ​So the name of the remote repository on github will be the same. ​So I'll just copy the name of this repository and I'll go to github. ​So I'm already logged into github.com. ​So I'll click on this green button which is the new repository. ​And here I'll fill the repository name, which is Demo ​Pool, ​rebase and rest of the thing I'll accept as default. 
Play video starting at :4:53 and follow transcript
4:53
​So you'll remain a public repository and not a private one because private one ​requires a paid account. And I'm not initializing any with ​me ​or adding any ​dot ​git ignore or a license. ​So I'll click on this green button, create repository ​and the repository gets created. ​So initially github ​presents me with this page filled up with instructions ​and the repository is empty. ​So here in this create a new repository on the command-line, ​I'll copy this line which is git remote ​add origin ​and then the URL of ​the remote repository. So I'll get back to my terminal and paste this one. ​Now, I'll press enter and our connection with the remote repository has got set up. 
Play video starting at :5:46 and follow transcript
5:46
​So just let's confirm it using git remote ​V press enter ​and here you go. ​Now, the remote repository is out there, but it is blank without any contents. ​So we'll push the contents of our local repository to remote repository. ​So let's get back to our browser ​and we'll simply copy this command. ​So basically this is command for pushing our contents to remote repository. ​Let's get back to a terminal once again ​and ​just paste it over here. So this is get push and ​dash ​you is ​required to set up the tracking branching relationship ​between master of local repository and remote repository. 
Play video starting at :6:35 and follow transcript
6:35
​So this is a one time requirement ​subsequently. If we push our ​changes to remote repository, we don't need this flag you or the parameter view. ​So let's push our changes, press enter. ​So get ​prompts ​us for our password or credentials for github.com. ​So I'll enter my credentials. So username is bro ​and press enter for password. ​So the password dialog box comes up and I enter my password. 
Play video starting at :7:7 and follow transcript
7:07
​So I'm on Windows platform, ​you may not be offered a password dialog box in a mac or Linux platform, ​you can probably simply enter ​enter the password ​on the command-line. ​So let's click OK button ​and all the objects on our local repository has been pushed. ​So let's get back to our browser ​and refresh the page. So I'm on Firefox browser, ​I'll click this button over here to refresh ​and all the artifacts ​have been pushed to our remote repository. ​Now, we are all set to make the changes in our local repository ​and interact with our remote repository. ​So I come to my terminal. So let me clear the screen. 
Play video starting at :7:56 and follow transcript
7:56
​So I'll do an LS and I will modify the file ​index dot H TM L. I'll use a Wim editor press enter ​and I'll first change the title. ​So it's a simple title. Pull ​rebase demo. So demo for demonstration ​and that's our first change ​press S ​KP colon ​WQ to query ​and save. And let's do an express commit using ​git ​commit. ​Am I'll tag the commit message ​with ​local since this is a local commit ​and this will help us to identify the commits. 
Play video starting at :8:35 and follow transcript
8:35
​So when I do a commit on the remote branch, ​I'll tag the commit message with remote. So our changes were added ​title ​and the file involved is index dot html. Press enter and the committee is done. ​Let's do a third comment. ​I'll simply modify here the reference to this image file, Apple touch ​icon dot ​PNG. ​So let's assume that we have a file, ​Apple touch ​icon two ​PNG. ​So this is our second change. 
Play video starting at :9:8 and follow transcript
9:08
​Press S ​KP colon ​WQ to query and save. Do an express ​retrieving an earlier command ​and just I'll modify ​the commit message. So commit message is modified ​image name, press enter ​and let's go ahead with our third ​and I'll change ​the version of this ​Js file. So I'll modify it to 1.4 0.3 dot min ​Js. ​And that's our third change, ​skip key colon ​WQ to quit and save. ​And let's do an express. ​And our simple commit message is modified ​Js file. 
Play video starting at :9:53 and follow transcript
9:53
​And the odd fact is index dot H TM L as usual press enter ​and the commit is done. ​So let's clear the screen ​and let's execute the ​keylog command. So I'll retrieve ​all your command. ​And here is our command git log ​with relevant flags, press enter ​and here you go. ​So this was his first comment when he did our repository setup. ​And these are the three commits I did right now. ​Now ​let's assume that ​we're working in a team and I'm one of the developer ​and I have another ​developer. 
Play video starting at :10:33 and follow transcript
10:33
​So this is my local repository. ​I made the necessary changes and my developer friend ​has made some changes in his local repository and pushed ​those changes ​in order to simulate that situation. ​I'll just modify the file 404 dot HTML pretending that these are the changes ​that was pushed by my developer friend. So I'll click on this edit button here. ​You can see ​in order to edit this file ​and let's make a few simple changes. So let's edit the title over here ​and here right now, this page not found. ​So I just add 404 error ​and that's it. 
Play video starting at :11:20 and follow transcript
11:20
​So I'm done with the change. ​I'll scroll down ​and commit these changes in the remote repository. ​So I'll tag the commit message with the remote ​and the action we took is added title ​and the file involved is 400 4h TM L. Let's scroll on further ​and click the green button over your commit changes. ​So you're done with this commit. Let's change this file once again ​so that we have at least two commit from my developer friend. ​So let's click on this edit button. 
Play video starting at :11:55 and follow transcript
11:55
​So I'll just modify the line height from 1.2 to 1.4. ​And that will be our second simple change. I'll commit this change. ​So let me scroll down ​and I'll tag my commit message with the remote again. ​And my commit message ​and the action I took is modified ​line height and the file involved is 44 dot HTML. So let's scroll on further. ​Click on the green button over here and commit the changes. 
Play video starting at :12:27 and follow transcript
12:27
​So we have two commits in the remote repository ​and now let's get back to our terminal. ​Now, let's assume that ​I'm ready ​to pull the changes from the remote ​repository that my developer friend has committed. ​So I'll simply execute this command with quick pull ​origin ​master press enter. ​So I've already explained earlier ​that ​git pull without rebase ​is equivalent to executing two commands. ​One is git ​fetch to fetch the changes from remote repository ​and then executing ​git merge to merge in the changes. ​So right now, execution of git pull origin master command ​has opened ​my default text editor, sublime text for doing a merge commit. ​So here is the default commit message provided by git, ​I'll just make a simple modification. So instead of having this long URL over here, ​I'll just ​have ​the demo ​pool rebase only. 
Play video starting at :13:39 and follow transcript
13:39
​So merge branch master of ​demo ​pool, ​rebase, ​remote repo. ​So repo is short for repository. ​So I'm happy with this commit message. ​I'll click on file save and then exit from the editor. ​And here you go, the merge commit has been done over here. As you can see, ​the merge is ​made by the recursive strategy ​and it mentions which file changes were merged. ​So let me zoom in a bit so that you can compare two git ​log outputs one ​before doing the merge and ​the other after doing the merge. 
Play video starting at :14:22 and follow transcript
14:22
​So now I'll execute the git log command. So let me retrieve an earlier command. ​So here we are press enter ​and here we go. ​Now, ​let's compare the commit history at the top prior to doing ​a gate pole and compare this one as well after doing ​the merge operation. ​So here you can see the four commits of the local repository. ​And after the merge, we have an additional commits. ​Here are the two comets from the remote repository as you ​can see which can be identified due to this remote tags ​I added while creating the commits ​and share ​is a merge commit that resulted from ​the command gate pull. 
Play video starting at :15:12 and follow transcript
15:12
​And over here, you can see the graph related to the merging. ​Now, this is OK ​if we pull in the changes related to a long feature, ​but if there are many small changes in the remote repository, ​and we consistently use a ​git pool command to merge in our changes, ​then our local commit history might get cluttered with lot of mergers. ​And in such scenario where you want to pull ​in small small changes from the remote repository, ​it's better to do a gate pull ​with rebase. ​So next, I'll show you how to do a git pull with rebase, ​which is a more convenient way to pull in small changes from remote repository.
