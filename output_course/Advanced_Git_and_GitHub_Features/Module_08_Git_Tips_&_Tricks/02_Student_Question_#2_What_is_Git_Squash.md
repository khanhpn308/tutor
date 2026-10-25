# 🎥 Student Question #2: What is Git Squash?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/203a87c9-7ad9-4205-a650-5e1be8c35cd9_be34d09e1f5343a1bfd15ca41c1b2f8c_video26_2.mp4.mediaconvert/full/203a87c9-7ad9-4205-a650-5e1be8c35cd9_be34d09e1f5343a1bfd15ca41c1b2f8c_video26_2_WEBM_540.webm?Expires=1793059200&Signature=Vnr~~z-TsMJukTjaRxGfyo6aExEW8ylk5vEudr3xKsEIObPh~NSoSov0QtF7CZBbv9o0vnve9VlrYAfLi-zjAl6BolV9wHIb5bWLp10wbECVt0RTVxesrE5xqgQ~zHecKUiV0m~wgtOf74~Q16wvct-y9H0Ly7kOlNXtW~Qepa4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hey, welcome to the lecture. ​So in this lecture, I'll address a student question, what is Get squash? ​So let's start explaining Getit squash ​before we actually run the commands. ​Squash is one of the several tools ​available under Gits interactive rebasing system. ​Now note that there is no command as such called git squash, ​but actually git squash functionality is ​dependent ​on ​git interactive rebasing system. ​Next ​squashing allows us to combine comets together. ​Now, why is it useful? 
Play video starting at ::53 and follow transcript
0:53
​This is useful for repackaging comets that are related to each other. ​In other words, ​squashing allows us to rewrite commit history by combining comets together. ​The dictionary meaning of squash is crush or squeeze something with force ​so that it becomes flat and soft. ​Now, when to squash comments, ​squashing might be required ​when we try to clean up commit history before we do a merge or rebase and then push ​up to an upstream repository. ​So here we'll be actually doing the gate squash ​and then ​we will not be going ahead with rebasing or merging. ​So this is what you can do. ​Now, next question is why squash commits. 
Play video starting at :1:46 and follow transcript
1:46
​So ​let's say ​you made a typo somewhere and had to create other comet to fix the spelling error. ​And there might be many such simple ​or silly comets ​or ​you might have a bunch of local comets related to a bug fix. ​In such cases. ​It's usually a good idea to squash or compress ​or combine such related comments into a single. ​Now, the concept out of the way having been explained, ​let's start running the commands. ​So we are in the demo ​gate squash repository ​and we have a bugfix branch ​that I'll show you shortly ​and it has three ​CTS. ​So let's run the first command which is git ​log ​oneline. 
Play video starting at :2:39 and follow transcript
2:39
​And you can see over here in the master branch, ​you can see only the initial commit where I committed all the artifacts of ​the repository. ​Now I'll switch to the bulk fix branch ​or you can just see what are the branches over here. ​Git branch. And you can see bulk fix and master are the two branches. ​The default mainline branch is master, of course. ​So let's check out to the bulk fix branch, ​bug fix ​and let's enter. ​And here we are in the bug fix. Let's run the git log ​oneline ​command once again. 
Play video starting at :3:19 and follow transcript
3:19
​And here we go. ​So you can see these are the three commits or ​rather four commits that are in the bugfix branch. ​So I'll just clear the screen to remove the ​clutter so that you can distinguish the comets. ​Well, ​so here you can see ​this is an initial comet ​related to the master branch. ​And these are the bug fix branch. ​Obviously, the head is at bugfix branch since we have checked out bugfix branch. ​And we have the ​four comets over here, these three ​and this three. 
Play video starting at :3:57 and follow transcript
3:57
​So basically, we'll try to do is ​we'll collapse ​all these three comets ​into a single comet. And that single comet will be ​this ​particular commit message integration test and the comet ​hash ​is ​one double 587. ​Now we'll pick this comment basically and not this commit or this commit ​for a certain reason, ​which will be evident or clear to you as we progress further in the lecture. ​So basically, we are trying to compress or combine or squash these three comets ​which are the three most recent comets ​and or you can say three comets back from head, right? ​OK. Let's go ahead to the next step. ​And here we'll be actually running the git rebase command ​to squash. Remember, there is no command as such called git squash. 
Play video starting at :4:59 and follow transcript
4:59
​Rather squash is a part of git interactive rebasing system. ​OK? So let's run the command git ​rebase. ​And then ​I I stands for interactive ​and then head tilde ​three. ​So let me explain you. ​I, as I already told, this is for the git interactive rebasing system ​and head, of course, you're very aware is the top ​most commit. ​And tiller three means the three most recent ​commits are three commits back from head. 
Play video starting at :5:35 and follow transcript
5:35
​So let's run and see ​where you go. ​So basically here, ​sublime text is my default text editor. ​So when I ran the git rebase command ​automatically, the sublime text editor opened up. ​So here, let's see what are the things over here. ​So you can see the three comets ​over here. ​These are the three comets we're trying to collapse or combine or squash, right? So ​one thing that you can notice is that git ​interactive rebase presence ​commit in the reverse order of what you are used to when you see ​the command git log being run. 
Play video starting at :6:17 and follow transcript
6:17
​So here you can see ​this was the most recent commit ​and these were the two older commits. ​If you want to confirm, let's switch back to the ​bash ​terminal. So just remember this, this is three BC five double four A. ​So let's switch back to the bash terminal. ​And here is the best terminal and you can see three BC five double for ​the most recent commit. And these three commits, as you can see in ​glog are being displayed in reverse order in the sublime text editor. ​So let's switch back to the ​editor once again. 
Play video starting at :6:54 and follow transcript
6:54
​And here we are. So it is saying that we are trying to rebase ​this ​three commits, right? ​So this is a commit id or commit hash for the ​second commit ​from the bottommost portion. ​So let's see once again and switch back to the bash terminal. So it is ​AA ​E 75, right? ​And here you can see this is a commit ID. ​So you're trying to collapse all these three commits into a single commit, right? 
Play video starting at :7:29 and follow transcript
7:29
​From this particular commits. ​Let's switch back. ​And here we are. ​So you can see there are several commands ​which are related to get interactive rebasing system ​such as pick ​reward, edit, squash, and so on. We'll be basically using only ​the two keywords which is squash ​and pick up and the rest of the ​keywords are not a matter of focus in this particular lecture, right? ​So ​when you scroll down further, you can see ​in line number 23 it says these lines can be ​reordered and they are executed from top to bottom. ​This is very important to remember. 
Play video starting at :8:16 and follow transcript
8:16
​And second, you can see in line 25 it says if you remove ​a ​line here, that commit will be lost. This is very important. You must note this. ​And finally in line 27 you can see, ​however, if you remove everything, the replace will be aborted. ​Well, now I'll not just attempt to ​show you what will happen if we remove everything, but you can test it for yourself ​that scroll upward. ​And here ​we'll try to actually collapse the comments, ​but here we'll do our things a bit differently. ​So what you should do is when squashing commits, ​you should squash recent commits to old ones and not vice versa. 
Play video starting at :9:2 and follow transcript
9:02
​This is very, ​very important So what I'm trying to say is that this is the most recent commit. ​This is a bit less recent and this is far ​less recent, right? ​So ​what we'll try to do is actually to get things right. ​We should collapse these two commits or squash these two commits ​onto this commit. ​But if you do in the diverse order, ​whereby you try to squash this commit into the most recent commit, ​you will get an error. ​So we'll try out this one by actually ​what we're not supposed to do, ​right? So I'll copy the squash keyword ​and we'll try to squash ​this. First two comets over here are seen in the editor and we'll pick this come ​when you say pick, ​basically you're picking this comet three BC five double four A to squash ​into a larger commit, right? So we need to save an exit and return back to the bash ​terminal, let's say file, save and then file exit ​and here we are. 
Play video starting at :10:16 and follow transcript
10:16
​So here you can see it says ​error, ​right? Cannot squash without a previous commit. ​You can fix this with git ​rebase ​edit Todo and then run git ​rebase ​continue ​or ​you can abort the rebase with ​git ​rebase, abort. So we will not be actually attempting to see the result ​of doing a ​git ​rebase edit ​Todo rather we simply do a ​git rebase abort, right? ​So that we are focused in what we are trying to achieve in this particular video. ​So copy this one ​and paste it right? ​And here we go, we have aborted ​the ​git rebase. You can see ​the prompt only shows bug fix and not the rebase. 
Play video starting at :11:7 and follow transcript
11:07
​That means we have aborted rebase successfully. ​Now, we need to do things right. So we'll be running the git ​rebase. ​I head till the three command once again. So let's retrieve the earlier command ​and here we are, ​we'll run the command once again to get things right? Or to do things right. ​Let's enter ​and here we are back again. 
Play video starting at :11:33 and follow transcript
11:33
​Now, ​I explained what are all the things written over ​in this editor so that you don't get confused. ​Now, we'll do things in the right way. We'll copy the command gate, squash again ​and we'll pick this commit. Hence, it means we'll squash ​this commit. ​Now, just notice one thing here, if you ​simply type out manually, the word splash ​and you do a typo ​git will ​warn you. ​So let's say we do a Typo by appending an extra S and you can see the red box over here. ​So it tells ​that this is a typo and you have not type the right keyword. 
Play video starting at :12:14 and follow transcript
12:14
​OK? ​So ​I do. ​And here we are back again in the right state of the file. ​So we have picked this ​git ​and this means we'll be squashing these two commits ​into this commit, which is one double five A ​seven. So that we get a single larger combined come, ​right? ​So let's save an exit, file, save ​and then file exit ​and here we are back ​now. You might be confused. What is this now? 
Play video starting at :12:48 and follow transcript
12:48
​It should have been completed by now. No, it's not. ​So just the reason is we need to really decide upon our combined commit message, ​right? ​We have not done it so far. ​So it automatically does it for us by opening the default text editor, ​which is sublime text edit ​for me. So here you can see what it says. So now you can see all these things. 
Play video starting at :13:12 and follow transcript
13:12
​This is basically generated by gate it. This is a combination of three commits. ​This is the first commit message. ​This is the second commit message and this is the third commit message. ​And these are the three commit messages ​that were associated with the three commits that we are trying to squash, right? ​And even you can see the timestamp over here. ​So now we'll be choosing the commit message that you want. 
Play video starting at :13:36 and follow transcript
13:36
​So if you commit out the commit message that you want, naturally, ​those things will not appear in the final commit message ​right ​now, ​simply saving this file without making any changes, right? ​Let's say we click save and exit. What will happen? ​What will happen is this that it will result in a single commit ​with a commit message. That is a concatenation of all these three commit message. ​So when I say three commit message, I mean all these three commit message, ​but we don't want that right. ​We want a proper commit message to appear. 
Play video starting at :14:11 and follow transcript
14:11
​So we can either write it afresh with a new commit message or you can ​simply decide to choose one of the commit message depending on what suits you. ​So ​let's say we'll decide that feature bug ​fix. Integration test is the commit message that you want to go for. ​So it simply comment out ​the commit messages that we don't want. ​So here I go and I'm committing them out, ​right? ​So now we're all done to actually squash all ​the three commits into a single large commits. ​So let's say we save and ​then ​we exit ​and here we go bingo. 
Play video starting at :14:57 and follow transcript
14:57
​So it says three files chains, three insertions, ​three relations successfully replaced and updated reps heads, but ​fix. ​So we are done. ​And are we really done? We need to verify, right. ​So we'll verify like this, we'll simply run or git ​log ​one line command once again. ​And you can see ​you can see ​that we had previously five comments right over here, right? ​Just go upward and you can see these are the five comets. 
Play video starting at :15:31 and follow transcript
15:31
​Now, this was the initial commit that was in the master, this was the commit, ​that was in the bug fix branch. ​And then there were three additional comets. ​And you can see that now there is a single large ​comet and the commit message is feature bulk fix integration test. ​That we decide ​not to commit out in our ​git editor. And naturally this has been chosen as a commit message. ​Another interesting point to note that ​the commit ID has changed, which means a fresh commit ID ​or commit hash has been introduced by git. ​And this doesn't match with any of these three commits over here. 
Play video starting at :16:13 and follow transcript
16:13
​So that's it. ​So I hope you enjoyed this lecture. And you got what? Git square she ​how to squash multiple comets into a single large comet. ​And actually when we should actually do a gate squash and why ​actually we should do a gate squash if you have any confusion, ​just go to the initial part of the lecture where I have explained what gate squash is ​why we should do get squash and when we should get squash, ​hope you enjoyed this lecture. ​See you in the next video.
