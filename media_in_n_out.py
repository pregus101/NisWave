import sys
import time
import threading
import plistlib
from typing import Any
from Song_Bar import SongBar
from input_handler import Inputs

oper: str

data_lock: threading.Lock = threading.Lock()

if sys.platform.startswith('win'):
    oper = "windows"
elif sys.platform.startswith('linux'):
    oper = "linux"
elif sys.platform == 'darwin':
    oper = "mac"
else:
    raise OSError("Unsupported OS")

_bridge: Any = None

if oper == "mac":
    from Foundation import (
        NSObject, NSData, NSPropertyListSerialization
    )
    from MediaPlayer import (
        MPNowPlayingInfoCenter,
        MPMediaItemPropertyTitle,
        MPMediaItemPropertyArtist,
        MPMediaItemPropertyPlaybackDuration,
        MPMusicPlaybackStatePlaying,
        MPMusicPlaybackStatePaused,
        MPNowPlayingInfoPropertyMediaType,
        MPNowPlayingInfoPropertyPlaybackRate,
        MPNowPlayingInfoPropertyElapsedPlaybackTime,
        MPRemoteCommandCenter,
        MPRemoteCommandHandlerStatusSuccess,
    )

    _elapsed_key: str = str(MPNowPlayingInfoPropertyElapsedPlaybackTime)

    def _make_ns_info(py_dict: dict) -> Any:
        plist_bytes = plistlib.dumps(py_dict)
        ns_data = NSData.dataWithBytes_length_(plist_bytes, len(plist_bytes))
        result, _, _ = NSPropertyListSerialization.propertyListWithData_options_format_error_(
            ns_data, 0, None, None
        )
        return result

    _bridge_state: dict = {}

    class _NowPlayingBridge(NSObject):
        def updateInfo_(self, info):
            _bridge_state['last_ns'] = info
            ic = MPNowPlayingInfoCenter.defaultCenter()
            ic.setNowPlayingInfo_(info)
            ic.setPlaybackState_(MPMusicPlaybackStatePlaying)

        def updateElapsed_(self, pos):
            py_dict = _bridge_state.get('info_py')
            if py_dict is None:
                return
            py_dict[_elapsed_key] = float(pos)
            ns_info = _make_ns_info(py_dict)
            if ns_info is None:
                return
            ic = MPNowPlayingInfoCenter.defaultCenter()
            ic.setNowPlayingInfo_(ns_info)

        def setPaused_(self, paused):
            ic = MPNowPlayingInfoCenter.defaultCenter()
            if bool(paused):
                ic.setPlaybackState_(MPMusicPlaybackStatePaused)
            else:
                ic.setPlaybackState_(MPMusicPlaybackStatePlaying)

    _bridge = _NowPlayingBridge.alloc().init()


def media_loop(media_handle, player: Inputs, data) -> None:
    running: bool = media_handle.running
    while running:
        running = media_handle.running
        if data.playing_song != media_handle.song:
            data.updated = False
            data.playing_song = media_handle.song
            data.artist = media_handle.artist

        if media_handle.paused != data.paused:
            data.paused = media_handle.paused
            data.pause_update = True

        

        if oper == "mac" and _bridge is not None:
            if not data.updated and data.playing_song and data.playing_song != "None":
                py_dict = {
                    str(MPMediaItemPropertyTitle): data.playing_song,
                    str(MPMediaItemPropertyArtist): data.artist,
                    str(MPMediaItemPropertyPlaybackDuration): float(media_handle.length),
                    str(MPNowPlayingInfoPropertyMediaType): 1,
                    str(MPNowPlayingInfoPropertyPlaybackRate): 1.0,
                    str(MPNowPlayingInfoPropertyElapsedPlaybackTime): 0.0,
                }
                _bridge_state['info_py'] = py_dict
                ns_info = _make_ns_info(py_dict)
                _bridge.performSelectorOnMainThread_withObject_waitUntilDone_(
                    'updateInfo:', ns_info, False
                )
                data.updated = True

            if data.pause_update:
                _bridge.performSelectorOnMainThread_withObject_waitUntilDone_(
                    'setPaused:', data.paused, False
                )
                data.pause_update = False

            if media_handle.pos_update:
                _bridge.performSelectorOnMainThread_withObject_waitUntilDone_(
                    'updateElapsed:', float(media_handle.pos), False
                )
                media_handle.pos_update = False

        time.sleep(0.1)


class data:
    def __init__(self) -> None:
        self.playing_song: str = ""
        self.artist: str = ""
        self.pos: str = ""
        self.updated: bool = False
        self.paused = True
        self.pause_update = False


class media_out_handle():

    def __init__(self, player: Inputs, bar: SongBar = None) -> None:
        self.song: str = ""
        self.artist: str = ""
        self.running: bool = True
        self.player: Inputs = player
        self.paused: bool = True
        self.length: int = 0
        self.pos: int = 0
        self.image: str = ""
        self.pos_update = False
        self.bar = bar

        if oper == "mac":
            _cmd = MPRemoteCommandCenter.sharedCommandCenter()
            _cmd.playCommand().addTargetWithHandler_(
                lambda e: (player.pause(bar), MPRemoteCommandHandlerStatusSuccess)[1]
            )
            _cmd.pauseCommand().addTargetWithHandler_(
                lambda e: (player.pause(bar), MPRemoteCommandHandlerStatusSuccess)[1]
            )
            _cmd.nextTrackCommand().addTargetWithHandler_(
                lambda e: (player.next(bar), MPRemoteCommandHandlerStatusSuccess)[1]
            )
            _cmd.previousTrackCommand().addTargetWithHandler_(
                lambda e: (player.previous(bar), MPRemoteCommandHandlerStatusSuccess)[1]
            )
            if hasattr(_cmd, 'changePlaybackPositionCommand'):
                _cmd.changePlaybackPositionCommand().addTargetWithHandler_(
                    lambda e: (player.visualizer.set_position(e.positionTime()) if player.visualizer else None, MPRemoteCommandHandlerStatusSuccess)[1]
                )

        self.media_loop_thread: threading.Thread = threading.Thread(
            target=media_loop, args=(self, player, data())
        )
        self.media_loop_thread.daemon = True
        self.media_loop_thread.start()

    def update_song(self, artist: str, song: str, length: int) -> None:
        self.set_pause(False)
        self.pos = 0
        self.song = song
        self.length = length
        self.artist = artist
        self.image = ""

    def update_pos(self, pos: int) -> None:
        self.pos = pos
        self.pos_update = True

    def pause_toggle(self) -> None:
        self.paused = not self.paused

    def set_pause(self, toggle: bool) -> None:
        self.paused: bool = toggle

    def kill(self) -> None:
        self.running = False

if __name__ == '__main__':
    while True:
        time.sleep(1)
