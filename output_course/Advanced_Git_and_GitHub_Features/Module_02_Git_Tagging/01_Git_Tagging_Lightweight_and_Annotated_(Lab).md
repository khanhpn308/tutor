# 🎥 Git Tagging: Lightweight and Annotated (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/682a0057-d54d-4cfc-8713-da745c5db6d4_43d92a20bb824f62af12811cc646d603_video20_1.mp4.mediaconvert/full/682a0057-d54d-4cfc-8713-da745c5db6d4_43d92a20bb824f62af12811cc646d603_video20_1_WEBM_540.webm?Expires=1793059200&Signature=dV9zPJUepclgEp~89GY7NGLuSBtAIQFJqPivVfcZQTNJKbELViADxuMSi8m772q0A2gFTTvo0tBZ79FkYAPup9rv0DUYOlz6C77bGq65bAXGsJ6ZcwuNCgTsfwNOr2DPArpcTVsQj9ciKVcs9LCV4k0SraVHFooSGFMqB28JwNA_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So in this lecture, ​we'll explain the concept of git tagging and we'll work with a repository demo tag, ​which is a freshly created repository, you can check the contents of the directory. ​Now, as a general introduction, ​git has the ability to tag specific points in history ​as being important tags acts as bookmarks. ​Normally people use a tag functionality to mark release points ​such as version 1.0 version 1.3 and so on. ​Now, git uses two main types of tag, ​lightweight tags ​and annotated tag. So we'll start working with the lightweight tag first. ​Now, a lightweight tag is very much like a branch ​that doesn't ​change. It is just a pointer to a specific comment. 
Play video starting at :1:5 and follow transcript
1:05
​So let me clear the screen ​and we'll start with a working example on lightweight tag. ​So before we create the tag, let's examine our history using ​git log and the following options press enter. ​So that's our commit history. ​I have edited and made a couple of changes and ​build up a commit history for the demonstration purpose. ​So let's now create the tag. So the command is git tag, then you got to have a tag name. ​So let's have our tag name ​V ​1.8 ​RC ​one. So RC one is basically a short form for release candidate ​press enter ​and our tag has been created. 
Play video starting at :1:51 and follow transcript
1:51
​Let's check using the command ​git tag, which lists all the tag in our repository press enter ​and here you go. It lists our tag, ​V 1.1 RC one. ​You can also list the tag using the command ​git tag with dash ​dash ​list, option press enter. ​Now remember that you should use the dash dash option with the list or else ​git will create ​a tag called list. ​So let's execute our git log command. ​Once again, we'll retrieve a earlier command press enter and here you go. ​So here in the newly executed git ​log command, ​you can see the tag over here and it has been tagged to this particular commit ID. 
Play video starting at :2:38 and follow transcript
2:38
​Now remember one important thing that if you execute the command ​git tag and then the tag name, ​it will always tag with the latest commit. ​However, you can associate the tag you create with a specific commit as well. ​We'll talk about associating a tag with a specific commit later on. ​Let's clear the screen ​and let's reexecute our ​git tag command to list our tag. ​And now if you want to list details about this particular tag, you can use the command ​git ​and then the name of the tag press enter ​and here you go. ​So hence the show command provides us the following details. ​It displays the commit id with which this tag is associated. 
Play video starting at :3:27 and follow transcript
3:27
​It provides the author and timestamp the ​commit message associated and the DIIF related ​to the involved file, which is 44 dot HTML. ​So that, ​that's all what I had to say about lightweight tags. ​And next comes the annotated tag, ​annotated tags are stored as full objects in the git database. ​They check out, they contain the tagger name, ​email and the date annotated tags also have a tagging message ​and can be signed and verified with GPG as well. ​So GPG stands for ​GNU Privacy ​Guard. ​Now, if you want a temporary tag and you don't want to keep other information, ​lightweight tags will be good enough for you. ​However, ​it is recommended that you create annotated tags so that you ​can have all this information which I just now mentioned. 
Play video starting at :4:30 and follow transcript
4:30
​So let's start with a working example. ​So we continue to work with a demo tag repository with which you worked earlier. ​So let's execute the git ​log command ​to check our commit history press enter. ​So let's modify the file index dot H TM L press enter ​and you'll simply modify this title over here. So let's name it annotated tag demo. ​Let's save and quit ​and let's do an express commit using ​git ​commit. ​AM ​index ​file is a track file and our simple ​commit message is master since this is a master branch ​So you have a typo here, ​I'll remove one extra M now let's continue with the commit message. 
Play video starting at :5:19 and follow transcript
5:19
​So it's master branch. ​So master column, modified title. And then the file name is index ​dot ​html ​codes, close press enter ​and our commit is done. ​And let's now create our annotated tag using the command git space. Then tag ​a, we'll explain the ​A option and then our tag name, which is V ​1.9. ​So V stands for version basically and then RC two. ​So RC stands for basically release candidate. 
Play video starting at :5:55 and follow transcript
5:55
​And then ​M so ​M stands for the tag message and then the tag message itself. ​So let the tag message be release version 1.9 codes, close press enter. ​So let me now explain the command. ​So the ​A option stands for annotated and is short for the ​annotated option. ​So let me show you that. ​So you can see here. ​So instead of ​a, ​you can use ​annotated as well. 
Play video starting at :6:31 and follow transcript
6:31
​And the ​aim specifies a tagging message ​and this tagging message is stored with the tag. ​If you don't specify a message for an annotated tag git launches your editor ​so you can type your tag message. So I'll show you an example of that ​reexecute the git log command. ​So I retrieve the earlier command press enter and here you go. ​So this was the last commit we created, modifying the file index dot H TM L. ​And after we executed our ​git tag command over here. Our latest commit got ​tagged with this tag, V 1.9 RC two. 
Play video starting at :7:15 and follow transcript
7:15
​So remember ​that wherever you execute the git tag command ​and you do not associate it with any particular commit ID, ​then the tag will get associated with the latest commit ID as in this case here. ​So let me clear the screen. So let's create another commit and then another tag. ​So I'll modify the file index dot HTML. Once again, press enter ​and I'll do ​a simple change over here. So here instead ​of normalize ​meant CSS, ​I'll simply use ​normalize ​CSS, ​which is a reference to a style sheet. So this is a simple change. 
Play video starting at :8: and follow transcript
8:00
​Let's save and quit and let's do an ​express commit by retrieving an earlier commit message. ​So we'll do an express commit this time and our express ​commit message is master since you are in the master branch ​and we took that action ​modified CSS ​and the file is ​index dot ​HTML codes, close press enter. ​Now let me create an annotated tag, but this time I'll not provide the ​A option. ​So as earlier, we'll execute the git tag command with the ​A option which means an annotated tag. And our tag name is V ​stands for version ​1.9 0.1 and that's it will not provide the ​A option this time, press enter ​and here you go. ​So you can see that our default text editor sublime text ​has opened and we will simply add our tag message. ​So our tag message is release version 1.9 0.1 will save our changes, file, save and in ​file exit. So let's execute our ​git ​log command press enter ​and here we are. So here is our latest comment and our latest annotated tag. 
Play video starting at :9:24 and follow transcript
9:24
​So let me clear the screen ​and let me execute the git log command once again ​and let's examine the two tags we created one was V ​1.9 0.1 and the other was V 1.9 ​RC two. ​So we'll list our tags first using git tag. ​You can provide ​the ​dash ​dash list option as well. Both will work press enter and here we are. ​Now, if you want to examine our tag or check the details related to the tag, ​then you can execute the command git show ​and then the name of the tag. So let's check the details of our latest tag, ​which is V ​19.1 press enter and here you are. ​So if you examine the information here closely, ​you can see that the information provided by git for an ​annotated tag is slightly different compared to a lightweight tag. 
Play video starting at :10:26 and follow transcript
10:26
​So first here you have the tag name and then the name of the tagger ​and then the timestamp or the date. ​And here is the tag message that we created in our default text editor ​and then you have the commit ID author name. ​And here, the author and tagger are the same which is me ​bash ​Roy. ​And then the timestamp for the commit here is ​the commit message with which the tag is associated. ​And lastly, ​you have this D ​information for the file ​index dot HTML. ​So remember that this was a file that was involved ​in the commit with which this tag is associated. ​So with this, we conclude this lecture.
