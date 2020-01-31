#
# MIDI SOUNDBOARD v1.0
#
# by Szymon Dziwak
# https://github.com/skdziwak/midi_soundboard
#

from pygame import midi
import sounddevice as sd
import soundfile as sf

import argparse
import threading
import json, atexit, os

# MIDI COLORS 24 35 41 7
PLAYING = 7
AVAILABLE = [24, 35]
UNAVAILABLE = 7
TEST = 7

parser = argparse.ArgumentParser(description='Soundboard loads sounds in [sounds_directory] (default: sounds).\n (Name format: "[note_id] *.wav") and assigns it to [note_id] on your input device.\n'
                   'You can configure output device. It is used for light feedback on some devices e.g. Launchpad Mini. [test_note] lets you switch between [audio_devices] and [test_audio_devices]. It can be used for preview. '
                    '[max_note_index] is used to turn off all notes on output device when program starts.')
parser.add_argument('--list_audio', '-la', dest='list_audio', action='store_true', help='Shows list of audio devices')
parser.add_argument('--list_midi', '-lm', dest='list_midi', action='store_true', help='Shows list of midi devices')
parser.add_argument('--config', '-c', dest='config_file', action='store', help='Select config file (default: config.json)')
args, remaining = parser.parse_known_args()

midi.init()

test_mode = False

if args.list_audio:
    print('Available audio devices:\n{}'.format(sd.query_devices()))
    print()
if args.list_midi:
    print('Available midi devices:')
    for i in range(midi.get_count()):
        info=midi.get_device_info(i)
        print('  {name} - {type}'.format(name=info[1].decode('utf-8'), type=(
            'input' if info[2] == 1 else ('output' if info[3] == 1 else 'unknown'))))
    print()
if not args.list_audio and not args.list_midi:
    # Loading config
    print('Loading config')
    with open(args.config_file if args.config_file else 'config.json', 'r', encoding='utf-8') as file:
        config = json.loads(file.read())
    print()

    # Loading sounds
    print('Loading sounds')
    sounds_directory = config['sounds_directory']
    sounds = {}
    for name in os.listdir(sounds_directory):
        path = '{directory}/{file}'.format(directory=sounds_directory, file=name)
        print('Found sound:', path)
        data, fs = sf.read(path, dtype='float32')
        note = name.split('.')[0].split(' ')[0]
        if note.isdigit():
            sounds[int(note)] = {'data': data, 'fs': fs}
    print()

    # Connecting to MIDI devices
    print('Connecting to MIDI devices')
    input_device = None
    output_device = None

    for i in range(midi.get_count()):
        info = midi.get_device_info(i)
        if config['input_device'] == info[1].decode('utf-8') and info[2] == 1:
            print('Found desired input device')
            input_device = midi.Input(i)
        if config['output_device'] == info[1].decode('utf-8') and info[3] == 1:
            print('Found desired output device')
            output_device = midi.Output(i)
    print()

    # Handling sound
    currently_playing = 0

    def play(n, d):
        sd.play(sounds[n]['data'], sounds[n]['fs'], device=d)
        global currently_playing
        currently_playing += 1
        sd.wait()
        currently_playing -= 1

    def note_pressed(n):
        if n in sounds:
            print('Playing sound:', n)
            if currently_playing == 0:
                for d in (config['test_audio_devices'] if test_mode else config['audio_devices']): # Playing sound on proper set of audio devices
                    threading.Thread(target=lambda : play(n, d)).start() # Playing sound in a new thread
            if output_device:
                output_device.note_off(note)
                output_device.note_on(note, PLAYING)
        else:
            if output_device:
                output_device.note_on(note, UNAVAILABLE)


    # Loop that awaits for notes from input device
    print('Ready')
    if output_device:
        for i in range(config['max_note_index'] + 1):
            if output_device:
                output_device.note_off(i)
            if i in sounds:
                output_device.note_on(i, AVAILABLE[(i + int(i / 16)) % len(AVAILABLE)])

    while True:
        if input_device.poll(): # Checking if user pressed a key
            data = input_device.read(1) # Reading data from device
            note = data[0][0][1] # Extracting note index
            velocity = data[0][0][2] # Extracting velocity
            if note == config['test_note']: # Checking if that key is assigned to test mode key
                if velocity > 0:
                    test_mode = not test_mode
                    if output_device:
                        if test_mode:
                            output_device.note_on(note, TEST)
                        else:
                            output_device.note_off(note)
                    print('Test mode', 'ON' if test_mode else 'OFF')
            else:
                if velocity > 0:
                    print('Pressed note:', note)
                    note_pressed(note)
                elif output_device:
                    output_device.note_off(note)
                    if note in sounds:
                        output_device.note_on(note, AVAILABLE[(note + int(note / 16)) % len(AVAILABLE)])