# midi_soundboard
Python script that can play audio simultaneously on multiple audio devices. It uses input from MIDI devices and supports LED ligts on Launchpad.

## Usage Guide

### Example config.json
```
{
    "input_device": "Launchpad Mini",
    "output_device": "Launchpad Mini",
    "sounds_directory": "sounds",
    "max_note_index": 120,
    "audio_devices": [
        6, 17
    ],
    "test_audio_devices": [
        6
    ],
    "test_note": 88
}
```

## Example file structure
```
soundboard.py
config.py
sounds/0 alert.wav
sounds/1 noise.wav
sounds/2 music.wav
```

## Assigning sound to a note
soundboard.py logs id's of pressed notes so running script is necessary to assign new sounds to notes.
Once you know id of a note, just move your sound to sounds directory and rename it.
### Sound file name format:
```
[note_id] *.wav
```
Name of file must start with id of a note and an empty space.

### Test mode and LED support configuration
If your output device doesn't support LED, change output_device value to ""

In test mode script plays sounds to test_audio_devices instead of audio_devices.

max_note_index is used to turn off LED lights when program starts.

test_note is id of a note that switches test mode.

### Finding information about your setup
To get a list of your audio devices and their id's, type this in commanad line.
```
python soundboard.py -la
```

To get a list of your midi devices, type this in commanad line.
```
python soundboard.py -lm
```

## Dependencies
```
pygame
soundfile
sounddevice
```
