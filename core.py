# encoding: utf-8

import os

import enzyme

from settings import MKVPROPEDIT_PATH, WINDOWS_CODE_PAGE
from utils import iter_directory, multi_filter, DefaultOrderedDict


if not MKVPROPEDIT_PATH:
    raise Exception('MKVPROPEDIT_PATH not set in settings.py')


class MKV(object):

    def __init__(self, path):
        with open(path, 'rb') as mkv_file:
            enzyme_mkv = enzyme.MKV(mkv_file)
        self.path = path
        self.filename = os.path.basename(path)
        self.audio_tracks = [MKVTrack(track) for track in enzyme_mkv.audio_tracks]
        self.subtitle_tracks = [MKVTrack(track) for track in enzyme_mkv.subtitle_tracks]

    def set_default_tracks(self, audio_track_number=None, subtitle_track_number=None):
        track_change_command = ''
        
        if audio_track_number:
            track_change_command += self._build_change_default_track_command(self.audio_tracks, audio_track_number)
        if subtitle_track_number:
            track_change_command += self._build_change_default_track_command(self.subtitle_tracks, subtitle_track_number)
        
        cmd_string = '"%s" "%s" %s' % (MKVPROPEDIT_PATH, self.path, track_change_command) 
        if os.name == 'nt':
            cmd_string = '"%s"' % cmd_string.encode(WINDOWS_CODE_PAGE)
        
        os.system(cmd_string)

    def _build_change_default_track_command(self, track_list, track_number):
        current_default_tracks, track_found = multi_filter(
            [
                lambda track: track.is_default, 
                lambda track: track.number == track_number
            ],
            track_list
        )

        if not track_found:
            raise Exception('Track (%s) not found' % track_number)

        track_change_command = ''    
        for track in current_default_tracks:
            track_change_command += ' --edit track:@%s --set flag-default=0' % track.number
        track_change_command += ' --edit track:@%s --set flag-default=1' % track_number

        return track_change_command


class MKVTrack(object):

    def __init__(self, enzyme_track):
        self.number = enzyme_track.number
        self.name = enzyme_track.name
        self.language = enzyme_track.language
        self.is_default = enzyme_track.default

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.number, self.name, self.language, self.is_default))


def all_mkvs(directory):
    return [MKV(path) for path in iter_directory(directory) if path.endswith('.mkv')]


def grouped_by_similar_tracks(mkvs):
    groups = DefaultOrderedDict(list)
    for mkv in mkvs:
        group_key = tuple(mkv.audio_tracks), tuple(mkv.subtitle_tracks)
        groups[group_key].append(mkv)
    return groups
