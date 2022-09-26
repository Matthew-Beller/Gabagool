from __future__ import unicode_literals
from __future__ import print_function
import sys
from time import sleep
from gooey import Gooey, GooeyParser

from xml.dom import IndexSizeErr
from moviepy.editor import VideoFileClip, concatenate_videoclips
from numpy import source
import srt
import os
from datetime import timedelta
import datetime
import tempfile
import time

def saveAsIndividualClips(subtitle_source, output_directory, buffer_seconds_start, buffer_seconds_end):
   video_number = 1
   source_name = os.path.splitext(os.path.basename(subtitle_source))[0]

   os.chdir(output_directory)
   os.mkdir(os.path.join(output_directory, source_name + "_videos"))
   os.chdir(os.path.join(output_directory, source_name + "_videos"))

   with open(subtitle_source, encoding='utf-8') as file:
      subtitle_generator = srt.parse(file)

      subtitles_list = list(subtitle_generator)
      buffer_start_datetime = datetime.timedelta(seconds=buffer_seconds_start)
      buffer_end_datetime = datetime.timedelta(seconds=buffer_seconds_end)
      
      for entry in subtitles_list:
         if(entry.start > buffer_start_datetime):
            entry.start = entry.start - buffer_start_datetime
         else:
            entry.start -= entry.start
         entry.end = entry.end + buffer_end_datetime

   total_clips = len(subtitles_list)

   for entry in subtitles_list:
      VideoFileClip(entry.proprietary).subclip(str(entry.start), str(entry.end)).write_videofile(source_name + "_" + str(video_number) + ".mp4", logger=None)
      print(f"progress: {video_number}/{total_clips}")
      video_number += 1 

def mergeMultipleClips(subtitle_source, output_directory, buffer_seconds_start, buffer_seconds_end):

      start = time.time()

      GROUPING_COUNT = 8
      clip_list = []
      video_number = 1
      video_counter = 0

      clip_counter = 0

      round_number = 1

      source_name = os.path.splitext(os.path.basename(subtitle_source))[0]

      temp_dir = tempfile.mkdtemp()
      os.chdir(temp_dir)
      print(os.getcwd())
      os.mkdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

      os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

      print(os.getcwd())
      with open(subtitle_source, encoding='utf-8') as file:
         subtitle_generator = srt.parse(file)

         subtitles_list = list(subtitle_generator)
         entry_number = 0
         buffer_start_datetime = datetime.timedelta(seconds=buffer_seconds_start)
         buffer_end_datetime = datetime.timedelta(seconds=buffer_seconds_end)

         for entry in subtitles_list:
            if(entry.start > buffer_start_datetime):
               entry.start = entry.start - buffer_start_datetime
            else:
               entry.start -= entry.start
            entry.end = entry.end + buffer_end_datetime

         while(entry_number < len(subtitles_list)-1):
            if(subtitles_list[entry_number].end >= subtitles_list[entry_number+1].start):
               subtitles_list[entry_number].end = subtitles_list[entry_number+1].end
               del subtitles_list[entry_number+1]
            else:
               entry_number += 1

         
         clip_number = 1
         for entry in subtitles_list:
            clip_list.append(VideoFileClip(entry.proprietary).subclip(str(entry.start), str(entry.end)))
            print("Added Clip" + str(clip_number))
            print(clip_list)
            clip_number +=1
            video_counter = video_counter + 1
            if(video_counter == GROUPING_COUNT):
               video_counter = 0
               temp_start = time.time()
               temp_clip = concatenate_videoclips(clip_list, method="compose")
               temp_end = time.time()

               print("\n\n\nconcat" + str(temp_end-temp_start) + "\n\n\n")
               temp_start = time.time()
               temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4", fps=30)
               temp_end = time.time()
               print("\n\n\n\nwrite" + str(temp_end-temp_start) + "\n\n\n")
               video_number += 1
               temp_clip.close()
               del temp_clip

               for clip in clip_list:
                  clip.close()
                  del clip
               clip_list = []

         if(len(clip_list) > 0):
            temp_clip = concatenate_videoclips(clip_list, method="compose")
            temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4", fps=30)
            temp_clip.close()
            del temp_clip

         for clip in clip_list:
            clip.close()
            del clip
         clip_list = []

         video_counter = 0
         
         os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         file_list = os.listdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         while(len(file_list) > GROUPING_COUNT):
            for clip in clip_list:
               clip.close()
               del clip
            clip_list = []

            clip_counter = 1
            video_number = 1

            round_number = round_number + 1 
            os.chdir(temp_dir)
            os.mkdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
            os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))

            for entity in file_list:
               for file in file_list:
                  if(file == ("TMP_" + source_name + "_" + str(clip_counter) + ".mp4")):
                     clip_list.append(VideoFileClip(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1), file)))
                     clip_counter = clip_counter + 1
                     video_counter = video_counter + 1
                     if(video_counter == GROUPING_COUNT):
                        video_counter = 0
                        temp_start = time.time()
                        temp_clip = concatenate_videoclips(clip_list, method="compose")
                        temp_end = time.time()
                        print("\n\n\n\n\n\ncontcattime" + str(temp_end - temp_start) +"\n\n\n\n\n")
                        os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
                        temp_start = time.time()
                        temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4", fps=30)
                        temp_end = time.time()
                        print("\n\n\n\n\n\nwritetiem:" + str(temp_end - temp_start) + "\n\n\n\n\n\n\n")
                        temp_clip.close()
                        del temp_clip
                        video_number = video_number + 1
                        os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))
                        for clip in clip_list:
                           clip.close()
                           del clip
                        del clip_list
                        clip_list = []
            file_list = os.listdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number))) 

            os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
            if(len(clip_list) > 0):
               temp_clip = concatenate_videoclips(clip_list, method="compose")
               temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4", fps=30)
               temp_clip.close()
               del temp_clip
            os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))
            for clip in clip_list:
               clip.close()
               del clip
            del clip_list
            clip_list = []

         clip_counter = clip_counter + 1
            
         file_list = os.listdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         clip_counter = 1

         for clip in clip_list:
            clip.close()
            del clip

         del clip_list
         clip_list = []
############################################ fps bug lies in here VVVVVVVVVVVVVVVVVVvv
## no it doesnt prolbem lies 
         for entity in file_list:
            for file in file_list:
               if(file == ("TMP_" + source_name + "_" + str(clip_counter) + ".mp4")):
                  print("clip_counter" + str(clip_counter))
                  clip_list.append(VideoFileClip(os.path.join(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)), file)))
                  clip_counter = clip_counter + 1

######################################################33 fps bug lies in here ^^^^^^^^^^^^^^

## funky error, check using different file
         print('\n\n\n\n\n\n\n\n\nmade it to final clip')

         final_clip = concatenate_videoclips(clip_list, method="compose")

         os.chdir(output_directory)
         final_clip.write_videofile("my_concatenation.mp4", fps=30)

         for clip in clip_list:
            clip.close()
            del clip
         del clip_list
         clip_list = []

         final_clip.close()
         del final_clip

         end = time.time()

         print("GROUPING_COUNT: " + str(GROUPING_COUNT))
         print("Total time: " + str(end - start))

         #TODO: Fix bug where merging clips presents video fps error