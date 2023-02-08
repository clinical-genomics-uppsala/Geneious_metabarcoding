#!/usr/bin/env python3

import sys
import os
import re
import subprocess
import shutil

# Geneious input/output and options
inFile = os.path.join("/geneious", sys.argv[2])
outFile = os.path.join("/geneious", sys.argv[4])

pathToDocker = sys.argv[6]
pathToGeneiousData = sys.argv[8]
pathToOutData = sys.argv[10]

# Find path to temporary Geneious folder - folders named with largest numbers
# Example: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
def getTaskPath(path):
    sessionDirs = os.listdir(path)
    sessions = [int(s) for s in sessionDirs if re.search('^([0-9]{13,13}){1}$', s)]
    sessionsSort = sorted(sessions, reverse=True)
    session = str(sessionsSort[0])

    taskDirsPath = os.path.join(path, session, "x")
    taskDirs = os.listdir(taskDirsPath)
    tasks = [int(t) for t in taskDirs if re.search('^([0-9]{1,5}){1}$', t)]
    tasksSort = sorted(tasks, reverse=True)
    task = str(tasksSort[0])

    taskPath = os.path.join(taskDirsPath, task, ":/geneious")

    return taskPath

 
mountPath = getTaskPath(pathToGeneiousData)
taskPath = mountPath.split(':/geneious')[0]

# Run emu docker container
subprocess.run( [pathToDocker, "run", "--rm", "-v", mountPath, "emu3.4.4_image", \
    "emu", "abundance", inFile, \
    "--db", "/tmp/geneious/emu-database", \
    "--keep-counts", "--keep-files", "--keep-read-assignments", "--output-unclassified", \
    "--output-dir", "/geneious"] )


# Copy outfiles to user selected folder
shutil.copytree(taskPath, pathToOutData, ignore=shutil.ignore_patterns('*.fastq.gz'), dirs_exist_ok=True)

