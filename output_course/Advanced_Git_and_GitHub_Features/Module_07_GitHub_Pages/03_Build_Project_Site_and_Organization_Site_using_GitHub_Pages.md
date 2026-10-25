# 🎥 Build Project Site and Organization Site using GitHub Pages

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/625f380a-af3e-4b68-a4c5-ba71cb01f973_a0086fb43cf6484e990b2d37b9aa390a_video25_3.mp4.mediaconvert/full/625f380a-af3e-4b68-a4c5-ba71cb01f973_a0086fb43cf6484e990b2d37b9aa390a_video25_3_WEBM_540.webm?Expires=1793059200&Signature=jUOwOz0ftySEleUNudOb7r6QQdBaRBupno4hYoQ4pMFJpsz-vtQEeTGAZkgsLLE42CPTYIN9yR-I7Lc14meGG9KWbugsQv03WsJV74ccjlxHUxldz94PI-MKwqZrk6FCnj~n1kaDZxDLUEx67Lxo1JLX5Onqqdzbv9nCZuU3EYI_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at :: and follow transcript
0:00
​Hey, welcome. So in this video, basically, we'll be talking about how to create ​project sites and organization sites. ​So I'll demonstrate this in a few text. ​Let's go to our sublime text editor. So I have written a few things for you. ​So previously, remember we are still working with non custom domain. ​So we talked about the user site ​and we mentioned in the previous lesson that we can ​host a repository named ​username, ​github ​dot IO. 
Play video starting at ::38 and follow transcript
0:38
​The username is the github username ​and we can get a github page based website ​at https username, ​github ​dot IO. ​Now, apart from user site, we talked about project site and organization site. ​Now let's try to understand what our project site and organization site, ​we'll be creating both this type of site in this video. ​So in the project site, basically, ​whenever you create any repository in your user account in github ​and try to host that repository in ​github pages, it becomes a project site. ​So I have a Typo here. ​So I'll remove this one. This is not about organization. 
Play video starting at :1:28 and follow transcript
1:28
​So I'll talk about repositories ​for projects. ​So the repository can be named any repository. ​So ​let's say the name of the repository is hello Bob, right? ​And if the repository is named is hello ​Bob, ​then we'll have a github page based website ​accessible at ​username dot github ​dot IO slash ​hello ​Bob. ​So that's a project site. ​But when it comes to organization site, ​again, I'm talking about non custom domain. ​In such case, you need to create a repository which has a name, ​organization name dot github ​dot IO. 
Play video starting at :2:22 and follow transcript
2:22
​And the website will be available ​at https colon, ​double ​slash ​organization name dot github ​dot IO. So let's first create a project site. ​Let's head over to our browser in github. So here we are in the dashboard of github ​and we'll create a new repository. We'll go from here ​your repositories ​and here we have created the repository, ​bro ​dot github ​dot IO, which is helping to build a user site based on ​github pages. ​We hit the new button ​and we'll create a repository. Let's say ​the name is ​GHP, ​any ​report. So GHV stands for ​beta pages for me. 
Play video starting at :3:14 and follow transcript
3:14
​So you can name anything you like for your repository. ​And when you name this repository, it has to be a public repository ​and this time will not add anything like R me or ​gitignore or license will simply hit the ​create repository button to create the repository. ​Now, when you create a blank repository like this, ​you get a set of instructions from github. ​Now ​this time we'll do it differently rather than ​creating everything directly on the github, ​we'll be going back to our local machine on our bash terminal for Mac and Linux users. ​You can use your own terminal for ​git for bash. ​So let's head over to our git bash. ​And here we are in the bash terminal in our good old ​git ​fast directory. So we will copy the name of the repository. 
Play video starting at :4:13 and follow transcript
4:13
​We need to create a directory with the same name. ​Let's copy the name of the repository which is GHP, ​any ​report. ​And this will have us create a project based website on github ​pages. So here I'm back in the bash terminal, I'll create a directory ​with the MKDR command, ​paste the name of the repo ​and the deposit is created. Let's check ​the name of the directory and here is it ghpne ​Report ​will CD to that particular directory ​and we'll run ​a ​git ​init command to create a depository. ​Just ​it says initialized mplot ​repository in this particular directory path. ​Now we'll create an index dot HTML file with the eco ​command. So eco ​column, ​we'll use a H one tag so that the text on the website is pretty much prominent. 
Play video starting at :5:17 and follow transcript
5:17
​And we'll type this one demonstration ​of ​a ​guitar ​best ​project site ​that was a Typo. ​So we need to close the H one tag ​and ​we need to ​direct the output to index dot HTML. ​There you go hit enter ​and let's do an LS index dot HTML is created. ​We'll add it to the staging area ​just for now you note this command, what you see over here. ​This depends on the configuration, the git config ​file. ​I have not got it right. ​But this warning has nothing to do with what you are doing right now. 
Play video starting at :6:18 and follow transcript
6:18
​OK? So we have added the index dot HTML. ​Now you are ready to commit using the git commit M command dash ​M ​and the commit message is a simple one, which is initial commit ​and the commit is done. Now, we'll create a main branch. As you can see in git ​installations automatically, it creates a master branch. ​But usually these days in github, ​we have the main branch. ​So we'll create a main branch ​so that we can properly sync with the upstream repository. So ​git branch command ​aim ​dash M ​and we'll create the main branch. 
Play video starting at :7:2 and follow transcript
7:02
​And as you can see over here, it switches from master to the main branch. ​Now, I'll go back to our browser in github once more ​and we'll copy this command. ​So add the remote and finally, we'll run this command, get push ​U origin main. ​So let's get back to our bash terminal. ​And here we are back in the bash terminal, we'll add the remote ​hit enter ​and the remote has been added. Let's check what we have done ​using the git remote ​command ​dash ​V. ​And here you can see the remote has been properly added. 
Play video starting at :7:46 and follow transcript
7:46
​Now ​we need to push our changes up to the github. ​So ​git push ​U ​origin ​main ​and here we go, ​all the changes we have made in our repository has been uploaded to github. ​Now we'll go back to your browser once again. Now we are back to github ​and we refresh the browser to see what changes we have pushed ​here. You can see we have ​the ​index dot HTML and this is the initial commit. ​Now let's check the github ​actions tab. ​Now here you can see nothing has happened. 
Play video starting at :8:30 and follow transcript
8:30
​So basically when you create a user site using the repository name, ​which is github username dot github dot IO ​github automatically starts building the site. ​OK? ​Now what happens over here is that we need to go to the settings tab ​and here in the settings tab, ​we need to go to the pages ​and here in the pages you can see ​it says deploy from a branch, ​but ​it doesn't show any branch here. So this is the thing we need to do manually over here ​and you need to click this dropdown, click on main ​and automatically this one pops up. ​And here we are doing the same thing which is ​putting the index dot HTML in the root folder. ​Now, what you need to do is click the save button. ​So here you can see is github pages is currently disabled, ​select a source below to enable github pages for this repository. 
Play video starting at :9:33 and follow transcript
9:33
​So that's what you have done actually. And we will hit the save button. ​And once you hit the save button, ​you can see it says your github pages site ​is currently being built from the main branch. ​Now, we can go to github ​actions ​and here you can see that the ​action ​is already activated ​and the build and deploy process has started. ​So the build is done and the deployment is happening. Let's scroll down a bit ​and it says deploying to get ​pages and ​the deployment has been done. ​Everything is green, both on the left hand side and in the middle panel. 
Play video starting at :10:12 and follow transcript
10:12
​Now we should be able to access this repository which is a project site. ​So let's right, click ​and open link in new tab. ​And here you go, ​it says demonstration of github ​based project site. Remember we added this line demonstration of github ​based project site in the index dot HTML while we are working in the git ​bash ​terminal. Now let's see how to create an organization based website. ​Now we'll get back to our sublime text once again. ​And here you can see what happens for an organization site. 
Play video starting at :10:49 and follow transcript
10:49
​So the report or the repository that needs ​to be created is the organization name dot github ​dot IO. ​And if you create this particular repository, then you can get a github ​pages based website ​at http's ​organizationname dot github ​dot IO. ​And again, just like user site, ​you can create only a single site for that particular organization. ​Now let's get back to your browser. ​So let's close this tab ​and let's click the code tab. ​And here ​we have been working on the project site using the ghpne Report repository. ​Now let's click here ​on the profile image ​and let's click on your organizations. 
Play video starting at :11:41 and follow transcript
11:41
​And here you can see, ​I have two organizations which is Cloud HP five and TACT Publishing. ​But ​we need to create a new organization for demonstration of this lecture. ​However, I could have used this organization ​to create a repository. So let's create a new organization ​so that you understand how to create an organization. ​So this is a free one. So we'll create a free organization. ​Let's select this one and create a free organization. 
Play video starting at :12:14 and follow transcript
12:14
​Let's name our organization ​GH pages ​org ​demo, ​right? ​This should suffice. ​I'll give a contact email and it says this organization ​belongs to my personal account or business or institution. ​So we'll select that my personal account ​and we need to verify and solve this puzzle. ​So I'll solve this one ​and click, submit ​and you are done verifying your account. ​Let's select this checkbox, selecting the terms of service and click on next. ​And here we have an organization. 
Play video starting at :13:10 and follow transcript
13:10
​So we'll get back to our, ​your organization's menu. ​And here you can see the GH page org demo organization has been created. ​Let's open this organization ​and we need to create a repository over here. ​Now, here we have this thing which you are looking for create new repository button ​and let's name it GH pages, ​any ​org ​ripple, ​that's a big ​Nle. ​But this will suffice for our demonstration. ​Now, remember ​for when you try to create a depository for a particular organization, ​the private one is selected by default. ​Now, if you create a private repository, ​you will not be able to create a github based ​pages website without upgrading to the paid plan of github. 
Play video starting at :14:8 and follow transcript
14:08
​So you'll select public from here. ​We'll just add a readme for the sake of it ​and we'll create the repository ​now that the repository has been created. Let's go to github ​actions tab ​and see what happens over here. ​And you can see nothing has happened here just ​like when he created a project based website. ​So what do we need to do over here? We need to head over to the settings tab ​and from the left sidebar, we need to click on the pages menu. ​And from here, we need to manually select the branch, ​the root folder. 
Play video starting at :14:44 and follow transcript
14:44
​Obviously, it remains the same and you need to click on the save button. ​And now it says that your ​github pages is currently being built from the main branch. ​Now, let's head over to the actions tab ​and now the pages build and deployment has started happening. ​Let's scroll down, ​the build is happening. Let's wait for a few more seconds. The bill is green. Now ​the deployment has been initiated ​and we should have our site very soon. 
Play video starting at :15:16 and follow transcript
15:16
​Let's wait a few more seconds and here you go. So here the deployment has been done. ​Now, the important thing over here now ​github has given us the entire URL and we have got a organization based ​github ​page website link. So here you can see GH pages or demo. ​This was the name of the organization, ​so name of organization ​dot github ​dot IO and then the name of the repository. So the repository was, ​let's open this in link tab. Then you can remember. 
Play video starting at :15:54 and follow transcript
15:54
​OK. So here it was, it was GH pages for any ​or ​RPO. ​Now, ​it doesn't look very well because we have forgotten to add an index dot HTML file. ​So we'll go back ​to the code ​because it was displaying from the Readme file. ​So it will create a new index dot HTML file. ​The name is index dot HTML ​and we'll add in H one tag just like before. ​So this is a demonstration ​of github ​pages website ​based on ​or ​organization. 
Play video starting at :16:51 and follow transcript
16:51
​OK. ​So you're done, we'll click commit, changes, accept the default commit message ​and commit our changes. ​And of course, the bill will start again ​and here you go. ​So I'll pause the video for a few seconds ​and we'll come back when the build is done. ​So the build is done. ​It's all green. So you can open the website by right clicking ​and opening a new tab or it's already open. So we'll refresh this website. 
Play video starting at :17:21 and follow transcript
17:21
​And here you can see this says this is ​a demonstration of a github pages website based on organization ​and this was the content we had put in our index dot HTML file. ​So let's summarize once again. ​So for a user site, which you can have only one for a github based account, ​and the depository has to be named github username dot github ​dot IO. ​And the github pages website is available at https ​colon slash slash username dot github ​dot IO. ​Now, for a project based site, ​if you have a repository called Hello Bob, ​you'll be able to access your repository on a github page based website ​at username, ​which is ​the ​github user name ​dot ​github ​dot IO slash ​hello ​Bob. ​And for an organization site, ​if you have a repo, ​which is ​organization dot github ​dot IO, ​then that ​repository can be hosted at website https ​organizationname dot github ​dot IO. ​So in our next video, we'll see how to configure a custom domain for our user site. 
Play video starting at :18:46 and follow transcript
18:46
​Hope you enjoyed this lesson. See you in the next video.
