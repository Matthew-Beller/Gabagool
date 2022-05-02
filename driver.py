import srt
import os
from gooey import Gooey, GooeyParser
from difflib import SequenceMatcher

@Gooey
def parse_args():
    parser = GooeyParser(description="Speeder")
    subparsers = parser.add_subparsers(required=True)
    input_menu = subparsers.add_parser("input")
    output_menu = subparsers.add_parser("output")
    input_menu.add_argument('source_directory_video', metavar="Video Files Directory", widget="DirChooser")
    input_menu.add_argument('source_directory_subtitle', metavar="Subtitle Files Directory", widget="DirChooser")
    input_menu.add_argument('key_phrase', metavar="Search Phrase")
    output_menu.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    return parser.parse_args()

args = parse_args()

source_directory_video = args.source_directory_video

source_directory_subtitle = args.source_directory_subtitle

key_phrase = args.key_phrase


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

        for entry in subtitles_list:
            if(entry.content.lower().find(key_phrase.lower()) != -1):
                print(entry.content)
    else:
        subtitle_not_found_list.append(video_file_name)