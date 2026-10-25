# 🎥 Git Tagging: Compare, Update, Delete Tags (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/9e566df1-559a-472b-b615-988021d36dfb_c903e7f89b5e4c3eb64c36b52617c1c4_video20_4.mp4.mediaconvert/full/9e566df1-559a-472b-b615-988021d36dfb_c903e7f89b5e4c3eb64c36b52617c1c4_video20_4_WEBM_540.webm?Expires=1793059200&Signature=AKIoGx3oiDExV5fKAaaDWDXwcyU5IpX792-ci-t5P1VJBduv5gRG7VqU9O7rbofYMrLPnnuoNTg13Y-GMWILF9wXmREFpJgbN5xYyUOpd2eRasLwC9eauTQQ4~61bkRXMVr4Fr2pmMsBR6z5df23mzW3VoPsl4pqvgxky2Vr2gE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So, in this lecture, I'll talk about several aspects of git tagging. ​So number one is how to see ​the diff between two tags or in other words, how to compare two tags. ​Secondly, we'll check how to update tags ​and finally, we'll see how to delete tags. So let's check our list of tags using ​git tag. So you have several tags over ​here. Let's also execute our git log ​command. 
Play video starting at ::43 and follow transcript
0:43
​And over here you can see our commit history that we ​have built up through our several lectures in this section. ​So let me clear the screen. ​So now I'll modify the file ​index dot H TM L press enter and let's modify our title. So our title will be tag D ​demo with seven quick ​colon ​WQ. And ​let's commit ​our ​file ​index dot HTML using ​gitcommit. ​So it's an express ​commit. ​We are in the master branch, we modified the title ​and the file is index ​dot ​H TM L codes, close press enter ​and our commit is done. Now, let's create our tag. 
Play video starting at :1:30 and follow transcript
1:30
​So let's associate our tag with the latest commit. ​So in such case, the command is ​git tag, ​which is an annotated tag. ​And then our tag name ​tag name is V ​3.1 ​dot ​So V stands for version. And then we provide our tag message release 3.1. ​And let's assume that this is an alpha release. So we associated the ​word alpha with the tag name press enter and our tag gets created. ​We'll make another simple modification ​file ​index dot H TM L press enter ​will go down ​and this time we modify ​the version number of this ​Js file over here. 
Play video starting at :2:19 and follow transcript
2:19
​And let's modify to 2.8 0.3 to 2.8 0.8. ​That's a simple change will save and quit ​and we'll do an express commit. So let's retrieve an earlier commit message ​and we'll simply modify the commit ​message. ​The action we took is modified ​Js ​file version ​and the file is of course index dot HTML press enter. ​So our head position changes to this latest commit ​and will associate this commit with our new tag. ​So let's create a new tag and let's assume that this will be our beta release. ​So we'll retrieve our earlier tag command. 
Play video starting at :3:5 and follow transcript
3:05
​And in this case, ​I'll simply modify it from alpha to beta and the ​tag message will be same which is release 3.1. ​We'll simply append the word beta with it, press enter and let's now clear our screen ​and let's execute the git log ​command, press enter ​and here we are. So this was our first commit. ​And we considered this as our alpha release and this was our second commit and we ​consider this as our beta release. ​Now, we'll compare the two tags we just now created. So for that, we'll use our ​DEV ​tool so we can use P ​four moge ​for this purpose. And the command we need to execute is get ​DV ​3.1. And then alpha and next, we'll compare V ​31 ​beta. 
Play video starting at :4:3 and follow transcript
4:03
​So first we'll do ​and de ​and then you'll use a DTO ​press enter and here you are. So you can see the D ​for the file ​index dot H TM L and ​the ​deed over here ​in a similar manner, you can use the git ​de ​tool. So I retrieve my earlier command for the DEA ​and I'll simply modify it to attend the word tool and will execute ​the git de tool for the alpha and beta release press enter. ​So the left pane represents the alpha release ​and the right pane represents the beta release. ​And here is a DIIF presented by the de tool. ​So let's click now that we have examined ​the difference between the alpha and beta tags file ​and then exit. Let me clear the screen ​and let me re execute the gate log command press enter. Now I'll show you how to ​did a ​commit. 
Play video starting at :5:4 and follow transcript
5:04
​So in order to demonstrate that I'll make a ​simple change to the file 44 dot HTML press enter ​and I'll simply modify the title over here. So this is git tag update ​demo. Let's save and quit. So let's do an express commit. ​Since this is already a track file for that, we'll use a ​A and ​M option and R branch is ​master and the action we took is modified the title and the file is 404 dot HTML code, ​close press enter and the current is done. ​We'll modify the file ​index dot H TM L as well and we'll update the title over here. So this is getit tag ​update ​demo. So we'll modify the title accordingly. 
Play video starting at :5:54 and follow transcript
5:54
​We'll save and quit and we'll do an express ​this time and this time we modified the ​as well. ​And the file name of course is different which is ​index dot HTML press enter and the commit is done. ​Let's clear the screen ​and let's re execute the git log command press enter. ​So we have two new commands over here and let's consider modifying this tag ​V ​3.1 dot ​beta. ​And we will associate this tag with this commit ID, ​which is the latest or the head. ​So the command for updating our tag and ​associating it with the latest commit is Gettag. ​So a stands for annotated and then our tag name, which is V ​3.1 dot ​beta. 
Play video starting at :6:47 and follow transcript
6:47
​So we'll simply copy it and paste it at the prompt and then the ​f option. So if stands for force, so instead of ​if you can write ​force as well and then the commit ID with which you want to associate it with. ​So we'll copy the latest commit ID ​and paste it over here, press enter and here you go. ​So git has launched the default editor for the tag message ​and it has provided a default tag message as well. ​So this is pretty good and will accept this tag message. ​So I save and quit, file, save ​and then file exit. And here we are. 
Play video starting at :7:33 and follow transcript
7:33
​Git has provided the response that it has updated the tag. ​So let's clear the screen press enter. ​So I'll reexecute the git log ​command press enter. And here you can see that the tag beta has been updated. ​So it has moved over from this commit id to the latest commit id or the head. ​So next, I'll show you how to delete a tag. So let me execute the git ​command once again and let's delete a particular tag and we'll choose this tag V ​19.1. So the command for that is git tag. 
Play video starting at :8:13 and follow transcript
8:13
​Then the tag name will copy the tag name, which is V ​19.1 and paste it over here. And then you provide the ​for deleting which is ​delete press enter and git comes up with the response that it has deleted tag, V ​191. Let's clear the screen and let's reexecute the ​glog command. ​And here you are, you can't see ​the V ​19 tag anymore and you can execute the command ​git tag as well to list all the tags. And you can see ​that V ​191 tag is no more visible in the list of tags. ​So the tag has been deleted completely. ​So to summarize, we have shown you three aspects of kit tagging. 
Play video starting at :9:5 and follow transcript
9:05
​Firstly, we've showed you ​how to compare tags. And next we showed you how to update tags and finally ​how to delete tags. So with this, we conclude this lecture.
