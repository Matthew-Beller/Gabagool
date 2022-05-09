from numpy import empty
import srt
import os
from gooey import Gooey, GooeyParser
import argparse
from difflib import SequenceMatcher

import subtitle_functions

@Gooey
def prompt_user():
    parser = GooeyParser(description="Speeder")
    subparser = parser.add_subparsers(dest='action')
    subparser.required = True

    single_file = subparser.add_parser("Single")
    batch_files = subparser.add_parser("Batch")

    single_file.add_argument('source_file_video', metavar="Video File", widget="FileChooser")
    single_file.add_argument('source_file_subtitle', metavar="Subtitle File", widget="FileChooser")
    single_file.add_argument('key_phrase', metavar="Search Phrase")
    single_file.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")

    batch_files.add_argument('source_directory_video', metavar="Video Files Directory", widget="DirChooser")
    batch_files.add_argument('--ignore_video', metavar="Ignore Phrase Video", help="Ignore a certain phrase in video file names", nargs="?", const="", default="", type=str, required=False)
    batch_files.add_argument('source_directory_subtitle', metavar="Subtitle Files Directory", widget="DirChooser")
    batch_files.add_argument('--ignore_subtitle', metavar="Ignore Phrase Subtitle", help="Ignore a certain phrase in subtitle file names", nargs="?", const="", default="", type=str, required=False)
    batch_files.add_argument('key_phrase', metavar="Search Phrase")
    batch_files.add_argument("save_style", metavar="Save Style", widget="Dropdown", choices=['One file', 'File for each folder', 'File for each video'])
    batch_files.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    
    return parser.parse_args()

args = prompt_user()

if(args.action == 'Single'):
    source_file_video = args.source_file_video
    source_file_subtitle = args.source_file_subtitle

    key_phrase = args.key_phrase

    output_directory = args.output_directory

    key_phrase_clean = ''.join(filter(str.isalnum, key_phrase))
    key_phrase_clean = key_phrase_clean.lower()

    save_style_num = 4

elif(args.action == 'Batch'):
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
else:
    pass


subtitle_not_found_list = []


#TODO: turn code into more functions

if(args.action == 'Single'):
    os.chdir(output_directory)
    output_file = subtitle_functions.find_output_file(os.path.basename(source_file_video), save_style_num, source_directory_video)
    subtitle_functions.find_matching_entries(source_file_subtitle, key_phrase, output_file, source_file_video)
elif(args.action == 'Batch'):
    directory_found = False

    source_directory_video_file_list = os.scandir(source_directory_video)
    for entry in source_directory_video_file_list:
        if(entry.is_dir()):
            directory_found = True
            os.chdir(os.path.join(source_directory_video, entry))
            subtitle_functions.find_video_matches(source_directory_subtitle, source_directory_video, os.getcwd(), output_directory, entry, save_style_num, key_phrase_clean, ignore_subtitle, ignore_video)

    if(not directory_found):
        os.chdir(source_directory_video)
        subtitle_functions.find_video_matches(source_directory_subtitle, source_directory_video, os.getcwd(), output_directory, None, save_style_num, key_phrase_clean, ignore_subtitle, ignore_video)

    if(len(subtitle_not_found_list) == 0):
        print("All video files matched")
    else:
        print("No subtitles found for following video files:")
        print(subtitle_not_found_list)
        print("Move subtitle file into subtitle source directory or rename existing subtitle file to match video file name")
else:
    pass

#TODO make subtitle and video function files separate from driver
# make separate branches for editing these files
# have obviously different fucitons, one splices video while other searches files
# make driver only driver and get rid of global variables if possible
# Add menu for video editing to driver
