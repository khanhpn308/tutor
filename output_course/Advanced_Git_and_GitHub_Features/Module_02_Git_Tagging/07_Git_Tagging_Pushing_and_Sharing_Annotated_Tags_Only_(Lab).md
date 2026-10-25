# 🎥 Git Tagging: Pushing and Sharing Annotated Tags Only (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/ab242fef-0272-4933-9ca8-eb42589fc4de_01cb6e121bd74e05b1ec184f7bf29305_video20_7.mp4.mediaconvert/full/ab242fef-0272-4933-9ca8-eb42589fc4de_01cb6e121bd74e05b1ec184f7bf29305_video20_7_WEBM_540.webm?Expires=1793059200&Signature=VMFHgL2CdI6unfY1sadpjkdXfIyHPONUwx0DO6BVlY5ZE0Ynx-wE7lJdHOYrYyvNPhl~bCLwO80jyCZDGiEwygLJo5qL5mD0xxnVUomh2XARa1XzE~84a0Xf-vtbTyaj2qApW4bw7fw47D~UCJd6e8OPPaQbuIMFjvw~fENh3WM_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So now I'll discuss about how to push and share annotated tags on a remote server. ​Now, the git push ​command doesn't transfer tags to remote servers such as github by default, ​one has to explicitly push tags to a shared ​server once tags are created in the local repository. ​So now there are two ways in which you can push tag, so you can push ​only annotated tags or ​you can push all tags, ​which includes both annotated tags as well as lightweight tags. ​Now, the command for pushing only annotated tags looks ​like this. Get push origin ​and then the option ​dash ​dash ​follow T. ​And if you want to push both annotated tags as well as lightweight tags, then you need ​this option only ​tags. So I'll show you examples for both of these commands. 
Play video starting at :1:19 and follow transcript
1:19
​So before I show you the execution of the command to push annotated tags, ​I'll simply create a comment. ​So let me modify the ​file ​humans ​dot ​txt ​and I'll simply add my name over here ​in the thanks section. ​So I add my name and I save and quit. So I'll do an express commit, using ​git ​commit. ​Ahum ​dot ​TXT ​is ​a ​tract file. So simple, committed message is committed. ​Humans ​codes close ​and the commit is done. So let me clear the screen and let's execute the git ​log command. 
Play video starting at :2:4 and follow transcript
2:04
​So I retrieve an earlier command ​and here we go. ​So you can see our latest committee over here ​and this was our commit message. ​So let's now execute the command to push ​annotated tags ​in the github repository. ​So before I execute the command ​to push ​annotated tag to the github repository, ​it's important that I show you the state of our repository right now. ​So let me get back to the browser. So here is our demo ​tag remote repository. ​And here are all the artifacts that I pushed earlier ​to set up the remote repository for the demonstration. 
Play video starting at :2:45 and follow transcript
2:45
​Now let's go to this release ​section. So I'll click on the link releases over here ​and let's click on the tags section over here. ​And the message github shows to us is that there aren't any releases here since ​we have not pushed any tags from our local repository to our remote repository. ​So let's get back to our terminal. Now, I'll execute the command git push ​origin where origin is a remote reference. ​And then our option followed tags to push all annotated tags on a local repository. ​So press enter subit prompts for the username and password. 
Play video starting at :3:31 and follow transcript
3:31
​So I enter my username and I enter the password too. ​And here you go. ​The message is very clear. Git pushes six annotated tags. ​So with our earlier knowledge, ​we can check any of our annotated tag using the command git cat ​file ​T and we copy this tag over here ​and paste and press enter. ​So git provides us the response tag which means this is a annotated tag. ​And likewise, if you want, you can examine all the tags over here ​and these are all annotated tags. 
Play video starting at :4:12 and follow transcript
4:12
​So let's get back to github. ​Now let me refresh the browser over here and here you go, you can see ​that ​all the six tags over here are being pushed to github ​with the help of the ​follow tags option. Now, if I get back to the terminal ​and execute the git log command, you can notice ​that there are some tags such as this one ​has not been pushed to the remote repository. ​And the reason is this tag is a ​lightweight tag and you can confirm this using the command git cat ​file ​and then just copy this tag over here and paste it, press enter ​and here you can see the response is commit, ​which means this tag is a lightweight tag. ​So let me scroll upwards and I can see ​our latest commit was this one and the commit message was committed ​humans ​dot ​TXT. So let me get back to the browser and I'll show you another important thing. ​So I'm in the github repository now. 
Play video starting at :5:19 and follow transcript
5:19
​And if I click on the commits section over here. Well, I can see ​the commit message committed ​humans ​dot ​TXT. And if I go to the release section, ​I can see that all the six ​annotated tags have been pushed. ​So this effectively means that the command git push origin follow tags, ​not only pushes annotated tags, but also ​the commits as well. Now, another point to be noted is that ideally ​you should only push annotated tags to the ​remote server such as github and keep the lightweight ​tags for local development to avoid tag clashes. ​However, ​having said that you still can push light tags ​to the remote server such as github as well. ​And this is what I'll show you shortly. So with this, ​I conclude this lecture.
