import os
from difflib import SequenceMatcher
import srt
import subprocess
import time

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

def find_video_matches(source_directory_subtitle, source_directory_video, output_directory, save_style_num, key_phrase, ignore_subtitle = "", ignore_video = ""):
    start = time.time()
    output_file_directory = output_directory

    source_directory_video_file_list = os.scandir(source_directory_video)

    for file in source_directory_video_file_list:
        if(file.is_dir()):
            current_video_subdirectory = os.path.join(source_directory_video, file)

            if(save_style_num == 2):
                directory_created = False
                directory_copy_count = 0
                while(not directory_created):
                    if(directory_copy_count == 0):
                        output_file_directory = os.path.join(output_directory, file.name)
                    else:
                        output_file_directory = os.path.join(output_directory, file.name + "(" + str(directory_copy_count) + ")")
                    try:
                        os.mkdir(output_file_directory)   
                        directory_created = True      
                    except:
                        directory_copy_count += 1

        os.chdir(output_file_directory)

        for video_file_name in os.listdir(current_video_subdirectory):
            video_file_path = os.path.join(current_video_subdirectory, video_file_name)
            if(os.path.isfile(video_file_path) and check_if_video_file(video_file_path)):
                subtitle_file = find_subtitle_file(source_directory_subtitle, video_file_name, ignore_subtitle, ignore_video)
                if(subtitle_file != None):
                    os.chdir(output_file_directory)
                    found_matches_file = find_output_file(video_file_name, save_style_num, source_directory_video, current_video_subdirectory)


                    found_entries = find_matching_entries(subtitle_file, key_phrase, os.path.abspath(video_file_name))

                    for found_entry in found_entries:
                        found_matches_file.write(found_entry.label + "\n")
                        found_matches_file.write(str(found_entry.start) + " --> " + str(found_entry.end) + "\n")
                        found_matches_file.write(found_entry.content + "\n\n")
                    found_matches_file.close()
                    end = time.time()
                    print(end-start)
                else:
                    return video_file_name
        else:
            if(check_if_video_file(os.path.join(source_directory_video, file))):
                subtitle_file = find_subtitle_file(source_directory_subtitle, file.name, ignore_subtitle, ignore_video)
                if(subtitle_file != None):
                    os.chdir(output_file_directory)
                    found_matches_file = find_output_file(video_file_name, save_style_num, source_directory_video, current_video_subdirectory)


                    found_entries = find_matching_entries(subtitle_file, key_phrase, os.path.abspath(video_file_name))

                    for found_entry in found_entries:
                        found_matches_file.write(found_entry.label + "\n")
                        found_matches_file.write(str(found_entry.start) + " --> " + str(found_entry.end) + "\n")
                        found_matches_file.write(found_entry.content + "\n\n")
                    found_matches_file.close()
                    end = time.time()
                    print(end-start)
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

def find_output_file(file_name, save_style_num, source_directory = None, intial_directory = None):
    if(save_style_num == 2 or save_style_num == 4 or source_directory == None):
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

def check_if_video_file(path):
    if(path.lower().endswith(('.mkv', '.mp4', '.webm', '.mov', '.avi', '.ogv'))):
        return True
    if(os.path.isdir(path)):
        return False
    try:
        process = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets,codec_type', '-of', 'csv=p=0', '%s' % str(path)], capture_output=True)
        std_out_str = process.stdout.decode("utf-8")
        process_output_list = std_out_str.split(",")
        if(process_output_list[0] == "video" and int(process_output_list[1]) >= 0):
            print("good" + str(path))
            return True
        else:
            print("bad" + str(path))
            return False
    except:
        print("error")
        return False

