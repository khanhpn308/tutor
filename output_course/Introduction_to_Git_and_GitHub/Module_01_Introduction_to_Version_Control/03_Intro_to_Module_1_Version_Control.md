# 🎥 Intro to Module 1: Version Control

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/ZxDtV9Y4RZ-txhGA_ns04A.processed/full/720p/index.mp4?Expires=1793059200&Signature=Jlm6clnMNJzjlVnjyadsNKl0ogZNhal3whe5gDFIUUpqJ2Q5i9-DfZwh2ncScc6s82OCwcjHPAA8SC2X54RhVEMybF5xKTnGc3IOjSI5QxebxPb2repRFAOsw8VR~x1HbyEnrzDlAiO6ioNzOf031TYQspYRKYrxHHJSUhZ7TJE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:51 and follow transcript
0:01
When you work in IT, you manage information across a lot of different files. You write automation scripts that might evolve over time. For example, you might add new features to your script or take into account additional conditions or modify the scope of systems where the script will be executed. You also manage configuration related to your infrastructure like the default settings on an application or the IP addresses assigned to the computers in your fleet. This information changes over time as the security requirements increase. The fleet grows or new versions of software gets deployed. When trying to manage change in IT, it's super important to have detailed historical information for your organization's configuration files and automation code. This lets the administrators see what was modified and when, which can be critical to troubleshooting.

Play video starting at ::1:35 and follow transcript
0:51
It also provides a documentation trail that will let future IT specialists know why the infrastructure is the way it is, and it provides a mechanism for undoing a change completely. This way, we don't have to undo changes from memory and there's less chance of human error. We'll see this in action when we talk about rollbacks. Imagine this, your team has added a new feature to a script that checks the health of all the computers that you're responsible for. The new check verifies that the firmware of the computer, also known as the UEFI, is updated to the latest version. When you roll this out, you suddenly realize that half the computers now say they're broken. After some investigation, you discover that the check needs to take into account different computer models.

Play video starting at ::2:23 and follow transcript
1:35
You might be tempted to do a quick code fix, push it to the affected machines right away especially if it seems like an easy fix. But more often than not, quick fixes include their own bugs because we don't take the time to test a new code properly. So after the first fix, you might end up doing a second or even third emergency push until things are really working correctly. To avoid these headaches, you can use a version control system to easily roll back your code to the previous version. Since you know that this version was working correctly before the change was made, it would be safe to go back to that one until you had time to fix the code, run some tests, and make sure everything works correctly for all machine models. By releasing code only after properly testing, you avoid having to push quick-fix after quick-fix.

Play video starting at ::3:06 and follow transcript
2:23
Version control systems let us do this and much more. They are crucial to maintaining a healthy codebase for all kinds of IT resources, and for letting multiple people collaborate on the same coding projects together. We're now going to take our first steps to learning this new tool, which will let us keep track of the changes that we make to our scripts, our configuration files, and any other kind of documents that need to be tracked. We'll start by looking at what people tend to do when they don't know about version control and then check out some related tools, like diff and patch. Once we have a clear idea of why we need proper version control, we'll jump into our first Git experience. We'll talk about what Git is and how it does what it does.

3:06
To follow along, you'll need to install Git locally on your machine and learn how to use it from the command line. If this sounds a bit scary, don't panic. We'll guide you along the way and you'll be using it in no time. Once you have Git installed in your computer, we'll do an overview of the basic Git workflow which will let you start keeping track of your scripts. So are you ready to start taking control of your code? Here we go.
