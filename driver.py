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


os.chdir(source_directory_video)


subtitle_not_found_list = []

def findSubtitleFile(source_directory_subtitle, video_file_name):
    os.chdir(source_directory_subtitle)
    for subtitle_file_name in os.listdir(source_directory_subtitle):
        if(subtitle_file_name.lower().endswith(".srt")):
            if(SequenceMatcher(None, subtitle_file_name, video_file_name).ratio() > 0.75):
                source_text = open(subtitle_file_name, "r")
                return source_text
    return None

for video_file_name in os.listdir(source_directory_video):
    subtitle_file = findSubtitleFile(source_directory_subtitle, video_file_name)
    if(subtitle_file != None):
        subtitle_generator = srt.parse(subtitle_file)

        subtitles_list = list(subtitle_generator)

        os.chdir(output_directory)

        found_matches_file_name = source_directory_video + "found phrases" + ".txt"
        try:
            found_matches_file = open(found_matches_file_name,"x")
        except:
            print(found_matches_file_name + "already exists.")
            continue

        found_matches_file = open(found_matches_file_name,"a")

        for entry in subtitles_list:
            if(entry.content.lower().find(key_phrase.lower()) != -1):
                found_matches_file.write(entry.content)

        found_matches_file.close()
    else:
        subtitle_not_found_list.append(video_file_name)