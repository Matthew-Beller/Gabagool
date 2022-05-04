import srt
import os
from gooey import Gooey, GooeyParser
import argparse
from difflib import SequenceMatcher

@Gooey
def prompt_user():
    parser = GooeyParser(description="Speeder")

    parser.add_argument('source_directory_video', metavar="Video Files Directory", widget="DirChooser")
    parser.add_argument('source_directory_subtitle', metavar="Subtitle Files Directory", widget="DirChooser")
    parser.add_argument('key_phrase', metavar="Search Phrase")

    parser.add_argument("save_style", metavar="Save Style", widget="Dropdown", choices=['One file', 'File for each folder', 'File for each video'])

    parser.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    
    return parser.parse_args()

args = prompt_user()

source_directory_video = args.source_directory_video
source_directory_subtitle = args.source_directory_subtitle
key_phrase = args.key_phrase

save_style = args.save_style

output_directory = args.output_directory


key_phrase_clean = ''.join(filter(str.isalnum, key_phrase))

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

    source_directory_subtitle_file_list = os.scandir(source_directory_video)

    for entry in source_directory_subtitle_file_list:
        if(entry.is_dir()):
            directory_found = True
            os.chdir(os.path.join(source_directory_video, entry))
            for subtitle_file_name in os.listdir(source_directory_subtitle):
                if(subtitle_file_name.lower().endswith(".srt")):
                    if(SequenceMatcher(None, subtitle_file_name, video_file_name).ratio() > 0.75):
                        source_text = open(subtitle_file_name, "r")
                        return source_text
    if(not directory_found):
        os.chdir(source_directory_subtitle)
        for subtitle_file_name in os.listdir(source_directory_subtitle):
            if(subtitle_file_name.lower().endswith(".srt")):
                if(SequenceMatcher(None, subtitle_file_name, video_file_name).ratio() > 0.75):
                    source_text = open(subtitle_file_name, "r")
                    return source_text
    return None


def find_video_matches(intial_directory, output_directory, video_subfolder):
    if(video_subfolder is not None):
        output_file_directory = os.path.join(output_directory, video_subfolder.name)
        os.mkdir(output_file_directory)
        os.chdir(output_file_directory)
    else:
        output_file_directory = output_directory
    for video_file_name in os.listdir(intial_directory):
        if(os.path.isfile(os.path.join(intial_directory, video_file_name))):
            subtitle_file = find_subtitle_file(source_directory_subtitle, video_file_name)
            if(subtitle_file != None):
                subtitle_generator = srt.parse(subtitle_file)

                subtitles_list = list(subtitle_generator)
                if(save_style_num == 2):
                    found_matches_file_name = video_file_name + "_found_phrases" + ".txt"
                else:
                    found_matches_file_name = os.path.basename(intial_directory) + "_found_phrases" + ".txt"
                os.chdir(output_file_directory)
                try:
                    found_matches_file = open(found_matches_file_name,"x")
                except:
                    print(found_matches_file_name + "already exists.")
                    continue

                found_matches_file = open(found_matches_file_name,"a")

                for entry in subtitles_list:
                    entry_clean = ''.join(filter(str.isalnum, entry.content)) 
                    if(entry_clean.lower().find(key_phrase_clean.lower()) != -1):
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