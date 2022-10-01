from numpy import empty
import srt
import os
from gooey import Gooey, GooeyParser
import argparse
from difflib import SequenceMatcher

import subtitle_functions
import video_editing_functions

@Gooey(optional_cols = 2, progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
        progress_expr="current / total * 100",
       disable_progress_bar_animation=True,
       hide_progress_msg=True,
       timing_options={
            'show_time_remaining':True,
            'hide_time_remaining_on_complete':True
        }
        )
       
def prompt_user():
    parser = GooeyParser(description="Gabagool")
    subparser = parser.add_subparsers(dest='action')
    subparser.required = True

    single_file_subtitle = subparser.add_parser("Single_Subtitle_File")

    batch_files_subtitle = subparser.add_parser("Batch_Subtitle_Files")

    create_video_file = subparser.add_parser("Create_Video_File")

    single_file_subtitle.add_argument('source_file_video', metavar="Video File", widget="FileChooser")
    single_file_subtitle.add_argument('source_file_subtitle', metavar="Subtitle File", widget="FileChooser")
    single_file_subtitle.add_argument('key_phrase_input_raw', metavar="Search Phrases", help="Delimit lists of keywords with |@|")
    single_file_subtitle.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    single_file_subtitle.add_argument('--ignore_spaces', metavar="Ignore Spaces during Search", help=" Ignore", widget="CheckBox", action="store_false", default=True)
    single_file_subtitle.add_argument('--ignore_punctuation', metavar="Ignore Punctuation during Search", help=" Ignore", widget="CheckBox", action="store_false", default=True)
    single_file_subtitle.add_argument('--case_sensitive', metavar="Case Sensitive Search", help=" Recognize Case", widget="CheckBox", action="store_true", default=False)

    batch_files_subtitle.add_argument('source_directory_video', metavar="Video Files Directory", widget="DirChooser")
    batch_files_subtitle.add_argument('--ignore_video', metavar="Ignore Phrase Video", help="Ignore a certain phrase in video file names", default="", type=str, required=False)
    batch_files_subtitle.add_argument('source_directory_subtitle', metavar="Subtitle Files Directory", widget="DirChooser")
    batch_files_subtitle.add_argument('--ignore_subtitle', metavar="Ignore Phrase Subtitle", help="Ignore a certain phrase in subtitle file names", default="", type=str, required=False)
    batch_files_subtitle.add_argument('key_phrase_input_raw', metavar="Search Phrases", help="Delimit lists of keywords with |@|", type=str)
    batch_files_subtitle.add_argument("save_style", metavar="Save Style", widget="Dropdown", choices=['One file', 'File for each folder', 'File for each video'])
    batch_files_subtitle.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    batch_files_subtitle.add_argument('--ignore_spaces', metavar="Ignore Spaces during Search", help=" Ignore", widget="CheckBox", action="store_false", default=True)
    batch_files_subtitle.add_argument('--ignore_punctuation', metavar="Ignore Punctuation during Search", help=" Ignore", widget="CheckBox", action="store_false", default=True)
    batch_files_subtitle.add_argument('--case_sensitive', metavar="Case Sensitive Search", help=" Recognize Case", widget="CheckBox", action="store_true", default=False)

    create_video_file.add_argument('source_file_subtitle_found', metavar="Searched Subtitle File", help="File generated by Single Subtitle File or Batch Subtitle Files options", widget="FileChooser")
    create_video_file.add_argument('output_directory', metavar="Output Directory", widget="DirChooser")
    create_video_file.add_argument('--buffer_time_start', metavar="Start Buffer", nargs="?", const="", default=0, type=int, required=False)
    create_video_file.add_argument('--buffer_time_end', metavar="End Buffer", nargs="?", const="", default=0, type=int, required=False)
    create_video_file.add_argument('save_style', metavar="Save Style", widget="Dropdown", choices=['One Compilation Video', 'Separate Video Files'])

    return parser.parse_args()
def main():
    args = prompt_user()

    if(args.action == 'Single_Subtitle_File'):
        source_file_video = args.source_file_video
        source_file_subtitle = args.source_file_subtitle

        key_phrase_input_raw = args.key_phrase_input_raw

        key_phrase_list = key_phrase_input_raw.split('|@|')
        output_directory = args.output_directory

        ignore_spaces = not args.ignore_spaces
        ignore_punctuation = not args.ignore_punctuation
        case_sensitive = args.case_sensitive

        save_style_num = 4

    elif(args.action == 'Batch_Subtitle_Files'):
        source_directory_video = args.source_directory_video
        ignore_video = args.ignore_video

        source_directory_subtitle = args.source_directory_subtitle
        ignore_subtitle = args.ignore_subtitle

        key_phrase_input_raw = args.key_phrase_input_raw
        key_phrase_list = key_phrase_input_raw.split('|@|')

        save_style = args.save_style
        output_directory = args.output_directory

        ignore_spaces = not args.ignore_spaces
        ignore_punctuation = not args.ignore_punctuation
        case_sensitive = args.case_sensitive

        if(save_style == 'One file'):
            save_style_num = 0
        elif (save_style == 'File for each folder'):
            save_style_num = 1
        elif (save_style == 'File for each video'):
            save_style_num = 2
        else:
            save_style_num = 0


        os.chdir(source_directory_video)

    elif(args.action == 'Create_Video_File'):
        source_file_subtitle_found = args.source_file_subtitle_found
        output_directory = args.output_directory
        buffer_time_start = args.buffer_time_start
        buffer_time_end = args.buffer_time_end
        save_style = args.save_style
    else:
        pass


    if(args.action == 'Single_Subtitle_File'):
        if(subtitle_functions.check_if_video_file(source_file_video)):
            os.chdir(output_directory)
            found_matches_file = subtitle_functions.find_output_file(os.path.basename(source_file_video), save_style_num, key_phrase_list)
            found_entries = subtitle_functions.find_matching_entries(source_file_subtitle, key_phrase_list, source_file_video, ignore_spaces, ignore_punctuation, case_sensitive)

            for found_entry in found_entries:
                found_entry.proprietary = source_file_video
                found_matches_file.write(found_entry.to_srt())
            found_matches_file.close()
        else:
            print("Invalid video file.")
            
    elif(args.action == 'Batch_Subtitle_Files'):
        subtitle_functions.find_video_matches(source_directory_subtitle, source_directory_video, output_directory, save_style_num, key_phrase_list, ignore_spaces, ignore_punctuation, case_sensitive, ignore_subtitle, ignore_video)
        print("Done")

    elif(args.action == 'Create_Video_File'):
        if(save_style == 'One Compilation Video'):
            video_editing_functions.mergeMultipleClips(source_file_subtitle_found, output_directory, buffer_time_start, buffer_time_end)
        else:
            video_editing_functions.saveAsIndividualClips(source_file_subtitle_found, output_directory, buffer_time_start, buffer_time_end)
    else:
        pass

# allow for multiple ignore phrases


if __name__ == '__main__':
    main()