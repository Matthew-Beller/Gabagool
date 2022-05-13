from moviepy.editor import VideoFileClip, concatenate_videoclips
import srt
import os
from datetime import timedelta

def clipTogetherVideos(video_source, subtitle_source, output_directory):
      clipList = []

      with open(subtitle_source, encoding='ISO-8859-1') as file:
         subtitle_generator = srt.parse(file)

         subtitles_list = list(subtitle_generator)

         for entry in subtitles_list:
            clipList.append(VideoFileClip(entry.proprietary).subclip(str(entry.start), str(entry.end)))

         final_clip = concatenate_videoclips(clipList, method="compose")
         os.chdir(output_directory)
         final_clip.write_videofile("my_concatenation.mp4")
