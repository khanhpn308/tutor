# 📖 Review: Applying Changes

This reading contains the code used in the instructional videos from [**Applying Changes** ](https://www.coursera.org/learn/introduction-git-github/lecture/qIzdp/applying-changes).

## Introduction

This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written and can be used as a reference as you work through the course.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.

`cat cpu_usage.py `

cat cpu_usage.py

**Code output:**

#!/usr/bin/env python3

import psutil

def check_cpu_usage(percent):

usage = psutil.cpu_percent()

return usage < percent

if not check_cpu_usage(75):

print("ERROR! CPU is overloaded")

else:

print("Everything ok")

`cat cpu_usage.diff `

**Code output:**

\--- cpu_usage.py 2019-06-23 08:16:04.666457429 -0700

+++ cpu_usage_fixed.py 2019-06-23 08:15:37.534370071 -0700

@@ -2,7 +2,8 @@

import psutil

def check_cpu_usage(percent):

- usage = psutil.cpu_percent()

+ usage = psutil.cpu_percent(1)

+ print("DEBUG: usage: {}".format(usage))

return usage < percent

if not check_cpu_usage(75):

`patch cpu_usage.py < cpu_usage.diff `

**Code output:**

patching file cpu_usage.py

`cat cpu_usage.py `

**Code output:**

#!/usr/bin/env python3

import psutil

def check_cpu_usage(percent):

usage = psutil.cpu_percent(1)

print("DEBUG: usage: {}".format(usage))

return usage < percent

if not check_cpu_usage(75):

print("ERROR! CPU is overloaded")

else:

print("Everything ok")
