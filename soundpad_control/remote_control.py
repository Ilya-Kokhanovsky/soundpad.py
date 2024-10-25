import enum
import time

from .errors import SoundpadRequestError, SoundpadNotLaunchedError

__all__ = ['SoundpadRemoteControl', 'PlayStatus']

class PlayStatus(enum.Enum):
    """Enumeration for playback states in Soundpad."""
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2
    SEEKING = 3

class SoundpadRemoteControl:
    """Remote controller for the Soundpad application through a named pipe."""

    CLIENT_VERSION: str = "1.1.2"
    STATUS_MAPPING: dict[str, PlayStatus] = {
        "PAUSED": PlayStatus.PAUSED,
        "STOPPED": PlayStatus.STOPPED,
        "PLAYING": PlayStatus.PLAYING,
        "SEEKING": PlayStatus.SEEKING,
    }

    def __init__(self):
        """Initializes the SoundpadRemoteControl instance with pipe configuration."""
        self.pipe = None
        self.pipe_name: str = 'sp_remote_control'
        self.chuck_size: int = 1024
        self.last_request_timestamp: int = int(time.time() * 1000)

    def _init_connection(self):
        """Initializes the connection to the Soundpad named pipe."""
        if self.pipe is None:
            try:
                self.pipe = open(r'\\.\pipe\{}'.format(self.pipe_name), 'r+b', buffering=0)
            except FileNotFoundError:
                raise SoundpadNotLaunchedError

    def _close_connection(self):
        """Closes the connection to the Soundpad named pipe."""
        if self.pipe:
            try:
                self.pipe.close()
            except Exception:
                pass
            finally:
                self.pipe = None

    def _join_params(self, *args: str) -> str:
        """Joins string representations of the provided arguments with a comma.
        
        Args:
            *args: A variable number of arguments.

        Returns:
            str: A single string containing all arguments concatenated by commas.
        """
        params: list[str] = [str(param) for param in args if param is not None]
        return ",".join(params)

    def _format_request(self, request: str | bytes) -> bytes:
        """Formats the request to be sent to the pipe.

        Args:
            request (str | bytes): The request to format.

        Returns:
            bytes: The formatted request as bytes.
        """
        return request if isinstance(request, bytes) else request.encode()

    def _is_empty(self, response: str) -> bool:
        return len(response) == 0

    def _is_success(self, response: str) -> bool:
        """Checks if the response indicates success.

        Args:
            response (str): The response string.

        Returns:
            bool: True if response indicates success, False otherwise.
        """
        return response.startswith("R-200")

    def _handle_string_get_request(self, request: str):
        response: str = self._send_request_no_exception(request)
        if response.startswith("R"):
            raise SoundpadRequestError(response)
        elif self._is_empty(response):
            raise SoundpadNotLaunchedError
        else:
            return response

    def _handle_empty_get_request(self, request: str):
        response: str = self._send_request_no_exception(request)
        if self._is_empty(response):
            raise SoundpadNotLaunchedError
        return response
    
    def _handle_simple_get_request(self, request: str) -> str:
        response: str = self._send_request_no_exception(request)
        if response.startswith("R"):
            raise SoundpadRequestError(response)
        else:
            return response

    def _handle_numeric_long_get_request(self, request: str | bytes) -> int:
        """Handles requests that expect a numeric long response.

        Args:
            request (str | bytes): The request to send.

        Returns:
            int: The numeric response, or -1 on failure.
        """
        response: str = self._send_request_no_exception(request)
        if response.startswith("R"):
            raise SoundpadRequestError(response)
        elif self._is_empty(response):
            raise SoundpadNotLaunchedError
        else:
            try:
                return int(response)
            except ValueError:
                return -1

    def _send_request(self, request: bytes) -> str:
        """Sends a request to the Soundpad named pipe.

        Args:
            request (bytes): The request data to send.

        Returns:
            str: The response received from the pipe.
        """
        self._init_connection()

        if int(time.time() * 1000) == self.last_request_timestamp:
            time.sleep(0.001)

        self.pipe.write(self._format_request(request))
        self.pipe.seek(0)

        response: bytes = self.pipe.read(self.chuck_size)
        self.pipe.seek(0)

        return response.decode()

    def _send_request_no_exception(self, request: str | bytes) -> str:
        """Sends a request to the Soundpad pipe and handles exceptions.

        Args:
            request (str | bytes): The request to send.

        Returns:
            str: The response from the request or an empty string on error.
        """
        try:
            return self._send_request(request)
        except Exception:
            self._close_connection()
            return ""

    def play_sound(self, index: int, speakers: bool = False, mic: bool = True) -> bool:
        """Plays a sound based on its index.

        Args:
            index (int): The index of the sound to play in the Soundpad list.
            speakers (bool, optional): Whether to play the sound through speakers. Defaults to False.
            mic (bool, optional): Whether to transmit the sound through the microphone. Defaults to True.

        Returns:
            bool: True if the sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                f"DoPlaySound({index},{speakers},{mic})"
            )
        )

    def play_sound_from_category(self, category_index: int, sound_index: int, speakers: bool = False, mic: bool = True) -> bool:
        """Plays a sound from a specific category based on indices.

        Args:
            category_index (int): The index of the category containing the sound.
            sound_index (int): The index of the sound within the specified category.
            speakers (bool, optional): Whether to play the sound through speakers. Defaults to False.
            mic (bool, optional): Whether to transmit the sound through the microphone. Defaults to True.

        Returns:
            bool: True if the sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                f"DoPlaySoundFromCategory({category_index},{sound_index},{speakers},{mic})"
            )
        )

    def play_previous_sound(self) -> bool:
        """Plays the previous sound in the Soundpad list.

        Returns:
            bool: True if the previous sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                "DoPlayPreviousSound()"
            )
        )

    def play_next_sound(self) -> bool:
        """Plays the next sound in the Soundpad list.

        Returns:
            bool: True if the next sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                "DoPlayNextSound()"
            )
        )

    def stop_sound(self) -> bool:
        """Stops the currently playing sound.

        Returns:
            bool: True if the sound was stopped successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                "DoStopSound()"
            )
        )

    def toggle_pause(self) -> bool:
        """Toggles the pause state of the currently playing sound.

        Returns:
            bool: True if the pause state was toggled successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                "DoTogglePause()"
            )
        )

    def jump_ms(self, time_millis: int) -> bool:
        """Jumps to a specific point in the current sound relative to the current playback position.

        Args:
            time_millis (int): The number of milliseconds to jump from the current position, positive or negative.

        Returns:
            bool: True if the jump was successful, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                f'DoJumpMs({time_millis})'
            )
        )

    def seek_ms(self, time_millis: int) -> bool:
        """Seeks to a specific time in the current sound.

        Args:
            time_millis (int): The time in milliseconds to seek to from the start of the sound.

        Returns:
            bool: True if the seek was successful, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                f"DoSeekMs({time_millis})"
            )
        )

    def add_sound(self, path: str, category_index: int = None, index: int = None) -> None:
        """Adds a sound file to the Soundpad library.

        Args:
            path (str): The file path of the sound to add.
            category_index (int, optional): The index of the category to add the sound to. Defaults to None.
            index (int, optional): The position within the category to insert the sound. Defaults to None.

        Returns:
            None
        """
        joined_params: list[str] = self._join_params(path, category_index, index)
        return self._send_request_no_exception(f"DoAddSound({joined_params})")

    def remove_selected_entries(self, remove_from_disk: bool = True) -> bool:
        """Removes selected sound entries from the library.

        Args:
            remove_from_disk (bool, optional): If True, deletes the sound files from disk as well. Defaults to True.

        Returns:
            bool: True if the entries were removed successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(
                f"DoRemoveSelectedEntries({remove_from_disk})"
            )
        )

    def get_sound_file_count(self) -> int:
        """Retrieves the count of sound files currently in the Soundpad library.

        Returns:
            int: The number of sound files.
        """
        return self._handle_numeric_long_get_request("GetSoundFileCount()")

    def search(self, search_term: str) -> bool:
        """Searches for sounds in the library by a given term.

        Args:
            search_term (str): The term to search for within the sound library.

        Returns:
            bool: True if the search was performed successfully, False otherwise.
        """
        response = self._send_request_no_exception(f"DoSearch({search_term})")

        if not response.startswith('R-200'):
            return False

        return True

    def reset_search(self) -> bool:
        """Resets the current search filter or results in the sound library.

        Returns:
            bool: True if the search was reset successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoResetSearch()")
        )

    def select_previous_hit(self) -> bool:
        """Selects the previous search result in the library.

        Returns:
            bool: True if the previous hit was selected successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoSelectPreviousHit()")
        )

    def select_next_hit(self) -> bool:
        """Selects the next search result in the library.

        Returns:
            bool: True if the next hit was selected successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoSelectNextHit()")
        )

    def select_row(self, index: int) -> bool:
        """Selects a row by index in the library.

        Args:
            index (int): The row index to select.

        Returns:
            bool: True if the row was selected successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoSelectIndex({index})")
        )
        
    def scroll_by(self, index: int) -> bool:
        """Scrolls by a specified number of rows in the library.

        Args:
            index (int): The number of rows to scroll by, positive or negative.

        Returns:
            bool: True if the scroll was successful, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoScrollBy({index})")
        )

    def scroll_to(self, index: int) -> bool:
        """Scrolls to a specific row index in the library.

        Args:
            index (int): The row index to scroll to.

        Returns:
            bool: True if the scroll was successful, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoScrollTo({index})")
        )

    def undo(self) -> bool:
        """Performs an undo operation for the last action in the library.

        Returns:
            bool: True if the undo was successful, False otherwise.
        """
        return self._is_success(self._send_request_no_exception("DoUndo()"))

    def redo(self) -> bool:
        """Performs a redo operation for the last undone action in the library.

        Returns:
            bool: True if the redo was successful, False otherwise.
        """
        return self._is_success(self._send_request_no_exception("DoRedo()"))

    def get_volume(self) -> int:
        """Gets the current volume level for sound playback.

        Returns:
            int: The current volume level as an integer.
        """
        return self._handle_numeric_long_get_request("GetVolume()")

    def is_muted(self) -> bool:
        """Checks if the sound playback is currently muted.

        Returns:
            bool: True if playback is muted, False otherwise.
        """
        return bool(self._handle_numeric_long_get_request("IsMuted()"))

    def toggle_mute(self) -> bool:
        """Toggles the mute state of the sound playback.

        Returns:
            bool: True if the mute state was toggled successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoToggleMute()")
        )

    def play_selected_sound(self) -> bool:
        """Plays the currently selected sound in the library.

        Returns:
            bool: True if the sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoPlaySelectedSound()")
        )
        
    def play_current_sound_again(self) -> bool:
        """Plays the currently active sound again.

        Returns:
            bool: True if the sound was played again successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoPlayCurrentSoundAgain()")
        )

    def play_previously_played_sound(self) -> bool:
        """Plays the sound that was previously played.

        Returns:
            bool: True if the previously played sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoPlayPreviouslyPlayedSound()")
        )

    def add_category(self, name: str, parent_category_index: int) -> bool:
        """Adds a new category to the sound library.

        Args:
            name (str): The name of the new category.
            parent_category_index (int): The index of the parent category.

        Returns:
            bool: True if the category was added successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoAddCategory({name}, {parent_category_index})")
        )
        
    def select_category(self, index: int) -> bool:
        """Selects a category by index in the library.

        Args:
            index (int): The index of the category to select.

        Returns:
            bool: True if the category was selected successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoSelectCategory({index})")
        )
        
    def select_previous_category(self) -> bool:
        """Selects the previous category in the library.

        Returns:
            bool: True if the previous category was selected successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoSelectPreviousCategory()")
        )

    def select_next_category(self) -> bool:
        """Selects the next category in the library.

        Returns:
            bool: True if the next category was selected successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoSelectNextCategory()")
        )

    def remove_category(self, category_index: int) -> bool:
        """Removes a category from the sound library.

        Args:
            category_index (int): The index of the category to remove.

        Returns:
            bool: True if the category was removed successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoRemoveCategory({category_index})")
        )
        
    def play_random_sound(self, speakers: bool = False, mic: bool = True) -> bool:
        """Plays a random sound from the library.

        Args:
            speakers (bool, optional): If True, plays the sound through speakers. Defaults to False.
            mic (bool, optional): If True, plays the sound through the microphone. Defaults to True.

        Returns:
            bool: True if the random sound was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoPlayRandomSound({speakers}, {mic})")
        )

    def play_random_sound_from_category(self, category_index: int, speakers: bool = False, mic: bool = True) -> bool:
        """Plays a random sound from a specified category.

        Args:
            category_index (int): The index of the category to play a sound from.
            speakers (bool, optional): If True, plays the sound through speakers. Defaults to False.
            mic (bool, optional): If True, plays the sound through the microphone. Defaults to True.

        Returns:
            bool: True if the random sound from the category was played successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception(f"DoPlayRandomSoundFromCategory({category_index},{speakers},{mic})")
        )
        
    def get_play_status(self) -> PlayStatus:
        """Gets the current play status of the sound library.

        Returns:
            PlayStatus: The current play status, mapped to the PlayStatus enum.
        """
        response: str = self._send_request_no_exception("GetPlayStatus()")
        try:
            return self.STATUS_MAPPING.get(response, PlayStatus.STOPPED)
        except Exception:
            return PlayStatus.STOPPED
        
    def start_recording(self) -> bool:
        """Starts recording sound.

        Returns:
            bool: True if recording started successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoStartRecording()")
        )

    def stop_recording(self) -> bool:
        """Stops the current sound recording.

        Returns:
            bool: True if recording stopped successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoStopRecording()")
        )

    def get_playback_position(self) -> int:
        """Gets the current playback position in milliseconds.

        Returns:
            int: The current playback position as an integer in milliseconds.
        """
        return self._handle_numeric_long_get_request("GetPlaybackPositionInMs()")

    def get_playback_duration(self) -> int:
        """Gets the total duration of the currently playing sound in milliseconds.

        Returns:
            int: The total playback duration as an integer in milliseconds.
        """
        return self._handle_numeric_long_get_request("GetPlaybackDurationInMs()")

    def get_recording_position(self) -> int:
        """Gets the current recording position in milliseconds.

        Returns:
            int: The current recording position as an integer in milliseconds.
        """
        return self._handle_numeric_long_get_request("GetRecordingPositionInMs()")
        
    def get_recording_peak(self) -> int:
        """Gets the peak level of the current recording.

        Returns:
            int: The peak level of the recording as an integer.
        """
        return self._handle_numeric_long_get_request("GetRecordingPeak()")

    def get_sound_list(self, from_index: int = None, to_index: int = None) -> str:
        """Gets a list of sounds from the library.

        Args:
            from_index (int, optional): The starting index of the sound list. Defaults to None.
            to_index (int, optional): The ending index of the sound list. Defaults to None.

        Returns:
            str: The list of sounds as a string.
        """
        joined_params: str = self._join_params(from_index, to_index)

        return self._handle_string_get_request(f"GetSoundlist({joined_params})")

    def get_main_frame_title_text(self) -> str:
        """Gets the title text of the main frame.

        Returns:
            str: The title text of the main frame.
        """
        return self._handle_simple_get_request("GetTitleText()")

    def get_status_bar_text(self) -> str:
        """Gets the text displayed in the status bar.

        Returns:
            str: The current status bar text.
        """
        return self._handle_simple_get_request("GetStatusBarText()")
        
    def get_version(self) -> str:
        """Gets the current version of the application.

        Returns:
            str: The application version.
        """
        return self._handle_empty_get_request("GetVersion()")
        
    def get_remote_control_version(self) -> str:
        """Gets the version of the remote control protocol.

        Returns:
            str: The remote control version.
        """
        return self._handle_empty_get_request("GetRemoteControlVersion()")

    def is_compatible(self) -> bool:
        """Checks if the current client version is compatible with the remote control version.

        Returns:
            bool: True if the client version is compatible, False otherwise.
        """
        return self.CLIENT_VERSION == self.get_remote_control_version()
        
    def is_alive(self) -> bool:
        """Checks if the application is alive and responsive.

        Returns:
            bool: True if the application is alive, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("IsAlive()")
        )

    def start_recording_speakers(self) -> bool:
        """Starts recording sound from the speakers.

        Returns:
            bool: True if the speakers' recording started successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoStartRecordingSpeakers()")
        )

    def start_recording_microphone(self) -> bool:
        """Starts recording sound from the microphone.

        Returns:
            bool: True if the microphone recording started successfully, False otherwise.
        """
        return self._is_success(
            self._send_request_no_exception("DoStartRecordingMicrophone()")
        )

    def is_trial(self) -> bool:
        """Checks if the application is currently in trial mode.

        Returns:
            bool: True if the application is in trial mode, False otherwise.
        """
        response: int = self._handle_numeric_long_get_request("IsTrial()")
        return bool(response)