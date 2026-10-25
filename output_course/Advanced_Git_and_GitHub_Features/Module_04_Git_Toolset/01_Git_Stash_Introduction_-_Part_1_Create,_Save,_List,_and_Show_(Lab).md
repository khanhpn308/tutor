# 🎥 Git Stash Introduction - Part 1: Create, Save, List, and Show (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/9328d401-b24d-42a8-96ae-fa8e63d7b705_7d4da9e6405640bd921537711435f175_video22_1.mp4.mediaconvert/full/9328d401-b24d-42a8-96ae-fa8e63d7b705_7d4da9e6405640bd921537711435f175_video22_1_WEBM_540.webm?Expires=1793059200&Signature=ejUYhwLAwzfRg1EGKDtFdkiIg4rB7zI13LFJX5nGJ71a589gRPZq7dOeG9AqNm1BO3ksKMfIscHNmgV0TK0plcNIq49Oht20c0fL-6ThJalUgP2vHDvzLI2nOpmmFG4oXfb3yVErmCZCvJhIJKDXnwwcVLsK2sClwrMoMj2s4D0_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome in this lecture. ​I'll talk about the git stash command and we'll work on an example as well. ​So the git stash command looks something like this. Git stash. ​Now the git stash command is used to temporarily ​store uncommitted work in order to clean out your working ​directory without having to commit unfinished work on a branch. ​Sometimes while working on a part of your project, things can be in a messy state ​and you might want to switch to a different branch to work on something else. ​But before moving on to another work, you do not want to commit your unfinished work. 
Play video starting at ::57 and follow transcript
0:57
​Basically, you want to return back to your unfinished work later on. ​So the solution to this problem is git ​stash command by executing the git stash command, ​you can save your Stack of unfinished work ​that includes modified tract files and staged changes. ​After you save your dirty state of your working directory, ​you can retrieve it at any point of time or whenever you need it. ​So let's get going with an example. So let's check the contents of the directory. ​So we have the several files over here and I have created this demo stash ​repository for you. ​This is a fresh new repository and if you check the git ​log ​one line, you can see a single commit over here. 
Play video starting at :1:50 and follow transcript
1:50
​So let's modify the file index dot ​HTML, ​we ​index dot HTML and we'll make a simple change. We'll add the title here, ​stash ​demo. So demo is short form for demonstration. So let's create the editor. ​We save our changes ​and we're back to the terminal. ​So let's think of the scenario that I was working on this file index dot HTML. ​And now my boss has asked me to work on a certain fix immediately. 
Play video starting at :2:24 and follow transcript
2:24
​So I need to save off my unfinished work. ​And for this git stash command will become very handy. So the command is git stash and ​optionally you can use the save, ​but this is not required if you don't provide any argument to the ​save command will not be providing any argument to the save subcommand here. ​So we'll simply use ​git stash press enter ​and you can see the git says that it has saved the working directory ​and the index state ​wip on master. So ​wip stands for work in progress. ​Now, whenever you execute the git stash command, ​stash is created which you can view using git stash list. ​So git stash list shows you what was a stash that was involved over here. 
Play video starting at :3:20 and follow transcript
3:20
​So you can see the stash is created over here. And the first ​ST is identified as Stash Act, then curly braces, ​zero and then the closing curly braces. ​And there is a set ​description over here. ​So this syntax is somewhat like the reflog syntax which you learned earlier. ​And now if I try to view the file ​index dot HTML, you can see that our file has returned back to the original one. ​And the title modification which we did a few moments ago is no ​more there because git has stashed or saved of our unfinished work. ​So let's quit the editor. 
Play video starting at :4:7 and follow transcript
4:07
​And now you can see ​our working directory status has also changed after execution of the ​git stash command. ​So earlier, there was change to the index ​H TM L and the star symbol shows there was a modification state. ​And now after the execution of the stash command, you can see ​there is no symbol over here, which means a clean working to. ​And of course, if you want, you can execute the git status command as well. ​And git status will say ​that working directory is clean ​and now ​that I have saved my unfinished work, I can switch back to the immediate task on hand. ​So I'll create a branch using git checkout ​B and name the branch as hot fix. Press enter. 
Play video starting at :4:58 and follow transcript
4:58
​And let's say the fix need to be done on the file humans ​dot ​TXT. ​So I'll do a simple fix over here. ​So let's assume that this is a fix. So I add my name over here ​and that's it. ​We'll save and quit and we'll do an express commit over here ​git ​commit ​M ​and the commit message is also a simple one. So fixed humans ​dot ​TXT ​will add just ​one index assuming this is our first fix for our humans ​TXT file press enter ​and the committee is done ​now that our fix is done. ​We'll switch back to master using git checkout master press enter ​and we have switched back to the master branch. 
Play video starting at :5:49 and follow transcript
5:49
​So let's clear the screen ​and I will not resume working on index dot ​html file ​on which I was working earlier. Instead, I'll start working on 404 dot HTML. ​So I'll make a simple edit. ​So let's assume that we're changing this line height ​and from 1.2 I'll change it to 1.3. ​So I'll quit and save. ​Now let's consider the scenario that I need to switch back ​to hot fix branch to work on another immediately pressing issue. ​So I need to save my unfinished work once again. 
Play video starting at :6:26 and follow transcript
6:26
​So in order to save my unfinished work this time too, ​I'll execute the git stash command. ​But this time I'll in addition, ​use the save subcommand with an message and this message will help us to identify ​our stash. So ​our ​message is modified ​line dimension ​and the file is 404 dot ​HTML. Right. Enter. ​Now let's check our stash list using ​git stash list press enter ​and here you can see another entry is in the stash list. ​So here it is much more easier to identify our stash because ​I have added this message modified line dimension 404 dot HTML. 
Play video starting at :7:18 and follow transcript
7:18
​Now, here is an important thing that you should notice ​is that the stash is listed in the reverse order. ​So the most current stash has an index zero ​and ​the earliest ​ST is ​index one. So basically there is a reverse order of display of stash. ​So now that we have saved our stash, ​I'll switch back to the hotfix branch using ​git checkout ​hot fix, press enter ​and again, I'll modify the humans ​dot ​TXT. ​So let's pretend this is another fix and I'll simply add the name here. ​So the name is wpe ​software team. ​So we're done with our fix and let's save and quit. 
Play video starting at :8:10 and follow transcript
8:10
​We'll do an express commit, retrieving an earlier commit message. ​So this is fix two. So we'll modify this commit message, press enter ​and we are done. So we'll switch back to master again using git checkout master. ​Let's clear the screen now. ​I'll not immediately start working on index dot STML and 404 dot HTML. ​Rather, I'll start working on another file. 
Play video starting at :8:38 and follow transcript
8:38
​So this time I'll start working on the file, browser ​config dot X ML press enter ​and I'll make a very simple change. So I'll modify the name of the file from tile dot ​PNG ​to tile ​one ​dot ​PNG. ​So this is our simple modification, we'll quit and save. ​And this time we'll also add our changes to the staging area. ​So get ​a ​browser ​conflict dot H tm L. So we have done some work on the file browser ​config dot X ML. ​And ​let's think of the scenario ​that we need to switch back to hot fix branch once again. 
Play video starting at :9:17 and follow transcript
9:17
​And in order to do that, we need to shave off our unfinished work. ​So we'll execute the git stash command once again, ​git stash. ​And this time too, ​we'll use a save subcommand and we'll have ​a stash message and our message is modified image ​one ​and ​the file was browser ​config dot X ML. So browser codes, close press enter and our stash is done ​and let's check our stash once again before we switch back to hotfix branch ​git stash list. And you can see our latest stash is on browser ​config dot X ML. ​Easily identified by the message that I added while creating the stash. ​So let's switch back to hotfix branch using git checkout hotfix press enter ​and we'll again have a fix on the humans ​dot ​TXT ​Wim ​humans ​dot ​TXT. 
Play video starting at :10:20 and follow transcript
10:20
​And this time ours ​fix is will add a role. ​So these are very small, small things ​just for the demonstration purpose. Let's assume these are very important fixes. ​So the role is software development ​and that's ​the fix will quit and save and we will do an express commit. ​We'll retrieve an earlier commit message ​and this is fix three press enter and the committee ​is done now that we have done our fix, ​we'll switch back to master branch using git checkout master ​press enter. ​Let's clear the screen. ​So we have created so far three STES ​and each of the STES ​corresponds to a single file. 
Play video starting at :11:9 and follow transcript
11:09
​Now, we can identify these STES ​related to browser ​config ​dot XML. ​This dash is related to 404 dot HTML. ​But we're not really sure that which file belongs to ​this stash. ​So there is a way out we can do ​git stash show ​and then you can copy this index stash at two ​and we'll just paste it here ​and press enter ​and here you go, you can easily identify ​that this dash belongs to index dot HTML. Now, the reason why we're not able ​to identify which file belongs to this stash is ​because of the fact that while creating the stash, ​we did not use the save subcommand with a stash message. ​Now, so far, we have been working with ​all the three files that were tracked once. Now, what about working with a ​on track file? 
Play video starting at :12:11 and follow transcript
12:11
​So let's create a file, ​new ​file ​dot ​txt press enter ​and we'll just add a very simple line. ​So this is a new file, press escape ​key and ​save and quit. ​Now, since this is a ontrack file, ​we are not able to see any change in the custom bash prompt as well. ​But if you do a ​git status, ​you can see ​git says that ​there is a ​ontrack file over here. Now, let's again, think of the scenario ​that we need to switch back to our hotfix branch once again. ​And in order to do that, we need to ​save our unfinished work on new ​file ​dot ​txt. So let's do that using git stash ​press enter ​and here you go. It says no local changes to save. 
Play video starting at :13:5 and follow transcript
13:05
​Now, the reason is if we execute the git stash command, ​it works by default on tract files. ​If you want to stash away a untracked file, ​then you need to execute the command git stash with the U option. ​So let's do that press enter ​and here you go. ​This time you can see ​that we could save our unfinished work on the new ​file dot ​TXT. ​Let's clear the screen ​and let's now do a ​git stash list once again, press enter ​and now we have four ST. ​Now this is our latest dash. ​And as you know, our ​git stash list will display stash ​in the River Sawer ​with the latest stash on the top. 
Play video starting at :13:52 and follow transcript
13:52
​Now we saved our unfinished work in order to do another fix in the hotfix branch. ​So let's do git check out hot fix, ​press enter this time to also we'll do a fix on the file humans. ​TXT ​press I ​to insert ​And this time, we'll add the Twitter handle. Let's assume that this is also a ​important fix we're doing to this file. ​So this time our fix is adding the Twitter handle to this file human dot ​txt. So the Twitter handle is white ​soft and we are done with our fix. We'll save and quit. 
Play video starting at :14:33 and follow transcript
14:33
​We will do an express commit by retrieving an earlier commit message. ​So this is our fourth fix ​and we will modify the earlier ​commit message appropriately. Let's press enter and we're done. ​So let's switch back to master that. We are done with our fix. Press enter. ​Let's clear the screen. So I'll stop this video here ​and I'll continue working on this example in the subsequent lecture.
