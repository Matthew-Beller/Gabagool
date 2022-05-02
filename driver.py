import srt
import os
import tkinter as tk
import tkinter.filedialog
import tkinter.simpledialog
from difflib import SequenceMatcher

def findSubtitleFile(source_directory_subtitle, video_file_name):
    os.chdir(source_directory_subtitle)
    for subtitle_file_name in os.listdir(source_directory_subtitle):
        if(subtitle_file_name.lower().endswith(".srt")):
            if(SequenceMatcher(None, subtitle_file_name, video_file_name).ratio() > 0.75):
                source_text = open(subtitle_file_name, "r")
                return source_text
    return None

application_window = tk.Tk()

source_directory_video = tkinter.filedialog.askdirectory()

source_directory_subtitle = tkinter.filedialog.askdirectory()

os.chdir(source_directory_video)

key_phrase = tkinter.simpledialog.askstring("Input", "Enter your search phrase:", parent = application_window)

for video_file_name in os.listdir(source_directory_video):
    subtitle_file = findSubtitleFile(source_directory_subtitle, video_file_name)
    if(subtitle_file != None):
        subtitle_generator = srt.parse(subtitle_file)

        subtitles_list = list(subtitle_generator)

        for entry in subtitles_list:
            if(entry.content.find(key_phrase) != -1):
                print(entry.content) 