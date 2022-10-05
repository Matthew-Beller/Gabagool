import os
from difflib import SequenceMatcher
import srt
import subprocess
import chardet

class FoundSubtitleMatch:
    def __init__(self, label, start, end, content):
        self.label = label
        self.start = start
        self.end = end
        self.content = content

def find_subtitle_matches_single(source_file_video, source_file_subtitle, key_phrase_list, output_directory, ignore_spaces, ignore_punctuation, case_sensitive, save_style_num):
    if(check_if_video_file(source_file_video)):
        source_name = os.path.basename(source_file_video)
        key_phrase_clean = ""
        
        for phrase in key_phrase_list:
            key_phrase_clean = key_phrase_clean + "_" + str(phrase)

        key_phrase_clean = key_phrase_clean.replace(' ', '_')

        punctuation_list = '''!{};:'"\,<>./?@#$%^&*~'''
        for char in key_phrase_clean:
            if char in punctuation_list:
                key_phrase_clean = key_phrase_clean.replace(char, "")

        duplicate_count = 0
        new_output_directory = os.path.join(output_directory, source_name + "_" + key_phrase_clean)

        while(os.path.isdir(new_output_directory)):
            duplicate_count +=1 
            new_output_directory = str(os.path.join(output_directory, source_name + "_" + key_phrase_clean + "(" + str(duplicate_count) + ")"))
        os.mkdir(new_output_directory)

        os.chdir(new_output_directory)
        found_matches_file = find_output_file(os.path.basename(source_file_video), save_style_num, key_phrase_list)
        found_entries = find_matching_entries(source_file_subtitle, key_phrase_list, source_file_video, ignore_spaces, ignore_punctuation, case_sensitive)

        for found_entry in found_entries:
            found_entry.proprietary = source_file_video
            found_matches_file.write(found_entry.to_srt())
        found_matches_file.close()
    else:
        print("Invalid video file.")

def find_subtitle_file(source_directory_subtitle, video_file_name, ignore_phrase_subtitle = "", ignore_phrase_video = "", comparison_tolerance = 0.70):
    """
    Matches subtitle file to video file based on file names.\n
    Match is found SequenceMatcher ratio function returns a result greater than comparison tolerance.\n
    Searches entire subtitle source directory including one subdirectory of depth\n
    Returns file path to matching subtitle file if successful.\n
    Returns None on failure.
    """
    video_file_name_clean = clean_input(video_file_name, ignore_phrase_video)

    for root, dirs, files in os.walk(source_directory_subtitle):
        for file in files:
            if(str(file).endswith(".srt")):
                subtitle_file_name_clean = clean_input(file, ignore_phrase_subtitle)
                if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() >= comparison_tolerance):
                    return os.path.join(root, file)

    return None

def find_subtitle_matches_batch(source_directory_subtitle, source_directory_video, output_directory, save_style_num, key_phrase_list, ignore_spaces, ignore_punctutation, case_sensitive, ignore_subtitle_list, ignore_video_list):
    """
    Find instances of key words within srt files found in subtitle source directroy. Matches these instances with corresponding video files in video source directory.\n
    Saves files with matching instances, video file directory, times, and contents to output directory.\n
    Save style 2 or 4 = One file per video\n
    Save sytle 0 = One large file with all videos\n
    Save style 1 = One file per sub directory\n
    Appends existing files same names file is found.\n
    ignore_subtitle_list and ignore_video arguments_list ignore certain phrases with subtitle and video file names when pairing these files together\n
    """
    source_name = os.path.splitext(os.path.basename(source_directory_subtitle))[0]
    key_phrase_clean = ""
    
    for phrase in key_phrase_list:
        key_phrase_clean = key_phrase_clean + "_" + str(phrase)

    key_phrase_clean = key_phrase_clean.replace(' ', '_')

    punctuation_list = '''!{};:'"\,<>./?@#$%^&*~'''
    for char in key_phrase_clean:
        if char in punctuation_list:
            key_phrase_clean = key_phrase_clean.replace(char, "")

    os.chdir(output_directory)
    if(save_style_num != 0):
        output_root = create_directory_tree_without_files(source_directory_video, output_directory, source_name + "_found_entries" + str(key_phrase_clean))
    else:
        duplicate_count = 0
        output_root = os.path.join(output_directory, source_name + "_found_entries" + str(key_phrase_clean))

        while(os.path.isdir(output_root)):
            duplicate_count +=1 
            output_root = str(os.path.join(output_directory, source_name + "_found_entries" + str(key_phrase_clean) + "(" + str(duplicate_count) + ")"))
        os.mkdir(output_root)
        os.chdir(output_root)

    for root, dirs, files in os.walk(source_directory_video):
        for file in files:
            file_path = os.path.join(root, file)
            if(os.path.isfile(file_path) and check_if_video_file(file_path)):
                subtitle_file = find_subtitle_file(source_directory_subtitle, file, ignore_subtitle_list, ignore_video_list)
                if(subtitle_file != None):
                    if(save_style_num != 0):
                        os.chdir(os.path.join(output_root, os.path.relpath(root, source_directory_video)))
                    found_matches_file = find_output_file(file, save_style_num, key_phrase_list, source_directory_video, os.path.split(root)[1])
                    found_entries = find_matching_entries(subtitle_file, key_phrase_list, file_path, ignore_spaces, ignore_punctutation, case_sensitive)
                    for found_entry in found_entries:
                        # In srt library, proprietary information is stored after time stamp
                        # To store directory of source video file, path is written in place of the proprietary information
                        found_entry.proprietary = file_path
                        found_matches_file.write(found_entry.to_srt())
                    found_matches_file.close()
                else:
                    print("Cannot find subtitle file for " + file)
    return None

