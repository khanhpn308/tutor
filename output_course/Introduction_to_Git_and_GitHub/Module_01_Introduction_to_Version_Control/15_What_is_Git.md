# 🎥 What is Git?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/ESRFoM_YSa2es9qgTI_QEA.processed/full/720p/index.mp4?Expires=1793059200&Signature=Ba5Iry1AtkERWF2OJc6NU8TojoRk4chuq6Y2kZNe1PK0MmLX68YSjMaTr76Xx0EM0ohq7mPFOYPM0Rv1V0IlJ3M9LmpM0bg2LzXvd15X28p92hq6fhX7TEH83ijGl9lnXP~Z68YUKwQug-W8eRGCJkUtsECo-e10Dn3t8edw9Mw_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:44 and follow transcript
0:01
Git is a VCS created in 2005 by Linus Torvalds. The developer who started the Linux kernel. Git is a free open source system available for installation on Unix based platforms, Windows and macOS. Linus originally created Git to help manage the task of developing the Linux kernel. This was difficult because a lot of geographically distributed programmers were collaborating to write a whole bunch of code. Linus had some requirements for the way that the system worked, and its performance that weren't being met by the VCS tools at a time. So he decided to write his own. Git is now one of the most popular version control systems out there and is used in millions of projects.

Play video starting at ::1:25 and follow transcript
0:44
Unlike some version control systems that are centralized around a single server, Git has a distributed architecture. This means that every person contributing to a repository has a full copy of the repository on their own development machines. Collaborators can share and pull in changes that others have made as they need. And because the repositories are all local to the computer being used to create the files, most operations can be done really fast. If you want to collaborate with others, it usually makes sense to set up a repository on a server to act as a kind of hub for everyone to interact with. But Git doesn't rely on any kind of centralized server to provide control organizations to its workflow.

Play video starting at ::2:11 and follow transcript
1:25
Git can work as a standalone program as a server and as a client. This means that you can use Git on a single machine without even having a network connection. Or you can use it as a server on a machine where you want to host your repository. And then you can use Git as a client to access the repository from another machine or even the same one. Git clients can communicate with Git servers over the network using HTTP, SSH or Git's own special protocol. If you're curious about diving deeper into Git architecture or communication protocols, we put a link for more information in the next reading. So you can use Git with or without a network connection. You can use it for small projects with like one developer or huge projects with thousands of contributors.

Play video starting at ::2:59 and follow transcript
2:11
You can use it to track private work that you can keep to yourself or you can share your work with others by hosting a code on public servers like Github, Gitlab or others. Are you starting to see how powerful Git can be? When looking for information online you might notice that the official Git website is called git-scm.com. And wonder what's the SCM at the end for? It's actually another acronym similar to VCS. It stands for Source Control Management. While both terms mean the same, we generally prefer VCS, because as we call that already, these systems can actually be used to store much more than just source code. In this course we chose Git for its popularity, multi platform support and robust set of features.

2:59
As with most things in the IT world, though, there are plenty of other tools that can be used to accomplish the same task. There are other VCS programs like Subversion or Mercurial. Feel free to experiment with alternatives if you think another VCS might better serve your needs. But before we jump into how to use Git, let's go through another quick quiz, to check that everything up until now is making sense.
