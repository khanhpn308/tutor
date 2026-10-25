# 🎥 Working with Remotes

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/Q1TuSxI1QgSRpyOvRmX83A.processed/full/720p/index.mp4?Expires=1793059200&Signature=IJFtqEE1HIDHDqjaVjqqfhAjL30PQNap66AxlFINPceKCSI1Y189ihXphyvfOOH2Hr6jSd2ZTjxOJNg4SEjVpGIO~5prKs4Tg~gtY1fABRLvBQW2WbomMp-80PAyw5BM~uPR~MhAyOeP~KjAci9tNe3tGVcxDmkHiNaefNnK0Cw_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:44 and follow transcript
0:01
When we call a git clone to get a local copy of a remote repository, Git sets up that remote repository with the default origin name. We can look at the configuration for that remote by running git remote -v in the directory of the repo. Here we see the URLs associated with the origin remote. There are two URLs. One will be used to fetch data from the remote repository, and the other one to push data to that remote repo. They'll usually point at the same place. But in some cases, you can have the fetch URL use HTTP for read only access, and the push URL use HTTPS or SSH for access control.

Play video starting at ::1:35 and follow transcript
0:44
This is fine as long as the contents of the repo that you read when fetching are the same that you write to in pushing. Remote repositories have a name assigned to them, by default, the assigned name is origin. This lets us track more than one remote in the same Git directory. While this is not the typical usage, it can be useful when collaborating with different teams on projects that are related to each other. We won't look at how to do that here, but we'll include a link for more information in the next reading. If we want to get even more information about our remote, we can call git remote show origin. There's a ton of information here, and we don't need all of it right now. We can see the fetch and push URLs that we saw before, and the local and remote branches too.

Play video starting at ::2:17 and follow transcript
1:35
For now we only have a master branch that exists locally and remotely. So the information here seems a bit repetitive. Once you start having more branches, especially different branches in the local and remote repo, this information starts becoming more complex. So what are these remote branches that we're talking about anyways? Whenever we're operating with remotes, Git uses remote branches to keep copies of the data that's stored in the remote repository. We could have a look at the remote branches that our Git repo is currently tracking by running git branch -r. These branches are read only.

Play video starting at ::3:05 and follow transcript
2:17
We can look at the commit history, like we would with local branches, but we can't make any changes to them directly. To modify their contents, we'll have to go through the workflow we called out before. First, we pull any new changes to our local branch, then merge them with our changes and push our changes to the repo. Remember how we've been using git status to check the status of our changes? We can also use git status to check the status of our changes in remote branches as well. Now that we're working with a remote repository, git status gives us additional information. It tells us that our branch is up to date with the origin/master branch, which means that the master branch in the remote repository called origin, has the same commits as our local master branch.

3:05
But what if it wasn't up to date? We'll talk about that in the next video.
