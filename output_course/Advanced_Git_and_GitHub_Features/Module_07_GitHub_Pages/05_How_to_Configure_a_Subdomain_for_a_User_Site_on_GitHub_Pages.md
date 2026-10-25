# 🎥 How to Configure a Subdomain for a User Site on GitHub Pages

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/630c314e-5c1b-4d53-8626-616d0d81f83a_5ba6fd453d9149a19af75f053f206fb8_video25_5.mp4.mediaconvert/full/630c314e-5c1b-4d53-8626-616d0d81f83a_5ba6fd453d9149a19af75f053f206fb8_video25_5_WEBM_540.webm?Expires=1793059200&Signature=dPZj0cBgy6JTn6U58C9BuY2kIoAGmfYmJs0CkmA0a~H82wHEEpWyJUO3jIu~6bqZwxG0iGbkxn21pdKJcrp8Pu0t~xpgXRsVvAEmqyvtOw38un-~K3SH3sr6YwyItap-Ohrl2rOb9ei8QeZEx7gT5Bo17Cq~SvYwI6TKnDZ-TXA_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at :: and follow transcript
0:00
​Hey, welcome. ​So in this video, we'll be talking about and working on how to configure a subdomain ​for a particular ​github ​pages based website, right? ​And what is the subdomain? ​We have talked about this earlier, but this time I'll repeat it. ​So let's say you have a domain Evergreen programmer.com ​and you want a subdomain such as blog dot Evergreen programmer.com, ​right? ​So when you are talking about, let's say when you are saying blog ​dot Evergreen ​programmer.com, so blog is a subdomain of ​the primary domain or root domain, Evergreen programmer.com. ​So that's what subdomain is ​now. We'll create a new repository so we can click ​the ​big new button ​and we'll create a repository. 
Play video starting at :1:1 and follow transcript
1:01
​So let's name this repository GHP which stands for ​git pages for me. You can do anything ​such as GH or ​GP ​now ​sub domain ​dash ​demo. ​So this is the repository name and it's available ​and it will be a public repository. We'll just initialize with a Readme file. ​So you have seen that sometimes I have been initializing with a readme file. ​The reason is ​basically if you don't initialize with a readme file or ​choose any of these particular things such as get ignore ​or license, it will create an empty depository ​and you cannot create a file or you don't get that option to create a file on github. ​When you have an empty blank repository, in such case, ​you have to actually clone that blank repository ​into your ​uh ​into your local machine using git batch ​terminal and then you need to sync with the repository. 
Play video starting at :2:11 and follow transcript
2:11
​So since we are trying to do the things and demonstrate it in a much easier process, ​we'll be doing everything on github mostly because that will ​make things faster. Otherwise we have to go to the local machine ​and then you have to create a mac directory or you have to clone the ​repository and you need to sync the local ​machine with the upstream repository on github. ​So ​we have initialized with the ad ​a Readme file ​and that's it. We'll create a repository ​and the repository is created. ​Now, ​we need to add a simple index dot HTML ​because that is required to display our website. ​Now ​we'll click on this plus button, create a new file ​and the file name is index dot HTML. ​And we'll add an H one tag ​to have our font in bold and big size ​and we'll add a simple line. 
Play video starting at :3:22 and follow transcript
3:22
​Remember we are adding a single line to our website's index dot HTML because ​we don't want to spend time by stuffing the index HTML with a lot of codes. ​But if you want a beautiful site with a lot of content, you can create the necessary ​index dot HTML and write the code over here and commit the changes. ​So we'll write a simple line. ​This is ​a demonstration ​of a guitar ​pages based ​data pages website ​based on ​subdomain. ​I think we can write it together subdomain ​and we will commit the changes, commit the changes, ​accepting the default commit message ​and we have our index dot HTML ready. ​Now, if you go to index, if you ​go to actions, ​you not see anything because this is a project ​site basically and this is not a user site. ​So you need to go to settings ​and click on pages. 
Play video starting at :4:42 and follow transcript
4:42
​We'll deploy from the main branch, ​which I did earlier. And definitely you are using the root folder, click on save ​now, ​the site is currently built from the main branch. ​We have gone through this process multiple times earlier ​and you can see this circle ​are this will rotating, ​we'll click on page pages, build and deployment. ​The site is being built and deployed. ​So why this thing is happening? We talked about earlier. ​If I have not talked about it, ​basically, when you have a code base, ​you need to really ​uh and if you want to use it to ​render a particular website, you need to compile all your code ​and you need to create the package, ​bundle them together and need to deploy to a server. 
Play video starting at :5:40 and follow transcript
5:40
​In our case, it is ​github based web server, github, web server. ​And then the build and deployment happens. That's why this thing is happening ​right ​now. Also you remember that for a user site, this ​build and deployment is being done automatically. ​But for a project site or organization site, ​we need to do it manually by deploying from the branch, ​we choose and selecting the root folder or the DOCS folder and then ​clicking on save and then the build and the deploy process is initiated. ​So the build and deployment has been done. It's all green. 
Play video starting at :6:18 and follow transcript
6:18
​Now, ​what do you need to do? ​We need to configure the subdomain. So here ​we ​have provided this one. ​So it says ​github ​catalyst, ​sorry, ​high ​ticket Business catalyst.com, GHP subdomain demo, ​right? ​So this is a project site and that's why this ​was our primary domain which we configured with custom domain. ​And now this project site is displayed like this, ​but that is not our intention. ​We want it under some subdomain like blog dot he ​cut Business ​catage.com. 
Play video starting at :6:58 and follow transcript
6:58
​So this is not the thing we need. ​So we need to go to ​settings ​and then pages ​and build and deployment and we come to custom domain. ​So here we'll type blog, let's say our custom domain. It's ​uh blog dot high ​business cat.com. It can be something else. Support dot high ​ticket ​business cats.com or ​let's say ​you can think about, ​I don't know ​anything ​you would like to have a subdomain for. Now. Remember one thing ​that when you create a subdomain based website, let's say blog dot High ​Business catalyst.com, ​this is entirely a new website and this is not like, you know, ​it's a part of the main website, High ​Business catalyst.com. 
Play video starting at :7:52 and follow transcript
7:52
​This is entirely a new website. Only thing is the domain appears as a subdomain of the ​primary or the root domain for us. High ticket ​Business catalyst.com is a route to domain. And ​when I type blog dot high ​ticket business Catalyst, it becomes a subdomain. ​Let's click on save ​and let's see what happens. ​So it says the custom domain blog is not properly formatted. ​I don't know why it says that. 
Play video starting at :8:25 and follow transcript
8:25
​Let's check ​once again. ​So ​we'll type again. OK, I got it. ​We typed it as blog again only. So we need to type blog dot ​high ​Business catage.com. I'll pick it up from clipboard. ​Let's check whether ​everything is correct. Yes. Blog dot high ​business catalyst.com. 
Play video starting at :8:53 and follow transcript
8:53
​Remove this space, hit the save button ​and let's see what happens. Custom domain blog dot hi, ​Catalyst, ​blog dot hi, ​ticket ​business cats.com is saved ​now. It says DNS check in progress ​and DNS check unsuccessful. ​So this was the thing that happened in our previous ​lesson also, ​right? ​Because we have not done the necessary DNS configuration. ​So we need to head over to namecheap once again, which is my domain registrar. ​So if I have not said to you earlier, domain register is basically ​where you purchase your domains purchase your domains. 
Play video starting at :9:38 and follow transcript
9:38
​So ​it says blog dot hi ​ticket Business catage.com is improperly configured. ​So you need to go to name ​shape and you need to add a CNAME record. ​Now, earlier, I have talked about what is a CNAME record? What is the A record? ​What is a a triple record? So you will not be going through all these once again. ​So we'll head over to name ​chip ​and we'll add a new record which is AC M record. 
Play video starting at :10:9 and follow transcript
10:09
​So C in the car. ​So our subdomain is let's say block ​or it can be anything else. It can be, ​let's say ​you can write test subdomain, ​right? ​Or anything you'd like. ​But we will keep it as blog ​assuming that we are creating a blog site based on our root domain. ​And here we need to put our target. So you can see over here, ​this is the type of the record. This is the host. 
Play video starting at :10:42 and follow transcript
10:42
​This is the value we are typing in ​and this is the time to live. ​So ​our sub domain for this, the host is the blog itself ​and we need to put our, ​I think I can get it from here because I have typed this, typed it earlier. That's why ​it was in the cache. ​Now ​the 2D, ​we'll put it as one minute ​and click on save changes. ​OK? So we have saved the CM. ​So what's the next step. Can you guess? 
Play video starting at :11:21 and follow transcript
11:21
​So, the next step is to go to what's my DNS .NET ​and check whether the DNS propagation for this subdomain has been done or not. ​So I'll just copy this thing ​from, ​go ​up ​great. ​And I'll just head over to watch my DNS .NET ​and remove this ​because we need what's my DNS .NET? ​And here instead of ​WW ​high ​Ticket business.com, which was a ​itself, a subdomain of high ​ticket business cats.com, ​we are using the subdomain blog dot high ​ticket business catalyst.com. 
Play video starting at :12:11 and follow transcript
12:11
​Now, can I guess what record you need to select? ​We need to select cname because that's what ​we configured in name chip or domain registrar. ​Now, let's click, search ​it refreshes ​and you can see the propagation has been mostly done ​except in few ​domain name servers ​and ​we'll try out, let's try out whether that works or not. ​So we'll head over to get her. ​So earlier, ​it said DNS check unsuccessful because that's the point of ​time when you're not ready with the configuration of subdomain. ​And we hit the check again button ​and see what ​github ​has to say for us. It says check in progress. DNS check in progress ​and it is, ​it is saying DNS check unsuccessful. 
Play video starting at :13:11 and follow transcript
13:11
​So ​I'll pause this video ​and wait for a few more minutes before this DNS propagation is done ​and then we'll come back again. ​OK. So I'm back. ​I waited around 10 minutes before this DNS check successful message was received. ​And actually I was hitting this DNS check again button, check again button. ​So and I was also continuously going to watch my ​DNS .NET. 
Play video starting at :13:42 and follow transcript
13:42
​And I was looking for searching whether this DNS propagation has completed or not. ​So after some repeated trials, the DNS check was successful. Now, remember ​the records, I mean, the documents of these various ​domain registers or whatever you get on the internet might say that it might ​take anything between 30 minutes to 24 hours for this DN ss propagation. ​And but usually in practical terms, ​it doesn't take so much time. So sometimes it happens within a few minutes ​or it might take a bit more for me, it took almost 10 minutes to pause the video ​and come back again and continuously check for ​whether the DNS check was successful or not. ​So the DNS check is successful. Now, we'll try to see whether this enforced HTTP ​works or not. So it says domain blog is not eligible for htps as at this time. 
Play video starting at :14:46 and follow transcript
14:46
​So I'm not sure whether this will work or not because I have been experiencing this ​and force https ​not working for subdomains. ​This could be some problem with the github ​servers. ​So I'll try once again, ​hit this checkbox, but you see this is disabled ​and I'm not able to enforce HTTP, ​it says unavailable for your site because your ​domain is not properly configured for to support HTTPS ​I'm not sure why it is saying this, it says troubleshooting custom domains. ​So I'll try to troubleshoot this or maybe contact github ​support and try to understand whether ​this will work or not. ​So for now, without these https, ​but with simple http, we'll be able to access this custom domain. ​Let's see whether this works or not. ​So I'll right click here ​and here we go. So it says not secure, right? 
Play video starting at :15:50 and follow transcript
15:50
​Because we are not able to, we have not been able to enforce https. So it is only HTTP. ​So if you select this entire thing ​and copy, ​I will paste this in a editor here. You can see it is HTTP colon slash slash ​and then the sub domain. ​So ​it sounds secure. ​But if I am able to troubleshoot ​or if I get in contact with github ​support and get an answer from them, ​I'll be able to fix this and then I'll create a new video about that. ​Else we'll stop here and we'll display the subdomain site on HTTP only. 
Play video starting at :16:39 and follow transcript
16:39
​So that's all for this video. ​So I hope you enjoyed this video and the earlier video where ​we tried to configure primary domain and the sub domain for a github ​pages based website. See you in the next lesson.
