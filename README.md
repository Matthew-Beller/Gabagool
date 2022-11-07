# Gabagool

Gabagool is an automated video editing program that uses subtitle files to edit videos.
This program works by searching subtitle files for user entered key words, then creating clips of every instance of these key words from source video files.
Check out our website [here](https://www.getgabagool.com/)

Before using Gabagool complete the following steps
1.	Install python
2.	Download ffmpeg and add it as a path variable for cmd
3.	Install pip
4.	Extract the contents of the Gabagool.zip file
5.	Install the required python packages using the requirements.txt file. The following command may be helpful: pip install -r requirements.txt (requirements.txt is the path to the requirements.txt file found in the unzipped Gabagool directory)

Gabagool currently only supports .srt subtitle files. Convert any subtitles to .srt before use.

Due to the inconsistency of subtitle and video file quality, it is recommended to verify synchronization, accuracy, and quality of subtitle and video files before use.

After building subtitle found matches file, do NOT alter the file structure or names of the source video files used in the search. This causes file not found errors when creating and saving video clips.

If the file structure of the source video files is altered, regenerate the subtitle matches file before use.
