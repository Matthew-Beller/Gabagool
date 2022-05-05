from numpy import empty
import srt
import os
from gooey import Gooey, GooeyParser
import argparse
from difflib import SequenceMatcher

@Gooey
def prompt_user():
    parser = GooeyParser(description="Speeder")

    parser.add_argument('source_directory_video', metavar="Video Files Directory", widget="DirChooser")
    parser.add_argument('--ignore_video', metavar="Ignore Phrase Video", help="Ignore a certain phrase in video file names", nargs="?", const="", default="", type=str, required=False)
    parser.add_argument('source_directory_subtitle', metavar="Subtitle Files Directory", widget="DirChooser")
    parser.add_argument('--ignore_subtitle', metavar="Ignore Phrase Subtitle", help="Ignore a certain phrase in subtitle file names", nargs="?", const="", default="", type=str, required=False)
    parser.add_argument('key_phrase', metavar="Search Phrase")

    parser.add_argument("save_style", metavar="Save Style", widget="Dropdown", choices=['One file', 'File for each folder', 'File for each video'])

    parser.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    
    return parser.parse_args()

args = prompt_user()

source_directory_video = args.source_directory_video
ignore_video = args.ignore_video

source_directory_subtitle = args.source_directory_subtitle
ignore_subtitle = args.ignore_subtitle

key_phrase = args.key_phrase

save_style = args.save_style

output_directory = args.output_directory

key_phrase_clean = ''.join(filter(str.isalnum, key_phrase))
key_phrase_clean = key_phrase_clean.lower()

if(save_style == 'One file'):
    save_style_num = 0
elif (save_style == 'File for each folder'):
    save_style_num = 1
elif (save_style == 'File for each video'):
    save_style_num = 2
else:
    save_style_num = 0


os.chdir(source_directory_video)

subtitle_not_found_list = []

def find_subtitle_file(source_directory_subtitle, video_file_name):

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


def find_video_matches(intial_directory, output_directory, video_subfolder):
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
            subtitle_file = find_subtitle_file(source_directory_subtitle, video_file_name)
            if(subtitle_file != None):
                with open(subtitle_file, encoding='utf-8-sig') as file:
                    subtitle_generator = srt.parse(file)

                    subtitles_list = list(subtitle_generator)
                if(save_style_num == 2):
                    found_matches_file_name = video_file_name + ".txt"
                elif(save_style_num == 0):
                    found_matches_file_name = os.path.basename(source_directory_video) + ".txt"
                else:
                    found_matches_file_name = os.path.basename(intial_directory) + ".txt"
                os.chdir(output_file_directory)
                try:
                    found_matches_file = open(found_matches_file_name,"x")
                except:
                    if(save_style_num == 2):
                        print(found_matches_file_name + "already exists.")

                found_matches_file = open(found_matches_file_name,"a")

                for entry in subtitles_list:
                    entry_clean = ''.join(filter(str.isalnum, entry.content)) 
                    entry_clean = entry_clean.lower()
                    if(entry_clean.find(key_phrase_clean) != -1):
                        found_matches_file.write(entry.content)

                found_matches_file.close()
            else:
                subtitle_not_found_list.append(video_file_name)




directory_found = False

source_directory_video_file_list = os.scandir(source_directory_video)

for entry in source_directory_video_file_list:
    if(entry.is_dir()):
        directory_found = True
        os.chdir(os.path.join(source_directory_video, entry))
        find_video_matches(os.getcwd(), output_directory, entry)

if(not directory_found):
    os.chdir(source_directory_video)
    find_video_matches(os.getcwd(), output_directory, None)

if(len(subtitle_not_found_list) == 0):
    print("All video files matched")
else:
    print("No subtitles found for following video files:")
    print(subtitle_not_found_list)
    print("Move subtitle file into subtitle source directory or rename existing subtitle file to match video file name")

