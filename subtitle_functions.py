import os
from difflib import SequenceMatcher
from numpy import number
import srt
import subprocess
import chardet

class FoundSubtitleMatch:
    def __init__(self, label, start, end, content):
        self.label = label
        self.start = start
        self.end = end
        self.content = content


def find_subtitle_file(source_directory_subtitle, video_file_name, ignore_phrase_subtitle = "", ignore_phrase_video = "", comparison_tolerance = 0.70):
    """
    Matches subtitle file to video file based on file names.\n
    Match is found SequenceMatcher ratio function returns a result greater than comparison tolerance.\n
    Searches entire subtitle source directory including one subdirectory of depth\n
    Returns file path to matching subtitle file if successful.\n
    Returns None on failure.
    """
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
                    if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() >= comparison_tolerance):
                        return os.path.join(os.getcwd(), subtitle_file_name)
        else:
            os.chdir(source_directory_subtitle)
            if(entry.name.endswith(".srt")):
                subtitle_file_name_clean = clean_input(entry.name, ignore_phrase_subtitle)
                if(SequenceMatcher(None, subtitle_file_name_clean, video_file_name_clean).ratio() >= comparison_tolerance):
                    return os.path.join(os.getcwd(), entry.name)

    return None

def find_video_matches(source_directory_subtitle, source_directory_video, output_directory, save_style_num, key_phrase_list, ignore_spaces, ignore_punctutation, case_sensitive, ignore_subtitle = "", ignore_video = ""):
    """
    Find instances of key words within srt files found in subtitle source directroy. Matches these instances with corresponding video files in video source directory.\n
    Saves files with matching instances, video file directory, times, and contents to output directory.\n
    Save style 2 or 4 = One file per video\n
    Save sytle 0 = One large file with all videos\n
    Save style 1 = One file per sub directory\n
    Appends existing files same names file is found.\n
    ignore_subtitle and ignore_video arguments ignore certain phrases with subtitle and video file names when pairing these files together\n
    """


    output_file_directory = output_directory

    source_directory_video_file_list = os.scandir(source_directory_video)

    current_video_subdirectory = source_directory_video
    source_name = os.path.splitext(os.path.basename(source_directory_subtitle))[0]
    key_phrase_clean = ""
    
    for phrase in key_phrase_list:
        key_phrase_clean = key_phrase_clean + "_" + str(phrase)

    key_phrase_clean = key_phrase_clean.replace(' ', '_')

    punctuation_list = '''!{};:'"\,<>./?@#$%^&*~'''
    for char in key_phrase_clean:
        if char in punctuation_list:
            key_phrase_clean = key_phrase_clean.replace(char, "")

    if(save_style_num != 0):
        output_path_string = str(os.path.join(output_directory, source_name + "_found_entries" + str(key_phrase_clean)))
        duplicate_count = 0
        while(os.path.isdir(output_path_string)):
                duplicate_count +=1 
                output_path_string = str(os.path.join(output_directory, source_name + "_found_entries" + str(key_phrase_clean) + "(" + str(duplicate_count) + ")"))

        os.mkdir(output_path_string)
        os.chdir(output_path_string)

        output_file_directory = output_path_string

    # Creates subdirectories to save output based on video source directory sub directories
    for file in source_directory_video_file_list:
        if(file.is_dir()):
            current_video_subdirectory = os.path.join(source_directory_video, file)

            if(save_style_num == 2):
                directory_created = False
                directory_copy_count = 0
                while(not directory_created):
                    if(directory_copy_count == 0):
                        output_file_directory = os.path.join(output_path_string, file.name)
                    else:
                        output_file_directory = os.path.join(output_path_string, file.name + "(" + str(directory_copy_count) + ")")
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
                    found_matches_file = find_output_file(video_file_name, save_style_num, key_phrase_list, source_directory_video, current_video_subdirectory)

                    found_entries = find_matching_entries(subtitle_file, key_phrase_list, os.path.abspath(video_file_name), ignore_spaces, ignore_punctutation, case_sensitive)
                    for found_entry in found_entries:
                        found_entry.proprietary = video_file_path
                        found_matches_file.write(found_entry.to_srt())
                    found_matches_file.close()
                else:
                    return video_file_name
            else:
                if(check_if_video_file(os.path.join(source_directory_video, file))):
                    subtitle_file = find_subtitle_file(source_directory_subtitle, file.name, ignore_subtitle, ignore_video)
                    if(subtitle_file != None):
                        os.chdir(output_file_directory)
                        found_matches_file = find_output_file(video_file_name, save_style_num, key_phrase_list, source_directory_video, current_video_subdirectory)


                        found_entries = find_matching_entries(subtitle_file, key_phrase_list, os.path.abspath(video_file_name), ignore_spaces, ignore_punctutation, case_sensitive)

                        for found_entry in found_entries:
                            # In srt library, proprietary information is stored after time stamp
                            # To store directory of source video file, path is written in place of the proprietary information
                            found_entry.proprietary = os.path.abspath(video_file_name)
                            found_matches_file.write(found_entry.to_srt())
                        found_matches_file.close()
                    else:
                        return video_file_name

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

