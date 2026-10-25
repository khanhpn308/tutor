# 🎥 Git Plug-in for Working Directory Status Information in Mac (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/e8af6e64-bb82-46f1-9f0f-582a0daa9b0f_99feffe9258a4548bf89932785643c34_video27_6.mp4.mediaconvert/full/e8af6e64-bb82-46f1-9f0f-582a0daa9b0f_99feffe9258a4548bf89932785643c34_video27_6_WEBM_540.webm?Expires=1793059200&Signature=I367a5DGd2DrA1GzYiQLkOMjhYbkIgG2OnfYZoQmrLmaVzqkZZNFOnePm3f6oApGjnwp6rWPw2wSIcFbVXKXmPD1JhrhxTU0fB5q04BnXo6TolCDwhxKCOjW7-CTN6OT1w5TY-hXrPW5AXk9a11e01zrkaTNZr2qRs1YtQa4mgc_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​So here I'm in the Mac terminal ​and I'll open a terminal. ​So likewise as we did in Linux, ​we'll be downloading the ​git ​prompt ​file in mac as well. ​So you'll use girl ​here ​and I'll paste the link for downloading the file press enter ​and the downloading is done. ​Let's check the content ​of the home directory ​and here you can see the ​git ​prompt ​has been downloaded. So let me now open ​the ​bash ​file ​and it's clean. ​So we'll copy, paste the code that is used in windows and Linux ​press the I key to insert right, click and paste. ​Of course, we need to use the export command ​and we'll add the line source home directory ​git ​prompt ​dots. 
Play video starting at :1:10 and follow transcript
1:10
​So this is the exact code that worked in Linux ​and it should be working as ​here ​in addition ​to sourcing the ​RC in ​bash ​profile. So press the S ​key colon ​WQ to put and save. Now I open the ​profile file press enter. ​And as you can see here, I have already sourced the ​bash ​RC within ​bash ​profile. So there is nothing to change here. ​I escape from the editor. ​Now, I'll quit ​the terminal and restart, ​press exit. 
Play video starting at :1:49 and follow transcript
1:49
​So I've restarted, it seems there is some error in the file. ​So there is a Typo here. So I'll change it just now. ​Bi ​Bashrc ​press enter ​and I have inadvertently ​introduced this parenthesis here, ​which should not be there. ​So press insert key ​and delete it, press escape, colon ​WQ. ​Now I'll read, ​start the terminal once again, press exit. ​So I've restarted the terminal and as you can see, things are pretty much fine here. 
Play video starting at :2:24 and follow transcript
2:24
​So let's check the contents of our home directory. ​Ok. ​So let's clear the screen. ​So in order to test the effectiveness of whatever we did so far, ​let's go through a git workflow. Let's create a directory. ​Get fast as we did earlier. Press enter, ​let's change into the directory, get fast ​and let's create a ​git repository ​using the git ​init command ​and let us name it ​my ​git ​repo as earlier press enter ​and the depositor is created, ​let us change into my ​GPO. 
Play video starting at :3:2 and follow transcript
3:02
​And as you can see the git prompt effect ​changes to show the current working directory, ​the status of the current working directory and the branch information. ​So let's create a file test file ​dot ​txt ​press enter. ​Let's press the I key to insert some line. ​This is the first line ​and let's quit and save ​from the editor. ​Now, ​the current working directory hasn't changed because ​the file is yet untracked by git. ​So let us add it to the staging area. ​And you can see the working directory status change. 
Play video starting at :3:45 and follow transcript
3:45
​So let us commit ​our changes, ​get ​commit ​and let us type a simple commit message, ​press enter and the working directory is clean. ​Let's clear the screen ​and let us edit the test file once again, ​press I ​to insert ​and this is the ​second line ​press escape, colon ​WQ to quit and save. ​And the working directory status changes ​with a star symbol. ​Let's add our changes, ​press enter ​the current directory status ​changes to reflect that we have added our changes to the staging area. ​And let's ​commit this file ​git commit command ​and we type a simple message. ​Press enter ​and the commit is done ​and the working director status is clean ​just to check the effectiveness of whatever you have done, ​you can issue the git status command ​and you can see the working directory is clean.
