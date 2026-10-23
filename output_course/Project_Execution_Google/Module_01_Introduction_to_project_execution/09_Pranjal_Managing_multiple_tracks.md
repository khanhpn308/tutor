# 🎥 Pranjal: Managing multiple tracks

🔗 **Link xem Video MP4:** [Xem / Tải Video](https://d3c33hcgiwev3.cloudfront.net/f6Z6z_wlR6Kmes_8Jfei3w.processed/full/540p/index.mp4?Expires=1792886400&Signature=d5tLhGzhckRAuE0L6GsydP8ss2dr6aQzpNDbAqHIJYFm1tXtCPpO8NwJhWPjKgP7rhqJzytFyLwaFV5pjkGNPa8FfVcRfqSEjAHCR93YlxbShxt3YETOhvZbS1wUhfSJJv37a589byG08rK36KBVjkj6bM96SLRp8jLjP1IwwCU_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)

---

## 📜 Transcript (Lời giảng viên)

​[MUSIC] ​Hi, my name is Pranjal, and ​I work as a program manager in the Site Reliability Engineering org. ​You can also call it SRE. ​What SRE does is they are primarily responsible for ​all the critical services within Google, ​and in case something goes wrong, ​we are the first line of defense. ​I think I can talk about the first big project I managed at Google. ​My tech lead and I co-founded this project about three years ago, ​and I continue to work on it as of right now. ​So the project of what we wanted to do in terms of ambition was we wanted to ​generalize some tooling to help mobile apps be reliable in production. ​So what that means is, let's say you're using a mobile app.

​[MUSIC]

​Hi, my name is Pranjal, and

​I work as a program manager in the Site Reliability Engineering org.

​You can also call it SRE.

​What SRE does is they are primarily responsible for

​all the critical services within Google,

​and in case something goes wrong,

​we are the first line of defense.

​I think I can talk about the first big project I managed at Google.

​My tech lead and I co-founded this project about three years ago,

​and I continue to work on it as of right now.

​So the project of what we wanted to do in terms of ambition was we wanted to

​generalize some tooling to help mobile apps be reliable in production.

​So what that means is, let's say you're using a mobile app.

​We want to make sure that in case something goes wrong, ​we detect it before the user does, ​and we take action before the user even knows that something's wrong behind ​the scenes, right? ​So we started out with this project, and my biggest fear in terms of working on ​this project was managing a trade off between ambition and project quality. ​So when we did our brainstorming sessions, and we wrote out a roadmap, ​it just seemed a bit too overwhelming—the ​scale at which we were planning to work. ​I think I would be really thankful to my manager at the time. ​She said, she gave me some really good advice, she said, "In case you have, ​let's say, five different tracks going on in a very big project, ​not all five tracks have to be worked on every single day. ​You could probably take out a quarter and ​make super-good progress on maybe track three and track five, ​whereas you can bootstrap the other tracks to make progress on it ​in the next quarter." ​So that gave me a bit of peace of mind.

​We want to make sure that in case something goes wrong,

​we detect it before the user does,

​and we take action before the user even knows that something's wrong behind

​the scenes, right?

​So we started out with this project, and my biggest fear in terms of working on

​this project was managing a trade off between ambition and project quality.

​So when we did our brainstorming sessions, and we wrote out a roadmap,

​it just seemed a bit too overwhelming—the

​scale at which we were planning to work.

​I think I would be really thankful to my manager at the time.

​She said, she gave me some really good advice, she said, "In case you have,

​let's say, five different tracks going on in a very big project,

​not all five tracks have to be worked on every single day.

​You could probably take out a quarter and

​make super-good progress on maybe track three and track five,

​whereas you can bootstrap the other tracks to make progress on it

​in the next quarter."

​So that gave me a bit of peace of mind.

​And she also empowered me to think in terms of—I'm ​in a position as a program manager to push and pull on those priorities. ​As long as people are aware of what we're working on, what risks need to be ​identified and mitigated, and if everything's being tracked properly, ​it's okay to maybe accelerate sometimes and pause sometimes In fact, ​I learned that zooming out and pausing sometimes can result in original ideas and ​then also gives people a little bit of a breather.

​And she also empowered me to think in terms of—I'm

​in a position as a program manager to push and pull on those priorities.

​As long as people are aware of what we're working on, what risks need to be

​identified and mitigated, and if everything's being tracked properly,

​it's okay to maybe accelerate sometimes and pause sometimes In fact,

​I learned that zooming out and pausing sometimes can result in original ideas and

​then also gives people a little bit of a breather.