def clean_input(file_name, ignore_phrase = ""):
    """
    Removes special characters and spaces from strings.\n
    Removes ignore phrase if specified.\n
    Also changes entire string to lowercase.\n
    Returns cleaned string
    
    """
    file_name_clean = file_name.replace(ignore_phrase, "")

    # Removes special characters
    file_name_clean = ''.join(filter(str.isalnum, file_name_clean))

    file_name_clean = file_name_clean.lower()

    return file_name_clean

def clean_string(string, ignore_spaces, ignore_punctutation, case_sensitive):
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

def extractSubtitles(source_file_video, output_directory):
    current_stream = 0
    temp_dir = os.getcwd()

    if(source_file_video.lower().endswith(('.mkv', '.mp4'))):
        os.chdir(output_directory)
        output_folder = os.path.join(os.getcwd(), (os.path.splitext(os.path.basename(source_file_video))[0]) + '_subs')
        try:
            os.mkdir(output_folder)
        except:
            pass
        os.chdir(output_folder)

        process = subprocess.run(['ffprobe', '-loglevel', 'error', '-select_streams', 's', '-show_entries', 'stream=index:stream_tags=title', '-of', 'csv=p=0', '%s' % (str(source_file_video))], capture_output=True)
        std_out_str = process.stdout.decode("utf-8")
        subtitle_title_list = std_out_str.split("\n")
        number_of_streams = len(subtitle_title_list)-1
        while(current_stream < number_of_streams):
            try:
                subtitle_title_list[current_stream] = subtitle_title_list[current_stream].replace('\r', '').replace(' ', '_').replace('/', '')
                subtitle_title_list[current_stream] = subtitle_title_list[current_stream].split(',')[1]
            except:
                pass
            current_stream += 1
        current_stream = 0

        process = subprocess.run(['ffprobe', '-loglevel', 'error', '-select_streams', 's', '-show_entries', 'stream=index:stream_tags=language', '-of', 'csv=p=0', '%s' % (str(source_file_video))], capture_output=True)
        std_out_str = process.stdout.decode("utf-8")
        subtitle_language_list = std_out_str.split("\n")
        number_of_streams = len(subtitle_title_list)-1
        while(current_stream < number_of_streams):
            try:
                subtitle_language_list[current_stream] = subtitle_language_list[current_stream].replace('\r', '').replace(' ', '_').replace('/', '')
                subtitle_language_list[current_stream] = subtitle_language_list[current_stream].split(',')[1]
            except:
                pass
            current_stream += 1

        current_stream = 0
        process = subprocess.run(['ffprobe', '-loglevel', 'error', '-select_streams', 's', '-show_entries', 'stream=index', '-of', 'csv=p=0', '%s' % (str(source_file_video))], capture_output=True)
        std_out_str = process.stdout.decode("utf-8")
        process_output_list = std_out_str.split("\n")
        number_of_streams = len(process_output_list)-1
        error_streams = 0

        while(current_stream < number_of_streams):
            try:
                process = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', '%s' % (str(source_file_video)), '-map', '%s' % ('0:s:' + str(current_stream)), '%s' % ((os.path.splitext(os.path.basename(source_file_video))[0]) + '_subs_' + str(subtitle_title_list[current_stream]) + "_" + str(subtitle_language_list[current_stream]) + '.srt')], check=True)
            except:
                os.remove(os.path.join(output_folder, ((os.path.splitext(os.path.basename(source_file_video))[0]) + '_subs_' + str(subtitle_title_list[current_stream]) + "_" + str(subtitle_language_list[current_stream]) + '.srt')))
                error_streams += 1
            current_stream += 1
        print(str(number_of_streams) + " subtitle track(s) found")
        if(error_streams > 0):
            print(str(error_streams) + " subtitle track(s) could not be processed \nThese subtitles may be bitmap based or improperly formatted making them unextractable.\nGabagool only supports .srt files")
        os.chdir(temp_dir)
    else:
        print("File must be type must be .mkv or .mp4")  