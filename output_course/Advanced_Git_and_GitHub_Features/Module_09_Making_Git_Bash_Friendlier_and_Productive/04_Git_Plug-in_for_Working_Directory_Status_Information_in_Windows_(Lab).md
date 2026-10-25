# 🎥 Git Plug-in for Working Directory Status Information in Windows (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/99384159-4a80-4b18-8b78-9b3dbe7a8f25_7cf8544c995f444485d99267cc1e2f42_video27_4.mp4.mediaconvert/full/99384159-4a80-4b18-8b78-9b3dbe7a8f25_7cf8544c995f444485d99267cc1e2f42_video27_4_WEBM_540.webm?Expires=1793059200&Signature=Zh4hEvIwYuqMIrKeIQGAFK1oIrfdZPcL~Sh1hC-NMhOcyTS5nSrIAqR0Se0HBr14pI4ZEAucsjJzk6KhXNR2h3x~zu5XBgy4ftih2yOB6Ptr4UgFG4PxnsEGRAIY4NQDXhjn4IL22cSKfdu54NJjfp5mBpAmM9ouCfjALeLzyzs_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So you have been able to display ​the branch information ​in the git ​bash prompt. ​Now, let's see how we can display the working directory status information ​within the bash prompt itself. ​So let's get into the ​bash ​file residing in the home directory. ​So bash ​enter, ​press the I key to insert so that you can make changes in the editor. ​Now, we'll go at the top press enter. ​Now I'll introduce a line of code ​that will perform the magic of ​providing working directory status information within the ​git path ​prompt itself. 
Play video starting at :1:1 and follow transcript
1:01
​So it's git ​underscore ​PS one ​underscore ​show ​dirty state ​equal to one. So setting the value of this variable ​git ​underscore ​PS one ​show ​dirty state to one ​will enable displaying the working directory status information ​within the gate batch prompt itself. So let's press the escape key to quit and save ​WQ ​press enter and you backed. ​Now, I'll restart the bash terminal ​exit. Now from the bash terminal press enter. ​Now I've restarted the bash terminal. So let's get into one of our git repositories. 
Play video starting at :1:47 and follow transcript
1:47
​So get fast ​and let's get into the early repository where you are in the git with ​github ​demo press ​enter ​and bingo here, you can see a star ​that actually ​signifies that we have pending changes ​in the ​working directory. ​So this symbol ​doesn't remain static at star, ​but it dynamically changes to display ​working directory information. ​So I'll show you right now step by step so that ​you understand better the significance of ​this working directory status information. ​So ​let me now demonstrate the behavior of this working directory ​status information by creating a fresh directory from scratch. ​So I'll return back to git ​first ​and I'll create a new directory. ​So Getit in it. ​And let's ​name this git repository, ​my git ​repo ​press enter. 
Play video starting at :2:58 and follow transcript
2:58
​Now let's check whether the git repository has been created or not ​and it has been created as you can see ​here. ​So now we'll get inside this git repository ​press tab for auto completion. Now we are in the git repository and here you can see ​there is a ​hash symbol which indicates a fresh ​git repository. ​Let's clear the screen and let me create a file to demonstrate the working ​directory status information dynamics. ​So let's name it test ​file dot ​txt ​press I ​to insert line within the editor. ​And now let me introduce a simple line. Let it be this is a simple ​change. 
Play video starting at :3:50 and follow transcript
3:50
​Press ​SK ​colon ​WQ to QN. ​So right now it stays still at the hash symbol. ​Now I'll issue the git status command. ​The whole idea of having the working directory status information ​within the git back ​prompt itself is to make our life easier ​by making us more productive. ​We don't need to issue the git status command at every step. ​However, in order to demonstrate the efficacy of this step, ​I'll still issue the git status command ​so that you can better appreciate how this works. ​So let's issue the git status command. 
Play video starting at :4:36 and follow transcript
4:36
​As you can see git status ​command says there is an untracked file ​which is test ​file ​dot ​TXT. And here in our working directory status information ​in the git dash ​prompt, we have the hash symbol. So let's clear the screen. ​Now let us add this file to the staging area press enter ​and it's create our working directory status information in the bash prompt. ​Changes from hash symbol ​to plus symbol ​to indicate ​that changes have been added to the staging area. Now, in order to better appreciate ​as to what is going on, ​I'll issue the git status ​command in parallel press enter. Now, as you can see, ​the status command says ​that a new file has been added to the staging area which is test ​file dot ​txt. 
Play video starting at :5:33 and follow transcript
5:33
​So I hope now you can better appreciate ​by comparison as to what is going on. ​Let's clear the screen ​and let's commit this file ​git commit ​M ​and let's have a commit message. ​Let it be a simple commit ​press enter. ​So here you can see ​it displays only the branch information right now ​and there is no working directory status information. So ​the absence of any information here signifies that the working directory ​is clean. ​Now, let's verify this by using the git status command ​git status press enter ​and here it is, it says nothing to commit. ​And the working directory is plain. Let's clear the screen. 
Play video starting at :6:28 and follow transcript
6:28
​Now, I'll go through another round of git workflow ​in order to display the efficacy of ​showing working directory information ​within the bash prompt itself. So let's make changes ​to the text file which you just now worked upon. ​So V ​test file, press enter, ​press I ​to insert changes, ​press enter to go to the next line ​and make a simple change. ​This is ​the ​second ​line ​press SK colon ​WQ to quit and save. Now, here you can see immediately ​the working directory status information change is signified by this star symbol. ​Now let's add this change to the staging area, ​get add ​test file, the TX ​press enter ​and here we go. ​We have the symbol switching from star to plus sym. 
Play video starting at :7:34 and follow transcript
7:34
​They indicate that changes have been added to the staging area. ​Now, let's commit these changes to ​get commit ​m ​for commit message. ​And let's have a simple message. ​Second, commit ​message, ​press enter. ​Now as again earlier, we have the branch information displayed, ​which means the working directory is clean.
