# 🎥 Git Tagging: Checking out Tags (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/7a183001-fbbb-42d2-87b5-004d404cfd58_cde63bf518754d0c93587603954faf69_video20_9.mp4.mediaconvert/full/7a183001-fbbb-42d2-87b5-004d404cfd58_cde63bf518754d0c93587603954faf69_video20_9_WEBM_540.webm?Expires=1793059200&Signature=PlWh-9PCbmvBZAHfXLLzjWDYn0az7zdrkrkyPGt0~EQ0V~nqKf0FvBVrtdmdOTieR1w4Cao2~Pf2e0tJ9bulAMYNMWDYXLI6ShCSEzs0S59t7QMGvFMGbZqzOlbQ9Xv6GZxw9kp83sZqeqqJyL0nepCyCt4cnW0Eoei-Sz~SDi8_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. So in this lecture, I'll talk about the topic, checking out tags. ​Now, at the very outset, I want to say that you can't really check out a tag in git. ​However, you can create a new branch at a specific tag. ​So let's start off with a working example. ​As you can see here, ​we're continuing with the demo tag repository with which ​we have been working in this section so far. ​So let's execute our git log ​command, I'll retrieve an earlier command and press enter. 
Play video starting at ::47 and follow transcript
0:47
​So you can see there are several tags over here. ​Now, ​let's try to check out a tag and let's see ​what's the outcome we'll choose this tag for our purpose. ​So this tag is V ​18 ​RC one. ​So let's try to check out the particular tag ​which I showed you right now. Get checkout ​V ​1.8 ​RC one press enter and here you go. ​As you can see here, checking out on a particular tag puts you ​in a detached head state ​and this is what git says us explicitly. So this is what we do not want. 
Play video starting at :1:32 and follow transcript
1:32
​So I'll quit from here using git checkout master press enter and we're back to our map ​branch. Let me clear the screen. ​So even though explicitly checking out a tag doesn't really work out in our favor. ​As I said, we can always create a branch and then check out at that tag. ​So let me show you how to do that. So you do get checkout ​B and since we want to create the branch at ​this particular tag, let's name our branch ​as branch ​B ​1.8. And then we provide the name of the tag. So let me copy the name of the tag ​and paste it over here, press enter and here you are. So I have created a branch ​and checked out this branch ​at the tag ​V ​18 ​RC one. 
Play video starting at :2:32 and follow transcript
2:32
​So let's do a side by side comparison using two ​git bash ​consoles. ​So I have opened another console for the same repository ​and I will execute the git log command once again, press enter and here we are. ​So here is our comparison. So I have opened two console. ​So this is console one and this is console two. ​So console one presents us the git ​log information over here prior to creation of the branch ​V ​18 ​at ​this ​tag and console two presents us the gate log information over here after creation ​of the branch at ​this tag, ​now you can directly compare between the two consoles. ​So the comparison between the two consoles shows us ​that the head now points to branch B dash ​18 ​at this particular commit id ​instead of this commit ​ID. 
Play video starting at :3:39 and follow transcript
3:39
​OK? So now the comparison is done, let me clear the screen ​and let me make a modification to the file ​index dot HTML. ​So we'll simply modify the title over here and the title will be tag checkout demo. ​Let's save and quit. And let's do an express commit using git ​commit ​a ​aim. ​And our commit message is ​18. ​We modified the title ​and the file involved is index dot HTML codes close and the committee is done. 
Play video starting at :4:18 and follow transcript
4:18
​Let's clear the screen ​and let's switch back to master branch press enter ​and let's re execute the git ​command. So I retrieve an earlier command press enter and here you are. ​Now, let's do a comparison once again. ​So console one represents the glog information after we ​did our commit for the file index dot HTML. ​And console two ​represents our ​git ​log information prior to the commit. ​So you can clearly see now the head points to this commit ID when we're at the branch V ​18 and ​the master ​and the branch V ​18 both have diverged. So let me clear the screen. 
Play video starting at :5:10 and follow transcript
5:10
​And now that our comment is done, we can switch back to master branch press enter ​and we'll simply merge the branch ​V ​18. So get merge branch ​V ​18 press enter. ​So you have a conflict here. We simply ​run our merge tool. So click, merge tool, press, enter. ​And as you can see here, we have a single conflict. ​And for us, the tag checkout demo is a good option for the title. So we'll accept that. 
Play video starting at :5:45 and follow transcript
5:45
​And hence, we'll click the blue button over here and the conflict is resolved. ​Let's click the save button over here and we'll quit. So file exit. ​So let's execute a ​git status command now that we have resolved our conflicts. ​So you have the modified index dot HTML. ​We'll simply commit away this particular change using ​git ​commit ​AM and simple ​commit message is committed ​index dot ​H TML. ​After ​conflict resolution, press enter and here you go, our conflict has been resolved. 
Play video starting at :6:25 and follow transcript
6:25
​So now that we are done with our merging, we simply delete our branch ​git branch ​D ​and then the branch is branch ​V ​18 ​enter ​and let's re execute our git ​command once again. ​And here you can see our ​git log displaying our commit history. So with this, we conclude this lecture.
