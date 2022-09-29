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
import subprocess


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
      # print(os.getcwd())
      # os.mkdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

      # os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

      video_number = 1
      source_name = os.path.splitext(os.path.basename(subtitle_source))[0]

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
         video_number += 1 
      # with open(subtitle_source, encoding='utf-8') as file:
      #    subtitle_generator = srt.parse(file)

      #    subtitles_list = list(subtitle_generator)
      #    entry_number = 0
      #    buffer_start_datetime = datetime.timedelta(seconds=buffer_seconds_start)
      #    buffer_end_datetime = datetime.timedelta(seconds=buffer_seconds_end)

      #    for entry in subtitles_list:
      #       if(entry.start > buffer_start_datetime):
      #          entry.start = entry.start - buffer_start_datetime
      #       else:
      #          entry.start -= entry.start
      #       entry.end = entry.end + buffer_end_datetime

      #    while(entry_number < len(subtitles_list)-1):
      #       if(subtitles_list[entry_number].end >= subtitles_list[entry_number+1].start):
      #          subtitles_list[entry_number].end = subtitles_list[entry_number+1].end
      #          del subtitles_list[entry_number+1]
      #       else:
      #          entry_number += 1

         
      #    clip_number = 1
      #    for entry in subtitles_list:
      #       clip_list.append(VideoFileClip(entry.proprietary).subclip(str(entry.start), str(entry.end)))
      #       clip_number +=1
      #       # video_counter = video_counter + 1
      #       # os.chdir(output_directory)
      #       temp_clip = concatenate_videoclips(clip_list, method="compose")
      #       temp_clip.write_videofile(os.path.join(temp_dir, source_name + "_" + str(clip_number) + ".mov"))
      #       temp_clip.close()
      #       del temp_clip
      #       for clip in clip_list:
      #          clip.close()
      #          del clip
      #       clip_list = []
      #       # os.chdir(temp_dir)
      #       # if(video_counter == GROUPING_COUNT):
      #       #    video_counter = 0
      #       #    temp_start = time.time()
      #       #    temp_clip = concatenate_videoclips(clip_list, method="compose")
      #       #    temp_end = time.time()

      #       #    print("\n\n\nconcat" + str(temp_end-temp_start) + "\n\n\n")
      #       #    temp_start = time.time()
      #       #    temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
      #       #    temp_end = time.time()
      #       #    print("\n\n\n\nwrite" + str(temp_end-temp_start) + "\n\n\n")
      #       #    video_number += 1
      #       #    temp_clip.close()
      #       #    del temp_clip

      #          # for clip in clip_list:
      #          #    clip.close()
      #          #    del clip
      #          # clip_list = []
      os.chdir(temp_dir)
      file_list = os.listdir(temp_dir)

      temp_video_list_file = open('temp_video_list_file.txt', "w")

      file_counter = 0
      video_counter = 0
      round_number = round_number + 1 

      for file in file_list:
         temp_video_list_file.write('file ' + str(os.path.splitdrive(os.path.join(str(os.path.abspath(temp_dir)), str(file)))[1]).replace('\\', '/') + '\n')
      temp_video_list_file.close()
      os.chdir(temp_dir)
      print(os.getcwd())
      input_path_string = str(os.path.join(str(os.path.abspath(temp_dir)), 'temp_video_list_file.txt'))
      output_path_string = str(os.path.join(str(os.path.abspath(output_directory)), source_name) + ".mp4")
      print(input_path_string)
      print(output_path_string)
      try:
         process = subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', '%s' % (input_path_string), '-c', 'copy', '%s' % (output_path_string)])
      except:
         print("akjdfkjsafkjah")
      # process = subprocess.run(['ffmpeg', '-f', 'concat', '-i', 'C:\Users\Matthew\AppData\Local\Temp\\tmpzj7k_215\\temp_video_list_file.txt', '-c', 'copy', 'C:\Users\Matthew\Desktop\sopranos_video_found_entries_capocollo_gabagoo.mp4'])
      # ffmpeg -f concat -i C:\Users\Matthew\AppData\Local\Temp\tmpzj7k_215\temp_video_list_file.txt -c copy C:\Users\Matthew\Desktop\sopranos_video_found_entries_capocollo_gabagoo.mp4

      # os.mkdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
      # os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
      # print((str(os.path.join(str(os.path.abspath(temp_dir)), 'temp_video_list_file.txt'))))
      # for file in file_list:
      #    if(file_counter == GROUPING_COUNT):
      #       video_counter +=1 
      #       try:
      #          process = subprocess.run(['ffmpeg', '-f', 'concat', '-i', '%s' % ((str(os.path.join(str(os.path.abspath(temp_dir)), 'temp_video_list_file.txt')))), '-c', 'copy', '%s' % ("temp_group_video" + "_" + str(video_counter))])
      #       except:
      #          print("ERRROROOROR")
      #       temp_video_list_file = open((str(os.path.join(str(os.path.abspath(temp_dir)), 'temp_video_list_file.txt'))), 'w')
      #       temp_video_list_file = open((str(os.path.join(str(os.path.abspath(temp_dir)), 'temp_video_list_file.txt'))), 'a')
      #    else:
      #       temp_video_list_file.write('file ' + str(os.path.abspath(file)) + '\n')
      #       file_counter += 1
      


      # ffmpeg -f concat -i mylist.txt -c copy output.mp4 use this, need to create temp file with name in order to reference
      # use process to do this 
      # closing process?
      # if(len(clip_list) > 0):
      #    temp_clip = concatenate_videoclips(clip_list, method="compose")
      #    temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
      #    temp_clip.close()
      #    del temp_clip

      # for clip in clip_list:
      #    clip.close()
      #    del clip
      # clip_list = []

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
                     temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
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
            temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
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

      for entity in file_list:
         for file in file_list:
            if(file == ("TMP_" + source_name + "_" + str(clip_counter) + ".mp4")):
               clip_list.append(VideoFileClip(os.path.join(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)), file)))
               clip_counter = clip_counter + 1

      final_clip = concatenate_videoclips(clip_list, method="compose")

      os.chdir(output_directory)
      final_clip.write_videofile(source_name + "_video.mp4")

      for clip in clip_list:
         clip.close()
         del clip
      del clip_list
      clip_list = []

      final_clip.close()
      del final_clip

      end = time.time()

      print("Total time: " + str(end - start))



# giong to have to get rid of moviepy due to this fps garabge
# chagne to raw ffmpeg processes

#  try:
#         process = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets,codec_type', '-of', 'csv=p=0', '%s' % str(path)], capture_output=True)
#         std_out_str = process.stdout.decode("utf-8")
#         process_output_list = std_out_str.split(",")
#         if(process_output_list[0] == "video" and int(process_output_list[1]) >= 0):
#             print("good" + str(path))
#             return True
#         else:
#             print("bad" + str(path))
#             return False
#     except:
#         print("error")
#         return False

# ffmpeg -i opening.mkv -i episode.mkv -i ending.mkv -filter_complex "[0:v] [0:a] [1:v] [1:a] [2:v] [2:a] concat=n=3:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" output.mkv