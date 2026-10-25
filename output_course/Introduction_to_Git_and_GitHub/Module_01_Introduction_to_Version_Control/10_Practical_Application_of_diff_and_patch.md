# 🎥 Practical Application of diff and patch

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/mJlxY6baRmmN93IKH4lVyg.processed/full/720p/index.mp4?Expires=1793059200&Signature=lRk0Lu30bwVCwDsygJ-YfX4k4ryPbYwiiFB0g83-BAusouA3u~1y8OU5aNWFHrNq~o7GEDHf~z9fGF1cimnAQzQ37M~69-Pihphnsy-sV4qrtaP6BkjVQ0ZVqMAlMmbxrrBroIqwOkeaYAVe~gENf4pOI6c-RMImG4uE6ulfdP4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:57 and follow transcript
0:01
Imagine this, a colleague is asking our help with fixing a script named disk_usage.py. The goal of the script is to check how much disk space is currently used, and print an error if it's too little space for normal operation. But the script is currently broken because it has a few bugs. We’ll help our colleague fix those bugs to demonstrate how to use diff and patch. Before we change anything, let’s make a couple copies of the script. We'll add _original to one copy, which we’ll keep unmodified and use for comparison and _fixed to the other copy, which we’ll use to repair our fix.

Play video starting at ::1:40 and follow transcript
0:57
Okay, now that we have our copies, we'll edit the _fixed version and actually fix it. This file has a bunch of code. Before we try to understand what it does and what's wrong with it, let's execute it and see what we get. The Python interpreter isn't too happy. It's complaining that there's a return outside of function. And if we look at the code, we can clearly see that there's a return that's not inside any function. You might remember that in Python, we can only use return statements inside functions. So how do we fix this?

Play video starting at ::2:20 and follow transcript
1:40
There's a couple options. We could turn the current code into a function and then call that function from the main part of our script. Or we could use sys.exit to make the return number of the exit code of our script, which is the code that causes a program to exit with the corresponding exit value. For now, let's go with the second option. Okay, we've made the change.

Play video starting at ::3:11 and follow transcript
2:20
Let's execute this new version of our script. Darn, we fixed the syntax error, but now the script is telling us we don't have enough space on our disk. But we know that we actually do have some free space, right? What's up with that? If you look closely at the code, you might notice that the script is converting to gigabytes twice. The function call to check_disk_usage is passing 2 times 2 double star 30. You might remember that the double star operator is used to calculate powers. In this case, 2 to the power of 30, which is how many bytes are in a gigabyte. So, this would be 2 gigabytes, but that’d be if the check_disk_usage function was expecting a value in bytes.

Play video starting at ::4:14 and follow transcript
3:11
If we look at the code of the function, we can see that it's already dividing the amount of free bytes by 2 to the power of 30. So in other words, we're doing the gigabyte conversion twice. Once when calling the function and once inside the function. We need to get rid of one of them. Let's change how we call the function. Okay, let's try it out again. It works now. Okay, now we need to send a fixe to our colleague so that they can fix their script. To do that, we'll use a technique we just learned to generate a diff file, like this.

Play video starting at ::4:59 and follow transcript
4:14
Let's check the contents of the diff using the cat command.Awesome. This seems to have what we want. So this is what we need to send to our colleague to have them patch their file. How would they do that? They would run the patch command like this. By calling patch with the diff file, we've applied the changes that were necessary to fix the bugs. Let's check that disk_usage.py now executes successfully.

4:59
Success. So we've now seen how we can look at differences between files, generate diff files together to gather our changes, and then apply those changes using patch. But this is still a very manual process, where version control systems can really help. But before we jump into that, in the next cheat sheet, you'll find a summary of the commands we just covered. So check that out and then head over to the practice quiz to make sure you've got a grasp on all this.