def find_matching_entries(subtitle_file, key_phrase_list, entry_label, ignore_spaces, ignore_punctuation, case_sensitive):
    """
    Finds instances of key word within srt files.\n
    Returns list of matched phrases including start and end time.\n
    Entries labeled by label argument\n
    Returns list of FoundSubtitleMatch objects
    """
    found_matches_list = []

    key_phrase_list_clean = []

    matchFound = False

    for phrase in key_phrase_list:
        key_phrase_list_clean.append(clean_string(phrase, ignore_spaces, ignore_punctuation, case_sensitive))

    with open(subtitle_file, "rb") as file:
        contents = file.read()

        original_encoding = chardet.detect(contents)

        if(original_encoding["encoding"] != "utf-8"):
            check_file = contents.decode(original_encoding["encoding"]).encode("utf-8")
        else:
            check_file = contents
        subtitle_generator = srt.parse(check_file.decode("utf-8"))

        subtitles_list = list(subtitle_generator)

    for entry in subtitles_list:
        entry_clean = clean_string(entry.content, ignore_spaces, ignore_punctuation, case_sensitive)
        for phrase in key_phrase_list_clean:
            if(entry_clean.find(phrase) != -1):
                matchFound = True
        if(matchFound):
            found_matches_list.append(entry)
            matchFound = False

    return found_matches_list

def find_output_file(file_name, save_style_num, key_phrase_list, source_directory = None, sub_directory = None):
    """
    Determines output file name based on file name, save style, source directory and sub directory.\n
    Save style 2 or 4 = One file per video\n
    Save sytle 0 = One large file with all videos\n
    Save style 1 = One file per sub directory\n
    Appends existing files same names file is found.\n
    Returns file where output will be written.
    """
    key_phrase_clean = ""
    
    for phrase in key_phrase_list:
        key_phrase_clean = key_phrase_clean + "_" + str(phrase)

    key_phrase_clean = key_phrase_clean.replace(' ', '_')

    punctuation_list = '''!{};:'"\,<>./?@#$%^&*~'''
    for char in key_phrase_clean:
        if char in punctuation_list:
            key_phrase_clean = key_phrase_clean.replace(char, "")

    if(save_style_num == 2 or save_style_num == 4 or source_directory == None):
        found_matches_file_name = os.path.splitext(file_name)[0] + "_found_entries" + str(key_phrase_clean) + ".srt"
    elif(save_style_num == 0):
        found_matches_file_name = (os.path.splitext(os.path.basename(source_directory))[0]) + "_found_entries" + str(key_phrase_clean) + ".srt"
    else:
        found_matches_file_name = (os.path.splitext(os.path.basename(sub_directory))[0]) + "_found_entries" + str(key_phrase_clean) + ".srt"
    try:
        found_matches_file = open(found_matches_file_name,"x")
    except:
        if(save_style_num == 2):
            print(found_matches_file_name + "already exists.")
    found_matches_file = open(found_matches_file_name,"a", encoding="utf-8")

    return found_matches_file

def clean_input(file_name, ignore_phrase_list):
    """
    Removes special characters and spaces from strings.\n
    Removes ignore phrase if specified.\n
    Also changes entire string to lowercase.\n
    Returns cleaned string
    
    """
    for phrase in ignore_phrase_list:
        file_name_clean = file_name.replace(phrase, "")

    # Removes special characters
    file_name_clean = ''.join(filter(str.isalnum, file_name_clean))

    file_name_clean = file_name_clean.lower()

    return file_name_clean


def clean_string(string, ignore_spaces, ignore_punctutation, case_sensitive):
    """
    Removes spaces and punctutation and changes case of string based on inputs
    Returns string with desired parts removed
    """
    clean_string = string

    if(not case_sensitive):
        clean_string = clean_string.lower()
        
    if(ignore_punctutation):
        punctuation_list = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        for char in clean_string:
            if char in punctuation_list:
                clean_string = clean_string.replace(char, "")


    if(ignore_spaces):
        clean_string = clean_string.replace(' ', "")

    return clean_string

def check_if_video_file(path):
    """
    When passed a file path, checks if path points to a video file.\n
    Uses ffprobe to check for compatibilty with MoviePy.\n
    Returns True if compatible.\n
    Returns False if not compatible\n
    """

    # Common video file types that are unquestionably supported by MoviePy
    # Speeds up performance for most common cases
    if(path.lower().endswith(('.mkv', '.mp4', '.webm', '.mov', '.avi', '.ogv'))):
        return True
    if(os.path.isdir(path)):
        return False

    # If file is an incompatible type, ffprobe will throw an exception.
    # This is used to detect incompatible file types
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

def create_directory_tree_without_files(source_directory, destination, name):     
    duplicate_count = 0
    output_directory = os.path.join(destination, name)

    while(os.path.isdir(output_directory)):
         duplicate_count +=1 
         output_directory = str(os.path.join(destination, name + "(" + str(duplicate_count) + ")"))
    os.mkdir(output_directory)

    for root, dirs, files in os.walk(source_directory):
        new_subdir = os.path.join(output_directory, os.path.relpath(root, source_directory))
        if not os.path.isdir(new_subdir):
            try:
                os.mkdir(new_subdir)
            except:
                print(str(new_subdir) + " already exists")
                
    return output_directory