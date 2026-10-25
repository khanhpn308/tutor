# 🎥 Git Tagging: Determining Tag Type (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/49b2f21b-c8ce-42af-9679-a55c8765faf2_696234559c6c4074b4b2dd230475a9b2_video20_2.mp4.mediaconvert/full/49b2f21b-c8ce-42af-9679-a55c8765faf2_696234559c6c4074b4b2dd230475a9b2_video20_2_WEBM_540.webm?Expires=1793059200&Signature=TnKR3Afd9PbrKit7mkXa1cpl6dOGgLwjBDpZMMFSXJGESn2pDBo04ogh2YdKI0JK3UDqSAROnQ4uGW-4FIEMwaThze4eYDTzMho1QutOEpE3rEl0CPKftCBkbbEFcdE5HGqxY7I9rBwE5nOKhDU7eUP3rLdArLw9uM0gwRjVizY_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​Now, ​I'll show you how to determine whether a tag is a lightweight tag or an annotated tag. ​Now, there are two ways in which you can do that. ​So let's execute the git log command that ​may retrieve an earlier command press enter. ​Now, ​there are seven tags approximately over here. ​And in a ​real life scenario, ​there can be more than hundreds of tags ​and you may want to determine ​what type of a tag, a particular tag is. ​So let's examine what type of tag is this particular tag, which is V ​19 ​RC two. 
Play video starting at ::54 and follow transcript
0:54
​So let me clear the screen so you can simply do get show and ​then you paste the name of the tag press enter and here you go. ​So if the tag is an annotated tag, ​then you'll be able to see certain information which are not really ​visible when you execute the git show command for a lightweight tag. ​So when you see information like this, ​like tagger and the order in which the information is displayed, ​you can be assured that this is an annotated tag. ​However, there is another way to do that. So let me clear the screen. ​So if I execute the command ​git cat ​file space ​T and then the tag name. ​So let me paste the earlier tag name which we examined, which is ​V ​19 ​RC two. Now let me explain what the command means. 
Play video starting at :1:56 and follow transcript
1:56
​So the command cat file provides size ​or type information about a particular git object. ​And the ​T actually indicate it's getit that we want the type information for the git object. ​Now here the git object is a tag object which is V ​19 ​RC ​two. So let me press enter. So if the execution of the command git cat ​file ​T ​and then the tag name produces an output which is tag, then you can be pretty much sure ​that the tag is an ​annotated tag. So let's examine another tag with the same command ​git cat ​file. ​So get ​cat ​file ​and then let's provide the tag name. Now here I'll examine the tag ​V ​18 ​RC, one press enter. 
Play video starting at :2:59 and follow transcript
2:59
​And here you are. Now, if the execution of the command get cat ​file ​T ​and then the tag name ​provides an output which is commit, ​then you can be pretty much sure that the tag is a lightweight tag. ​So let's summarize if the execution of the command ​git cat ​file ​T produces an output, which is tag, then you can be pretty much sure ​that the tag is an annotated tag. ​And if the output is commit, ​then you can be pretty much sure that the tag is a lightweight tag.
