# 🎥 How to Configure a Custom Domain for a User Site on GitHub Pages

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/e7082008-009c-47d3-bd02-47a72d0b4bc8_44d0173d36a740f090f4ed889c9f3315_video25_4.mp4.mediaconvert/full/e7082008-009c-47d3-bd02-47a72d0b4bc8_44d0173d36a740f090f4ed889c9f3315_video25_4_WEBM_540.webm?Expires=1793059200&Signature=Uef29MGtAajSEF8zJdN~-N-ufJNIU7MZ15z5NgnBNytZ-DGrcbkmd1tzLmt4ALrXDvrSoeQYiHNto6HXfqVBjlCN0i0FjLfpn1J8AGRoHjvFVYFvRjo~9WCRG40J89wP0MBz~8eRfIQJB5QCDO6xsXtLsFto87XClmlzCcQ14ZE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at :: and follow transcript
0:00
​Hey, welcome. So in this video, we'll be talking about how to configure ​a custom domain for our user site. So this was our repository for user site, ​bro ​dot github ​dot IO. ​And we'll configure a custom domain so that when you access the website, ​it does not appear as https ​bro ​dot github ​dot IO, but it will be something like ​https. ​Then let's say xyzxyz.com ​and ​I have purchased a custom ​domain which is Evergreen programmer.com from Namecheap ​and we will see how to work with it. ​So let's now hit the settings tab ​and we as usual go to the pages from the left side bar ​and this has already been depart earlier. ​Now we'll go to this section which is custom domain, ​right? 
Play video starting at :1:7 and follow transcript
1:07
​So it says custom domains allow you to serve your site from a domain other than ​bro ​dot github ​dot IO ​and learn more. ​So you can click on this, learn more ​and get to see what are the information provided here, ​right? ​In fact, actually, we'll go to this particular page which is configure ​a custom domain. Then custom domains in github ​pages. ​This is the one which we need. I think ​now we need this one, manage a custom domain ​where you'll get all the necessary information. ​OK? 
Play video starting at :1:45 and follow transcript
1:45
​So let's put this aside right now. ​And ​our custom domain is Evergreen programmer.com. ​We have talked about what is custom domain earlier. ​So basically I'm repeating it. ​So a custom domain is basically ​a ​any particular custom name, for example, Evergreen ​programmer.com. So Evergreen programmer is a custom domain and it is the ​primary domain. It's not a subdomain. We'll talk about sub domain ​in the next lecture when we configure ​our ​repository for a particular sub domain. 
Play video starting at :2:23 and follow transcript
2:23
​So let's paste this ​custom domain. So it's Evergreen programmer.com. Let me scroll on the left side. ​So here you can see Evergreen programmer.com, ​right? ​So we need to hit the save button and let's ​see what happens when you click the save button. ​So here it says the custom domain. Evergreen programmer is already taken. 
Play video starting at :2:51 and follow transcript
2:51
​If you are the owner of this domain, check out this one. OK? ​So let's go. ​OK? ​So we'll try to configure the custom domain once again, ​basically got that error because I have used that custom domain, ​Evergreen programmer.com earlier ​and that's why ​it needs to be released. ​So I'll try to paste it once again ​and click on save and let's see what happens. ​So here it says the custom domain is already taken and ​I'm not able to release this custom domain for reasons. 
Play video starting at :3:30 and follow transcript
3:30
​I don't know. ​And ​I'll try with another custom domain. Which I already have. ​So let's try out ​another custom domain ​and let's hit save ​and let's see what happens. ​OK. ​This was the custom domain, which I used earlier also, ​but I don't know why it got released automatically ​anyway. ​So you saw ​what happened over here when he added the custom domain and click save button. 
Play video starting at :4:6 and follow transcript
4:06
​It was trying to check the do a DNS check ​and it now says DNS check unsuccessful. ​Now, the reason why you got this message, DNS check, unsuccessful is that ​basically we have not done any DNS configuration for this particular domain. ​So now what's DNS? So DNS stands for domain name server. ​So instead of myself explaining you what is DNS, why don't you Google ​and see what is DNS? ​So I'll Google, ​what is DNS? ​OK? 
Play video starting at :4:48 and follow transcript
4:48
​And here it says, ​what is DNS? Let's click on this link ​and let's try to understand what it says. So this is an article from Cloudflare. ​So it says the domain name system is the phone book of the internet. ​Humans access information online through domain names ​like Ny times.com or espn.com ​web browsers interact through internet protocol ​IP addresses. ​DNS translates domain names to IP addresses, ​so browsers can load the internet resources. ​So this is a key thing. 
Play video starting at :5:27 and follow transcript
5:27
​So a human cannot remember something like IP address, right, ​right. 119.101 102.85 0.74. ​Those are the kind of IP addresses and difficult to remember. ​So we have designed, the scientists have designed ​DNS or domain names which a human can easily remember. ​And these domain names under the covers get translated to IP address ​and that's the way we access various websites, right? ​Ok. Let's get over to github. 
Play video starting at :6:6 and follow transcript
6:06
​Once again, I'll bring this tab over here and remove these ones ​and here it says DNS check unsuccessful. ​So now we need to head over ​to that particular domain registrar. ​So a domain register is basically a, a ​particular application or a particular company ​where you purchase the domain and you ​do the necessary configurations for the domain. ​So I have purchased this particular domain, High ​Ticket Business catalyst.com ​in name ​chip. So I'll head over to name ​and here is the domain ​and I need to really do the configurations. ​So in domain name configurations, we add several records such as ​a ​record, ​a AAA ​CNAME record. So these are the three records we'll add for this particular domain. 
Play video starting at :7:7 and follow transcript
7:07
​And so that basically ​github ​server can identify this particular domain. Right? ​Now, we need to understand what are the various types of record. ​But before we try to understand that, ​let's start adding those records ​and then we'll try to explain what this record means. OK. ​So ​we'll do another Google ​and that is github ​pages, ​custom domain, right? ​We need to access the information from github ​and you click on this, manage a custom domain ​and we'll scroll down ​and here you can see it, gives the information ​how to create the records. 
Play video starting at :7:58 and follow transcript
7:58
​So here are the A records ​and here it is a AAA, that's the way you pronounce it. So there are four days. So A AAA ​and we need to add the CM record as well. ​So CM record ​talks about, ​I am not sure what is the CM record here. ​So we'll check later. Let's add these records first, right? ​OK. 
Play video starting at :8:29 and follow transcript
8:29
​So ​these are the four records we need to add ​in name ​chip. ​So I'll go over to Namea ​and ​I need to add the record. So it said no records found. ​And here I need to click a ​record, ​I'll add four A ​records. So I'll click on a ​record once again. ​Eight AOR eight A card ​right ​now. ​Here you need to put ​at ​symbol. So a means this particular host ​and that's how we will be adding the A records. 
Play video starting at :9:11 and follow transcript
9:11
​Now, we need to add the actual IP addresses. ​So we'll go to this particular page, ​right? Click, ​go to name chip, ​add this ​again, right? Click copy, ​add this record ​again, right, click ​copy, ​add this record ​and then right click copy ​at this IP address. ​Right now. We need to do one particular thing over here. ​We'll not go for the automatic one, ​we'll go for one minute. So TTL basically means time to leave. 
Play video starting at :9:56 and follow transcript
9:56
​So how quickly this DNS resolution will happen, ​right? ​So one minute, ​we click one minute once again ​and we'll click one minute. You could have chosen ​uh either of these things, automatic, 60 minute, ​30 minute and all those kind of things. ​But we'll try to ​quickly ​resolve these things. So we have selected one minute ​now, ​we need to click the save changes ​one by one, ​one by one ​and we have saved this changes. ​Now, what is the next step? ​The next step is to add the A records? 
Play video starting at :10:39 and follow transcript
10:39
​Don't worry, we'll be explaining what a A record, what A AAA record means. ​But let's first get these things done. ​So we'll add a AAA record. We need another A AAA. ​We need actually four of them ​and that's it. ​So ​we'll go over to this page on github ​once again ​and we'll copy all these areas, ​right? Click copy, ​right, click copy. 
Play video starting at :11:19 and follow transcript
11:19
​Let's add the rest of them ​and we have another left. ​This is the last ​A AAA record. ​OK? ​And we need to add the at symbol as usual ​at ​means the host itself. ​And then we'll configure this ​TTL to one minute as usual ​for quicker DNS resolution ​and we'll save the records one by one. ​OK? So you're done saving all the A records. 
Play video starting at :12:12 and follow transcript
12:12
​Now, we need to add the CNAME ​right ​again. Let me repeat that. I'll explain all what this record means. ​So in CNAME ​is basically we have to add ​WWW ​and then we need to add ​our user site name ​Deroy ​dot github ​dot IO. ​Ok. ​And we need to configure the TTL to one minute and see the changes ​and we are done. ​So, what's the next step? 
Play video starting at :12:54 and follow transcript
12:54
​Now, we need to go to one particular site, which is called, what's ​my DNS .NET? So we need to see whether these DNS changes we have made, ​has already propagated ​to all the DNS servers or not. But let us give some time. ​Meanwhile, we'll do a Google ​and we'll try to ​basically ​uh ​hm we'll see what are these DNS record. So let's do ​what is ​our DNS record? ​I've done it already. 
Play video starting at :13:30 and follow transcript
13:30
​Let's open ​this web site. I got a much better one. ​Let's see whether ​this gives us the necessary information or not. ​So here is a ​record. It talks about a record only, ​but I got a better sight. ​Now, this is what are DNS records. So let me check. 
Play video starting at :14:5 and follow transcript
14:05
​OK. Here it is. ​So this is a web page from Cloudfare. Cloudfare is a very well known website in ​this particular domain. ​So ​Acord says the record that holds the IP address of a domain ​and you can click this link, learn more about the AOR ​and what is a AAA record? ​The record that contains IPV six address for a particular domain ​as opposed to AOR, ​which list the IP ​four ​IP P four. ​So there are two versions of IP addresses. One is IPv4 and another is IPv6, ​IPv4 is the earlier one and IPv6 is the latest one. 
Play video starting at :14:55 and follow transcript
14:55
​And what is the CM record? ​It says forwards one domain or subdomain to another domain, ​right? ​So it's ​all about this, a ​record. A AAA and CM. ​So if you want to learn more about all these records, ​you can click on these links and learn more. ​Now, ​we need to go to what's my DNS spot net ​in order to check the DNS name propagation. ​Now, I have used once again a new term DNS propagation, right? 
Play video starting at :15:32 and follow transcript
15:32
​And let's check ​what is a DNS propagation? ​Right? ​So I think I have Googled it earlier so you can check this one itself, ​whatever Google has suggested. ​So what does DNS propagation mean? DNS propagation is the time it takes ​to update all the DNS records to be in full effect across the servers on internet. ​It says changes don't take effect ​instantaneously because name servers store domain record ​information in the cache for a certain amount of time before refreshing. ​So that's all about DNS propagation. And we'll go over to what's my ​DNS .NET ​and we'll check ​whether the propagation has been done or not. 
Play video starting at :16:24 and follow transcript
16:24
​Now, we need to check ​the DNS propagation. So we'll do a right click ​and I will just ​paste this one high ​ticket business catalyst.com ​and we'll check the propagation ​or the DNS propagation for all the records. So let's click for a first the A record ​and let's click on the search button ​and here you can see ​all the DNS servers around the world. ​So it doesn't propagate to this server. ​It is propagated to all the servers because these are green tick ​and mostly it is propagated, right? Except one server that is visible here. ​Let's check the A AAA card ​and ​this has mostly propagated except for these two server, Dortmund Germany ​seize ​Switzerland. 
Play video starting at :17:27 and follow transcript
17:27
​If you give some more time, this will get propagated fully ​and let's check the CNAME ​and this has not propagated yet. ​So I think we need to put this ​WW ​dot High ​Ticket Business catalyst.com ​and do the search. Yes. ​So you can see here. Also, most of the DNS servers ​have been synced ​with ours. ​So we'll wait for some time more. What I'll do is I'll pause the video ​and come back after a few seconds or minutes ​because I'll continue to do the search over here and to check the propagation ​and when it's all green, I'll come back and resume the video. OK. 
Play video starting at :18:18 and follow transcript
18:18
​So ​I'm resuming the video once again and it seems most of the propagation has been done. ​Barring few DNS servers here, you can see all green ​except one or two ​and we'll try out ​and go to github and check ​how it works out. ​So here ​this is the thing. ​So it says ​DNS check unsuccessful ​and check again. ​So it says both High ​ticket Business catalyst.com and its alternate name are improperly configured. ​OK, ​buddy. We have properly configured things now and ​let's see what your response is. 
Play video starting at :19:7 and follow transcript
19:07
​So let's click on, check again ​and let's see what github ​has to say. ​And it says DNS check in progress. ​Please wait ​for the DNS check to complete. ​Let's wait and Voila ​DNS check successful. ​So it's all green with a tick mark. ​Now, ​interestingly, we have these enforce https ​ticked. ​So it says HTTPS provides a layer of encryption that prevents ​others from snooping on or tampering with traffic to your site, ​right? 
Play video starting at :19:48 and follow transcript
19:48
​Whenever you access a web address on the browser, you have seen that HTTPS, right? ​And HTTPS is a secure layer of protocol ​unlike HTTP. ​And this is allowing us to check this check mark which is enforce HTTPS. So ​sometimes it doesn't allow ​because ​it requires installation of the SSL certificates. ​So when you click on this enforce HTTPS, it ​installs the SSL certificate and enforces HTTPS on this particular site ​now have already worked with this particular domain, HTTP oh, sorry, ​high ticket business ​c.com and I enforced HTTP earlier. ​That's why this time it didn't create any trouble for me. ​But normally when you try to configure a custom domain for yourself, ​you need to check this check mark ​and ​or I would say check this check box ​and try to enforce https ​and it will take some time ​because it will say something like you know ​that TLS certificate is being provisioned. 
Play video starting at :21:5 and follow transcript
21:05
​This may take up to 15 minutes to complete blah, blah, blah. ​So those are the kind of things or message you might get from ​github ​for, for us. Fortunately, ​it has been already configured earlier and that's why ​this time it didn't get any this time, ​it didn't create any trouble for us. ​Now, ​now, I would like to mention another thing is that when you click on enforce HTTPS, ​as I said, it will install a certificate ​and usually that's let's encrypt certificate. ​So if I ​Google, let's encrypt ​and this is a website ​which provides free SSL certificate. ​And github ​also uses this service for let's encrypt cert ​certificate. ​So when you click on the check box, ​which is ​enforce https, ​the github ​servers and the let's encrypt servers will talk to each other ​and let's ​encrypt will allow that SSL certificate to be installed on github ​and which will enforce https. 
Play video starting at :22:23 and follow transcript
22:23
​In turn for the website, you are to configure, you are trying to configure, right? ​So ​let's now check whether we can access our website or not. ​So we open a new tab ​and we'll ​actually ​try to access the high ​ticket ​business ​catalyst.com. ​No, ​let's check what we had on our index dot HTML. ​So that you understand what exactly will be displayed. ​So we'll go to code, ​I don't remember exactly what was ​the thing. OK. 
Play video starting at :23:6 and follow transcript
23:06
​We pasted and ​code from Chatgpt as you remember index dot HTML and styles dot CSS ​and we had a minimalist website earlier. ​So the same thing should be visible now. ​So let's hit enter ​and what ​you can see this is my pretty tiny website using git ​pages. Voila. ​So this was the thing that was visible earlier when we try to access the website https ​colon slash slash bro ​dot github ​dot I ​now that we have configured high ​ticket ​business cats.com as our custom domain. ​The same ​index dot HTML ​is now rendered for high ​ticket business cats.com. ​Now, I'll show you one particular thing ​if you try now to access ​bro.github.com. 
Play video starting at :24:8 and follow transcript
24:08
​What happens? ​Sorry, ​Dlo dot github ​dot IO. ​You see it's redirected to high ticket ​business catalyst.com because we have already ​configured the custom domain for this particular website. ​So that's all for this lecture. ​We have talked ​and we have shown ​how to configure a custom domain for a user site on ​github. ​And what is a user site? A user site is a site which is hosting a repository from github ​with our naming convention which is github ​username dot github ​dot I ​hope you enjoyed this ​video. See you in the next lesson.
