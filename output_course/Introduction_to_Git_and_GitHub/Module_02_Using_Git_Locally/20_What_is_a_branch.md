# 🎥 What is a branch?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/a90D6mbiScyyr1Bk7f21Og.processed/full/720p/index.mp4?Expires=1793059200&Signature=GVd2WQ135NFjAbSXTvIp2Y9dTVfMARb---x8-lWBUg-Giw4~1Un7gcJZK884lSDgjAZ2YIVL0gWq5ZykXdOSEvu7yjrZH0wYBiVDDuoRovbVLHX0gkCxjblp-coZLKHPdSNg3~A2nSLvuikiDVPX4pTIVHNM23-vIX62Yeh0Kwo_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:46 and follow transcript
0:01
Up until now, we've only briefly mentioned branches. You might have seen the text on branch master and commit messages, or you might remember that we talked about branches in the context of the head pointer. Branches are an important part of the Git work flow. So we'll branch out and explore them more thoroughly in the coming videos. So what is a branch? What is it used for? In Git, a branch at the most basic level is just a pointer to a particular commit. But more importantly, it represents an independent line of development in a project. Of which the commit it points to is the latest link in a chain of developing history. The default branch that Git creates for you when a new repository initialized is called master.

Play video starting at ::1:29 and follow transcript
0:46
All of our examples and development have taken place on this branch so far. The master branch is commonly used to represent the known good state of a project. When you want to develop a feature or try something new in your project, you can create a separate branch to do your work without worrying about messing up this current working state. If this seems confusing, maybe an analogy will help. You can think of a Git project as an assignment your teacher gives you in a class. You do all your work on the assignment in a set of notebooks, each notebook representing a different branch. You use some notebooks to jot down rough drafts in experiments, but you keep one notebook, the master branch, in a tidy state and you copy the polish versions of these drafts into it.

Play video starting at ::2:11 and follow transcript
1:29
No doodling in the master notebook, please. Branches make it really easy to experiment with new ideas or strategies and projects. When you want to add a feature or fix something, you can create a new branch and do your development there. You can merge back into the master branch, when you've got something you like, or discard your changes without negative impact if they don't work out. In Git, branches are used all the time, as a part of the normal development workflow. As an example, think back to the problematic commit we fixed in an earlier video. We added a call to the disk full function, but forgot to actually define the function. So we had to roll it back because our users were seeing errors.

2:11
Knowing what we know now, we could have done that work on a separate branch, maybe called something like add disk full. In that case, we could have iterated on our code there until it was working correctly, without it affecting the master branch. Only after the code is ready to be deployed, we would merge those changes back into the master branch. In the next few videos, we'll look into how to create new branches and merge their content into the master branch. We'll also go over what to do if you run into any scary merge conflicts. Heads up, this is about to get pretty complicated. So make sure that you follow all of our exercises along in your computer and keep practicing coming up with new ways of using branches and merging, until you're comfortable with each of the steps we show.
