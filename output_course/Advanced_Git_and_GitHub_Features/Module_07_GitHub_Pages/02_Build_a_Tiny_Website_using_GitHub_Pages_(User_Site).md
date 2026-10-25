# 🎥 Build a Tiny Website using GitHub Pages (User Site)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/dc84492e-fbcb-49b2-b7ae-a97f9886fcff_4ced7f64bd6946c285b22b35d8346df8_video25_2.mp4.mediaconvert/full/dc84492e-fbcb-49b2-b7ae-a97f9886fcff_4ced7f64bd6946c285b22b35d8346df8_video25_2_WEBM_540.webm?Expires=1793059200&Signature=bbuVB1upezhbP4qbvISpwraQeydomkJ0XvFt5VyU8wNreYiRo92-eH89MMIBcH6T9vCWpfVtxaDGcyqPQYC3VMxoFsANu4oqU-SQkig3JYrr7EeFF8AIRBpvVCjhReX~AHamObNWAcJZhJ~wvqyL0-L1lQrlF2CY7lR0-asltFA_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at :: and follow transcript
0:00
​Hey, welcome to this lesson. ​So in this lesson, we'll be actually creating a tiny website based on github ​pages. ​So you're in the dashboard, as you can see over here, ​we'll click this big green new button to create a repository. ​Now, let's scroll down and see what will be the repository name. ​Now, the name of the repository will be ​bro ​dot github ​dot IO. ​Now you might ask this particular question, why this specific name? ​Now, as we recall in the previous introductory lesson on git pages, ​we talked about three types of website. 
Play video starting at ::41 and follow transcript
0:41
​One is the user site ​and one is organization site and the third is project based site. ​We are talking here about the user site ​and you can have only one user site with the name, ​bro ​dot github ​dot IO ​that will allow ​you to host a website based on ​github pages. Now, let's show what I mean by this in the description. ​So if you type the URL https ​colon slash double slash ​and then bro ​dot github, ​github ​dot IO, you'll be able to access whatever HTML artifacts ​you host in this ​repository as your github pages website. ​Now, let's remove this ​and let's go ahead and create this website. ​So this repository will be a public one and not a private one. ​We'll be mostly working with public repositories ​that is allowed by the github's free version. 
Play video starting at :1:50 and follow transcript
1:50
​And we'll initialize with a readme file. This is not necessary, ​but we'll just for the sake of it, add a readme file. ​We'll ignore gitignore file and license. Now, I'll hit this big ​create repository button ​and create the repository. Now, here, the depository has been created. ​Now, we'll create a index dot HTML file. Now why an index dot HTML file? 
Play video starting at :2:19 and follow transcript
2:19
​Basically when you create a website ​and if you create an index dot html file, ​which is available at the root folder of the website, ​then automatically browser displays that ​particular file or renders that HTML file. ​That's why we'll create an index HTML file and that's ​the way usually the default behavior of the web servers. ​So we'll create this plus button ​and create new file. ​Now, let's create an index dot HTML file. So the name of the file will be index dot HTML ​and we'll simply just ​add a single line. We'll create a very simple site that displays a single line. ​So we'll make the font ​here big. So that's why I'm adding the H one tag, ​which is the HTML tag. So H one will display it in the highest size. 
Play video starting at :3:22 and follow transcript
3:22
​So there are other HTML tags if you know it already H two H three H four, ​they are gradually decreasing in size. ​So basically we'll type here hello ​github ​pages ​and that's it. ​That's it we need for now and we'll commit the changes. ​We'll accept the default commit message ​and hit the green commit changes button. ​And the changes have been committed right now. ​Let's go to this particular tab actions tab ​and in the actions tab, ​we click these pages build deployment here. ​You can see github is deploying this website ​and before deploying it is building the website. 
Play video starting at :4:10 and follow transcript
4:10
​So here you can see a rotating ​w and it's green now. So the ​has been happened now. It is creating the report build status ​and at the same time deploying to github ​pages. So it's green and when it's all green, we'll try to access the website ​and here it's all green. Here. You can see ​and ​now we can ​display the website. ​But before that, I want to show you one particular thing, ​let's click this settings tab ​and let's go in the left sidebar and click on pages ​and let's scroll down a bit. 
Play video starting at :4:52 and follow transcript
4:52
​And here you can see the build and deployment how it is happening basically. ​So deploy from a branch, which is definitely the case for us, ​we are not deploying directly from ​github ​actions ​because this is best for using frameworks ​and customizing your build process. ​We are accepting the simple option which is deployed from a branch. ​And here you can see the main branch, which is the default branch created by github. ​There are no other branches over here ​and ​deploying from the root folder. We can also deploy from the docs folder ​for that. You have to create a Docs folder. 
Play video starting at :5:31 and follow transcript
5:31
​We'll try to create a project, ​simple project by trying to deploy a website from the docs folder. ​But for now, it's deployed from the main branch and from the root folder. ​And remember we have our index dot HTML file in the root folder. Now, here ​it says your site is live at https ​slash bro ​dot github ​dot IO. So let's click the right tab and open this site in link ​in new tab. ​So here you can see, ​bro ​dot github ​dot IO is the address ​in the address bar and ​and hello ​github pages has been displayed. ​So congratulations. 
Play video starting at :6:18 and follow transcript
6:18
​You have been able to create a very tiny website with a single line on ​github ​using the feature ​github ​pages. ​Now let's get back to the repository. ​We have created a very simple bare bones website. ​We'll try to beautify this site a bit, ​so we'll go to Chatgpt ​and try to do some magic. So here is a Chatgpt ​and ​we type a simple message. ​The message is give me ​now, this is called a prompt and not message. My apologies, ​the code ​for a simple but pretty index dot HTML ​for a simple ​but pretty ​index dot HTML. 
Play video starting at :7:22 and follow transcript
7:22
​The HTML code and CSS should be in separate files, ​the HTML code ​and the ​CSS ​should be ​in separate files. ​Let's hit enter ​and here Chatgpt is working out its magic. ​So we have the index dot HTML as you can see over here ​and we have the styles dot CSS ​and Mr Chatgpt is done. ​So it says that you can save the HTML and style dot CSS ​in the same directory and open the index dot HTML in your browser ​to see the result. ​OK? ​Now ​we'll copy this ​code ​of index dot HTML ​till here, right? Click copy. 
Play video starting at :8:27 and follow transcript
8:27
​We'll go to github ​and we'll hit the code tab, ​we'll click index dot HTML, ​click the edit this file button ​and we'll remove this existing line of code ​and paste whatever chat GP D has given us. ​We'll do some simple editing. ​So here the editing is, let's say ​welcome to github ​pages, right? ​That will be a good message. ​Welcome to good ​pages. ​Now, this title will appear here, right? ​As you can see ​and ​here we'll change, do a simple change. Let me see where to make that change. 
Play video starting at :9:17 and follow transcript
9:17
​And here it should be the case. Each one, ​ok? ​I'll change this one a bit. We'll type here. Welcome ​to get her pages. ​We'll change this ​title over here ​and now in each one, ​which will be the main ​line in the guitar pages will type ​this is ​my pretty ​tiny website ​using ​get ​up ​pages, write dot and Voila ​and we are done. Now, you'll hit the commit changes button ​and commit our changes. We update the index dot HTML, access the default ​commits ​button. Now the commit is done. 
Play video starting at :10:16 and follow transcript
10:16
​We have still one work to do, which is create a styles dot CSS page, ​right? ​So we'll hit this plus button, ​not this one, we'll go to the code ​once again ​and ​we click this plus button, create new file ​and the file name is styles ​dot CSS. ​We'll head over to Chatgpt. ​Once again, we have copied already ​the index dot HTML. Now it's time to copy the styles dot CSS. ​And let's check whether we have selected the entire thing. Yes. 
Play video starting at :10:57 and follow transcript
10:57
​Right. Click copy here. Head over to github ​and simple paste, ​right? ​That's all. ​Now hit the commit changes button, accept the default commit message, ​hit the commit changes button ​and the commit is done. ​And let's see what is happening in actions. ​And here ​you can see actions is working hard for us to build and deploy. 
Play video starting at :11:23 and follow transcript
11:23
​Let's wait, let's turn everything green. ​The build is happening 11 seconds, 12 seconds. ​As you can see everything has been displayed ​and ​now the report ​is to be ​done. ​The circle is wearing ​the deploy is happening. ​The port is green now ​and the deployment is done ​and now voila. ​So we'll actually ​open the website from here. ​You can as well refresh the page over here or ​you can simply right click and open a new tab. 
Play video starting at :12:1 and follow transcript
12:01
​Let's refresh the page. ​Ok. So that site doesn't seem much pretty. ​Probably you have done some wrong copy pasting here. ​Something is appearing which is not desirable. Let's check our files once again. ​So here I'm in the index dot HTML. Let's scroll down. 
Play video starting at :12:20 and follow transcript
12:20
​I think some inadvertently things happened. ​So this is not supposed to be here. I need to edit this ​one ​and I'll remove this extra bit of code. ​So here it is, ​let's remove this one ​and we have the ​closing HTML tag and the opening STML tag over here. ​Let's commit the changes ​and we're done. Let's look at styles of CSS over here on the left side bar ​and let's see whether it looks all good or not. ​Since all good ​will not do any changes over here. 
Play video starting at :13:8 and follow transcript
13:08
​Let's refresh the page. ​But before that, we'll inspect actions, ​whether the deployment has been done or not, ​it's not ​github ​is still ​working on it ​and the reporting is happening ​and the deployment is still continuing ​and let's wait a few more seconds ​and, ​and it's done. ​So let's go to this tab, ​refresh the page once again. ​Now it looks much better, not much pretty though, ​but much better than the first version, ​which is looking very empty and bare bones one. ​So here in this lesson, we have learned how to create a github ​pages based website ​and which is basically a user site, creating a repository with the name, ​bro. Dot github ​dot IO ​and which is ​accessible accessible at the website URL https ​colon slash ​slash bro ​dot github ​dot IO. ​So I hope you enjoyed this lesson. See you in the next video.
