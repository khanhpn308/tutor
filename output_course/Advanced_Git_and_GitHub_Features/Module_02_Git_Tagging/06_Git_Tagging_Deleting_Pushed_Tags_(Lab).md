# 🎥 Git Tagging: Deleting Pushed Tags (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/e9e47545-eccf-493f-b0fc-d5d1d5e22b58_1edeea8ecf154c5d83fc7f46a95e5fb5_video20_6.mp4.mediaconvert/full/e9e47545-eccf-493f-b0fc-d5d1d5e22b58_1edeea8ecf154c5d83fc7f46a95e5fb5_video20_6_WEBM_540.webm?Expires=1793059200&Signature=XBjCgTqkrRNkdb3N1Eqg6TAJc2w7g4Q~WpIiwHpjAIIzhF2TriYX37dsxCvRY6FVIeo93N5BXBglwI8o73ENntdIj6~5vfoK6c1pwPUZEQFZ8qIyZnp0ckP6s6jMi48lstpMj81N9o-ts3QtnpTTcauq2pvvK~NPnLizJI~zXbE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So, in this lecture, ​I'll show you how to delete the tags that ​you've pushed through remote server such as github. ​So let's get back to our remote repository demo tag on github. ​And you can see there are several tags over ​here that we pushed in our earlier lecture. ​And let's say we want to delete this particular tag, which is V ​19 ​RC two. So we have to do this from our terminal. So let's get back to our terminal. 
Play video starting at ::43 and follow transcript
0:43
​So the command for deleting a tag that has been already pushed to a remote ​server is get push and then the remote reference which is origin in our case. ​And then you need to provide the name of the tag. ​But prior to providing the tag name, you need to precede it ​or prepend it with a colon. ​And let me copy the tag name from ​github. ​So the tag name is V ​19 ​dot ​R ​two. ​So let's copy it and get back to our terminal and paste it over here. ​Press enter and I need to put my username ​and password and here is the password and well, ​git comes up with a response that it deleted the tag V ​19 ​RC ​two. 
Play video starting at :1:30 and follow transcript
1:30
​Let's confirm it by visiting our remote repository. ​So we are still able to see this tag V ​19 ​RC ​two. ​And if we refresh our browser ​and you can clearly see the tag V ​19 ​RCW ​is missing, which means the tag has been deleted. Let's get back to our terminal. ​Now, let's ​list the tags we have using git tag. ​Now here with this command, you deleted a single tag. ​But with the same command, you can delete multiple tags as well. 
Play video starting at :2:5 and follow transcript
2:05
​Let me show you how to do that. So the command is git push ​origin the remote reference ​and then the tag name preceded by column. ​So let's say that I want to delete all the tag in the CDS V ​dash 2.1 0.5. ​So let me copy it and paste it over here and I want to delete the entire series. ​So I paste it once again and modify it to RC two ​and then the RC three. ​So here is a command with the help of which you can delete multiple tags. ​You simply name the tags separated by space and preceded ​by colon press enter and we enter our user name ​and password as usual ​and ​says ​that all these three tags have been deleted. 
Play video starting at :2:52 and follow transcript
2:52
​Let's confirm this by going to a remote repository and let ​me refresh the browser over here and here you go, ​you can't see any of the tags in the cds 215. ​And this means that all the tags have been deleted in one go. ​So by this, I conclude this lecture.
