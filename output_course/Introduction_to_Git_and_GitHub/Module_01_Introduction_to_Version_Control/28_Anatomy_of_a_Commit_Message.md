# 🎥 Anatomy of a Commit Message

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/4am3srpkSFWCvlp4TQH6_g.processed/full/720p/index.mp4?Expires=1793059200&Signature=Ob-u8V4eWRFK7GBVdDDP446cz6VLofYhtpcClnupmyzkUHfNd-h0duI~dTEBsQnJkpuq9PyH-XifzYDm-NdTEdRDo4MoFN2nIsfnly4WzICuno3XsePLPMRsJaVq0VfJDA9aPBA1VObxGqKeZeS4SNTbkCu5sLw1U6Pn12WNcvc_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:58 and follow transcript
0:01
In earlier videos, we saw how we can commit snapshots of changes to the Git repository. Let's now talk a little bit more about what makes a good commit message. Writing a clear informative commit message is important when you use a VCS, future you or other developers or IT specialists who might read the commit message later on will really appreciate the contextual information as they try and figure out some of the parts of the code or configuration. So what makes a good commit message? It can be helpful to keep your audience in mind when you write commit messages. What would someone reading a message weeks or months from now want to know about the changes you've made? What might be especially important or tricky to understand about them? Is there extra information that might help the reader out, like links to design documents or tickets in your ticketing system? Similarly to how style guides exist for writing code, your company might have specific rules for you to follow when you write commit messages.

Play video starting at ::1:41 and follow transcript
0:58
Even if they don't, it's good to use a few general guidelines to make sure your commit messages are as clear and useful as possible. A commit message is generally broken up into a few sections. The first line is a short summary of the commit followed by a blank line. This is followed by a full description of the changes which details why they're necessary and anything that might be especially interesting about them or difficult to understand. When you run the git commit command, Git will open up a text editor of your choice so you can write your commit message. A good commit message might look something like this. So the first line is usually kept to about 50 characters or less.

Play video starting at ::2:25 and follow transcript
1:41
The line contains a short description of what the commit changes are about. After the first line, comes an empty line, and the rest of the text is usually kept under 72 characters. This text is intended to provide a detailed explanation of what's going on with the change. It can reference bugs or issues that will be fixed with the change. It can also include links to more information when relevant. The line limits can be annoying but they help in making the commit message be more digestible for the reader. There's a git command used to display these commit messages called git log. This command will do any line wrapping for us. Which means that if we don't stick to the recommended line wrapping, long commit messages will run off the edge of the screen and be difficult to read.

Play video starting at ::3:05 and follow transcript
2:25
Now, take a look at the lines in the commit message that start with the pound symbol. Just like in Python, this symbol indicates that these lines are comments and won't get included in the commit message. Git shows them to us whenever we're writing a commit message as a reminder of what files were about to commit. Sometimes it can be tempting to just write something short like update, change or fix as the description of our commit messages. Don't do it. It's super frustrating to go back to repository’s history and discover that there's not enough context to understand what was changed and why. It takes only a few more seconds to write a better description. This can be invaluable down the line.

Play video starting at ::3:52 and follow transcript
3:05
Following these guidelines can help make your commit message really useful, and the investment of work now will really pay off later. If you're interested in learning more about git commit style, there are plenty of resources out there to read including the Linux kernel documentation itself along with impassioned opinions from other developers. We'll include links to all of them in the next reading. We said that we can check the history of the commits of our project using the git log command. Let's go back to our example scripts directory where we performed two commits and check out what git log has to say about those two commits. Take a look at what git tracks as part of the log. It's packing a lot of information in just a few lines.

Play video starting at ::4:36 and follow transcript
3:52
The first thing listed for each commit is its identifier, which is a long string of letters and numbers that uniquely identify each commit. The first commit in the list also says that the head indicator is pointing to the master branch. If this is gibberish to you, don't worry. We'll talk more about what a head and master means in later videos. For each commit, we see the name and the email of the person who made the commit which is indicated as the author. Then we get the date and time the commit was made. Finally the commit message is displayed. Our commit messages are very brief as we're just starting to work on our repository. As the work we do becomes more complex, we'll probably write longer descriptions with a lot more detail.

4:36
Coming up, we've got a cheat sheet for you that lists all the git commands we've seen up until now along with links to additional information that you might find useful. After that, head over to the next practice quiz to help make sure you've wrapped your head around all these new concepts.
