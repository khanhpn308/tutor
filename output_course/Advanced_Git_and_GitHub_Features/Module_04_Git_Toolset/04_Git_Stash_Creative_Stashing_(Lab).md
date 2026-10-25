# 🎥 Git Stash: Creative Stashing (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/ee489284-dbd8-4a97-a2eb-1bc748f3e490_f795aaaaa79d4713adb84e856e5edcc4_video22_4.mp4.mediaconvert/full/ee489284-dbd8-4a97-a2eb-1bc748f3e490_f795aaaaa79d4713adb84e856e5edcc4_video22_4_WEBM_540.webm?Expires=1793059200&Signature=LL-tnDs~rOVh66yLfXr4XpeYNCqkbGRhvRxW0eoqyamHC74QMQt29DYzEYrBdtnSdInbHODVKTtvvgEV7hB6Cc02S9gOeuDPGHoGIYyrjcmEYHyPA0twzLKftAsNBP5DbQ2ZDUyBD0eHjf4UUvRXllOoMp1vVuFqssWEm8jAD2I_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So we'll continue to work with concepts related to stash. ​I'm still in the demo stas ​repository with which we worked earlier in this section. ​So this time I'll show you how to work with stash ​and the index or the staging area. ​So let's check whether we have anything in our list of stash. ​So stash is empty. Let's modify the file ​index dot HTML. So this time ​we'll modify the title ​and we'll name it ​stash ​with index ​demo. So demo is short for demonstration. So we'll quit and save. 
Play video starting at ::52 and follow transcript
0:52
​Let's modify the file 44 dot HTML as well. ​And this time we'll modify the attribute width ​below as you can see. So from 100% will modify it to 50%. ​So that's a simple change, colon ​WQ to cred ​and save. And after changing 404 dot H tm L, we'll add it as well to the staging area. ​So get add 404 dot H TM L. ​So our custom bash prompt changes from ​star ​to star plus ​indicating we have changes both in working directory as well as staging area. 
Play video starting at :1:34 and follow transcript
1:34
​If you wish though. There is no need. You can still execute the git status ​or git status with dash ​option ​and it will show you the status of your working directory. ​Now, let's save our unfinished changes into a stash. So git stash ​with subcommand save. And we have a simple message for saving the stash. ​Let's name it in short index and 404 ​press enter ​and the stash have been saved and we have a clean working directory as you can see ​in the custom bash prompt. Now let's clear the screen and let's apply our stash ​it dash, ​apply press enter ​and here you go. Now, notice a very important thing that ​happened over here. Let's scroll up. And if you remember that 44 ​HTML file was added to the staging area and index dot ​html was modified but not added to the staging area. 
Play video starting at :2:38 and follow transcript
2:38
​So our custom batch prompt both has a start as well as plus. ​However, after we created the stash ​and then applied the stash using git stash, ​apply command, both our files are in modified ​stage. ​So the changes for 44 ​STL that were added to the staging area is simply gone. ​So this is not really a desired effect. If you want exact restoration of your stash, ​then you need to apply your stash ​with ​index option. ​OK. ​So in order to show you that I'll just undo the changes we can see. 
Play video starting at :3:20 and follow transcript
3:20
​So using git checkout dash ​44 dot HTML. So that undoes the change in that file. ​We'll also undo the changes in index dot HTML ​and you can see the working directory is clean now ​and we have undone all the changes in our working directory. ​So let's clear the screen and we'll just walk through ​the earlier steps that we did. So we'll modify the file index dot HTML. ​Press enter, we'll modify the title ​stash ​width index ​demo. ​Let's save and quit And we modify the file 4 ​4h TM L as well. 
Play video starting at :4:1 and follow transcript
4:01
​And this time also, we will modify the width attribute from 100% to 50%. ​Let's save and quit. We'll add the changes for 400 4h ML to the staging area. ​And now our ​BPT changes to signify ​two kinds of modifications. ​And let's check the stash ​using git stash list. ​So we still have our stash lying over there which we created earlier. ​So let it be there. 
Play video starting at :4:30 and follow transcript
4:30
​We'll save our current changes or rather the ​unfinished changes to another stash on the Stack. ​So let's save it a simple message. Our simple message is second change set for ​index 404 codes. Close press enter. ​So let's check our ​list using ​git stash list. And over here you can see ​that our ​second stash is over there at the top of the stash. ​And if you remember the goal was to restore our working ​directory to its exact state before we created the stash. 
Play video starting at :5:14 and follow transcript
5:14
​So in order to do that, we need to execute the command git stash, apply dash dash ​index. ​So ​will do the magic press enter. ​And here you go. ​We have an exact restoration of our working directory status. ​404 dot HTML returns to modified state and the modification is in staging area. ​And index dot H TM L also returns to its own modified state. ​And of course, this file was not added to the staging area. ​So you have an exact restoration ​with the dash dash ​index option. 
Play video starting at :5:52 and follow transcript
5:52
​So let's clear the screen ​and let's execute the git status once again. ​And we want to undo all the changes now that I have demonstrated you the utility of the ​index option. ​So in order to return back to our earlier state, ​we need to execute the command git checkout dash dash ​index dot HL. So it will undo ​this particular change, ​press enter and you can see our custom batch prompt ​changes to indicate that this particular change has been undone. ​And in order to undo the changes in the 404 dot HTML, ​you need to just execute the command, get reset head and then the 404 dot HTML ​press enter. ​Now the changes have been unstaged and you need to execute ​the command git checkout 404 dot HTML press enter and well, ​we have returned to our exact state when he started working in the example. ​Now I'll show you another ​important option which ​keep ​index. 
Play video starting at :7:6 and follow transcript
7:06
​So in order to demonstrate the utility of the keep index option, ​we have to go through another setup changes in our files. ​So let's modify the ​file ​index dot H TM L press I ​to insert. So this time I'll modify ​the name of the image ​Apple ​touch ​icon dot ​PNG ​to Apple touch ​icon, ​two dot ​PNG press escape key to save and quit and let's modify the file 404 dot HTML as well. ​And the simple change is we'll change the text align attribute from center to left. ​Let's save and quit. ​And we'll add our changes to 404 dot HTML to the staging area. ​So you have both kinds of changes, as you can see ​in the custom brash prompt. 
Play video starting at :7:54 and follow transcript
7:54
​If you wish, you can execute the git status option as well or git status with ​option. ​Now, so far in our earlier examples in this lecture, we have modified both ​index dot HTML and 44 dot H tm L. And when it created ST ​we added both the changes to the stash. ​This time, we'll do something different. ​We'll add our changes to index dot HTL to the ​stash, but we'll retain our staged changes to 4 ​4h tm L ​and we do not want to ​are changes in 404 dot HTML. Now changes in 404 dot HTML is ​in the staging area. ​So we need to keep our index ​or keep all changes in the index or staging area. 
Play video starting at :8:47 and follow transcript
8:47
​So the way to do it is using the ​git stash, ​then keep index option, press, enter ​and here ​the working directory status changes from star plus to start, ​which means we have been able to reserve our changes in ​the staging area and not move it to the stash. ​You can execute the git status or git status with ​task option ​and you can see ​that ​our changes in the staging area have been retained.
