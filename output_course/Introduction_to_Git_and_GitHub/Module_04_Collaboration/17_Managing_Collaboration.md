# 🎥 Managing Collaboration

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/nX0cdJleQGeAsvIK-VIF0Q.processed/full/720p/index.mp4?Expires=1793059200&Signature=hMh5rQG73OYs1lepXuw0ubYDSesCPF1KCWoM4mLO8ZFicq9c-39lP6CmoCcdBaC0w2giFcGmfOy23WAGR5AlznGtDpDxmBh7UKnedu-5CbpJwdEw25XYLIsvniRlk-tPnF5TI928PdB1~HEqnJUPnxGTavptgM6fPQU8GQOyQhw_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:55 and follow transcript
0:01
Over the past few videos, we've looked at how we can collaborate with others using tools provided by platforms like GitHub. These tools can be very helpful but some coordination outside of the platform is always going to be needed. For example, the project you're working on might need a medium or large refactor that will affect multiple lines of code across several files. It's important to give your colleagues the heads up that this refactor is coming. If possible, try to do the refactor while the other developers are working on a different part of the project because this helps avoid large and complicated conflicts. We've called on a bunch of times that documenting your work is super important. When working together with a large group of people, documenting what you do and why you do it becomes even more important, otherwise you'll spend most of your time answering everybody else's questions.

Play video starting at ::1:36 and follow transcript
0:55
Also, say there's a problem with your service while you're on vacation or the person who developed the code is on the other side of the world and currently sleeping. In these situations, the documentation needs to be good enough to help someone else fix the problem. The most basic form of this is writing clear code with good comments and documentation for those functions in the code. On top of that, you'll want to create documentation files to let others know how they can interact with your project like the readme.md file that we created in an earlier video. If you're a project maintainer, it's important that you reply promptly to pull requests and don't let them stagnate.

Play video starting at ::2:19 and follow transcript
1:36
The more time that passes until a pull request gets reviewed, the more likely it is that there's a new commit that causes a conflict when you try to merge in the change. On top of this, if the person contributing the changes of volunteer that's just trying to help, they may lose their motivation to work on the project if you make them wait too long for feedback. Another thing to remember when you maintain a project especially if it's an open source project that volunteers are contributing to is that it's important that you understand any changes you accept. You never know if the other person is going to stick around to maintain the code after you merge it in so you better make sure you can do that. You should also be careful with which patches you accept or reject.

Play video starting at ::3:01 and follow transcript
2:19
Accepting everything that gets sent your way might make your project grow too much and become unmanageable or it might take into account too many corner cases and cause complicated code that's hard to maintain. On the flip side, if you don't accept any pull requests you'll discourage contributors and miss out on keeping your project active and relevant. We've talked about style guides a few times already. If you're contributing to a project, you want to check out the style guide and make sure you follow it. If you own a project, it makes sense to create a style guide so that others know what you're expecting from them. In our next reading, we'll include links to some of the most common style guides and pointers and how to include a style guide in your own project.

Play video starting at ::3:51 and follow transcript
3:01
When it comes to coordinating who does what and when, a common strategy for active software projects is to use an issue tracker. This is a super useful tool and we'll find out more about it in the next video. On top of that, when the project is large enough, it's important to have another way of communicating and coordinating between contributors. For many years, most projects used mailing list and IRC channels for communication. Recently, new forms of communicating have gained popularity like Slack channels or Telegram groups. If you're managing your own project, choose whatever communication medium best fits your needs and those of your contributors. If you're collaborating with a project you don't own, you'll want to find out what channels are being used for collaboration and with that you now have a rough idea of how to collaborate with others across the internet.

3:51
Up next, we'll talk about two important tools that can help us collaborate better, tracking issues and continuous integration.
