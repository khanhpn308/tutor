# 🎥 Git Plug-in for Branch Information (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/6ed858e5-8e83-4827-8ad0-41f5eadb846b_e3950bc46e8f46c1af1dd22047e3262f_video27_3.mp4.mediaconvert/full/6ed858e5-8e83-4827-8ad0-41f5eadb846b_e3950bc46e8f46c1af1dd22047e3262f_video27_3_WEBM_540.webm?Expires=1793059200&Signature=GdsSvhalQQ5rU~epXerAg4~SSuumQoUs3S69hSh8RFgyAlNkdLh7RBDQbmRWdvCOIXnm6~hQXs03l3ikr0CsBqQF7s3EBI83U5HxWclnfFcuPTXMv9SWM2OuIGbAq8OlyaEO0di2UO2wIV8AQuHM4~YQMy7Uc5yEdjTubVOfzFU_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. In ​this lecture. ​I will actually show how we can further modify ​the bash prompt. ​I mean the git bash prompt to ​fetch the working directory status info ​and current branch information. ​Now, if we can have the working directory status information ​and current branch information ​within the ​git bash prompt itself, then it becomes very useful ​and it makes us much more productive. So let's see where you are right now. ​We are ​the git fast directory ​and ​here we have certain ​git repositories. 
Play video starting at ::58 and follow transcript
0:58
​So let's CD into one of the git repositories, ​git with ​github ​demo press tab for auto completion press enter. ​And here we are in a ​git repository. ​Let's clear the screen ​now to have information about working directory and branch information, ​we normally issue the git status command. ​So let's press enter. ​So as you can see the status information says that we are on the branch master. ​And here ​the working directory status information says that we have a modified file ​called robots ​dot ​TXT. Now, what if we could have ​the information that git status provides in the git bash ​prompt itself? 
Play video starting at :1:53 and follow transcript
1:53
​I think it would be very useful and very productive. ​And let's see how we can do that. And right now we have this git bash prompt ​and this prompt only provides information regarding the ​working directory, ​but it doesn't have any information regarding the current branch information ​or it doesn't provide any information ​regarding the working day ​status. ​So let's clear the screen. ​So let's check the contents of the ​bash ​file, ​which is in the home directory. Now, the home directory is represented by delay ​bash. ​And so here is ​the contents of the ​bash ​file. 
Play video starting at :2:45 and follow transcript
2:45
​So let's do one thing here. Let's comment out this code and we'll quit and save. ​So let's press ​escape, ​key colon ​WQ ​and we're back in the terminal. So why I commented out the code in the ​patch ​file. ​So I actually want to return back to the original prompt that is available ​when kit is installed on Windows. So right now I'm on Windows platform. ​Don't worry for Linux and mac platform users. 
Play video starting at :3:20 and follow transcript
3:20
​I'll also demonstrate how things work. ​So I'll right now quit the terminal ​and restart it. ​So let's type exit ​to quit the terminal. ​So have restarted the batch terminal. ​So I have returned back to the original prompt that a window ​user will get after installing git. So let's ​get into one of the git repository ​which resides in the git fast directory. ​So one of them is git with github ​demo. Let's press tab for auto completion ​and let's press enter and here you can see ​that by default when git is installed on Windows, the branch information ​is automatically available. 
Play video starting at :4:9 and follow transcript
4:09
​However, ​the working directory status information is not available by default. ​Now, I'll show you ​how to modify the git bash prompt ​so that you can bring this particular information, ​which is a branch information ​as well as working directory status information ​within the git bash prompt itself. Now let's check the value of the PS one variable. ​And let's try to examine ​which component of the value of the PS one variable ​is responsible for providing ​this branch information. So I'll type out the command for the same. So it's ​eco ​dollar ​PS one ​press enter. ​So this is the portion of the PS one value ​that provides branch information within the bash prompt. So ​git PS one is actually a shell plugin provided by git ​so that the branch information is available ​within the git bash prompt itself. 
Play video starting at :5:20 and follow transcript
5:20
​Now I'll clear the screen ​and change to the home directory. ​Now, I'll open the ​bash ​file press I ​to insert and I'll remove the comment. Now here within the PS one value, ​I will embed the ​git ​PS one ​shall plugin ​so that I can have the branch information within our custom bash prompt itself. ​Now let's type out the code. So I'll press a space here, ​then ​opening bracket, ​E ​in lower case, then the opening bracket, ​one for bold color ​or the brighter color. Now let's have the branch information in blue color. ​So 34 represents the blue color aim in lower case to terminate the color sequence, ​then backslash ​closing bracket as we did earlier and then we have the ​git plugin git PS one. So ​since this is a function, it will be invoked with a dollar ​parenthesis ​underscore ​underscore ​git ​underscore ​PS ​one. 
Play video starting at :6:37 and follow transcript
6:37
​So the code continues in the next line closing parenthesis and that's it. ​So let's reexamine what changes we made. ​So this is our coloring code ​E opening bracket, ​one ​semicolon 34 M ​and this is ​wrapped ​as usual ​with backslash ​opening bracket ​and terminated ​with backslash ​closing bracket. ​And here we have the gate plugin ​which extends into the next line ​till here. ​So let's quit and save, press the escape ​key colon ​WQ ​and now we're back in the terminal. ​So we'll restart the terminal. Let's exit from the terminal, press enter. 
Play video starting at :7:29 and follow transcript
7:29
​So I've restarted the terminal. ​And as you can see, ​I have the desired ​customized bash prompt ​which we created in our earlier lecture. ​However, we need to examine as to whether ​the branch information is displayed ​in the bash prompt or not. ​So for that I need to get inside a ​git repository. ​So let's do that. ​Let's see into git ​fast press staff for auto completion ​and then again, press staff for auto completion. So git with ​github ​demo ​is one of the git repositories that we're having in the git ​fast directory. 
Play video starting at :8:11 and follow transcript
8:11
​So let's press enter ​and here you go. ​We have the branch information ​nicely displayed within the git bash ​brand. ​So ​right now we are on the master branch ​and ​this branch information is displayed ​in, ​in bold blue color. ​So with this, we'll conclude this lecture. ​And in the next lecture, ​we'll make an attempt ​to display ​the working directory status information within the git bash prompt.
