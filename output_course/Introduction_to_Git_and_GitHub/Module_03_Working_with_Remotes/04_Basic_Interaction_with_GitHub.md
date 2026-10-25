# 🎥 Basic Interaction with GitHub

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/H44D8nawQBOneH6Y1dXdng.processed/full/720p/index.mp4?Expires=1793059200&Signature=ReJqqNrUtIKF0iZSiaFUzJv3cOVWk5SOLrYtkMBo9QhjlS9stfHRTQi7Q5Fu00N-IFFTHmB8I1OH9G4OpqqCvarL6w9sJwJlDQ1uIDJBrPOL3sjyFZUIorvgaRcCQnGAyFe3dYoi6aItOOferuzY3mqQNpW4-8dppyRZiyt~fB8_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:43 and follow transcript
0:01
As we called out, GitHub is an online service. To use it, you first need to create an account on the site. Once you have your account, you're ready to create your brand new repository on GitHub. Let's do this now. Going step-by-step. We'll start by clicking the Create a repository link on the left. This will take us to the repo creation wizard. The wizard is pretty straightforward. The first thing we need to do is give a name for our repo. We'll call this repo health checks.

Play video starting at ::1:27 and follow transcript
0:43
After that comes a description of what the repo will be used for. We'll say that'll be used for scripts that check the health of our computers. Then we need to select whether we want the repo to be public or private. We'll go with private for now. Finally, the wizard can help us get started with some few initialization files like a README, a gitignore, or license file. We'll go with just the README for now, and then create the repo. Yeah. Using the wizard, we created the repo and have a fresh remote repository ready to go. Just like magic. Let's get to work. First step is to create a local copy of the repository. We'll do that by using the git clone command followed by the URL of the repo.

Play video starting at ::2:10 and follow transcript
1:27
GitHub conveniently lets us copy the URL from our repo from the interface so that we don't have to type it. We're now ready to clone the repo into our computer. We'll do that by calling git clone and paste in the URL we copied. To do this, GitHub will ask for our username and password. Just like that, we've downloaded a copy of the remote repository from GitHub onto the local machine. This means that we can perform all the git actions that we've learned up till now.

Play video starting at ::3:04 and follow transcript
2:10
Since the repo is called health checks, a directory with that name was automatically created for us and now has the working tree of the Repository in it. So let's change that directory and look at the contents. Our repo is basically empty. It only has the README file that GitHub created for us. This file is in a special format called markdown. Let's add a bit more content to it.

Play video starting at ::3:46 and follow transcript
3:04
We've changed this file. What do we need to do now? We need to stage the change and committed. We've seen a couple of different ways to do that. Let's use our shortcuts to do this in just one command. Okay. We've modified our README file. But we've seen all this before. We got to a remote repository set up on GitHub. So let's use it. We can send our changes to that remote repository by using the git push command which will gather all the snapshots we've taken and send them to the remote repository. In this case, we've only taken one snapshot.

Play video starting at ::4:30 and follow transcript
3:46
We'll talk more about what's going on behind the scenes with git push and remote repositories in later videos. But the mechanics are pretty simple. To push our modified README up to GitHub, we'll just call git push. Once again, we're asked for our password. After that, we see a bunch of messages from git related to the push. When we access our project, we see the contents of the README file. So if we check our repository on GitHub, we should see the updated message. Pretty cool, right? We've taken the local changes on our computer and pushed them out to a remote repository hosted on GitHub.

Play video starting at ::5:12 and follow transcript
4:30
You've probably noticed that we had to enter our password both when retrieving the repo and when pushing changes to the repo. There are a couple ways to avoid having to do this. One way is to create an SSH key pair and store the public key in our profile so that GitHub recognizes our computer. Another option is to use a credential helper which caches our credentials for a time window so that we don't need to enter our password with every interaction. Git already comes with a credential helper baked in. We just need to enable it. We do that by calling git config - - global credential.helper cache.

Play video starting at ::5:52 and follow transcript
5:12
Now that we've enabled the credential helper, we'll need to enter our credentials once more. After that, they'll be cached for 15 minutes. To check this, we can try another git command, git pull which is the command we use to retrieve new changes from the repository. We'll enter our credentials on the first call to the command and they'll be cached, so we won't need to enter them again. With that, we've seen how to create repositories on GitHub, clone our remote repository, push changes to it, and pull changes from it.

5:52
There's a lot going on behind the scenes here and we'll dive deeper into the details and more collaboration techniques in later videos. For now, check out the next reading for a summary of this basic workflow. Then there's a quick quiz to make sure this is making sense.
