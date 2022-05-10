import os
from difflib import SequenceMatcher
import srt


class FoundSubtitleMatch:
    def __init__(self, label, start, end, content):
        self.label = label
        self.start = start
        self.end = end
        self.content = content


## Changed fixed cleaned
def find_subtitle_file(source_directory_subtitle, video_file_name, ignore_phrase_subtitle = "", ignore_phrase_video = ""):

    video_file_name_clean = clean_input(video_file_name, ignore_phrase_video)

    source_directory_subtitle_file_list = os.scandir(source_directory_subtitle)

    directory_found = False

    for entry in source_directory_subtitle_file_list:
        if(entry.is_dir()):
            directory_found = True
            os.chdir(os.path.join(source_directory_subtitle, entry.name))
            for subtitle_file_name in os.listdir(os.getcwd()):
                if(subtitle_file_name.endswith(".srt")):
                    subtitle_file_name_clean = clean_input(subtitle_file_name, ignore_phrase_subtitle)
                    if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() > 0.70):
                        return os.path.join(os.getcwd(), subtitle_file_name)
    if(not directory_found):
        os.chdir(source_directory_subtitle)
        for subtitle_file_name in os.listdir(os.getcwd()):
            if(subtitle_file_name.endswith(".srt")):
                subtitle_file_name_clean = clean_input(subtitle_file_name, ignore_phrase_subtitle)
                if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() > 0.70):
                    return os.path.join(os.getcwd(), subtitle_file_name)
    return None

def find_video_matches(source_directory_subtitle, source_directory_video, intial_directory, output_directory, video_subfolder, save_style_num, key_phrase, ignore_subtitle, ignore_video):
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
                os.chdir(output_file_directory)
                found_matches_file = find_output_file(source_directory_video, video_file_name, save_style_num, intial_directory)


                found_entries = find_matching_entries(subtitle_file, key_phrase, os.path.abspath(video_file_name))

                for found_entry in found_entries:
                    found_matches_file.write(found_entry.label + "\n")
                    found_matches_file.write(str(found_entry.start) + " --> " + str(found_entry.end) + "\n")
                    found_matches_file.write(found_entry.content + "\n\n")
                found_matches_file.close()
            else:
                return video_file_name
    return None

## Changed Fixed
def find_matching_entries(subtitle_file, key_phrase, entry_label):
    found_matches_list = []
    
    with open(subtitle_file, encoding='utf-8-sig') as file:
        subtitle_generator = srt.parse(file)

        subtitles_list = list(subtitle_generator)

    for entry in subtitles_list:
        entry_clean = clean_input(entry.content)

        key_phrase_clean = clean_input(key_phrase)

        if(entry_clean.find(key_phrase_clean) != -1):
            found_matches_list.append(FoundSubtitleMatch(entry_label, entry.start, entry.end, entry.content))

    return found_matches_list

def find_output_file(source_directory, file_name, save_style_num, intial_directory = None):
    if(save_style_num == 2 or save_style_num == 4):
        found_matches_file_name = file_name + ".txt"
    elif(save_style_num == 0):
        found_matches_file_name = os.path.basename(source_directory) + ".txt"
    else:
        found_matches_file_name = os.path.basename(intial_directory) + ".txt"
    try:
        found_matches_file = open(found_matches_file_name,"x")
    except:
        if(save_style_num == 2):
            print(found_matches_file_name + "already exists.")
    found_matches_file = open(found_matches_file_name,"a")

    return found_matches_file

def clean_input(file_name, ignore_phrase = ""):
    file_name_clean = file_name.replace(ignore_phrase, "")
    file_name_clean = ''.join(filter(str.isalnum, file_name_clean))
    file_name_clean = file_name_clean.lower()

    return file_name_clean
