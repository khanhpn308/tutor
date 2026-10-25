# 🎥 Amending Git Commits (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/f61ec245-77ac-4261-830c-9c9a406650de_244466bc80324eea9e1cd0120022affd_video19_1.mp4.mediaconvert/full/f61ec245-77ac-4261-830c-9c9a406650de_244466bc80324eea9e1cd0120022affd_video19_1_WEBM_540.webm?Expires=1793059200&Signature=H3qP5H5P~jcnjs5G2HriaQgKlD59JehlzG0OAdj31cGt~NYl3i7XhP-IIz2oh8MpfdfrwLaAo~kpAPy-7yztAelgJq~tkfQZFRPjTRljWBinP0WyKcAkT3WzSkiV5tC9lcmaKrg4PHEDPGZCoVJk0oPq2teMm4-YEi3Fu2S5FZ0_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hey there, ​welcome. So in this lecture, I will talk about how to amend or change commits. ​Git's main job is to make sure ​you never lose a committed change. ​But git is also designed to give you total control over your development workflow. ​This includes letting you define exactly ​what your project history looks like. ​Now, ​this also creates the potential to lose commits. ​Git provides its history writing commands ​under the disclaimer ​that using them may result in lost content. 
Play video starting at ::55 and follow transcript
0:55
​So let's see how to amend commits. So I'm in the repository demo, amend commit ​and I have created this repository for you. ​There are several files over here and we can check the log git ​log ​one line. ​So I have a single commit over here as you can see. ​So this commit basically was used to set ​up the repository by committing all the files. ​So let me clear the screen ​and let me modify the file ​index dot HTML. ​So I'm in the editor ​and I'll just change the title over here. 
Play video starting at :1:36 and follow transcript
1:36
​So let's add the title ​amended ​commit, ​demo. So demo is short form for demonstration press escape key colon ​WQ to quit and save ​and I'll do an express commit since this is already a track file. ​So I'm in the master branch ​and I have just ​modified the title ​in the file index ​dot html ​codes, close press ​and the commit is done. ​So let's do a git log ​by retrieving the earlier command. ​And you can see we have just these two commits over here. ​Now, let's consider a situation ​that I ​need to modify the file 404 dot HTML as well. ​But ​the intention is to change the 404 dot HTML file ​commit ​and ​the commit should be done in such a way ​so that we can club ​the commit of this particular file ​along with this commit ID ​or in other words, ​our commit should look so that we modify the file 4.4 HTML ​and index dot HTML ​together. 
Play video starting at :3:1 and follow transcript
3:01
​So let's modify the file 4 ​4h TM L ​press I ​to insert and we'll edit the title. ​We'll just make a simple modification, ​just write 404 error ​and the page not found ​that's it. Press ​SQQ ​colon ​WQ to clear ​and save. Now, I'll stage these changes. So we'll do get ​a ​404 dot HTML. Press enter ​and our changes have been staged. ​Now, ​we'll modify this commit so that this commit ​includes the changes of both 404 dot HTML ​and index dot HTML. 
Play video starting at :3:48 and follow transcript
3:48
​So for that, we'll issue the git commit command ​with the amend flag ​or you can say the amend option ​and we add an additional flag, ​which is the no edit. ​Now, what is this no edit flag? ​The no edit flag will allow you to make the ​amendment to your commit without changing its commit message. ​So let's see what happens. Press enter ​and the commit is done. So let's execute the glock command once again. ​So I retrieve the earlier command, press enter and here you go. 
Play video starting at :4:28 and follow transcript
4:28
​So here you can see that we had two commits earlier over here. ​And after the execution of git commit with amend option, ​we also have two commits. ​But the significant ​difference is that the commit ID has changed from this one ​to ​this one. ​Or in other words, we have this one as our brand new car. ​However, ​the commit message remains same over here as you can see by comparing with ​this one because of the fact that we use the no edit option. ​So let's clear the screen ​and let's just re execute the ​git log command once again, press enter. ​Now ​I want to ​modify the file ​browser ​config ​dot H ​internal. 
Play video starting at :5:23 and follow transcript
5:23
​But this time too, I decide ​that after the change of this file, ​the commit of this file should be clubbed again with this commit ID. ​But this time we want to modify ​the commit message as well. ​So that the commitment ​takes into consideration the change we made to browser ​config ​dot XML. So let's see how to do that. But before we do it, ​we'll just make the modification to browser ​config dot XML. ​Press enter, ​press I to insert ​and we have decided that we'll modify the name of the ​PNG ​file over here. So instead of tile dot ​PNG, ​I'll change the name of the file to simply tile two ​PNG. 
Play video starting at :6:14 and follow transcript
6:14
​So that's the simple change we want ​and we're done with it. Press ​SQ colon ​WQ to quit and save. ​And we'll simply ​add this change to the staging area. ​Get a ​browser ​conflict dot X ML. ​And ​the plus symbol ​indicates that we have done the staging successfully. ​Now we'll amend ​this particular commit ID. ​The simple trick is that this time we will not use a no edit option. 
Play video starting at :6:47 and follow transcript
6:47
​So git commit ​amend ​and that's it. Press enter ​and this simply opens our default editor which ​is sublime text and here is a commit message ​and we'll just modify it to reflect the change that we're making. ​So this time we'll make this simple change, modify the title in ​index dot ​HTML and 44 dot HTML. ​So that was the previous ​we made. ​But at the time, we did not ​edit the commit message. ​And also we ​simply add this change, ​modified ​browser ​config ​dot ​XML. ​So this is our entire commit message. 
Play video starting at :7:34 and follow transcript
7:34
​Now you save, changes, clicking file, ​save and will quit from the editor file exit ​and our commit is done. ​Now let's check our git log So I'll retrieve the earlier command, we executed, ​press enter ​and here you go. ​So this time, we have been able to change our commit message to reflect ​the change that we made. ​And not only that ​the commit ID over here has appropriately change ​to this one, ​which means we have again, another brand new comet ​replacing the earlier one. ​So let's summarize ​the git comet with amend flag ​is a convenient way to fix up the most recent comet. ​It lets you combine staged changes ​with the previous commit. ​Instead of committing it as an entirely new snapshot, it combines the stage changes ​with the previous commit ​and replace the previous commit with the resulting snapshot. 
Play video starting at :8:42 and follow transcript
8:42
​But amending doesn't just alter the most recent commit. ​It replaces it entirely ​to get, it will look like a brand new commit, ​premature commits happen all the time in the course of your everyday development. ​It's easy to forget to stage a file ​or to format your commit message the wrong way. ​The A ​flag ​is a convenient way to fix this little mistakes. ​Now, ​there is one caveat or warning ​never amend commits ​that have been pushed to a public repository. If you amend a commit ​that other developers have based their work upon, ​it will look like the basis of their work vanished from the project history. ​Now, this is a confusing situation for developers to be in ​and it's complicated ​to recover from. 
Play video starting at :9:43 and follow transcript
9:43
​So with this, we conclude this lecture.
