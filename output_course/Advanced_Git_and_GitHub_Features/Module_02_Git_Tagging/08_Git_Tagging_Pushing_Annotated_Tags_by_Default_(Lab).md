# 🎥 Git Tagging: Pushing Annotated Tags by Default (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/0b1bca1e-e6f5-41e4-9bab-c81e9d0becbf_b432dbffb77649b88b1994c67ed200ac_video20_8.mp4.mediaconvert/full/0b1bca1e-e6f5-41e4-9bab-c81e9d0becbf_b432dbffb77649b88b1994c67ed200ac_video20_8_WEBM_540.webm?Expires=1793059200&Signature=Wk7uYOoNYfWJ433huOv6N4wzodp2KD1wPMRM1V9iPi1CZfLDJKpSQp~vKMzCFHkHXzaufvcPXVNHiobYKbVvLqZissXByNiU8M6r~e6z32k6nSIziY-DzIX5YasTBLLtyfHrCP4lPog5i44cOz9GG5ek2R05iRuL0QrBhetU7Rw_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hey there, welcome. ​So in this lecture, we'll work on a new and fresh repository, which is demo tag two. ​Now let me explain you the setup of the ​repository which I have done for this demonstration. ​So let's execute the command git log. ​So I am retrieving an earlier executed command press enter and here you are. ​So these are the five ​commits as you can see over here. So this is the first commit for the setting up of ​the repository where I committed all the files ​and then I created additional four commits. 
Play video starting at ::48 and follow transcript
0:48
​And at these four commits, I have created four tags. So this is the first tag ​V ​10. ​So a signifies annotated tags. So I've prefixed these tags with a, ​just to help us identify ​that what type of tags you have created. Of course, in earlier lecture, you saw ​that how to identify annotated tag versus lightweight tag by executing the command ​git cat files. But this prefixs an and ​LW will help us to quickly identify the type of tags. ​So these are the three annotated tags which I have created. 
Play video starting at :1:35 and follow transcript
1:35
​And finally, I created a lightweight tag as well over here. ​So this is the setup I have created for the demonstration in this lecture. ​Now comes the important question what actually ​will be demonstrated in this lecture. ​Now earlier I said that ideally you should only push annotate add tags to the remote ​server such as github and keep the lightweight ​tags for local development to avoid tag clashes. ​Now, since the ​git push ​command doesn't transfer tags to remote servers such as github by default. ​And you have to actually explicitly push tags to a shared server ​once the tags are created in the local repository. However, ​git has provided us an option which if configured in the ​git config file will allow us automatic pushing of annotated tags. 
Play video starting at :2:33 and follow transcript
2:33
​Now, this configuration is push ​follow tags. ​Now, if this configuration push ​follow tags is set to true, this will enable the flag, follow tags option by default. ​Now this is a ​great and convenient feature and I'll demonstrate it right now. ​Now let's go to our browser and visit the demo tag two ​remote depository on github. And here is the demo tag to repository. ​As you can see also, the repository is empty. ​As you can see the default page presented ​by github for a freshly created repository. 
Play video starting at :3:13 and follow transcript
3:13
​So we have no artifacts over here. So let's get to a terminal and do the need for. ​So before we push all our artifacts to a remote repository, ​we need to set up the configuration ​for automatic pushing of annotated tags using push ​follow tags option. ​So let's clear the screen and let's do the configuration using git ​config ​global. And then ​the option we want to configure which is push ​dot follow tags ​and we need to set it to true press enter. And let's check our configuration using ​git ​config ​global ​list. Oops, that was a typo. So let me re execute the command. 
Play video starting at :4:1 and follow transcript
4:01
​We need to put A T over here. So it's list press enter. ​So here is the configuration we wanted to do ​and it has been done. So push, ​follow tags is set to true. Now, ​now let me clear the screen ​and we are all set to push our artifacts. So this is the first time push. ​Hence, we need to use the command git push ​U origin the remote reference ​and then master. 
Play video starting at :4:28 and follow transcript
4:28
​So ​you will set up a tracking branching relationship as you have seen earlier. ​And this is a first time usage subsequently in all push, ​you don't need to use the dash you option. ​So normally when you push by default, only the commits are pushed, ​but this time something different will happen as will be evident soon. ​Let's press enter. ​And here we are git prompts us for username and password ​and I enter both of them press OK button ​and here we go. So ​something interesting has happened. ​So git has compressed the object and started writing the object. 
Play video starting at :5:9 and follow transcript
5:09
​And in addition, this time, ​git has done something different ​due to our configuration, push ​follow tags, git has pushed all the annotated tags as you can see over here. ​So that's why I prefix the tags with an to help us easily identify what's happening. ​But you can also see ​that the tag prefixed with ​LW, which was a lightweight tag has not been pushed. ​So all this magic has happened due to our push ​follow tags option. ​So let's get back to our browser ​and visit the remote repository. So here you are. ​So let's refresh the browser to see what has happened. 
Play video starting at :5:52 and follow transcript
5:52
​So here is our demo tag to repository and ​you can see all the artifacts have been pushed. ​If you go to the comment section of ​here, ​you can see all the five commits appropriately displayed over here. ​But the interesting thing that has happened can ​be seen if we go to the releases section ​and you can see ​all the three annotated tags have been pushed along ​with all the artifacts and the commit history. ​So this is what normally doesn't happen until and unless you configure the push, ​follow tax option. So let's get back to our terminal. ​And this time, I'll show you another nice effect of configuring the push ​dot follow tax option. ​So for that purpose, ​I need to delete all the tags that I have ​pushed now so that I can demonstrate to effectively. 
Play video starting at :6:45 and follow transcript
6:45
​So in order to delete all the tags, I need to execute the command, ​get push origin and then all the annotated ​which have been pushed prefixed with colon. ​So I'll simply copy one of the tags and paste it over here. So this is V ​one ​and the next one is V 11 ​and lastly is V ​12. ​So that needs to be prefixed with colon as well. ​And let's press enter, we'll enter the username and password. ​Now, this entering of username and password each time ​push to github ​might be quite inconvenient. And git provides us an option to store our passwords. 
Play video starting at :7:27 and follow transcript
7:27
​So I'll demonstrate in a subsequent lecture how to do that. ​But let's enter the username and password this time, press enter and here we go, ​all the three annotated tags have been deleted. ​That's what git says. ​And let's confirm it by visiting our browser in ​a remote repository and let's refresh our browser from here ​and here you are. ​There aren't any releases here, which means all the tags have been deleted. ​So let's get back to a terminal. ​So during our first push to github, ​I demonstrated you how ​a ​tags get pushed by default. 
Play video starting at :8:3 and follow transcript
8:03
​And now this time, I'll also show that when you push any tag such as a lightweight tag, ​your Anna ​tags will also be pushed by default due to your push ​dot follow tags option. So let's list our tags using ​git tag. You can use dash ​list option as well. And here is our lightweight tag. ​So let's push this tag to github. ​We'll use the command ​git push ​origin and then the tag name. So I'll just copy the tag name from here ​and paste it over here, press enter and the username and password click. Ok. 
Play video starting at :8:42 and follow transcript
8:42
​And here we are. So down below, you can see ​that our lightweight tag have been pushed as you desired. ​In addition, all the annotated tags have been pushed as well. ​Sure enough, ​let's get back to our browser to confirm and let's refresh the browser over here. ​And you can see over here, ​our lightweight tags have been pushed over here and ​our ​annotated ​tags have been pushed along as well because we have configured the push ​follow ​tax option. ​So with this, I conclude this lecture.
