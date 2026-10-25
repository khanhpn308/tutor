# 🎥 Git Rebase Implementation (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/00c79c42-affb-4fd9-965f-02801f935a48_ff6b938bc0e24c068c7d21ee45bcec40_video19_4.mp4.mediaconvert/full/00c79c42-affb-4fd9-965f-02801f935a48_ff6b938bc0e24c068c7d21ee45bcec40_video19_4_WEBM_540.webm?Expires=1793059200&Signature=SO2L6-Z2Fcg0h-cThbCzviYovp1dqVxAs49CY3--No-PVJqgdCP7k07hYiieiRj4s~otuwaqa-e6J1WQ3WbplLx1RXdTI16KIzwZ9KZZKnyUWFeNpmtTDd6GMtPqBujT3bywyogGUYqI5~Y3ivfY2W3JiIH7ctkrZSX6O5LanrY_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So in our earlier lecture, we had set up the example for demonstrating how ​git ​rebase works. So in this lecture, we'll actually do the real work of ​implementing git ​rebase. ​So before we do that, let's check our commit history to see what's the situation ​press enter. ​And here you go. ​Now let's compare this commit history with a diagrammatic representation. ​So here is C zero, ​our first commit when you set up the repository and ​here is the second commit in the master branch. 
Play video starting at ::51 and follow transcript
0:51
​And here is the third commit, which is C two. ​After that, we created the branch, we did some work ​the top feature branch and this is the first commit in the top feature branch. ​And this is the ​second commit in the top feature branch. Lastly, we switched back to master ​and then we created two comets. ​So these are the two comets, which is one is C one. ​And lastly, we created the C four comets over here, ​which is ​now that we have identified the comets. ​Let's actually do the git rebase. Now, ​so before we do the git rebase, ​we need to switch back to the top feature branch ​so that we'll do using the git checkout command, ​top feature ​press enter ​and let's do the rebase. Now, ​git rebase ​master press enter ​and here you are. 
Play video starting at :1:49 and follow transcript
1:49
​So this is an interesting git response as you can see over here. ​So git rebase ​these two commits. Number one is this one ​and number two ​is this one. ​So now comes the interesting part. ​So I'll reexecute the git ​L command. ​So I retrieve an earlier command which I executed and here it is press enter. ​So this is the commit history ​before rebasing ​and this is the commit history after debasing. 
Play video starting at :2:21 and follow transcript
2:21
​So now let's do a comparison between the two. ​So these are the three commits, as you can see over here ​after ​a ​base which remains unchanged as you can see ​when you compare with these three comets. ​And these are the two comets over here in master as you can see prior to rebase, ​which remains unchanged as you can see after rebase over here. ​However, in the tough feature branch, we have two new commits after the rebase. ​And this is ​what we exactly explained in our git rebase introduction lecture. ​So you can see ​these were the two comets ​which were earlier in the top feature branch prior to rebasing. ​And after rebasing, ​we have completely two new comets over here ​and these two comets have been removed by ​git. 
Play video starting at :3:19 and follow transcript
3:19
​So now we'll do a diagrammatic comparison. ​So let's re execute the ​Glock command ​So after rebase, these are the five commits ​in the master branch ​that you can directly compare over here ​in sequence. ​And these are the two new comets that are generated after rebasing ​in the top feature branch. ​And the tough feature branch base initially was C ​which was this ​commit. ​And this switch from C two ​to C four, which is ​this ​commit. ​Now we're nearing the end of this lecture. ​So we'll see an entire replay of the action ​we went through in this lecture. So this is the master branch. 
Play video starting at :4:10 and follow transcript
4:10
​We started off with this commit. Then we made these ​two commits in our lecture. After that, we created this branch, ​we had these two comets in this branch ​and then the master diverged from the top feature branch ​and we had these two comets and let's see ​our rebase in action. ​So the top feature branch rewinds ​and there is a replay of the master branch ​rebasing creates two entirely new comets and the top feature branch head points to K ​to ​master branch head points C ​four. ​Now that the rebasing is done, ​we are ready for a fast forward merge so that ​we have a completely flat and linear commit history. ​So after the fast forward ​the master branch and the top feature branch ​will both point to K two. After that, we'll delete the top feature branch ​and only the master branch will remain. 
Play video starting at :5:13 and follow transcript
5:13
​So we'll get back to our terminal ​and we'll start working on the fast forward merge. So let's clear the screen. ​So let's switch back to master using git checkout command ​master ​press enter. And then we do a ​git merge top feature press enter ​and bingo, ​we're done with a fast forward merge. ​Let's do a git log ​by retrieving an earlier command press enter. ​And well, here you can see ​the head points to both master ​and the top feature branch. ​Let's clear the screen. 
Play video starting at :5:49 and follow transcript
5:49
​And now that we're done with the top feature branch, we no longer need it. ​And hence, we'll delete it using git branch ​D ​feature ​press enter ​and the branch is deleted. ​Let's re execute our ​git lock command. ​And here you can see ​that the top feature level has been deleted from here ​and we have only the master branch. ​So with this, we conclude this lecture.
