# 🎥 Course Introduction

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/IbktzWKZRbqujPq60FViXQ.mediaconvert/full/IbktzWKZRbqujPq60FViXQ_eaba67cea7814eefa1334a535c44c4f1_C3M1-Course-Introduction_MP4_540.mp4?Expires=1793059200&Signature=NIY4gDIz~E~x6TLe9rhyq8rvUGTfIMPKXSr5UdhABWhYVzsHOj2sOHbRy35s0DClVMpiiYy2kf-g8DMv-i-YPPLIr990EDmZ~vhVnLZNC4UzLobc8eQ7rKaUIxx4sAWBffe8gIYNIXVUxzom4lX7u9R54SP2saSHqW3klzkiN-c_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at :: and follow transcript
0:00
​Hi there, and welcome back. ​You've heard us talk a lot about programming and automation. ​This course focuses on a slightly different aspect, ​how to keep track of the different versions of your code and ​configuration files using version control systems or VCSs. ​These are tools that everyone in IT can benefit from, ​even if it's not just for programming or automation itself. ​It will allow us to easily roll back when mistakes happen and ​also help us collaborate with others. ​You might have already heard of version control systems in the context of ​managing configuration files or ​maintaining the source code of programs and scripts. ​In this course, we'll introduce you to a popular VCS called Git and ​show you some of the ways you can use it.

Play video starting at ::46 and follow transcript
0:46
​We'll also go through how to set up an account with a service called GitHub, so ​that you can create your very own remote repositories to store your code and ​configuration. ​By the end of this course, you'll be able to store your code's history in Git ​and collaborate with others in GitHub, ​where you'll also start creating your own portfolio. ​Nowadays, lots of employees will ask to see your GitHub portfolio when you're ​interviewing for IT roles. ​GitHub portfolios give companies an idea of what projects you've worked on ​and what kind of code you can write. ​This course will help you get yours set up. ​I'm Kenny Suliman, and I'll be your instructor for this course. ​I work as a technical program manager for Android System Health and Velocity.

Play video starting at :1:29 and follow transcript
1:29
​In my role, I work with engineering and leadership to ensure that we launch healthy and ​stable Android devices for all of our users. ​I'm thrilled to be your instructor for this course. ​As a technical program manager, my main challenge is making sure that ​everyone involved is aligned on a shared vision. ​To ensure our project's a success, my team creates a narrative, ​figures out all the stakeholders, and makes sure everyone is on the same page. ​After that comes the hardest part, executing the project to completion. ​To do that, it's essential we have a version control system, ​where each engineer can store and share the code they create. ​This lets us track different revisions, ​roll back problematic changes, and work together effectively.

Play video starting at :2:13 and follow transcript
2:13
​Before we jump in, I'd love to take a quick moment and ​share why I'm so excited to be here with you, participating in this program. ​Ever since I was young, I've always been obsessed with this technology. ​I used to fix my friend's old broken computers, for a small fee of course, ​and would spend hours trying to mod my old video game systems so ​I could squeeze some more fun out of my favorite games. ​So once I found out I can get paid to work on computers and ​cool gadgets for a living, I was sold. ​There was only one problem. ​When I started my first IT job, there were very few people that, well, ​looked like me. ​As I started to move up the ranks, this disparity only grew.

Play video starting at :2:53 and follow transcript
2:53
​I quickly realized that this isn't only an IT support issue, but ​something the entire tech industry is struggling with. ​The representation problem is something I'd like to solve one day. ​And the only way I can do that is to lead by example, share my knowledge, and ​help as many people as I can achieve their goals. ​And who knows? ​Maybe one day someone will take the information they've learned here and ​use it to change the world. ​Psst, remember me when you're famous. ​Anyway, enough about me, let's get back to the course.

Play video starting at :3:28 and follow transcript
3:28
​There's a lot to learn with Git and version control. ​We'll break it down step by step, so you can fully understand how it works and ​why it's so useful in your IT role. ​Whether you're an IT support specialist, a systems administrator, ​or looking to expand your skills towards other roles in IT. ​Throughout this course, you'll learn about Git's core functionality, ​so you can understand how and why it's used in organizations. ​We'll look at both basic and more advanced features, like branching and ​merging. ​We'll demonstrate how having a working knowledge of a VCS like Git ​can be a lifesaver in emergency situations or when debugging. ​And we'll explore how to use a VCS to work with others ​through remote repositories like the ones provided by GitHub.

Play video starting at :4:12 and follow transcript
4:12
​To do all this, and so you can follow along with the exercises in these videos, ​you'll need to install Git on your computer. ​This will also let you interact with GitHub and upload your code there. ​For the examples in this course, we'll show a bunch of different Python scripts. ​While you don't need to know any Python to use Git, ​we do recommend that you have a basic knowledge of the language, so ​that you can understand the examples and the functionality we'll be demonstrating. ​If you've done the courses on Python in this program, you're covered. ​If you haven't, that's okay. ​But you might need to freshen up your Python skills to follow some of ​our examples.

Play video starting at :4:47 and follow transcript
4:47
​Also, since all the scripts will use Python 3, ​you'll need to have Python 3 installed in your computer to run them. ​For our examples, we're going to use a Linux computer, ​interacting with the Linux command line through the most common command line ​tools. ​Again, if you joined us for the Python courses, ​you're already familiar with all these concepts. ​If you're jumping into this program with this course, ​you might benefit from reviewing some of the most basic Linux commands. ​Please remember, some of these topics and videos are a little complex, so ​they might not 100% sink in the first time around. ​That's totally natural. ​Take your time and review any content that's not completely clear.

Play video starting at :5:25 and follow transcript
5:25
​You'll get the hang of it eventually. ​All right, we're ready to get started learning about Git and version control. ​Let's get to it.
