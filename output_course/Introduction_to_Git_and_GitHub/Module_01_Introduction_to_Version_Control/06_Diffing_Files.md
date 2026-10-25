# 🎥 Diffing Files

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/R7HRVAgYT86_f-V5kkTUEQ.processed/full/720p/index.mp4?Expires=1793059200&Signature=innAkd5NO61n5mFPE9y6mSZsR9oyNzkTxXNOMpcgQCeMghbgc05bcSPL0iEo5Hosd4Ey6FQEPMOQdLMVycE9DX1CEiEt9QRi3taXes5ZW3IOutnnQpUp7FBlc46WMB43potoxOcpohwaqbrPD0iF-ybNJ~9MOIJhbJeMLV69RIM_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:42 and follow transcript
0:01
Imagine you had two copies of some code, and you wanted to see what the difference was between them. How would you do it? You could open both files in the editor side by side, look at one then look at the other to spot the differences, but that's super error-prone. We're human and by comparing with our eyes we are bound to miss some differences. Fortunately, there's a better way. You can use some nifty tools that will do this automatically. We can use the diff command line tool to take two files or even two directories, and show the differences between them in a few formats. Let's check it out with an example. We have two files rearrange 1.py and rearrange 2.py which contain two different versions of the same function.

Play video starting at ::1:34 and follow transcript
0:42
Let's take a look at them using CAT. Can you spot the difference? Maybe you can but it's not super obvious. Let's use the diff command so that we don't have to strain our eyes trying to spot it. When we call the diff command, we get only the lines that are different between two files. It's much easier to find the difference when we just have two lines. See the symbols at the beginning of each of those lines? The less than symbol tells us that the first line was removed from the first file, and the greater than symbol tells us that the second line was added to the second file. In other words, the old line got replaced by the new one.

Play video starting at ::2:15 and follow transcript
1:34
In this example, we had one line that was replaced with a new one. This is a common change when modifying code, but not the only possibility. Let's check out another example. Here there are more changes going on. We can see that diff splits the changes in two separate sections. The section that starts with 5c5,6 shows a line in the first file that was replaced by two different lines in the second file. The number at the beginning of this section indicates the line number in the first and second files. The c in between the numbers means that a line was changed.

Play video starting at ::3:03 and follow transcript
2:15
The section that starts with 11a13,15 shows three lines that are new in the second file. The a stands for, you guessed it, added, but that block looks a bit strange doesn't it? It seems like we're adding a return and an if condition but nobody for the if block. What's up with that? To understand this better we can use the dash u flag to tell diff to show the differences in another format. Let's check that out. This unified format is pretty different from the one that we saw before. It shows the change lines together with some context, using the minus sign to mark lines that were removed, and the plus sign to mark lines that were added.

Play video starting at ::3:43 and follow transcript
3:03
The extra context lets us better know what's going on with the change that we're diffing. We can see that the new file actually has a completely new if block that's part of a chain of conditionals that looks very similar, and that's why with the diff output that we saw before, it was a little confusing which lines had been added. There are a lot of tools out there to compare files. Diff is the most popular one, but not the only one available. For example, wdiff highlights the words that have changed in a file instead of working line by line like diff does. To help us even more, there are a bunch of graphical tools that display files side by side and highlight the differences by using color.

3:43
Some examples of this include: meld, KDiff3, or vimdiff. We can use these tools to give better contexts to the changes that we see. We've talked about how we can see differences between two files, now how can we use those differences to apply changes? That's coming up in the next video.
