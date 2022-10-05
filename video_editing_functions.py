from __future__ import unicode_literals
from __future__ import print_function

import srt
import os
import datetime
import tempfile
import subprocess
import math


def saveAsIndividualClips(subtitle_source, output_directory, buffer_seconds_start, buffer_seconds_end):
   video_number = 1
   source_name = os.path.splitext(os.path.basename(subtitle_source))[0]

   os.chdir(output_directory)

   output_path_string = str(os.path.join(output_directory, source_name + "_videos"))

   duplicate_count = 0
   while(os.path.isdir(output_path_string)):
         duplicate_count +=1 
         output_path_string = str(os.path.join(output_directory, source_name + "_videos(" + str(duplicate_count) + ")"))

   os.mkdir(output_path_string)
   os.chdir(output_path_string)

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

   max_numbers_places = int(math.log10(total_clips))+1
   for entry in subtitles_list:
      try:
         process = subprocess.run(['ffmpeg', '-loglevel', '-8', '-ss', '%s' % (str(entry.start)[:11]), '-i', '%s' % (str(entry.proprietary)), '-t', (str(entry.end-entry.start)[:11]), '-map', '0', '%s' % (source_name + "_" + str(video_number).zfill(max_numbers_places) + ".mp4")])
      except:
         print("Error")
      print(f"progress: {video_number}/{total_clips}")
      video_number += 1 

def mergeMultipleClips(subtitle_source, output_directory, buffer_seconds_start, buffer_seconds_end):
      video_number = 1

      source_name = os.path.splitext(os.path.basename(subtitle_source))[0]

      temp_dir = tempfile.mkdtemp()
      os.chdir(temp_dir)

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

      entry_index = 0
      while(entry_index < len(subtitles_list)-1):
         if(subtitles_list[entry_index].proprietary == subtitles_list[entry_index+1].proprietary):
            if(subtitles_list[entry_index].end >= subtitles_list[entry_index+1].start):
               subtitles_list[entry_index].end = subtitles_list[entry_index+1].end
               del subtitles_list[entry_index+1]
            else:
               entry_index += 1
         else:
            entry_index += 1
      total_clips = len(subtitles_list)
      max_numbers_places = int(math.log10(total_clips))+1

      video_number = 1
      for entry in subtitles_list:
         process = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', '%s' % (str(entry.start)[:11]), '-i', '%s' % (str(entry.proprietary)), '-to', (str(entry.end-entry.start)[:11]), '-map', '0', '%s' % (str(source_name + "_" + str(video_number).zfill(max_numbers_places) + ".mp4").replace(' ', '_'))])
         video_number += 1
         print(f"progress: {video_number}/{total_clips}")
      os.chdir(temp_dir)
      file_list = os.listdir(temp_dir)

      temp_video_list_file = open('temp_video_list_file.txt', "w")

      for file in file_list:
         temp_video_list_file.write('file ' + str(os.path.splitdrive(os.path.join(str(os.path.abspath(temp_dir)), str(file)))[1]).replace('\\', '/').replace(' ', '_') + '\n')

      temp_video_list_file.close()

      input_path_string = str(os.path.join(str(os.path.abspath(temp_dir)), 'temp_video_list_file.txt'))
      output_path_string = str(os.path.join(str(os.path.abspath(output_directory)), source_name) + ".mp4")
      
      duplicate_count = 0
      while(os.path.isfile(output_path_string)):
         duplicate_count +=1 
         output_path_string = str(os.path.join(str(os.path.abspath(output_directory)), source_name + "(" + str(duplicate_count) + ")") + ".mp4")
      try:
         process = subprocess.run(['ffmpeg', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', '%s' % (input_path_string), '-c', 'copy', '%s' % (output_path_string)])
      except:
         print("Error")