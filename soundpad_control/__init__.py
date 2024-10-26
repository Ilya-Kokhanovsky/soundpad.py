"""
Soundpad Control API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A basic wrapper for controlling Soundpad remotely.

:copyright: (c) 2024-present Ilya Kokhanovsky
:license: MIT, see LICENSE for more details.

"""

__title__ = 'soundpad_control'
__author__ = 'Ilya Kokhanovsky'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024-present Ilya Kokhanovsky'
__version__ = '0.1.2'

from .remote_control import SoundpadRemoteControl

__all__ = ['SoundpadRemoteControl']