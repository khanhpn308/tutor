# 🎥 Pushing Remote Branches

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/eSFJQZa0TlOU2Czxpaw-gA.processed/full/720p/index.mp4?Expires=1793059200&Signature=F0aIaL48s-tseglKJ0Qxk3ri9cACj6PggLlmDuPLAlZ6caesrie-IaRf5ZJqlAQftbYkJ8JNmn4dHyVOMuoaC-y7ZGTNhI~7ex3sCaP3DkbMnXHrLBzZHEvwfnVTG4pw77EJ7mwFMkUaiR86tfpnfmjDci6Gx2e5vgH-sJeHm28_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:42 and follow transcript
0:01
As we called up before, when using Git to work on a new feature or a big refactor of some kind, it's recommended best practice to create separate branches. There are many advantages to doing this. For example, it might take you a while to finish a new feature and in the meantime, there could be a critical bug that needs fixing in the main branch of the code. By having separate branches, you can fix the bug in the main branch, release a new version and then go back to working on your feature without having to integrate your code before it's ready. Another advantage of working in separate branches is that you could even release two or more versions out of the same tree. One being the stable version and the other being the beta version.

Play video starting at ::1:24 and follow transcript
0:42
That way, any disruptive changes can be tested on a few users or computers before they're fully released. So let's start a new branch to work on a small refactor of our code. Do you remember how to do that? You could create the branch first, and then check it out or we can just create it and check it out with git checkout-b and the new branch name. We're ready to start working on our refactor. Let's open up the file, and have a look at it.

Play video starting at ::2:04 and follow transcript
1:24
We've noticed there's a pattern of repeating code in our all checks pi script. For each check that we call, we check if it returns true or false. When it returns true, we print an error and exit. If we add a new check, we'll have to repeat this pattern again. On top of the repeated pattern, if a computer has more than one problem, only the error for the first one will be printed. So let's refactor our code to avoid the duplication and print all relevant errors. We'll do it step-by-step making each commit self-contained. The first thing we'll do is create a function that checks if the disk is full without any parameters so it matches the pattern.

Play video starting at ::2:56 and follow transcript
2:04
This new wrapper function will pass the right parameters for us. Then we'll change the code to call this function instead. We'll also change the error message to something more accurate.

Play video starting at ::3:39 and follow transcript
2:56
We've changed the function, let's save and test our code. Awesome, it's working. Let's commit the change. We're ready for the next step in our refactor. To avoid code repetition, we'll create a list containing the names of the functions that we want to call, and then message to print if the function succeeds. After that, we'll add a for loop that iterates over the list of checks and messages.

Play video starting at ::4:56 and follow transcript
3:39
Then we'll call check, and if the return value is true, print the message and exit with an error code of one. After doing that we can delete the old code that we've already replaced.

Play video starting at ::5:42 and follow transcript
4:56
With this change made, let's save once again and tests that our script still runs. Yes, it's still working. Let's commit the new change. By now, we've re-factored our code to avoid code duplication. The current code does the same as the old code. Once we're ready to add new checks, we can do that by adding the function name and error message to the list of checks. The last change that we want to do is to let our script show more than one message if more than one check is failing.

Play video starting at ::6:26 and follow transcript
5:42
To do that, we add a Boolean variable called "Everything Ok" before the iteration. Changes variable to false if one of the checks finds a problem, and then exit with an error code only after having done all the checks. All right, one last time. Let's save and test to see if this works.

Play video starting at ::7:07 and follow transcript
6:26
Let's now do a file commit for this change. With that, we have three commits and our refactor branch. Before we merge any of this into the master branch, we want to push this into the remote repo, so that our collaborators can view the code, test it, and let us know if it's ready for merging. The first time we push a branch to a remote repo, we need to add a few more parameters to the Git push command. We'll need to add the -u flag to create the branch upstream, which is another way of referring to remote repositories.

Play video starting at ::7:50 and follow transcript
7:07
We'll also have to say that we want to push this to the origin repo, and that we're pushing the refactor branch. Whoa, that's a lot of information that Git's giving us. It's telling us if we want, we can create a pull request. We'll talk more about pull requests later on. For now, we're happy to see that a new refactor branch has been created in the remote repo, which is what we wanted. This was a super complex example that incorporated a lot of concepts that we've learned about in this course, and also carried out some interesting Python concepts. If anything is still unclear, feel free to re-watch this video and follow along in your computer until you're comfortable with these steps.

7:50
So now that our branch is pushed to the remote repo, it can be reviewed by our collaborators. Assuming they say it's okay, how should this branch get merged back into the master branch? We'll talk about that in our next video.
