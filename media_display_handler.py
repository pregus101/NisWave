import sys
import time
import threading
import objc

# 1. Protect imports for cross-platform compatibility
if sys.platform == 'darwin':
    from Foundation import NSDictionary, NSRunLoop, NSDate, NSBundle
    from MediaPlayer import (
        MPNowPlayingInfoCenter, 
        MPMediaItemPropertyTitle, 
        MPMediaItemPropertyArtist, 
        MPNowPlayingInfoPropertyElapsedPlaybackTime,
        MPNowPlayingInfoPropertyPlaybackRate,
        MPMediaItemPropertyPlaybackDuration,
        MPNowPlayingPlaybackStatePlaying,
        MPRemoteCommandCenter,
        MPRemoteCommandHandlerStatusSuccess
    )
    
    # 2. Trick macOS into treating this script as a real App (The "Bundle ID" fix)
    bundle = NSBundle.mainBundle()
    info = bundle.infoDictionary()
    if info is not None:
        info['CFBundleIdentifier'] = 'com.niswave.player'
    IS_MAC = True
else:
    IS_MAC = False

class MediaHandler:
    def __init__(self, song, artist, total_time, player):
        self.song = song
        self.artist = artist
        self.total_time = total_time
        self.current_time = 0
        self.running = True
        self.player = player
        
        if IS_MAC:
            # Setup the 'Buttons' in Control Center
            self._setup_commands()
            # Start background thread to keep the OS connection alive
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def _setup_commands(self):
        """Registers listeners using the more stable block-based API."""
        command_center = MPRemoteCommandCenter.sharedCommandCenter()
        
        # 1. Play Command
        play_cmd = command_center.playCommand()
        play_cmd.setEnabled_(True)
        # We use a lambda/function block instead of a selector string
        play_cmd.addTargetWithHandler_(self.handle_play_event)
        
        # 2. Pause Command
        pause_cmd = command_center.pauseCommand()
        pause_cmd.setEnabled_(True)
        pause_cmd.addTargetWithHandler_(self.handle_pause_event)

    # Note: No @objc.signature needed for this approach!
    def handle_play_event(self, event):
        print("macOS: Play button pressed in Control Center")
        # Add your music resume logic here
        return 0 # MPRemoteCommandHandlerStatusSuccess

    def handle_pause_event(self, event):
        print("macOS: Pause button pressed in Control Center")
        # Add your music pause logic here
        return 0 # MPRemoteCommandHandlerStatusSuccess

    def _run_loop(self):
        """Background thread that keeps the macOS 'RunLoop' pumping."""
        while self.running:
            # We must process system events or the media info will be cleared
            NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.5))
            time.sleep(0.1)

    def update(self, current_time):
        """Call this method whenever the song time changes."""
        self.current_time = current_time
        if IS_MAC:
            now_playing_center = MPNowPlayingInfoCenter.defaultCenter()
            
            # Construct the metadata dictionary
            song_info = {
                MPMediaItemPropertyTitle: self.song,
                MPMediaItemPropertyArtist: self.artist,
                MPMediaItemPropertyPlaybackDuration: self.total_time,
                MPNowPlayingInfoPropertyElapsedPlaybackTime: self.current_time,
                MPNowPlayingInfoPropertyPlaybackRate: 1.0 # Tells OS the clock is moving
            }

            # Push to System
            now_playing_center.setNowPlayingInfo_(NSDictionary.dictionaryWithDictionary_(song_info))
            now_playing_center.setPlaybackState_(MPNowPlayingPlaybackStatePlaying)

    def stop(self):
        self.running = False