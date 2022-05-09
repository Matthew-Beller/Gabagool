import os
from difflib import SequenceMatcher
import srt
def find_subtitle_file(source_directory_subtitle, video_file_name, ignore_subtitle, ignore_video):

    source_directory_subtitle_file_list = os.scandir(source_directory_subtitle)

    directory_found = False

    for entry in source_directory_subtitle_file_list:
        if(entry.is_dir()):
            directory_found = True
            os.chdir(os.path.join(source_directory_subtitle, entry.name))
            for subtitle_file_name in os.listdir(os.getcwd()):
                if(subtitle_file_name.lower().endswith(".srt")):
                    subtitle_file_name_clean = subtitle_file_name.replace(ignore_subtitle, "")
                    subtitle_file_name_clean = ''.join(filter(str.isalnum, subtitle_file_name_clean))
                    subtitle_file_name_clean = subtitle_file_name_clean.lower()
                    video_file_name_clean = video_file_name.replace(ignore_video, "")
                    video_file_name_clean = ''.join(filter(str.isalnum, video_file_name_clean))
                    video_file_name_clean = video_file_name_clean.lower()

                    if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() > 0.70):
                        return os.path.join(os.getcwd(), subtitle_file_name)
    if(not directory_found):
        os.chdir(source_directory_subtitle)
        for subtitle_file_name in os.listdir(os.getcwd()):
            if(subtitle_file_name.endswith(".srt")):
                subtitle_file_name_clean = subtitle_file_name.replace(ignore_subtitle, "")
                subtitle_file_name_clean = ''.join(filter(str.isalnum, subtitle_file_name_clean))
                subtitle_file_name_clean = subtitle_file_name_clean.lower()
                video_file_name_clean = video_file_name.replace(ignore_video, "")
                video_file_name_clean = ''.join(filter(str.isalnum, video_file_name_clean))
                video_file_name_clean = video_file_name_clean.lower()
                if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() > 0.70):
                    return os.path.join(os.getcwd(), subtitle_file_name)
    return None

def find_video_matches(source_directory_subtitle, source_directory_video, intial_directory, output_directory, video_subfolder, save_style_num, key_phrase_clean, ignore_subtitle, ignore_video):
    output_file_directory = output_directory
    if(video_subfolder is not None):
        directory_created = False
        directory_copy_count = 0
        if(save_style_num == 2):
            while(not directory_created):
                if(directory_copy_count == 0):
                    output_file_directory = os.path.join(output_directory, video_subfolder.name)
                else:
                    output_file_directory = os.path.join(output_directory, video_subfolder.name + "(" + str(directory_copy_count) + ")")
                try:
                        os.mkdir(output_file_directory)   
                        directory_created = True      
                except:
                    directory_copy_count += 1
    os.chdir(output_file_directory)
    for video_file_name in os.listdir(intial_directory):
        if(os.path.isfile(os.path.join(intial_directory, video_file_name))):
            subtitle_file = find_subtitle_file(source_directory_subtitle, video_file_name, ignore_subtitle, ignore_video)
            if(subtitle_file != None):
                found_matches_file = find_output_file(video_file_name, save_style_num, source_directory_video, intial_directory)

                os.chdir(output_file_directory)

                find_matching_entries(subtitle_file, key_phrase_clean, found_matches_file, os.path.abspath(video_file_name))
            else:
                return video_file_name
    return None

def find_matching_entries(subtitle_file, key_phrase, found_matches_file, video_file_path):
    with open(subtitle_file, encoding='utf-8-sig') as file:
        subtitle_generator = srt.parse(file)

        subtitles_list = list(subtitle_generator)

    for entry in subtitles_list:
        entry_clean = ''.join(filter(str.isalnum, entry.content)) 
        entry_clean = entry_clean.lower()
        key_phrase_clean = ''.join(filter(str.isalnum, key_phrase))
        key_phrase_clean = key_phrase_clean.lower()
        if(entry_clean.find(key_phrase_clean) != -1):
            found_matches_file.write(video_file_path + "\n")
            found_matches_file.write(str(entry.start) + " --> " + str(entry.end) + "\n")
            found_matches_file.write(entry.content + "\n\n")

    found_matches_file.close()

def find_output_file(video_file_name, save_style_num, source_directory_video, intial_directory = None):
    if(save_style_num == 2 or save_style_num == 4):
        found_matches_file_name = video_file_name + ".txt"
    elif(save_style_num == 0):
        found_matches_file_name = os.path.basename(source_directory_video) + ".txt"
    else:
        found_matches_file_name = os.path.basename(intial_directory) + ".txt"
    try:
        found_matches_file = open(found_matches_file_name,"x")
    except:
        if(save_style_num == 2):
            print(found_matches_file_name + "already exists.")
    found_matches_file = open(found_matches_file_name,"a")

    return found_matches_file