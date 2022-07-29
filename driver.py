from numpy import empty
import srt
import os
from gooey import Gooey, GooeyParser
import argparse
from difflib import SequenceMatcher

import subtitle_functions
import video_editing_functions

@Gooey
def prompt_user():
    parser = GooeyParser(description="Speeder")
    subparser = parser.add_subparsers(dest='action')
    subparser.required = True

    single_file_subtitle = subparser.add_parser("Single_Subtitle_File")

    batch_files_subtitle = subparser.add_parser("Batch_Subtitle_Files")

    single_file_video = subparser.add_parser("Single_Video_File")

    extract_subtitles = subparser.add_parser("Extact_Subtitle_File_From_Video")

    single_file_subtitle.add_argument('source_file_video', metavar="Video File", widget="FileChooser")
    single_file_subtitle.add_argument('source_file_subtitle', metavar="Subtitle File", widget="FileChooser")
    single_file_subtitle.add_argument('key_phrase', metavar="Search Phrase")
    single_file_subtitle.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")

    batch_files_subtitle.add_argument('source_directory_video', metavar="Video Files Directory", widget="DirChooser")
    batch_files_subtitle.add_argument('--ignore_video', metavar="Ignore Phrase Video", help="Ignore a certain phrase in video file names", nargs="?", const="", default="", type=str, required=False)
    batch_files_subtitle.add_argument('source_directory_subtitle', metavar="Subtitle Files Directory", widget="DirChooser")
    batch_files_subtitle.add_argument('--ignore_subtitle', metavar="Ignore Phrase Subtitle", help="Ignore a certain phrase in subtitle file names", nargs="?", const="", default="", type=str, required=False)
    batch_files_subtitle.add_argument('key_phrase', metavar="Search Phrase")
    batch_files_subtitle.add_argument("save_style", metavar="Save Style", widget="Dropdown", choices=['One file', 'File for each folder', 'File for each video'])
    batch_files_subtitle.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")

    single_file_video.add_argument('source_file_subtitle_found', metavar="Searched Subtitle File", help="File generated by Single Subtitle File or Batch Subtitle Files options", widget="FileChooser")
    single_file_video.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    single_file_video.add_argument('--buffer_time_start', metavar="Start Buffer", nargs="?", const="", default=0, type=int, required=False)
    single_file_video.add_argument('--buffer_time_end', metavar="End Buffer", nargs="?", const="", default=0, type=int, required=False)

    extract_subtitles.add_argument('source_file_video', metavar="Video File", widget="FileChooser")
    extract_subtitles.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")

    return parser.parse_args()

args = prompt_user()

if(args.action == 'Single_Subtitle_File'):
    source_file_video = args.source_file_video
    source_file_subtitle = args.source_file_subtitle

    key_phrase = args.key_phrase

    output_directory = args.output_directory

    key_phrase_clean = ''.join(filter(str.isalnum, key_phrase))
    key_phrase_clean = key_phrase_clean.lower()

    save_style_num = 4

elif(args.action == 'Batch_Subtitle_Files'):
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

elif(args.action == 'Single_Video_File'):
    source_file_subtitle_found = args.source_file_subtitle_found
    output_directory = args.output_directory
    buffer_time_start = args.buffer_time_start
    buffer_time_end = args.buffer_time_end

elif(args.action == 'Extact_Subtitle_File_From_Video'):
    source_file_video = args.source_file_video
    output_directory = args.output_directory
else:
    pass


subtitle_not_found_list = []


#TODO: turn code into more functions

if(args.action == 'Single_Subtitle_File'):
    if(subtitle_functions.check_if_video_file(source_file_video)):
        os.chdir(output_directory)
        found_matches_file = subtitle_functions.find_output_file(os.path.basename(source_file_video), save_style_num)
        found_entries = subtitle_functions.find_matching_entries(source_file_subtitle, key_phrase, source_file_video)

        for found_entry in found_entries:
            found_entry.proprietary = source_file_video
            found_matches_file.write(found_entry.to_srt())
        found_matches_file.close()
    else:
        print("Invalid video file.")
        
elif(args.action == 'Batch_Subtitle_Files'):
    subtitle_functions.find_video_matches(source_directory_subtitle, source_directory_video, output_directory, save_style_num, key_phrase_clean, ignore_subtitle, ignore_video)

    if(len(subtitle_not_found_list) == 0):
        print("All video files matched")
    else:
        print("No subtitles found for following video files:")
        print(subtitle_not_found_list)
        print("Move subtitle file into subtitle source directory or rename existing subtitle file to match video file name")

elif(args.action == 'Single_Video_File'):
    video_editing_functions.clipTogetherVideos(source_file_subtitle_found, output_directory, buffer_time_start, buffer_time_end)
elif(args.action == 'Extact_Subtitle_File_From_Video'):
    subtitle_functions.extractSubtitles(source_file_video, output_directory)
else:
    pass

# Add speeding part of video editing functions
# Add different save style options for video editing functions
# Add buffer options for video editing fuctions

# Use ffmpeg to make built in subtitle extractor DONE

# Allow for multople search terms in subtitle search
# Allow for punctuation and special symbols to matter
# Enable and disable space ignores

# Warn that results are not 100% accuarate, best results may require manually checking searched file

# Progress bar on video clipping

# come up with better funcdtion name than clippvideos toghet