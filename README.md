soundpad_control
================

![PyPI - Version](https://img.shields.io/pypi/v/soundpad_control) ![GitHub License](https://img.shields.io/github/license/Ilya-Kokhanovsky/soundpad.py) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/soundpad_control)

A simple Python wrapper for controlling Soundpad remotely.

Overview
--------

`soundpad_control` is a Python library for interacting with Soundpad over a remote control interface, enabling automated control of sounds in Soundpad from Python scripts. This project aims to provide a simple, user-friendly interface for sending commands to Soundpad.

Features
--------

- Play sounds by index or category
- Pause, resume, or stop playback
- Control volume, mute status, and playback position
- Add or remove sounds and categories
- Start and stop recording audio
- Query and select sounds or categories

Quick Start
-----------

You can install the library via `pip`:

```
$ pip install soundpad_control
```

Usage Example
-------------

Here’s a quick example of how to use `soundpad_control` to play a sound by index.

```python
from soundpad_control import SoundpadRemoteControl

soundpad = SoundpadRemoteControl()

# Play a sound at index 1
soundpad.play_sound(1)
```

Requirements
------------

- Python 3.6+
- Soundpad

License
-------

This project is licensed under the MIT License. See the LICENSE file for more details.

Links
-----

- [GitHub](https://github.com/Ilya-Kokhanovsky/soundpad.py)
- [PyPI page](https://pypi.org/project/soundpad_control)
- Original Java implementation: [SoundpadRemoteControl.java](https://www.leppsoft.com/soundpad/files/rc/SoundpadRemoteControl.java)

