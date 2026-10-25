# 🎥 Git Rebase Introduction (Lab)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/66b4c670-ef3d-4cfe-a28d-66bca8d0bdd6_35c0a92636c34cdfb2eac318b0801ed9_video19_2.mp4.mediaconvert/full/66b4c670-ef3d-4cfe-a28d-66bca8d0bdd6_35c0a92636c34cdfb2eac318b0801ed9_video19_2_WEBM_540.webm?Expires=1793059200&Signature=Un~phVS2HPB9B-jaeyHMrn6bVS9MmZD1VD3jWnwmDMJGyNESLsX~SJEl1xHmIxRMHQHlT5nfhy4K8OXQcXdQN7bHiqLOixoCEpD7OdqXrzpPfRgyuEFm9yZ~9HD3F3MAA51FBT9zWAw8LhvlHoiyQclC7~ZVRc57dtb-3YlbmOI_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

Play video starting at ::10 and follow transcript
0:10
​Hi, welcome. ​So in this lecture ​I will discuss about ​git rebase. ​So what's ​git rebase? ​Rebasing is the process of moving a branch ​to a new base commit. So let's explain this using a diagram. ​Well, you can see over here a mass branch ​and all these are commits ​related to the master branch. ​And here is a feature branch ​over here ​and these are the comments related to the feature branch. 
Play video starting at ::47 and follow transcript
0:47
​This is the head for the feature branch ​and this is the head for the master branch. ​So as I said, ​rebasing is just ​changing the base. Basically we ​rebase a branch. So this is the branch over here and the base commit for this branch ​is C two. ​So let's see what happens when you ​ate feature branch. ​So here you go. ​So here is the feature branch now ​and here are the commits related to the feature branch. 
Play video starting at :1:28 and follow transcript
1:28
​And the base commit for this feature branch ​is now C four ​instead of C two. ​So the base has changed from C two ​to C four. ​So that's what rebasing is ​now. ​From a content perspective, ​rebasing really is just moving a branch from one commit. ​To another. But internally get ​accomplishes this by creating new comments ​and applying them to the specified base. ​So ​it's literally rewriting your project history. 
Play video starting at :2:6 and follow transcript
2:06
​It's very important to understand that ​even though the branch looks the same, it is composed of entirely new comets. ​So here it is ​K one and K two are entirely new comets. ​So if I rewind in the diagram, you can see B one and B two where the comets over here. ​And when I rebase ​the particular branch ​or the feature branch, two entirely new comets, K one and K two are generated. ​Now let's get back to a terminal. Now let's create a branch using ​git checkout ​B option ​and let's name it feature branch ​and we have switched to our feature branch. ​Now, the git ​rebase command looks something like this ​git ​rebase ​and then base. So the command says that rebase the current branch onto base. 
Play video starting at :3:10 and follow transcript
3:10
​So the current branch is a feature branch as you can, you can see over here. ​And the command says rebase the current branch on the base. ​Now this base can be any type of commit reference. ​It can be an ID, ​it can be a branch name, ​it can be a tag ​or a relative reference to head. ​Now, don't worry, ​I'll talk about tags in subsequent sections. So here, Jolly, well, instead of base ​I can write here, ​git rebase master. Now, the primary reason for rebasing ​is to maintain a linear project history. 
Play video starting at :3:53 and follow transcript
3:53
​So let me get back to the diagram to explain you what I mean by this ​right now, as you see in the diagram prior to rebasing, ​there is not a linear path from C four to B two. ​Rather the path is something like this. ​So the reason is after the creation of the branch, ​the master has already progressed in terms of commits. ​So the path is not linear over here. So once I do a rebase, ​I clearly have a linear path from C four to K two. ​So that's the concept of rebasing. ​And with this, we conclude this lecture.
