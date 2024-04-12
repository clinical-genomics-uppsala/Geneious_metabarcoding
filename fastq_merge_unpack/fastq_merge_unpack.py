import glob
import shutil
import os
 
# Copy and merge fastq.gz files from barcode subfolders in "input/fastq_pass" directory to "output" directory
scriptPath=os.path.dirname(__file__)

fastqDirs=sorted(glob.glob(scriptPath + "\\input\\fastq_pass\\barcode*"))
barcodes=[d.split(scriptPath + "\\input\\fastq_pass\\")[1] for d in fastqDirs]

# Merge files
for d, b in zip(fastqDirs, barcodes):
  with open((scriptPath + "\\output\\" + b + ".fastq.gz"),'wb') as mergeFile:
    for f in glob.glob(os.path.join(d, "*fastq.gz")):
      with open(f,'rb') as fastqFile:
        shutil.copyfileobj(fastqFile, mergeFile)