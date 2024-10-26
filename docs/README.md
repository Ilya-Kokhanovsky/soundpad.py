soundpad_control
================

![PyPI - Version](https://img.shields.io/pypi/v/soundpad_control) ![GitHub License](https://img.shields.io/github/license/Ilya-Kokhanovsky/soundpad.py) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/soundpad_control)

A simple Python wrapper for controlling Soundpad remotely.

Overview
--------

This Python package, soundpad_control, offers a remote control interface for Soundpad through Python, enabling programmatic management of audio playback and manipulation features. Modeled after SoundpadRemoteControl.java, it supports functionalities such as playing, pausing, and stopping sounds, managing categories, and controlling audio settings. With easy-to-use methods, users can add, search, and organize audio files, making it ideal for automated setups or complex audio workflows.

### Features

- **Play and Stop Sounds**: Start, stop, and navigate sounds, with options to output to speakers or a microphone.
- **Sound Navigation**: Play previous, next, and random sounds or sounds from specific categories.
- **Sound Management**: Add or remove sounds and categories, select rows and categories, and manage playback order.
- **Volume and Playback Control**: Control volume, mute, pause, seek, and scroll playback.
- **Recording Support**: Start, stop, and monitor recording sessions.
- **Soundpad Version Check**: Confirm compatibility and connection status with Soundpad.

Installing
-----------

**Python 3.6 or higher is required**

A [Virtual Environment](https://docs.python.org/3/library/venv.html) is recommended to install the library, especially on Linux where the system Python is externally managed and restricts which packages you can install on it.

You can install the library via `pip`:

```
$ pip install soundpad_control
```

Quick Example
-------------

Here’s a quick example of how to use `soundpad_control`.

```python
from soundpad_control import SoundpadRemoteControl

# Initialize the Soundpad remote control
soundpad = SoundpadRemoteControl()

# Play a specific sound by index, here at index 1
soundpad.play_sound(1)

# Play the next sound in the playlist or queue
soundpad.play_next_sound()

# Add a new sound to Soundpad using the specified file path
soundpad.add_sound('/path/to/sound.mp3')

# Search for a sound file by its filename or keyword
soundpad.search('filename')

# Remove selected sound entries; here, `False` keeps the files on disk
soundpad.remove_selected_entries(False)

```

Requirements
------------

- Python 3.6+
- Soundpad

Links
-----

- [GitHub](https://github.com/Ilya-Kokhanovsky/soundpad.py)
- [PyPI page](https://pypi.org/project/soundpad_control)
- Original Java implementation: [SoundpadRemoteControl.java](https://www.leppsoft.com/soundpad/files/rc/SoundpadRemoteControl.java)

