# 🎥 Installing Git on Windows (Optional)

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/eairSOlQRtSIt7172NtSCw.processed/full/720p/index.mp4?Expires=1793059200&Signature=R1c42XP7AzGi7TRTyRN4nWerTPaUkShANiU1YZCv07zSEu0C86l8UUiQwnEbkRbdWLO6E1GtnJIOzIhFX4ZwbSlm3nEdpX46n3CgM689vPRvVKCMYCyPvE1IYD96fv-ZfiIlN2RamgalG3B7mp4yfC6~uI2f5DDkgL4b4kly9Zk_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at ::0:44 and follow transcript
0:01
In this video, we'll show you how you can install Git on Windows. We'll dive into the different options that you can select and what they all mean. We'll start by downloading the latest version of the software from the gitforwindows.org website. The software package we get includes a bunch of other tools that might come in real handy. It comes with a Bash emulation environment, where we can run all the Git commands we'll explain in this course. And a bunch of Unix like utilities that we'll show in this and other courses. This bundle also includes a graphical user interface to interact with Git.

Play video starting at ::1:31 and follow transcript
0:44
We won't look at it during this course, but you can experiment with it on your own. All right, we've downloaded the file, let's get it installed. First, let's start by clicking Keep. The first window we get is the license of the software. Git is released under the GPL version two license, which is a free software license. This means that if we want, we can look at Git's code to learn how it works, and we can even modify it to do something different. All right, let's accept this license and continue with the setup.

Play video starting at ::2:12 and follow transcript
1:31
The first option we get is the installation path, we'll keep it as is. This window lets us select additional components to add to our Git installation. By default, Git integrates with the Windows Explorer to let us run Git Command Line or the Git Graphical Interface in the current folder. This software bundle comes with an extension for improving the support of how large files, like audio or video files, get stored in the version control system. It's a good idea to keep this enabled. The installer will also register the Git configuration files as files that should be opened with a text editor, and the .sh files as files that should be executed with Bash.

Play video starting at ::2:59 and follow transcript
2:12
All of this makes sense, so we'll keep these options selected. If you want, you can also enable some of the other options, that will cause the icons to be displayed on the desktop, true type fonts to be used in the console, or software to automatically check for updates. All right, let's keep going. We get prompted for the name of the folder where we want to create all the shortcuts. Git is fine as the name for this, so let's continue. Okay, now's the time to choose the editor. This is the option that you'll most likely want to adjust. You want to select an editor that you're comfortable with. The installer already has a list of possible options that you could choose here, like Notepad++, Visual Studio Code, or Sublime Text.

Play video starting at ::3:47 and follow transcript
2:59
And we can even select any other editor we wanted by entering the path to the editor's executable file. For this course, we'll be using Atom in all of our examples. So let's choose Atom for this installation. Heads up, the bundle doesn't ship with any of these graphical editors installed, you'll need to install the one you want separately. All right, we're now asked to choose how we want to adjust the PATH environment. This option lets us decide how we want to execute Git from the command line. Selecting the first option will make Git only accessible through the embedded command line that is shipped with the bundle.

Play video starting at ::4:33 and follow transcript
3:47
The second option, the one that's pre-selected, allows us to execute Git from the embedded command line and from the Windows Command Prompt. The third option will add the Unix-like tools shipped together with Git to the Windows Command Prompt. If you choose this option, any commands that have the same name as those in the OS will then come from the bundle and not the basic OS. We'll keep the second option selected, as it's the one that's most convenient for us, while not interfering with the local tools. This window lets us choose how we want to validate the SSL certificates used for HTTPS connections. We can choose to use the OpenSSL library that shipped together with Git, or use the native Windows library.

Play video starting at ::5:13 and follow transcript
4:33
You'll want the second option if you need to interact with your company's internal systems. As we'll only be interacting with GitHub, we'll keep the default option selected. This window lets us select what we want to do about line endings. The characters used to indicate the end of the line are different between Windows, Linux, and Mac OS. So the Git software bundle lets us decide how we want to handle these differences. The default is to store Windows line endings on the local files, but use Unix line endings in the files stored by Git. This works well when you're using your Windows computer to collaborate with others using a different OS.

Play video starting at ::5:53 and follow transcript
5:13
The second option is to keep the line endings unchanged when copying the files locally, and use Unix line endings for the files stored in Git. This would work well if you're using a Unix like OS, or if you're only editing through Unix-like editors on Windows. The third option is to not do any conversions. This option doesn't work well if you're trying to work with people using a different OS. So it's only recommended if all your collaborators will be running the same OS as you. All right, let's keep the first one selected and move on. This window lets us configure the terminal emulator.

Play video starting at ::6:42 and follow transcript
5:53
The software bundle ships with its own terminal emulator that includes a bunch of nice features, like better Unicode support and a long history of commands that we can scroll. We'll keep that one selected, but if you feel like you're more comfortable with the Windows default console window, you can choose that one. All right, we have a few extra options that we can choose to enable if we want. We'll keep these as they are, that way we'll get the performance improvements of letting Git do file system caching, and we'll be able to use Git's credential manager. We don't need to use symbolic links in our repositories, so we'll leave that disabled. Finally, we get one last prompt before installing, which lets us choose which experimental features we want to select.

6:42
The features offered here will change with time, as some get adopted and others get dropped. You can decide whether you want to work on the bleeding edge, or you'd rather go with what's already well tested. We aren't feeling too adventurous today, so we won't enable the experimental features. We'll just click install here to get our installation started. All right, Git is installing on our machine. It'll take a while for it to complete. Once it's done, we'll have all the Git goodness at our fingertips. In case you need a bit more help, you can find links for more information regarding Git installation in our next reading.
