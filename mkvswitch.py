# encoding: utf-8

from __future__ import print_function

import argparse
from itertools import islice
import logging
import os
import sys

from core import MKV, all_mkvs, grouped_by_similar_tracks
from settings import WINDOWS_CODE_PAGE


command_line_parser = argparse.ArgumentParser(prog='mkvswitch')
command_line_parser.add_argument('-r', action='store_true', dest='is_recursive')
command_line_parser.add_argument('paths', nargs='+', metavar='path')

program_args = command_line_parser.parse_args()
if os.name == 'nt':
    program_args.paths = map(lambda path: path.decode(WINDOWS_CODE_PAGE), program_args.paths)



def print_file_info(header, mkv):
    print(header)
    print_mkv_tracks('Audio', mkv.audio_tracks)
    print_mkv_tracks('Subtitle', mkv.subtitle_tracks)


def print_mkv_tracks(group_caption, tracks):
    if len(tracks) == 0:
        print(' NO', group_caption)
        return
    print(' ', group_caption)
    for track in tracks:
        number = ('[%s]' if track.is_default else ' %s ') % track.number
        language = track.language.upper() if track.language else ''
        name = track.name if track.name else ''
        print(3*' ', number, language, name)


def process_single_file(mkv):
    print()
    print_file_info(mkv.filename, mkv)
    
    new_default_tracks_num = process_user_input()
    if new_default_tracks_num:
        mkv.set_default_tracks(*new_default_tracks_num)


def process_file_group(mkvs):
    print()
    print('%s files: ' % len(mkvs))
    for mkv in mkvs:
        print(mkv.filename)
    print_mkv_tracks('Audio', mkvs[0].audio_tracks)
    print_mkv_tracks('Subtitle', mkvs[0].subtitle_tracks)
    
    new_default_tracks_num = process_user_input()
    if new_default_tracks_num:
        for mkv in mkvs:
            mkv.set_default_tracks(*new_default_tracks_num)


def process_user_input():
    user_input = raw_input('> New default tracks (e.g. "2 5") / <RETURN> / <q> : ').lower()
    if not user_input:
        return
    if user_input == 'q':
        sys.exit()
    new_default_tracks_num = map(int, user_input.strip('\'\"').split())
    return new_default_tracks_num
    

for path in program_args.paths:
    
    if not os.path.exists(path):
        print('ERROR. Path "%s" doesn\'t exist.' % path) 

    if os.path.isfile(path):
        process_single_file(MKV(path))
        continue

    file_seq = os.walk(path)
    if not program_args.is_recursive:
        file_seq = islice(file_seq, 1)

    for dirpath, dirnames, filenames in file_seq:
        print('\n---', 'MKV files in', dirpath)
        try:
            mkvs = grouped_by_similar_tracks(all_mkvs(dirpath))
            if len(mkvs) == 0:
                print('No MKV files found')
                continue
            for group_key, mkv_group in mkvs.iteritems():
                try:
                    if len(mkv_group) == 1:
                        process_single_file(mkv_group[0])
                    else:
                        process_file_group(mkv_group)
                except Exception as e:
                    logging.exception(e)
                    print("ERROR. Skipping file(s).")
        except Exception as e:
            logging.exception(e)