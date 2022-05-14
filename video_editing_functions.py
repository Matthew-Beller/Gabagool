from xml.dom import IndexSizeErr
from moviepy.editor import VideoFileClip, concatenate_videoclips
from numpy import source
import srt
import os
from datetime import timedelta
import tempfile
import time

def clipTogetherVideos(video_source, subtitle_source, output_directory):

      start = time.time()

      clip_list = []
      video_number = 1
      video_counter = 0

      clip_counter = 0

      round_number = 1

      source_name = os.path.basename(subtitle_source)

      temp_dir = tempfile.mkdtemp()
      os.chdir(temp_dir)
      print(os.getcwd())
      os.mkdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

      os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

      print(os.getcwd())
      with open(subtitle_source, encoding='ISO-8859-1') as file:
         subtitle_generator = srt.parse(file)

         subtitles_list = list(subtitle_generator)
         for entry in subtitles_list:

            clip_list.append(VideoFileClip(entry.proprietary).subclip(str(entry.start), str(entry.end)))

            video_counter = video_counter + 1
            if(video_counter == 10):
               video_counter = 0
               temp_clip = concatenate_videoclips(clip_list, method="compose")
               temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
               video_number += 1
               clip_list.clear()
         
         temp_clip = concatenate_videoclips(clip_list, method="compose")
         temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")

         clip_list.clear()
         video_counter = 0
         
         os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         file_list = os.listdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         while(len(file_list) > 10):
            clip_list.clear()
            clip_counter = 1
            video_number = 1

            round_number = round_number + 1 
            os.chdir(temp_dir)
            os.mkdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
            os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))

            file_list = os.listdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))

            for entity in file_list:
               for file in file_list:
                  if(file == ("TMP_" + source_name + "_" + str(clip_counter) + ".mp4")):
                     clip_list.append(VideoFileClip(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1), file)))
                     clip_counter = clip_counter + 1
                     video_counter = video_counter + 1
                     if(video_counter == 10):
                        video_counter = 0
                        temp_clip = concatenate_videoclips(clip_list, method="compose")
                        os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
                        temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
                        video_number = video_number + 1
                        os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))
                        clip_list.clear()

            os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))
            temp_clip = concatenate_videoclips(clip_list, method="compose")
            temp_clip.write_videofile("TMP_" + source_name + "_" + str(video_number) + ".mp4")
            os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number-1)))
            clip_list.clear()
      
         clip_counter = clip_counter + 1
            
         file_list = os.listdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         os.chdir(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)))

         clip_counter = 1
         clip_list.clear()
         for entity in file_list:
            for file in file_list:
               if(file == ("TMP_" + source_name + "_" + str(clip_counter) + ".mp4")):
                  clip_list.append(VideoFileClip(os.path.join(os.path.join(os.path.abspath(temp_dir), "TMP_Edit_Round_" + str(round_number)), file)))
                  clip_counter = clip_counter + 1

         final_clip = concatenate_videoclips(clip_list, method="compose")

         os.chdir(output_directory)
         final_clip.write_videofile("my_concatenation.mp4")

         end = time.time()

         print(end - start)