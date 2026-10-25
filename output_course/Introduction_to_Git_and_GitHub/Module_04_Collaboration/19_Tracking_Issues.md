# 🎥 Tracking Issues

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/vYnvCrKmSi2XkK2k0IVcAQ.processed/full/720p/index.mp4?Expires=1793059200&Signature=cJYC-n7cyh5jUbOX6bNc2otmcKrgRmI42M14b3SnxR~Zg90HXfpjFqUGrCOqTYvla3Nzpp09ok14f8TZu7nTLXF9ZioiiaQN4rX85taTj-IQwe-SC74SqkQWeY6rBWrcf6wtNH8FVAXbXAXaSdab7uJ9-XU9XF4u9-AkZVkHJB4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:45 and follow transcript
0:01
Deciding who's going to do what is critical when collaborating with others, with no coordination, two or more people might spend time working on the same part of a project while nobody works on the other critical parts. Imagine that you and your colleagues decided that you'd work on building automation software, for keeping the computers on your network up to date. But then instead of dividing the task into smaller pieces and assigning them to different people, you just randomly started working on some part of the infrastructure. The result would probably be total chaos, with different pieces of software that won't work well together, and lots of gaps that nobody worked on. For small teams, it's usually easy enough to discuss in person who's going to be working on what.

Play video starting at ::1:27 and follow transcript
0:45
But as soon as the group starts growing, talking about responsibilities and what to do next becomes more of a hassle. That's when a tool like an issue tracker or bug tracker can help us coordinate our work better. An issue tracker tells us the tasks that need to be done, the state they're in and who's working on them. The system also let's us add comments to the issue, these comments can be super helpful. They can give us more details about the problem, explain a way to solve it, or detail how to test if it's been solved. Issue trackers aren't just useful for people actively working on projects. They also let users report bugs when they come across them, even if they don't know how to solve the problem.

Play video starting at ::2:09 and follow transcript
1:27
Sometimes users come across problems that we never even thought possible. And having them report these issues through a bug tracker can help make our projects better. And the tracker can also help volunteers that want to start contributing to the project. Having a clear visible list of the pending work, lets new contributors figure out how to help and where to jump in. There are a bunch of different solutions to track bugs or issues. There's a popular bug tracker called Bugzilla, which is used by quite a few open source projects. On the flip side, platforms like GitHub have an issue tracker baked in. So, if you're hosting your project there, it can be very handy to track work on your project.

Play video starting at ::2:49 and follow transcript
2:09
Like the problems to solve, the features to add and the use cases to include it, let's check it out. This is the list of issues for our health-checks projects. For now, it only has one issue asking us to update our documentation. One of our colleagues suggested that we create a new health check that verifies if there are any critical error messages inside the system logs like current log or syslog. Errors that appear there might help troubleshoot some interesting problems. So, this sounds like a good idea for a new check.

Play video starting at ::3:32 and follow transcript
2:49
Let's create an issue for this feature by clicking on the New issue button. For the title of the issue, we'll say that we want to check for critical errors in system logs. And for the issues description we'll say that the new check should go through var/log/currentlog. And var/log/syslog and check if there are any critical errors that need attention. When writing in issues description, it's a good idea to include all the information that we have about the problem or missing feature and any ideas on how to solve it. And if new information comes up later on, it can be added as additional comments on the same issue.

Play video starting at ::4:15 and follow transcript
3:32
Great, we're now ready to submit the new issue. Okay, we now have the new list in our list of issues to solve. The issues in the list all have numbers that identify them, as we called out in an earlier video, in GitHub, each issue or pull request in a project has a unique number associated with it. So, if we have a pull request with the ID five, there won't be an issue with ID five. GitHub will automatically reference issues and pull requests and comments when we mention them using the hash tag number format.

Play video starting at ::5:15 and follow transcript
4:15
For example, if we use #2 in a comment, it will automatically reference the issue we just created. If you're fixing an issue through a pull request, it's possible to automatically close the issue directly once the code is merged. To do this, you need to include a string like closes:#4 in your commit message or as a part of the description of your pull request. Once the code gets merged into the main tree, GitHub will automatically close the issue with a message linking it to the new commit. Let's try this out by updating the documentation, like the #1 issue requested. This issue seems easy enough to fix, we need to update the README file to use the new file name and explain a bit more about how our script works. Before we start working on this, let's get the issue assigned to us.

Play video starting at ::5:57 and follow transcript
5:15
Assigning issues to collaborators helps us track who is working on what. By assigning the bug to yourself, you can let others know that you're working on it, so they don't need to. All right, let's update the documentation. So, we're still using the old name of the name file, all_checks.py, we renamed that file a while back to healthchecks.py. Let's change our README to use a new file name using inverted quotes to show monospace text.

Play video starting at ::6:42 and follow transcript
5:57
Then we'll add that the script will print everything okay, if all checks pass and it will print the corresponding error messages if something fails. We've updated the documentation, let's save the file and commit this change. This time, we'll call git comit -a so that we can edit the commit message in the text editor. We'll say that we've updated the README to use the new name of our script. And in a longer description, we'll add that we've included more info about how the script works.

Play video starting at ::7:30 and follow transcript
6:42
Finally, we'll wrap up by adding the string closes #1, so that the issue will get automatically closed once this commit is integrated into the main tree. Our commit message looks good, let's save it and push it to the repo. Now let's go back to the issue that we were addressing.

7:30
We see that our issue is automatically closed with the commit we pushed. We can click on the commit ID to see the full commit. So here's the commit message we created with the associated change. See how the #1 that we included as a part of the commit message is automatically detected as a link to the #1 issue. There's a bunch more to learn about tracking issues, but this should be enough to get you started. Feel free to experiment on your own and try more ways to interact with the system.
