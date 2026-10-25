# 🎥 The Code Review Workflow

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/ZbblxSp7T1iSrcT9IwVQKQ.processed/full/720p/index.mp4?Expires=1793059200&Signature=DLgoWp5aC5-zvJN-goP-miAsy2vv7XERx7Xe1n~rJvLSFwx9~-26hnaae5mHs48~RAufX3OMdxg8HaOmsBqZ14nMYNSktczHVvUcPwneqp6gAvVDUhbc83L5I6oQoeDrpRXSeogxkmdRMojVZ19l9xjW0wCILyudMxU-x0TBnKg_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:50 and follow transcript
0:01
In our last video, we explained what code reviews are and how they can make our code better. Now, we'll check out a typical code review using a reviewing tool. Imagine we've just finished a bunch of code changes, now, we'll ask a reviewer to look at our code. The reviewer might say that everything is okay and our changes approved, but usually they'll find something that needs improving. So they'll add comments to our changes explaining what needs to be fixed and how. When we get the review comments will address them by fixing our typos, adding any missing tests and so on. After addressing a comment, we can mark it as resolved so that we know it's been taken care of. If there's something that we aren't sure how to do or we think a different approach might be better, we can reply to the comment and ask our reviewer for more information without marking the comment as resolved.

Play video starting at ::1:34 and follow transcript
0:50
Once all comments have been resolved and our viewer is satisfied with the results, they'll approve the change and we'll be able to merge it. You may be wondering, what are all of these comments that I receive? There's a wide range of things your reviewer might have to say about your code. Sometimes, you might have forgotten to take into account something important and you'll need to do significant work to fix it. Sometimes, your reviewer might point out something small that's not really critical. And the comment is mostly a suggestion for making the code better. These comments are usually prefixed, saying that it's a Nit. Whatever it is, it's important that you take the time to understand what the comment is and what you need to do to address it.

Play video starting at ::2:22 and follow transcript
1:34
For example, if you've written a piece of code and your reviewer asks you to explain why or how the code is doing something, it might be tempting to just answer their question in the comment and mark it as resolved. But this isn't a great idea, because only the reviewer gets to see your answer. Instead, it's better to take this as an opportunity to make the code clearer. For example, you could do this by using better variable names or splitting a large piece of code into smaller functions. On top of that, you can add comments to the code and documentation to your functions to make sure that the how and why are clearly explained. It's common for code reviews to include several comments about the style of the code. To avoid a lot of back and forth, it's a good idea to refer to a style guide that explains the preferred coding style for the project.

Play video starting at ::3:07 and follow transcript
2:22
For example, lots of Python projects use the PEP8 style guide. If the project you're contributing to doesn't include a style guide, make sure that you ask for one. And in case you need inspiration, we've included links to some common style guides in the next reading. There are a bunch of code reviewing systems out there. And while they all follow the same patterns, they don't all work exactly the same way. In some code reviewing tools, you'll need one of the project maintainers to approve your code before it's submitted. In other tools, you'll just need to get a couple +1s from contributors to the project before you can submit. The goal is to always ensure that your code has been reviewed by people who are familiar with the project, so that it's ready to be submitted.

3:07
Can you think of a project you've worked on in the past where code reviews could have been helpful? Maybe you worked as a part of a team and had trouble making sure that everyone agreed on how things should be done. Or maybe you were learning how to use a new tool and you would have benefited from a second pair of eyes on your work. No matter how simple or complex a project is, it can always be improved with good code reviews. Up next, we'll dive into how this code reviewing process works on GitHub.
