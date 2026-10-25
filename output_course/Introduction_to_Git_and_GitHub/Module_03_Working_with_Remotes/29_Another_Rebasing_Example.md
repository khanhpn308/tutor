# 🎥 Another Rebasing Example

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/zxSexucJToeldKWeA8lHJg.processed/full/720p/index.mp4?Expires=1793059200&Signature=g6ZeIxdDeD9y4MVD8f2MdKcpBeaE8qZLiJRvRU80NOorDnzTEUBXb9OgoVeMPFpRwwECKzgSpwos881lool15TVz8WdVmzTvXZSd6CDAK4gA2p2KM~HeA0ikdTSqtUK0KVDcyPfpJf3W7SJiHMf-k3hMzbqgG81FU7mx-4G5s00_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:44 and follow transcript
0:01
In our last video, we looked at an example use case for git rebase. Where we used it to rebase a feature branch so that it could be cleanly integrated. There are many other possible uses of rebase. One common example is to rebase the changes in the master branch when someone else also made changes and we want to keep history linear. This is a pretty common occurrence when you're working on a change that's small enough not to need a separate branch and your collaborators just happened to commit something at the same time. Let's check out how this would work in practice. First, we'll make a change to our script. Now that we've made it easy to add new checks, we’ll add a check to warn when there's no working network.

Play video starting at ::1:46 and follow transcript
0:44
There's a ton of things to check for this but for now we'll keep it simple and just check whether we can resolve the google.com URL. To do this, we'll use the socket module. We'll add a new function called check no network that will return true if it fails to resolve the URL and false if it succeeds. This socket.gethostbyname function raises an exception on failure. So we'll use it try except block to wrap the call to the function and return false when the call succeeds or true when it fails.

Play video starting at ::2:37 and follow transcript
1:46
With this new function defined, we can now add the check to our list of checks. We'll just add the name of the function and the message will be, "No working network." We've made the change, let's save it and commit it. Once more we'll use the git commit -a shortcut and pass a message saying that we've added a simple network connectivity check.

Play video starting at ::3:35 and follow transcript
2:37
We want to check if one of our teammates also made a change in the master branch while we were working on our change. In an earlier video, we showed how to do that by running git pull which will automatically create a three-way merge if necessary. In this example, we want to look at a different approach to keep our project history linear. So we'll start by calling git fetch which you might remember. We'll put the latest changes into the origin slash master branch but we won't apply them to our local master branch. We see that we fetched some new changes. This means that if we tried to merge our changes, we end up with a three-way merge. Instead, we'll now run git rebase against our origin/master to rebase our changes against those made by our colleague and keep history linear. We've got a conflict and we'll need to fix it.

Play video starting at ::4:22 and follow transcript
3:35
Git is giving us a lot of info on what it tried to do including what worked, what didn't work and what we can do about it. Since we asked it to rebase, it tried to rewind our changes and apply them on top of what was in the origin/master branch. The first commit made by our colleague, renamed all_checks.py to health_checks.py. Git detected this and automatically merged our changes into the new file name. But when trying to merge our changes with the changes made by our colleague in the file, there was a merge conflict. The output gives us a bunch of instructions on how to solve this. We could fix the conflict, skip the conflicting commit or even abort the rebased completely. In this example, we want to fix the conflict.

Play video starting at ::5:28 and follow transcript
4:22
So let's do that. We'll start by looking at the current state of the health_checks.py file. We see that while we were adding the connectivity check, our colleague was adding a check for the CPU being constrained. We want both functions and the end result. So let's remove the conflict markers, cleaning up our file. This looks good.

Play video starting at ::6:13 and follow transcript
5:28
Let's save and test our script out. So close it looks like our colleague forgot to import the psutil module. Let's do that now. Let's hope this works.

Play video starting at ::6:55 and follow transcript
6:13
We fix the conflict and our script is working again. We now need to add the changes made to the health_checks.py file and continue with the rebase. Now, the rebase has finished successfully. Let's check out the output of git log --graph --oneline to see what the history looks like at this point. We see that we've applied our change on top of the other changes without needing a three-way merge. What we did just now to resolve the conflict is very similar to what we did earlier to merge our changes.

Play video starting at ::7:38 and follow transcript
6:55
The difference is, that the commit history ended up being linear instead of branching out. We're now ready to push our new check to the remote repo. In this example, we've seen how we can use the fetch rebase push workflow to merge our changes with our collaborators changes while keeping the history of our changes linear. As we called out, keeping history linear helps with debugging especially when we're trying to identify which commit first introduced a problem in our project. We've now seen two examples of how to use the git rebase command.

7:38
One for merging feature branches back into the main trunk of our code and one for making sure that our commits made in the master branch apply cleanly on top of the current state of the master branch and it doesn't stop there. We can also use git rebase to change the order of the commits or even squash two commits into one. This is a very powerful tool but don't worry you don't need to memorize all of its possible uses, you'll learn them as you need them. Up next, we'll do a round up of some of the best practices for operating with git when collaborating with others.
