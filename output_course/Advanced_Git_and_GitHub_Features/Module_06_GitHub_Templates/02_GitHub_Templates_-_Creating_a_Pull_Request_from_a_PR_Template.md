# 🎥 GitHub Templates - Creating a Pull Request from a PR Template

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/6cdc6c0c-5a66-45de-832e-767965e1856b_b6d3785d417c4720b9ec879ef79b219c_video24_2.mp4.mediaconvert/full/6cdc6c0c-5a66-45de-832e-767965e1856b_b6d3785d417c4720b9ec879ef79b219c_video24_2_WEBM_540.webm?Expires=1793059200&Signature=KuGeHnwz5u6K~lL2s1YOhK4g9S6hYIqz6RIid6~DeYMpbvBX8vIdadSa0hrw3fCh44rDRocecAhYPVZCpy~9uFBu~nty0FSVUNrtePshqbMP73-s8qRg9tG7UueBNDtjLMgfOHSZkGw2wlhXS~9EOXmcb4CFjH7TIjlaFiHZIiA_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at :: and follow transcript
0:00
​Hey, welcome back. ​So in this video, ​we'll be working on and we'll be discussing pull request templates. ​So just like a repository template in earlier lesson, ​we can have templates for pull request. ​Now, what do we create pull request template? ​Now, a template is something which gives us some kind of basis to work with, right? ​It gives us a framework or a structure ​that helps in ease out things ​so that we don't need to ​create certain things from scratch. ​That's the advantage of a template. 
Play video starting at ::36 and follow transcript
0:36
​So when you create a pull request, ​there are certain things you need to fill out the information ​as to what it is regarding ​and what kind of things you are aiming for to achieve in this pull request. ​So you need to have some kind of template ​that makes this creation of pull request ​much easier. And so that ​the information is shared across the developers ​so that they understand what is the purpose of the pull request. ​So that's where is the utility of a pull request. ​So you are in the ​bro ​account of ​github ​and we'll be working with another collaborator which is GO ​CORS one which also has a github ​account. ​So let's create a repository first. ​And the repository name will be GH ​dash pull, request ​dash demo, ​right? Pull ​request. I think we should add the word pull, ​request template. 
Play video starting at :1:38 and follow transcript
1:38
​So pull request, template demo, GH pull request template, demo ​and it will be a public repository. ​We'll add a readme file to get started with something ​instead of a blank repository and we'll create the repository. ​So the repository is created. Now, I want to show you one thing is ​I will add first an ​simple file, ​index dot HTML. We could have done our changes with the Read me itself, but ​we'll try to make things a bit interesting. ​So I'll add an index dot HTML file ​with a simple line H two ​and then hello word. ​That's it. 
Play video starting at :2:22 and follow transcript
2:22
​We'll commit the changes. We will accept the default ​commit message ​right ​now. We'll create a new branch. But instead of ​the main account owner, ​Wero ​creating the branch will go to go ​coders one which is a collaborator for the ​repository and which has push access to the repository ​there. We will create a branch ​and then it'll create basically a feature branch. ​We will edit the index dot HTML file ​and we'll try to create a pull request and see whether ​what happens when we don't have any pull request template. ​And then after that, we'll again, try to ​initiate another pull request. 
Play video starting at :3:6 and follow transcript
3:06
​After the template, pull request, template is created right. ​So let's go to another browser ​and here you are in the browser which has ​the GO ​coders one account here you can see Google ​one account ​and this is this user is a collaborator for this repository. ​But let's first check whether this user is actually collaborator because ​we have created a new repository. And I don't think so ​that Go ​coders one is a collaborator. So we need to add ​GO coders one as a collaborator for this repository. ​Now earlier, you have seen how to add a ​user as a collaborator. ​So I will not go through this process of creating the collaborator. 
Play video starting at :3:50 and follow transcript
3:50
​Instead, I'll pause the video ​and I will come back once I add go ​codes one as a collaborator for the repository we created just now in the ​bro ​user account. ​OK? So I'm back and here you can see go ​coders, one is a collaborator for the repository GH pull request template demo. ​So I'll go back to the browser where go ​coders one account exists. ​And here we are in the go ​codes one account as you can see over here ​and you have just added as a collaborator and it says you now have push access to ​bro ​GH pull request template demo repository. ​So there you go. ​So now we'll create a new branch since GO ​code is a collaborator ​and as push access to this repository goal, coders can create a branch. 
Play video starting at :4:42 and follow transcript
4:42
​So let's say we have the branch, feature branch ​onean, right? ​We'll create this feature branch ​and now we are in the feature branch one. As you can see, ​we will open the index dot HTML. ​We will edit the file ​and we simply ​add the line, ​we'll copy this ​and paste it, ​we'll simply change it to ​three. ​OK ​H three. ​And that's all ​we will commit the changes ​and go ​codes. One has initiated ​a change within, within this repository. You will go to the code tab ​and here you can see github ​offers for comparing and doing a pull request. 
Play video starting at :5:35 and follow transcript
5:35
​So if I click on this button, I can click on this button ​or I can go to the pull request tab ​and here I can click, ​click new pull request or even click this compare and pull request, ​right? ​So we'll click this compare and pull request. ​And if you open this pull request editor, ​you can see nothing. Is there right? It's a blank template ​and you have to add a description. ​Now, had there been a pull request template? ​Adding this description would have been much easier. 
Play video starting at :6:8 and follow transcript
6:08
​I think you will appreciate this fact. ​So that's what we are after. ​So we want to create a pull request template in the ​br user account and get back to this go coders one user once again. ​So let's switch to the other browser ​and here we are. ​So go to the code tab ​and here you are. ​So ​the need is to create a dot github ​folder. ​So here we will create the file ​dot github ​folder. 
Play video starting at :6:41 and follow transcript
6:41
​So let's name the folder dot github ​and it has to be named exactly dot github. ​No other name will do. ​So this is a necessity or the rule. Then you need to create the file pool ​underscore request ​underscore template ​and the file extension will be dot MD which stands for a ​markdown file, ​right? ​So ​let's check the name of the file once again because this is very important, ​there should not be any typo and the name ​should be exactly pull request underscore template dot MD. ​OK? ​Now I'll copy paste here, a mark on copy that will make things faster for us. 
Play video starting at :7:29 and follow transcript
7:29
​And here you are, we'll paste the content ​and this is ​basically a template for a pull request, but it doesn't have to be this one. ​You can create your own pull request template, ​but I have copied this here so that we have ​something to get started with, right? ​So what does it say? ​It says what type of pr is this? So pr stands for pull requests, check all applicable. ​Then there is a task list, new feature enhancement features bug. ​Then ​there is a markdown which is titled H two equivalent. 
Play video starting at :8:8 and follow transcript
8:08
​So describe your code changes ​and then we have related feature and documents, ​then we have screenshots, recordings, link and sharepoint. ​Then here, then we have created unit test, etcetera question mark. ​Then you have another talk list. Yes, no, because they aren't needed. ​No, because I need help. ​And then you have another which is added to documentation. ​Read me dot MD wiki, no question, no documentation needed. 
Play video starting at :8:40 and follow transcript
8:40
​So these are the kind of information which if ​one adds while raising or creating a pull request, ​it becomes much easier ​for the reviewer and other developers working in a team to understand ​what does this pull request mean and what it is all about. ​So this is the markdown code ​and raw markdown rather. ​And if you see in the preview tab, ​this is what it looks ​in the formatted state, right? ​So we'll create a pull request and we'll show how to use this particular ​pull request format. ​So we covered the changes, ​accept the default commit message ​and the commit is done. We'll go to the code tab ​and here you can see the dot get ​folder ​and within it the put ​request dot MD, right? ​So now we'll go back to the go ​coders one user account and you are trying to ​create a scenario or rather a collaborative scenario, ​which is all a pool request is about because in pool request, we really work in a team ​where various team members raises the pool request ​and ​those pool requests are reviewed and then merged. 
Play video starting at :9:55 and follow transcript
9:55
​So let's go back to the other browser ​and here we are ​and we'll go back to this one, ​right? ​That's ​the change is still there ​the ​go ​CORS one user account created ​change in the index dot HTML under the feature branch one. ​So this time we'll click compare and pull request and let's ​see whether the pull request template is in action or not. ​To ensure we'll refresh the repository once again ​and we'll click compare and pull request ​and there we go. ​Look at that. ​Here we have, we don't have a blank description, text box. ​We have the ​Polar ​Quest template which the ​bro user account created, right? 
Play video starting at :10:47 and follow transcript
10:47
​So here ​let's create a Polar ​Quest. ​And here is here at the top. You can see the base is the main ​the feature branch. ​Here is a change that has been done and we will ​be able to merge these branches can be automatically merged, ​right? ​So ​let's use this one. ​And what type of ​feature is this? So let's consider this is a new feature, right? 
Play video starting at :11:15 and follow transcript
11:15
​So we'll add XX means it, ​it checks the box. Basically ​we'll go to the preview tab after we have done all the changes. ​So this is a new feature, ​we'll scroll down ​next. It says describe your code changes, right? Please do not leave blank. ​This pull ​request or PR P is an acronym for pull ​request. ​This pr ads remove fixes, replaces ​the ​feature ​bug, etcetera. So let's add this ​change, ​this pull ​request. 
Play video starting at :11:53 and follow transcript
11:53
​Since this is a new feature request, this pull request adds the ​feature, ​let's say ​log in button, ​right? ​So ​next we have related features and documents. ​Please use this format link ​issue numbers, fixes ​123. So we don't have any issue here. ​So how do we have any issue link to this pull request? ​One should mention the issue number, ​right? ​And if somebody has screenshots or recordings, you can always add, you can have, ​you can see this paste drop or click to add files. 
Play video starting at :12:45 and follow transcript
12:45
​So you can use this button to add screenshots or even recordings of video. Right? ​Then you have another checklist created unit test. Let's say yes ​and we'll put an X here so that the box is checked. ​And let's say we add it to the documentation. ​Let's say we created a readme dot MD or rather, let's say we created a wiki for this. ​So we check this box as well ​and that's it. 
Play video starting at :13:15 and follow transcript
13:15
​So ​in a real scenario, one has to be more careful. So here I did it quickly ​because this is only a demonstration. ​So we'll go to the preview tab and let's see ​here it is a new feature. ​I have not described the code changes actually. ​So once you do that actually ​and then related features and documents, screenshots and recordings. ​Here, I have checked this box created unit test ​here. I have added to documentation. Yes, I have updated wiki. 
Play video starting at :13:47 and follow transcript
13:47
​So these are all basically you're assuming you ​updated wiki and you have created unit test ​and this is a new feature now hit the button, create pull request ​right ​now. ​The pull request is created. Let's go to the pull request tab. ​Here you can see update index dot HTML, ​right? ​So we'll go back to the GO ​coders, ​we'll go back to the bi ​user ​and here ​we go to the pull request tab and here you can see ​the pull request is visible. Let's open this one. ​So the pull request has been erased by user go ​coders one ​and ​bro ​user will be the reviewer. 
Play video starting at :14:28 and follow transcript
14:28
​So it will merge the pull request, let's say ​and click on merge and confirm, merge. ​And the pull request is merged. ​So you can delete the branch as well after creating the pull request. ​But you are not demonstrating here pull request. ​The whole purpose of this video was to demonstrate ​you the effectiveness of creating a pull request template, ​right? ​Hope you enjoyed this video. See you in the next one.
