# 🎥 How to Use Code Reviews in GitHub

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/tZex5JTdRAmaxdRzUIl32A.processed/full/720p/index.mp4?Expires=1793059200&Signature=d2iiQtXnKZF~9etaTIQBNdC2SnAgPrLy~rkqiGUB-HYHAG0DM5IMuEMtV2pBj5Em44XXL4yd8l1GbPjHSKYrrJSHDKhFQA01IVI5sqS~YXhKHpU3wcksZNVKKVpyMfrr1xPCUreWvlQF-I3GJfp~4Xf5R7Eh2D2jIrXE5rO2Ihc_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:42 and follow transcript
0:01
Up till now, we've talked about the general process of doing code reviews. This process applies to any platform with code reviewing tools. Now, let's check out how this process looks on GitHub, specifically. Remember, a while back in this module, we created a pull request that added a read me file. Conveniently, our colleague just replied with a few comments. Let's have a look.

Play video starting at ::1:22 and follow transcript
0:42
The code review has one overall comment, and line by line, comments, highlighting the things that we need to get done. We can view all changes requested for the file we created by clicking on the view changes button. Our reviewer made three comments about our file. The first one is asking us to add a period at the end of the sentence. The second one asks us to add another hashtag which will make the title render and a smaller font. The last one will require a bit more work since it's asking us to include a couple more examples.

Play video starting at ::2:18 and follow transcript
1:22
Let's fix these. We'll add a period at the end of the second sentence, and then add a second hashtag before the example title, and finally, add a few more examples. To do that, we'll use the star character, which is another feature of the markdown language that lets us easily create bullet points. So we'll add a couple of more lines with the same format, and say that Hopper, Grace M. turns into Grace M. Hopper, and that Voltaire stays as Voltaire.

Play video starting at ::3:02 and follow transcript
2:18
All right. We've addressed all the comments in our code review. Let's save our file and then commit the changes. Since we want this change to be a part of the previous commit, we'll call Git commit dash A with the dash dash amend flag, which will edit the original commit. Once we've done that, let's call Git status to see what Git has to say about our repo. Just like before, we see that our change has diverged from the origin slash master branch. You might remember that git commit dash dash amend modifies commits. So it's not safe to do with commits that have been pushed to the repo. Using amend is pretty much the same as creating a new commit, and then using an interactive rebase to fix up a change.

Play video starting at ::3:54 and follow transcript
3:02
So, the commit gets replaced by a completely new commit with a completely different commit ID. This means that to push it, we'll need to use the dash F flag again. Remember that forcing pushes is fine for pull request branches because nobody else should have cloned it. But this isn't something that we want to do with public repos. All right. We've done what our colleague asked. Let's now go back to look at the pull request and resolve the comments.

Play video starting at ::4:34 and follow transcript
3:54
See that comment that says outdated, that's because we've pushed a new version since we've made the change. But, since we've taken care of their request, we can ignore the outdated comment and just resolve the conversation. Cool, we've addressed all the comments. We can leave a message in our conversation to let our reviewer know that we've resolved all the comments and ask them to take another look.

4:34
Our reviewer can now check out the new changes and approve them if they're satisfied. As with lots of other topics we've covered, making the most out of the code review process will require some practice. It's great to have some tips but in the end we need to learn by experience. So don't be afraid to practice practice practice. Up next, you'll find some resources to learn more about code reviews and a quiz to put this knowledge into action. After that, you can try out doing a code review on GitHub.
