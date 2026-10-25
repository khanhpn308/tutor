# 🎥 A Simple Pull Request on GitHub

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/13aboQB0RpCIpWfIg-toyw.processed/full/720p/index.mp4?Expires=1793059200&Signature=DH9EGMMaVcWupziEx0hQ0dFRnsXtc2MZ8HNkhDk6BrfZK3cIdx6Te355j8rUybcFNVCpFhwl~1zdrhYMDdOltm6rbl~DxJZoCZyw06qie311td4bKn-567Or7s~DR059gCvzn~TJ-q2bfmpkdyKXpjMwp3t9bpo-Vdo5P5AAdoQ_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:46 and follow transcript
0:01
As we called out, we can use GitHub to look at other people's code and collaborate with them. Let's see this in action by having to look at one of the projects from our colleague, blue-kale. Okay, so our colleague has created the project to include all validation functions. Let's have a look at the validations.py file. We can see the code of a function that validates username. But, if you look closely at the functions documentation, you might notice that there's a typo. We can improve our colleague's code by fixing that typo. Let's do that.

Play video starting at ::1:32 and follow transcript
0:46
We'll click on the little pencil icon which lets us edit the file directly from the web interface. We're trying to edit a file in a project that we don't have a right access to. GitHub tells us it created a fork of this project for us, which we can commit our changes to. And if we submit changes to this file, it will create a new branch so that we can send a pull request. But what exactly is a fork? Forking is a way of creating a copy of the given repository so that it belongs to our user. In other words, our user will be able to push changes to the forked copy, even when we can't push changes to the other repo. When collaborating on projects hosted on GitHub, the typical workflows, first, create a fork of the repo, and then work on that local fork.

Play video starting at ::2:15 and follow transcript
1:32
A forked repo is just like a normal repo, except Github knows which repo it forked from. So we can eventually merge our changes back into the main repo by creating a pull request. A pull request is a commit or series of commits that you send to the owner of the repository so that they incorporate it into their tree. This is a typical way of working on GitHub, because in most projects, only a few people have commit rights to the repo. But anybody can suggest patches, bug fixes or even new features by sending pull requests that people with commit access can then apply. Typically, the owners of the repo will review the changes before merging them.

Play video starting at ::2:55 and follow transcript
2:15
Checking that they match the development guidelines for the project and that the license is valid and so on. Let's fix the typo in the file to see what the pull request looks like. Once we're done making changes to the file, we can make a change proposal, by scrolling down and filling in the description of the change. In this case, we fix the typo in the function documentation. Clicking on the Proposed file change button, we'll create a commit in our forked repo, so that we can send the change to our colleague.

Play video starting at ::3:47 and follow transcript
2:55
Let's do that now. We've created a commit on our forked repo. But we haven't yet created the pull request that will send the changes to the owner of the original repo. On this screen, we can see a lot of information about our change. We can see what repositories and branches are involved in the creation of the pull request. We can also see that GitHub automatically created a branch called patch-1 for us. And that our change can automatically be merged, yay, no conflicts. This window also lets us review the change before we create an actual pull request. Once we're ready, we just click the Create pull request button.

Play video starting at ::4:34 and follow transcript
3:47
This opens a text box where we can enter comments about our change. In this case, a change is really simple, we just fixed the typo so there's nothing extra to add. If we were suggesting a more complex change, we could use this text box to provide more context. The checkbox at the bottom lets us allow edits from maintainers. This can be useful for example, if by the time a project maintainer gets around the merging or change, there's been more commits and our change needs rebasing. By allowing edits, the maintainer can do it themselves instead of asking us to do it, less work, yes please. Okay, we're ready, let's click Create pull request.

4:34
Cool, we've created a pull request with our change. Our colleague can now look at it and decide whether they want to merge it to the project or not. In this video, we checked out the simplest way of making pull requests, which is doing them directly through the GitHub interface. By using this workflow, you can already start contributing to projects on GitHub. Up next, we'll see how to do more complex pull requests.
