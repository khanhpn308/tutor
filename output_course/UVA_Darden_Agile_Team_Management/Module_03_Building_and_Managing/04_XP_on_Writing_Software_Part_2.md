# 🎥 XP on Writing Software: Part 2

🔗 **Link Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/hjI2U_ELEeWdog4J34Sclw.processed/full/540p/index.mp4?Expires=1792886400&Signature=O3dKsWvnrLV36TocCI2LDdRxzxjtg0Lroeq-OZZnuzurqdK0mddp3PPgTKNg97XlBJ0wv2e7vMceITBacD9lRHux7CFzjaTYaoxbcHRZjuXw~5Lm-QGeLUhovkKOevoQ~QFRg9T5YhXE~lmPYib2bdVfu2SUdYi5jlVZICC14lk_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Lời giảng viên (Transcript)

Play video starting at :: and follow transcript
0:00
​All right, back to the Java building and how XP can help you do it better. ​Here are a couple of last practices, the Ten Minute Build and ​Continuous Integration. ​Continuous Integration refers to this idea that developers will check out versions ​of the code, make their changes, add stuff, do whatever they're working on at ​the moment, and then those things will all have to be merged back together and built. ​And it'll all have to work again. ​And the fact that you should do this continuously a lot, because if you have ​a lot of unmerged code, you may find, days later, that there's conflicts. ​These things don't make sense together. ​And you're going to have generated a lot of waste and need for rework. 
Play video starting at ::40 and follow transcript
0:40
​So if you do this very constantly, then, one, developers don't have to worry as ​much that, ghee, this might make a problem with somebody else's code, and ​they'll just, boom, integrate it together, see, and if it does, they fix it. ​And two, those problems won't accrue as much size if you're doing this a lot, ​is what XP would say about this. ​And you've heard Spotify talk about how everything's in automation, ​so that they can do this. ​They, Continuous Integration will generally run a set of ​batch processes that take the code, build it into whatever form it needs to be ​in to be kind of working software, and then run a bunch of tests against it. ​Unit tests, as well as, functional tests. ​Let's talk about that for a minute. ​A unit test we talked about, this is a kind of lower level, ​where we're testing individual pieces of code, and then, up above that, ​we have this idea of functional tests. 
Play video starting at :1:34 and follow transcript
1:34
​And these test the system as a whole after you put all the code together. ​And, typically, a build process will run this all and ​build the software, run all the unit tests, and ​then once the softwares put together, it'll run these functional tests. ​And automating that means that you can do it a lot and ​find the problems quickly and fix them. ​So the idea of the Ten Minute Build, which is kind of a corollary to this, is that ​you should put things together so that it can run in ten minutes, and because that ​facilitates you being able to do it a lot and not having it take too long. ​So, this is something that you will, ​I think consistently hear from high functioning Agile teams. ​Is that all the kind of testing and build, that's all automated. ​Even sometimes putting up test environments, and ​related things like that. 
Play video starting at :2:22 and follow transcript
2:22
​And we'll talk more about that in Course 4. ​But they've invested in automation. ​So there's a tedious task that a developer or a tester is obliged to do, ​they look to automate that early and then accrue that investment, ​add to it over time, so that they are able to integrate a lot, test a lot, and ​see how things are working before. ​Whereas, the sort of counter example or counter case there is that ​it's really hard to get everything put together and working. ​Releases are infrequent and kind of a big mess and generate a lot of overhead. ​And that's a case where XP would say, we focus on automation. ​Invest in this and your practice of Agile will become healthier. 
Play video starting at :3:1 and follow transcript
3:01
​So we've talked about the Java building. ​And even if you're not a software developer or even if that's not your job ​now in your team, I hope you've learned enough to make room for these practices, ​and introduce them to your team, so that they can decide if and ​which ones of those they want to apply, in what way. ​And then you can help them integrate that into your overall practice of Agile in ​a way that helps the team improve and become more productive.
