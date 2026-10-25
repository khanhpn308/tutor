# 🎥 What is version control?

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/YGfxBgJmQ2KvWduiPsN2hA.processed/full/720p/index.mp4?Expires=1793059200&Signature=FIbCS5XYAEu-j6uCYyO3DHnk4-k7EAX~xpoDtFbJwwMraWfHVMQsd07g6~q1squ54CAXuMuyCflmbWSazAiPFrDaPaJm8fkz4qr8fFpZ6dfsFlF1Oinp9gZ2cdzpBLsSsiHhoqCof51WoLDXfMNePgFgDvSQV1XG~jX-ToXuk6k_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:47 and follow transcript
0:00
We've seen up till now, how we can use existing tools to extract differences between versions of files and apply those changes back to the original files. Those tools are really useful. But most of the time, we won't be using them directly. Instead, we'll use them through a Version Control System, or VCS. A Version Control System keeps track of the changes that we make to our files. By using a VCS, we can know when the changes were made and who made them. It also lets us easily revert a change if it turned out not to be a good idea. It makes collaboration easier by allowing us to merge changes from lots of different sources. At first-look, a Version Control System can seem like a complicated, possibly intimidating tool.

Play video starting at ::1:34 and follow transcript
0:47
But if you look closer, you'll see that it's really just a system that stores files. However, unlike a regular file server which only saves the most recent version of a file, a VCS keeps track of all the different versions that we create as we save our changes. There are many different version control systems, each with their own implementation and with their own advantages and disadvantages. But, no matter how the VCS is implemented internally, they always access the history of our files. Let us retrieve past versions of the file or directory and see who changed which files, how each file was changed and when the file was changed. On top of this, we can make edits to multiple files and treat that collection of edits as a single change which is commonly known as a commit.

Play video starting at ::2:14 and follow transcript
1:34
A VCS even provides a mechanism to allow the author of a commit to record why the change was made, including what bugs, tickets or issues were fixed by the change. This information can be a lifesaver when trying to understand a complex series of changes, or to debug some obscure issue. So, be sure to record this extra info in your commits to be truly committed to better code. In any organization that produces software, a VCS is a key part of managing the code. Files are usually organized in repositories which contains separate software projects or just group all related code.

Play video starting at ::3:04 and follow transcript
2:14
If there's a lot of people involved in developing software, some developers may have access to only some of the repositories. A single repository can have as little as one person using it. And it can go up to thousands of contributors. And, as we called that earlier, a Version Control System can be used to store much more than just code. We can use it to store configuration files, documentation, data files, or any other content that we may need to track. Because of the way tools like diff and patch work, a VCS is especially useful when tracking text files, which can be compared with diff and modified with patch. We can also store images, videos or any other complex file formats in a VCS, but it won't be easy to check the differences between versions when comparing these file formats.

3:04
It might not be possible to automatically merge changes made to older versions of a file. You now have a basic idea of what a Version Control System is, and how it works You might be asking yourself, do I really need this? Can't I just keep making backups of my code once in a while? We'll answer that in our next video.
