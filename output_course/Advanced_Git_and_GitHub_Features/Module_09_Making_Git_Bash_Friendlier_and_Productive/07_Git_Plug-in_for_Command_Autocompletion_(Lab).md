# 🎥 Git Plug-in for Command Autocompletion (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/562b1a15-c2fe-4b1a-8ad9-9598d0dc2781_6aa5193bc0ee4474aa521ee5ecb9dcfc_video27_7.mp4.mediaconvert/full/562b1a15-c2fe-4b1a-8ad9-9598d0dc2781_6aa5193bc0ee4474aa521ee5ecb9dcfc_video27_7_WEBM_540.webm?Expires=1793059200&Signature=hrErBdAKJs9UOzkOr4wThQFnAMCH-8-9PSE42AvytISxhYlhi2KjvXTemCXWP0OWg6la6F4EzlEq6-Wi9GIy9NUp1ScwNUkH1~ENVe4hqpRHA~ap3w72L5OGpyQ~KbIPQAqFGaUihEOO0ZMdxIhas999bnPQZ8UIMtAgdkvgRlA_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​Now, I'll show you a cool feature of git bash. ​That's autocompletion. ​So what autocompletion is? ​So normally when you issue bash commands, ​you get an auto completion feature. ​So let's demonstrate that. ​So for example, let's check the contents of this home directory. 
Play video starting at ::33 and follow transcript
0:33
​So ​there are too many files over here. ​So let me get into ​the git fast directory ​and let me check the contents of the directory. ​Let me get into. ​So right now, I'm in one of the git repositories. ​So let me check the contents of the directory. ​OK? ​So there are several files over here. 
Play video starting at ::58 and follow transcript
0:58
​So let's say I'm trying to open the file humans dot ​TX. ​So I'm trying to use a V editor. ​So if I type VIH ​and press tab ​automatically, ​I get the humans ​dot ​txt ​part completed. ​So this is autocompletion. ​Now, this is available by default for all the batch commands. But what about the ​git commands? So let's try to find out ​the autocompletion ​regarding the git commands. 
Play video starting at :1:32 and follow transcript
1:32
​So I clear the screen ​and let me try to find out ​the autocompletion feature ​for a particular command, say git config. ​So I want ​git config to be autocompleted. So let me press tab ​for auto completion. ​So there are two commands that starts with C one is the commit and another is configd. ​So if I type N ​and press tab ​automatically the command gets completed. ​So right now I'm in the Windows platform. ​And as you can see, ​the autocompletion feature ​is available for git commands ​out of the box. 
Play video starting at :2:16 and follow transcript
2:16
​However, this is not the case ​with ​the Linux ​or the mac platforms. ​So we ​need to do an extra bit of work ​to make the autocompletion feature work for git commands ​on Linux ​and Mac. ​So I'll show you how to do that. So right now, I'm on the Linux platform. ​So let's check whether autocompletion works ​for gate commands on the Linux platform or not. ​So let's check the contents of the directory ​and let me change into directory git fast and ​let's check the contents of this directory too. ​And I'm in ​a ​git repository my ​git ​report. 
Play video starting at :3:2 and follow transcript
3:02
​Let's check the contents. So there is a test file over here. Let's clear the screen. ​So let's check the autocompletion feature for bash ​commands in ​Linux. ​So if I type V ​type ​T and press tab, ​the file gets automatically completed and I can view the file in the editor. ​However, this is not the case with git commands. ​So let's try to execute the git ​config command. 
Play video starting at :3:31 and follow transcript
3:31
​So I type ​co ​and press tab. ​So basically nothing happens, ​which means ​the autocompletion feature is not available out of the box for Linux. ​This too is a case for mac as well. ​So as I said, we need to do ​a ​of extra work. ​What is that? ​Let me show you now. ​So let's CD to the home directory. 
Play video starting at :4: and follow transcript
4:00
​So we need to download a particular file and we need to source that file in ​the ​RC file. ​So this is just similar to what we did ​for the file ​git ​prompt. S ​So let me use the cURL command for downloading ​cURL ​uppercase O. ​You could have used W gate as well. And let me paste this URL. ​So as you see, I need to download the file ​completion dot bash. ​Let me press enter ​and the download starts and the download gets completed. 
Play video starting at :4:39 and follow transcript
4:39
​Let's check the contents of the directory. ​And as you can see ​the git ​completion ​bash file has been downloaded. ​So let's clear the screen ​and let me ​get into the ​bash ​RC file. ​So we ​do ​bashrc ​press I ​to insert ​and I'll simply source ​the file ​git completion dot ​So that's in the home directory. ​That is where I downloaded it ​and I'll just paste the file name, press escape ​key, colon ​WQ ​and we're back in the terminal. ​So either I need to source the ​file in the terminal right now ​or I need to restart the terminal ​to see the ​effect of our action in work. ​So I'll restart the terminal, press exit So I've restarted the terminal. And ​in order to see ​the autocompletion ​work for git commands, ​I need to check into a git repository. So that's in the git fast directory. 
Play video starting at :5:53 and follow transcript
5:53
​And one of the git repository we have is my ​git report. So let me try the git config ​command as we tried in windows. So ​press tab ​for auto completion and here we go. ​So we are being offered two commands that starts with ​commit and config. ​So if I type N and press tab, once again, ​automatically ​the command gets completed. So whatever we did right now on Linux ​will work on Mac as well. ​However, ​if you source ​the git completion file ​within the ​bash ​file in mac, you need to source the ​file within the ​git profile file. 
Play video starting at :6:44 and follow transcript
6:44
​So right now I'm in the mac terminal and ​let's try to autocomplete the git config command. ​So I type git co ​and press tab ​and nothing happens over here. ​So ​as usual, ​we need to do the additional thing of downloading the git completion file and so on ​the same in ​bash ​file, ​let's ​CD to home screen ​and let me download the file. ​You can use Wgt ​as well. We paste the URL and press enter ​and the download gets completed. ​So let's check the download ​and yes, the download has been done. ​Let's clear the screen and let's open the ​bash ​file. So here is a ​bash ​file, ​press I for inserting ​press enter ​and we source the file with the source command ​and I'll simply paste the name of the file git completion dot ​bash. 
Play video starting at :7:57 and follow transcript
7:57
​Now I'll exit from the editor press ​SK ​column ​WQ for quit and save. Now, we need to go into the ​bash profile file. ​So that's do ​bash profile ​press enter. ​And as you can see, ​the last line, we have already sourced ​the ​bash ​file, so we need to do nothing here. ​So I'll ​type colon Q ​to quit. ​So the last step we need to do right now ​is to execute the ​bash ​profile. ​So for this purpose, we'll restart the terminal and I have restarted the bash ​terminal. So we need to get inside ​the git repository. 
Play video starting at :8:49 and follow transcript
8:49
​So that's in the git fast directory. And the name is my ​Gitrepo ​press ​enter and we are in the repository. ​So let's check ​the autocompletion feature for git ​config ​command. So I have typed Getit ​co ​press tab. ​And here we are being offered commit and config commands since both starts with C ​and if I type N and then press tab again. As usual, ​the command gets completed.
