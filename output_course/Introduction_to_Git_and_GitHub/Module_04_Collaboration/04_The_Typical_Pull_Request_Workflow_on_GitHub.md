# 🎥 The Typical Pull Request Workflow on GitHub

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/mauqBaKYS46DR_N9ijhOEA.processed/full/720p/index.mp4?Expires=1793059200&Signature=cZbgFBQPe86b98KfPeFIiOeHRjEVoysbmJjU4B3Nf8LjDgQ3rtsPqx4Uu1fN3AMdxJpFPneKllq8-vq7Ee2O2YRNZKgfFXuAMJ~yM9Ptdawgg9ZlUU1AcFZG2war~XPB8im9Rjo5S6BxjGnNEX~3z4VVXSir8fG595~bNj7-~L8_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:57 and follow transcript
0:01
In our last video, we saw how to create pull requests directly on GitHub by using the web interface to edit files. This works for simple changes like fixing typos or adding documentation to a function, but it's not so great for making larger changes that we want to preview or test. To do that, we'll normally have a local copy of the repo in our computer and work with the forked repo as a remote. We'd need to use all the Git commands that we've learned up till now to do this. Let's check out this process by creating a fork of another repo. On top of the validations repo, our colleague blue-kale has created a rearrange repo, and we want to help them out. We'll go to the rearranged repo and create a fork by pressing the Fork button.

Play video starting at ::1:40 and follow transcript
0:57
It takes a few seconds to create a copy of the repo for our user. The copy will contain the current state of the repo including files and commit history. Once the fork is created, we're shown a page that corresponds to the same repo name, but it's under our user. See how it shows that it's a forked repo by stating the original repo under the name. All right. We've created a forked version of the repo on GitHub. We can now get a local copy of the repo on our computer by copying the URL and then calling the git clone command with it.

Play video starting at ::2:23 and follow transcript
1:40
We now have a new directory called rearrange with the contents of the repo. We can look at the contents by changing into that directory, enlisting all files. We can look at the commit history using our old friend git log. Now that we have a local copy of the repo, we can make any changes we'd like to it. For example, this project doesn't currently have a README.md file. Let's improve the documentation by creating that. To do that, we'll create a new branch called Add README. Do you remember how to create new branches? We do it by running git checkout -b add -readme.

Play video starting at ::3:24 and follow transcript
2:23
We can now start editing the README.md file. The MD extension indicates that we're using markdown, which is a lightweight markup language. We can use it to write plain text files that are then formatted following some simple rules. In this case, we'll start with a title with the module's name and a brief description that says it's used to rearrange names. Our README file is small, but it'll do for now, let's save it and commit it.

Play video starting at ::4:17 and follow transcript
3:24
Now, to push the change to our forked repo, we need to create the corresponding remote branch. Do you remember the command for that? Yes. It's git push - u origin add -readme. So when we push the change to the new branch, we got a message that we can create a pull request if we want to. We'll do that in a minute. First, let's check out how our file looks when rendered.

Play video starting at ::5:06 and follow transcript
4:17
Yes. Our README file rendered successfully. We're ready to create a pull request for our change. To do that, let's look at the top of the Project page. GitHub tells us that our branch is ahead of the original repository's master branch by one commit, which is the commit we just made. We can start our pull requests by clicking on the Pull Request link. As we called out, before creating a pull request, it's always important to check that the code will merge successfully. GitHub tells us that our change can be automatically merged, which is great news. If this wasn't the case, we'd need to rebase our change against the current branch of the original repo so that it could be merged.

Play video starting at ::5:46 and follow transcript
5:06
The window is showing us the TextBox where we can enter comments about our change. As we mentioned before, we should use this to explain why we're creating this pull request. This lets the person that will approve the change understand why they should merge the change into the main tree. Are we fixing a bug? This is a new feature to let the project support more use cases. How will the project benefit from including our change? Whatever info might be useful to the approver, record it here. We can also use this box to explain how the change was tested. If the project includes automatic test infrastructure, our pull request should include a test for our changes and we can state that all tests still pass.

Play video starting at ::6:37 and follow transcript
5:46
But if there's no automatic testing, then we can use this box to explain how we tested the change manually. In this case, we've just added a README file that the project was missing before. So we'll just say we're adding a README file that was missing for the project. We should also check that the change we're sending looks correct. It's always a good idea to double-check that we're sending the right change. To do that, let's look at the diff that appears at the bottom of the page. Yes, that's exactly what we want. All right. We're ready. Let's click the Create Pull Request button.

6:37
Awesome. We've created our second pull request. The number next to the name of our pull request is the identifier that's used in GitHub to track issues and pull requests. We can use this identifying number to access this pull request anytime we need it. But why would we need to access a pull request after we send it? It's pretty common for project maintainers to come back with questions, comments, or even ask us to fix our pull requests. Imagine you've just finished preparing a pull request for a great new feature, and you get a comment saying that it's missing some documentation. What would you do? We'll talk about that in our next video.
