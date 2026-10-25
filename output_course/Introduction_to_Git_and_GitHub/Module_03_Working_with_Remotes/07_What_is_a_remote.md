# 🎥 What is a remote?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/PuLKf8VOR9655WH-xacS1A.processed/full/720p/index.mp4?Expires=1793059200&Signature=N-beExI341MSepUSWWwRTRSQPxlRRO73MTS6pGv2bfZppJjvCEzYmVM8vXUOjEOSWcKLQHbmtuPylCfwjDQQK4KgUOeftiUpq6ip8wYSh6dlTjpbuSw8HhP4J13ZjmKbmzku0EQ8YDKJU5TIjcNwaq~ZZw5BxoXt3bw0LM3e8OI_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:46 and follow transcript
0:01
When we clone the newly created GitHub repository, we had our local Git Repo interact with a remote repository. Remote repositories are a big part of the distributed nature of Git collaboration. It let lots of developers contribute to a project from their own workstations making changes to local copies of the project independently of one another. When they need to share their changes, they can issue git commands to pull code from a remote repository or push code into one. There are a bunch of ways to host remote repositories. As we called out, there is many internet-based Git hosting providers like GitHub, BitBucket or GitLab which offer similar services.

Play video starting at ::1:38 and follow transcript
0:46
We can also set up a Git server on our own network to host private repositories. A locally hosted Git server can run on almost any platform including Linux, mac OS, or Windows. This has benefits like increased privacy, control, and customization. To understand remote repositories, and Git's distributed nature a bit better, imagine you're working together with some friends to design a computer game, each of you has a different portion of the game you're responsible for. One person is designing the levels, another the characters while others are writing the code for the graphics, physics, and gameplay. All these areas will have to come together into a single place for the final product. Although your friends might work on their parts by themselves, from time to time, everyone needs to send out progress updates to let each other know what they've been working on.

Play video starting at ::2:24 and follow transcript
1:38
You will then need to combine their work into your own portion of the project to make sure it's all compatible. Using Git to manage a project helps us collaborate successfully. Everyone will develop their piece of the project independently in their own local repositories, maybe even using separate branches. Occasionally they'll push finished code into a central remote repository where others can pull it and incorporate it into their new developments. So how does this work? Alongside the local development branches like master, Git keeps copies of the commits that have been submitted to the remote repository and separate branches. If someone has updated a repository since the last time you synchronized your local copy, Git will tell you that it's time to do an update.

Play video starting at ::3:08 and follow transcript
2:24
If you have your own local changes when you pull down the code from the remote repo, you might need to fix merge conflicts before you can push your own changes. In this way Git let's multiple people work on the same project at the same time. When pulling new code it will merge the changes automatically if possible or will tell us to manually perform the integrating if there are conflicts. So when working with remotes the workflow for making changes has some extra steps. We’ll still modify, stage and commit our local changes. After committing, we'll fetch any new changes from the remote repo manually merge if necessary and only then will push our changes to the remote repo.

Play video starting at ::3:48 and follow transcript
3:08
Git supports a variety of ways to connect to a remote repository. Some of the most common are using the HTTP, HTTPS and SSH protocols and their corresponding URLs. HTTP is generally used to allow read only access to a repository. In other words, it lets people clone the contents of your repo without letting them push new contents to it. Conversely HTTPS and SSH, both provide methods of authenticating users so you can control who gets permission to push. If all this protocol talk is making your head spin you might want to review the video on the subjects made by my colleague Gian.

3:48
You'll find the link to this in the next reading.The distributed nature of the work means that there are no limits to how many people can push code into a repository. It's a good idea to control who can push codes to repos and to make sure you give access only to people you trust. Web services like GitHub, offer a bunch of different mechanisms to control access to Repositories. Some of these are available to the general public while others are only available to enterprise users. By now you have an idea of what a remote repository is and how it interacts with local Git repositories. Up next, we'll dive into some of the commands that let us interact with remotes.
