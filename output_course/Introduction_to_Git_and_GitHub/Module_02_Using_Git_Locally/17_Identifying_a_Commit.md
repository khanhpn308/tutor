# 🎥 Identifying a Commit

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/qLwyZHDnSKm82eyqtKh4dw.processed/full/720p/index.mp4?Expires=1793059200&Signature=iWz2KHE8pv6rxToW76sEOeovaSMGN--xd7rdTHvOkjti4wyp8rkemh8UaDc6AxX-CZlTq-BedWQg0qDuZaUmdyldoHnN94MAn1ZcK2D3Co7-tdcAhxc1klI198rZ4-B9g2n9aoBdeNt7o7fKUajIl7vvKX2vCFemwCJGCDZE3jI_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:49 and follow transcript
0:01
So far we've used the head alias to specify the most recently checked out commit in our Git history. In our bad snapshot example, the error also happened to be in the most recently created commit, but errors can sometimes take a while to be detected. And so, we might need to revert other commits farther back in time. We can target a specific commit by using its commit ID. We've seen commit IDs a few times already. They show up when we're running the git log command, and we also saw the commit ID of the reverted commit in our last example. Commit IDs are those complicated looking strings that appear after the word commit in the log messages. Let's have a look at the latest log entry in our checks repo.

Play video starting at ::1:29 and follow transcript
0:49
The commit ID is the 40 character long string after the word commit, you really can't miss it. This long jumble of letters and numbers is actually something called a hash, which is calculated using an algorithm called SHA1. Essentially, what this algorithm does is take a bunch of data as input and produce a 40 character string from the data as the output. In the case of Git, the input is all information related to the commit, and the 40 character string is the commit ID. Cryptographic algorithms like SHA1 can be really complex, so we won't go too deep into what this means. If you're interested, you'll find links to more information in the next reading.

Play video starting at ::2:12 and follow transcript
1:29
Still you might be wondering, why on earth would you use a long jumble of letters as an ID for commit, instead of incrementing an integer, like 123, etc? To answer that, let's take a quick look at the reason why Git uses a hash instead of a counter, and how that hash is computed. Although SHA1 is a part of the class of cryptographic hash functions, Git doesn't really use these hashes for security. Instead, they're used to guarantee the consistency of our repository. Having consistent data means that we get exactly what we expect. To quote Git's creator, Linus Torvalds, you can verify the data you get back out is the exact same data you put in.

Play video starting at ::2:55 and follow transcript
2:12
This is really useful in distributed systems like Git because everyone has their own repository and is transmitting their own pieces of data. Computing the hash keeps data consistent because it's calculated from all the information that makes up a commit. The commit message, date, author, and the snapshot taken of the working tree. The chance of two different commits producing the same hash, commonly referred to as a collision, is extremely small. So small, it wouldn't happen by chance. It'd take a lot of processing power to cause this to happen on purpose. If you use a hash to guarantee consistency, you can't change anything in the Git commit without the SHA1 hash changing too.

Play video starting at ::3:36 and follow transcript
2:55
Remember our discussion about fixing commits with the dash dash amend command? Each time we amend a commit, the commit ID will change. This is why it's important not to use dash dash amend on commits that have been made public. The data integrity offered by the commit ID means that if a bad disk or network link corrupts some data in your repository, or worse, if someone intentionally corrupts some data, Git can use the hash to spot that corruption. Aha, it will say, the data you've got isn't the data you expected, something went wrong. Thank you, Detective Git, you've saved the day once again. Okay, enough backstory.

Play video starting at ::4:38 and follow transcript
3:36
How can you use commit IDs to specify a particular commit to work with, like during a rollback? Let's look at the last two entries in our repo using the git log -2 command. Say we realized that we actually liked the previous name of our script, and so we want to revert this commit where we renamed it. First, let's look at that specific commit using git show, which we mentioned in an earlier video. We've copied and pasted the commit ID that we wanted to display, and that works. Alternatively, we could provide just the first few characters identifying the commit to the command, and Git will be smart enough to guess which commit ID starts with those characters, as long as there's only one matching possibility. Let's try this out.

Play video starting at ::5:22 and follow transcript
4:38
Two characters is not enough, but usually four to eight characters will be plenty. Okay, now that we've seen how we can identify the commit that we want to revert, let's call the git revert command with this identifier. As usual, this will open an editor where we should add a reason for the rollback. In this case, we'll say that the previous name was actually better. Hooray for flip-flopping. As we called out before, when we generate the rollback, Git automatically includes the ID of the commit that we're reverting.

Play video starting at ::6:08 and follow transcript
5:22
This is useful when looking at a repo with a complicated history that includes a lot of commits. Now, once we save and exit the commit message, Git will actually perform the rollback and generate a new commit with its own ID. See how before the name of our commit the revert command already shows the first eight characters of the commit ID? Let's use git show to look at it. All right, we've managed to revert a commit that wasn't the most recent one. Well done, time travelers. Over the past several videos we've covered a bunch of ways to undo things in Git. Whether for unstaged changes, staged changes, amending commits, or rolling back changes.

6:08
If anything still seems unclear, now's a great time to practice these commands on your local computer, try things out, and come up with more examples of use cases you want to test. Up next, we've spun up a handy cheat sheet summarizing all the content we just covered. When you're ready, move on to the next quiz and put all this new knowledge into practice. We've been learning a lot of complex things over the past few videos, so once you're done with that quiz you should reward yourself for getting through this technical detail with a break. You earned it. Grab a coffee, tea, or snack and let the concepts settle for a bit. I'll meet you over at the next video.
