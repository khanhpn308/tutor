# 🎥 Resolving Git Rebase Conflict (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/2fc4e5e9-eff0-4fb9-b77a-e703be1ad08c_8ea51f96b5d64ef38837c7b8025f1b18_video19_5.mp4.mediaconvert/full/2fc4e5e9-eff0-4fb9-b77a-e703be1ad08c_8ea51f96b5d64ef38837c7b8025f1b18_video19_5_WEBM_540.webm?Expires=1793059200&Signature=aumg3yqfjrKGLi2ty4-RVS3wkc18aEG4dHOh2goD0z6OZ9JiwPjC9qrfP05X3XDB5Gyoy50UVOHD6GQGo1XfaLY-tf8e0IcWsfcg9ZFLr47mZ0tBQrY8PtOuEUmcbvzXyjwc1c1TYWAl6prY-xVXVPrPsHPyd4iKvSwadEaAAs8_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So, in this lecture, I'll show you how to tackle conflicting situation in a git ​rebase. So we are in the demo. Rebase repository. ​Let's check the contents of the directory ​and we have several files over here. ​So let's modify the file ​humans ​dot ​TXT ​press I ​to ​insert ​and here in this line, I'll just add my ​email ID. ​So ​bash at WICs ​soft.com press S ​KP colon ​WQ to query and save. 
Play video starting at ::44 and follow transcript
0:44
​So I'll do an express commit using git ​commit. ​Am since this is already a tract file ​and branch is master branch ​and our simple commit message is ​prior ​to ​rebase ​conflict ​code, close press enter and the commit is done. Now we'll create a branch ​using ​git checkout ​B. Now I'll name this branch as rebase Conflict. ​Since we'll actually create a situation ​that will give rise to a conflict ​while doing a rebase press enter. ​Now, I'll modify the file index dot HTML. Use the Wim editor ​press enter ​and we'll go down below ​and modify the title. So just add the word conflict. 
Play video starting at :1:38 and follow transcript
1:38
​So the title is rebase Conflict demo. ​And we'll come down here and we have a reference to the image file over here, Apple ​touch ​icon dot ​PNG. ​And we'll change this reference assuming that we have a image file, ​Apple touch ​icon two dot ​PNG. ​And our third change will be this javascript file reference. ​So we'll change this version of the file to 2.8 0.4. ​So those are the three changes that we need to do now that we're done. ​Let's press escape ​key colon ​WQ to query ​and save and we'll do an express commit. 
Play video starting at :2:15 and follow transcript
2:15
​So we will modify this commit message. So the branch is rebase conflict. ​Our action was three changes ​and the file is index ​dot ​HTML, ​press enter ​and we're done with the commit. So let's clear the screen ​and we'll switch back to the master branch using git checkout master press enter ​and here now we'll do the conflicting changes. ​And in order to ensure that we make conflicting changes, ​we need to modify the same part of the file index dot HTL ​that we did while we were in the rebase conflict branch. ​So Wim ​index dot H TM L. ​So modify this title to demonstration of ​rebase ​Conflict. And our second change which too will be a conflicting one. 
Play video starting at :3:7 and follow transcript
3:07
​So here we'll change the file name ​from Apple touch ​icon, ​PNG ​to Apple touch ​icon ​five dot ​PNG. ​And our third conflicting change ​will be here itself. ​So instead of 2.8 0.4 version of this file ​modernizer, 2.8 0.3 respond. ​1.4 0.2 main dot Js will just change it to 2.8 0.6. ​So we are done with all the three conflicting changes. Let's now quit and save, ​escape colon ​WQ to quit and save ​now do an express commit. ​So, appropriately modify this ​earlier commit message. 
Play video starting at :3:49 and follow transcript
3:49
​So the branch is master branch ​and ​we have three conflicting changes and the file remains say press enter ​and the commit is done. ​So let's clear the screen ​and we reexecute the ​Glock command ​press enter ​and here you can see the commit related to the rebase conflict branch ​and the commit related to the master branch. ​So let's clear the screen. ​So now it's time to do the rebase. So for that, we need to switch back to the ​base conflict branch ​and you have switched. ​So let's now execute the command. ​Git rebase ​master press enter. So as expected, Getit response with a merge conflict ​and git advises us to execute this command. 
Play video starting at :4:40 and follow transcript
4:40
​Git rebase continue ​once we have resolved the conflict ​or in case ​we decide to stop rebasing. ​Git advises us to execute ​git ​rebase abort command. Notably, ​the prompt has changed over here ​to rebase conflict, then pipe rebase. ​So let's assume that ​the situation seems complicated for us and we decide to stop rebasing. ​In such case we need to execute the command. ​Git rebase ​abort press enter ​and we return to the normal prompt, ​which means we're out of rebase. Let's clear the screen. 
Play video starting at :5:26 and follow transcript
5:26
​OK? ​So now that I have demonstrated you the command get rebase about, ​I will actually go ahead with ​the git rebase operation. So ​we execute the command git rebase master press enter. ​And now is the time to resolve the conflicts ​in the file ​index dot ​HTML. ​So we'll use a tool, git merge tool once again, ​which we earlier used while resolving, merge conflicts, press enter ​and here you go. ​So this represents the remote pen ​or ​the changes in the rebase conflict branch. ​This represents the original file and this pane represents ​the local ​or the master branch. 
Play video starting at :6:13 and follow transcript
6:13
​So now we'll go ahead and resolve the conflicts. ​So we decide to keep this change rebase demo ​that comes from the original file or the base. ​So you click button over here so that resolves the first conflict. ​So let's scroll down. ​Next. We decide that Apple touch ​icon two ​PNG is a right reference to the image file. ​So we decide to keep changes as can be seen here. 
Play video starting at :6:41 and follow transcript
6:41
​So we hit the blue button ​and we come to the last conflict ​wherein we decide ​that 2.8 0.6 is the right javascript file or Js file that we need. ​So we decide to keep changes that are ​in the master branch. ​Hence I click the green button ​so that completes the whole cycle ​and we have resolved three conflicts. ​Now at the top, we have the save button we'll click on it, ​save our changes and we exit from the tool while exit. ​Let's clear the screen ​and let's do a git status. ​So, git says that the rebase is in progress and the base is this particular commit ID. ​And it also says that odd conflict has been fixed and it advises ​us to execute the command git rebase continue and we have a modified ​status for the index dot html file. So let's execute the command ​git ​rebase ​continue press enter and the git response shows ​that we have successfully done our rebase. 
Play video starting at :7:55 and follow transcript
7:55
​So let's clear the screen and let's inspect our content, which is the file ​index dot HTML. And here you can see ​we have access ​this change ​while doing the resolution ​GRE ​demo. ​And our second resolution was accepting the change for Apple touch ​icon two ​PNG ​and the third resolution was accepting this version of this ​Js file. ​So this confirms that we have done a successful ​conflict resolution. ​So let's quit from the editor ​and now I'll execute the git log command. So I retrieve an earlier command. ​So the command continues into the next line. 
Play video starting at :8:38 and follow transcript
8:38
​So here is our first commit which was done prior to rebase conflict. ​And this was a commit related to the conflicting changes in ​the master branch we did in the index dot html file. ​And these were the conflicting changes related commit for ​rebase conflict branch, ​the head points to rebase conflict. ​And we have a pretty much flat commit history that you have done our rebase. ​And also you can see that rebase conflict branch is ahead of master by a single come. ​So let's clear the screen. ​So we'll switch back to master now using git checkout master press enter and ​now that we have resolved all conflicts and the rebasing process is done, ​we'll simply merge rebase conflict branch with the master branch. 
Play video starting at :9:27 and follow transcript
9:27
​So you'll execute the command. Get merge, rebase conflict press enter ​and we have successfully done a fast forward merge. Let's clear the screen ​and let's re execute the git log command. ​Both master ​and rebase conflict branches are at the same level ​and the head points to ​this ​commit ID. ​Now that we're done with the rebase Conflict branch, we can safely delete it using ​git branch, ​D. ​Rebase ​conflict ​press enter ​and the branch is deleted. ​Let's clear the screen ​and let's do a git log once again ​and you can see ​only the master branch remains over there. 
Play video starting at :10:13 and follow transcript
10:13
​And the reference or label to Rebase's conflict branch has been deleted by ​git. ​So with this, we conclude this lecture.
