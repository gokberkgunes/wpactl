#!/usr/bin/python

import subprocess
import sys
import re

def get_wpctl_status():
    # Run wpctl status and collect its output
    wpctl_raw_output = subprocess.run(["wpctl", "status"], capture_output=True, text=True)
    # strip stdout data of wpctl status
    wpctl_stdout = wpctl_raw_output.stdout
    # Only leave ascii characters (remove tree structure)
    wpctl_stdout = wpctl_stdout.encode('ascii', 'ignore').decode('ascii')
    return wpctl_stdout

def wpctl_list(wpctl_status, *args):
    # Default args
    media_type="audio"
    stream_device="sink"
    for arg in args:
        if (arg == "video"):
            media_type="video"
        elif (arg == "source"):
            stream_device = "source"
        elif (arg == "device"):
            stream_device = "device"
        elif (arg == "audio" or arg == "sink"):
            continue
        else:
            print(f"ERROR: Arg '{arg}' is unknown.", file=sys.stderr)
            sys.exit(1)
    items = []
    all_found = False
    media_type_found = False
    # Go through the lines one by one. When media type and stream device are
    # found save all the other lines until empty line is also found.
    for line in wpctl_status.splitlines():
        if all_found:
            # If we meet a whitespace line, no more media devices left.
            if line.strip() == '':
                break
            else:
                # remove whitespace at start and end. Moreover, put * after the
                # number: allow grep '*' | cut -d'*' -f1 to get default ID.
                line = re.sub(r'^(\*?)\s*(\d+)\s*.\s*', r'\2\1\t', line.strip())
                line = re.sub(r' \[.*$', '', line) # remove [...] at the end
                items.append(line) #remove the dot in the ID
                continue
        # We have found requested media_type: mark it.
        elif media_type == line.lower():
            media_type_found = True
        # If media type is found, try to find stream device: audio or video
        elif media_type_found and ("  " +stream_device+"s:" == line.lower()):
            all_found = True
    if not items:
        return ''
    else:
        return '\n'.join(items) + '\n'

stream_list = wpctl_list(get_wpctl_status(), *sys.argv[1:])

print(stream_list, end = '')
