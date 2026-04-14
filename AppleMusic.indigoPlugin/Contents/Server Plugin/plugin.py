#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Apple Music Control Plugin for Indigo
Provides comprehensive control and monitoring of Apple Music playback
Version 1.0.7 - Reduced AppleScript/UI scripting load, added timeouts, and ASCII-safe payload delimiter
"""

import indigo
import time
import subprocess
import json
import re
import threading

kUpdateFrequencyKey = "updateFrequency"
MIN_UPDATE_FREQUENCY = 2.0
APPLE_SCRIPT_TIMEOUT = 3.0
BUSY_RESULT = "__BUSY__"


class Plugin(indigo.PluginBase):
    """Main plugin class for Apple Music control"""

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get("showDebugInfo", False)
        self.deviceDict = {}
        self.scriptLock = threading.Lock()

    def startup(self):
        self.debugLog(u"Apple Music Plugin startup called")

    def shutdown(self):
        self.debugLog(u"Apple Music Plugin shutdown called")

    def deviceStartComm(self, dev):
        self.debugLog(u"Starting device: " + dev.name)
        updateFreq = max(MIN_UPDATE_FREQUENCY, float(dev.pluginProps.get(kUpdateFrequencyKey, 5)))
        self.deviceDict[dev.id] = {
            'device': dev,
            'updateFrequency': updateFreq,
            'lastUpdate': 0,
            'previousVolume': None,
        }
        self.updateAppleMusicStatus(dev)

    def deviceStopComm(self, dev):
        self.debugLog(u"Stopping device: " + dev.name)
        if dev.id in self.deviceDict:
            del self.deviceDict[dev.id]

    def runConcurrentThread(self):
        try:
            while True:
                currentTime = time.time()
                for devId, devInfo in list(self.deviceDict.items()):
                    dev = devInfo['device']
                    updateFreq = devInfo['updateFrequency']
                    lastUpdate = devInfo['lastUpdate']
                    if currentTime - lastUpdate >= updateFreq:
                        self.updateAppleMusicStatus(dev)
                        devInfo['lastUpdate'] = currentTime
                self.sleep(0.25)
        except self.StopThread:
            pass

    def updateAppleMusicStatus(self, dev):
        try:
            if not self.isProcessRunning("Music"):
                dev.updateStatesOnServer([
                    {'key': 'playerState', 'value': 'stopped'},
                    {'key': 'isPlaying', 'value': False},
                    {'key': 'isPaused', 'value': False},
                    {'key': 'isStopped', 'value': True},
                    {'key': 'status', 'value': 'Not Running'}
                ])
                return

            script = r'''
            tell application "Music"
                try
                    set playerState to player state as string
                    set soundVol to sound volume
                    set isShuffleEnabled to shuffle enabled
                    set repeatMode to song repeat as string
                    if playerState is not equal to "stopped" then
                        set trackName to name of current track
                        set trackArtist to artist of current track
                        set trackAlbum to album of current track
                        set trackDuration to duration of current track
                        set playerPos to player position
                        set trackNumber to track number of current track
                        set discNumber to disc number of current track
                        set trackGenre to genre of current track
                        set trackComposer to composer of current track
                        set trackRating to rating of current track
                        set trackYear to year of current track
                        set albumArtist to album artist of current track
                        set trackName to my replaceText(trackName, "|", "__PIPE__")
                        set trackArtist to my replaceText(trackArtist, "|", "__PIPE__")
                        set trackAlbum to my replaceText(trackAlbum, "|", "__PIPE__")
                        set trackGenre to my replaceText(trackGenre, "|", "__PIPE__")
                        set trackComposer to my replaceText(trackComposer, "|", "__PIPE__")
                        set albumArtist to my replaceText(albumArtist, "|", "__PIPE__")
                        return "SUCCESS:" & playerState & "|" & trackName & "|" & trackArtist & "|" & trackAlbum & "|" & trackDuration & "|" & playerPos & "|" & trackNumber & "|" & discNumber & "|" & trackGenre & "|" & trackComposer & "|" & trackRating & "|" & trackYear & "|" & albumArtist & "|" & soundVol & "|" & isShuffleEnabled & "|" & repeatMode
                    else
                        return "STOPPED|" & soundVol & "|" & isShuffleEnabled & "|" & repeatMode
                    end if
                on error errMsg number errNum
                    return "ERROR:" & errNum & ":" & errMsg
                end try
            end tell
            on replaceText(theText, oldString, newString)
                set AppleScript's text item delimiters to oldString
                set textItems to text items of theText
                set AppleScript's text item delimiters to newString
                set theText to textItems as string
                set AppleScript's text item delimiters to ""
                return theText
            end replaceText
            '''
            result = self.executeAppleScript(script, waitForLock=False)
            if result in (None, BUSY_RESULT):
                return

            def safe_int(value, default=0):
                if value in ('missing value', None, ''):
                    return default
                try:
                    return int(float(value))
                except (TypeError, ValueError):
                    return default

            def safe_float(value, default=0.0):
                if value in ('missing value', None, ''):
                    return default
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return default

            if result.startswith("SUCCESS:"):
                parts = result[8:].split("|")
                if len(parts) < 16:
                    return
                playerState = parts[0]
                trackName = parts[1].replace("__PIPE__", "|")
                artist = parts[2].replace("__PIPE__", "|")
                album = parts[3].replace("__PIPE__", "|")
                genre = parts[8].replace("__PIPE__", "|")
                composer = parts[9].replace("__PIPE__", "|")
                albumArtist = parts[12].replace("__PIPE__", "|")
                duration = safe_float(parts[4])
                position = safe_float(parts[5])
                volume = safe_int(parts[13], 50)
                stateList = [
                    {'key': 'playerState', 'value': playerState},
                    {'key': 'isPlaying', 'value': playerState == 'playing'},
                    {'key': 'isPaused', 'value': playerState == 'paused'},
                    {'key': 'isStopped', 'value': playerState == 'stopped'},
                    {'key': 'trackName', 'value': trackName},
                    {'key': 'artist', 'value': artist},
                    {'key': 'album', 'value': album},
                    {'key': 'albumArtist', 'value': albumArtist},
                    {'key': 'trackNumber', 'value': safe_int(parts[6])},
                    {'key': 'discNumber', 'value': safe_int(parts[7])},
                    {'key': 'genre', 'value': genre},
                    {'key': 'composer', 'value': composer},
                    {'key': 'rating', 'value': safe_int(parts[10])},
                    {'key': 'year', 'value': safe_int(parts[11])},
                    {'key': 'duration', 'value': int(duration)},
                    {'key': 'durationFormatted', 'value': self.formatTime(duration)},
                    {'key': 'playerPosition', 'value': int(position)},
                    {'key': 'playerPositionFormatted', 'value': self.formatTime(position)},
                    {'key': 'progressPercent', 'value': int((position / duration) * 100) if duration > 0 else 0},
                    {'key': 'soundVolume', 'value': volume},
                    {'key': 'muted', 'value': volume == 0},
                    {'key': 'shuffleEnabled', 'value': parts[14] == 'true'},
                    {'key': 'songRepeat', 'value': parts[15]},
                ]
                if playerState == 'playing':
                    status = u"▶ {} - {}".format(artist, trackName)
                elif playerState == 'paused':
                    status = u"⏸ {} - {}".format(artist, trackName)
                else:
                    status = u"⏹ Stopped"
                stateList.append({'key': 'status', 'value': status})
                dev.updateStatesOnServer(stateList)
                if dev.pluginProps.get('updateVariables', False):
                    self.updateVariables(dev, stateList)
                return

            if result.startswith("STOPPED"):
                parts = result.split("|")
                volume = safe_int(parts[1], 50) if len(parts) > 1 else 50
                shuffleEnabled = parts[2] == 'true' if len(parts) > 2 else False
                repeatMode = parts[3] if len(parts) > 3 else 'off'
                dev.updateStatesOnServer([
                    {'key': 'playerState', 'value': 'stopped'},
                    {'key': 'isPlaying', 'value': False},
                    {'key': 'isPaused', 'value': False},
                    {'key': 'isStopped', 'value': True},
                    {'key': 'soundVolume', 'value': volume},
                    {'key': 'muted', 'value': volume == 0},
                    {'key': 'shuffleEnabled', 'value': shuffleEnabled},
                    {'key': 'songRepeat', 'value': repeatMode},
                    {'key': 'status', 'value': u'⏹ Stopped'}
                ])
        except Exception as e:
            self.errorLog(u"Exception in updateAppleMusicStatus: {}".format(str(e)))

    def updateVariables(self, dev, stateList):
        try:
            prefix = dev.pluginProps.get('variablePrefix', 'AppleMusic')
            for state in stateList:
                varName = prefix + state['key'][0].upper() + state['key'][1:]
                if varName not in indigo.variables:
                    indigo.variable.create(varName, value=str(state['value']), folder=0)
                else:
                    indigo.variable.updateValue(varName, value=str(state['value']))
        except Exception as e:
            self.errorLog(u"Exception in updateVariables: {}".format(str(e)))

    def formatTime(self, seconds):
        try:
            seconds = int(seconds)
            minutes = seconds // 60
            secs = seconds % 60
            return u"{}:{:02d}".format(minutes, secs)
        except Exception:
            return "0:00"

    def isProcessRunning(self, processName):
        try:
            result = subprocess.run(['pgrep', '-x', processName], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return result.returncode == 0
        except Exception:
            return False

    def executeAppleScript(self, script, timeout=APPLE_SCRIPT_TIMEOUT, waitForLock=True):
        lockAcquired = False
        try:
            if waitForLock:
                self.scriptLock.acquire()
                lockAcquired = True
            else:
                lockAcquired = self.scriptLock.acquire(False)
                if not lockAcquired:
                    return BUSY_RESULT
            process = subprocess.run(
                ['osascript', '-'], input=script, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
            )
            if process.stderr:
                self.debugLog(u"AppleScript stderr: {}".format(process.stderr.strip()))
            return process.stdout.strip()
        except subprocess.TimeoutExpired:
            self.errorLog(u"AppleScript timed out after {} seconds".format(timeout))
            return None
        except Exception as e:
            self.errorLog(u"Exception in executeAppleScript: {}".format(str(e)))
            return None
        finally:
            if lockAcquired:
                self.scriptLock.release()

    ########################################
    # Device Action Control
    ########################################
    
    def actionControlDevice(self, action, dev):
        """
        Main entry point for device actions from Indigo
        This method is called when actions are executed from Action Groups
        """
        try:
            self.debugLog(u"actionControlDevice called: action={}, device={}".format(action.deviceAction, dev.name))
            
            # Map device actions to their handler methods
            actionMap = {
                indigo.kDeviceAction.TurnOn: self.actionPlay,
                indigo.kDeviceAction.TurnOff: self.actionPause,
                indigo.kDeviceAction.Toggle: self.actionPlayPause,
            }
            
            # Execute the mapped action if it exists
            if action.deviceAction in actionMap:
                actionMap[action.deviceAction](action, dev)
            else:
                self.errorLog(u"Unknown device action: {}".format(action.deviceAction))
                
        except Exception as e:
            self.errorLog(u"Exception executing action on {}: {}".format(dev.name, str(e)))
            
    ########################################
    # Action Handlers
    ########################################
    
    def actionPlay(self, pluginAction, dev):
        """Play action"""
        self.debugLog(u"actionPlay called for device: " + dev.name)
        script = 'tell application "Music" to play'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionPause(self, pluginAction, dev):
        """Pause action"""
        self.debugLog(u"actionPause called for device: " + dev.name)
        script = 'tell application "Music" to pause'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionPlayPause(self, pluginAction, dev):
        """Play/Pause toggle action"""
        self.debugLog(u"actionPlayPause called for device: " + dev.name)
        script = 'tell application "Music" to playpause'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionStop(self, pluginAction, dev):
        """Stop action"""
        self.debugLog(u"actionStop called for device: " + dev.name)
        script = 'tell application "Music" to stop'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionNextTrack(self, pluginAction, dev):
        """Next track action"""
        self.debugLog(u"actionNextTrack called for device: " + dev.name)
        script = 'tell application "Music" to next track'
        self.executeAppleScript(script)
        time.sleep(0.5)  # Give Music time to switch tracks
        self.updateAppleMusicStatus(dev)
        
    def actionPreviousTrack(self, pluginAction, dev):
        """Previous track action"""
        self.debugLog(u"actionPreviousTrack called for device: " + dev.name)
        script = 'tell application "Music" to previous track'
        self.executeAppleScript(script)
        time.sleep(0.5)  # Give Music time to switch tracks
        self.updateAppleMusicStatus(dev)
        
    def actionSetVolume(self, pluginAction, dev):
        """Set volume action"""
        self.debugLog(u"actionSetVolume called for device: " + dev.name)
        volume = int(pluginAction.props.get('volume', 50))
        volume = max(0, min(100, volume))  # Clamp between 0-100
        script = f'tell application "Music" to set sound volume to {volume}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionVolumeUp(self, pluginAction, dev):
        """Volume up action"""
        self.debugLog(u"actionVolumeUp called for device: " + dev.name)
        amount = int(pluginAction.props.get('amount', 10))
        currentVolume = int(dev.states.get('soundVolume', 50))
        newVolume = min(100, currentVolume + amount)
        script = f'tell application "Music" to set sound volume to {newVolume}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionVolumeDown(self, pluginAction, dev):
        """Volume down action"""
        self.debugLog(u"actionVolumeDown called for device: " + dev.name)
        amount = int(pluginAction.props.get('amount', 10))
        currentVolume = int(dev.states.get('soundVolume', 50))
        newVolume = max(0, currentVolume - amount)
        script = f'tell application "Music" to set sound volume to {newVolume}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionMute(self, pluginAction, dev):
        """Mute action"""
        self.debugLog(u"actionMute called for device: " + dev.name)
        devInfo = self.deviceDict.get(dev.id)
        if devInfo:
            # Store current volume
            currentVolume = int(dev.states.get('soundVolume', 50))
            devInfo['previousVolume'] = currentVolume
        script = 'tell application "Music" to set sound volume to 0'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionUnmute(self, pluginAction, dev):
        """Unmute action"""
        self.debugLog(u"actionUnmute called for device: " + dev.name)
        devInfo = self.deviceDict.get(dev.id)
        previousVolume = 50  # Default
        if devInfo and devInfo.get('previousVolume'):
            previousVolume = devInfo['previousVolume']
        script = f'tell application "Music" to set sound volume to {previousVolume}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionSetPosition(self, pluginAction, dev):
        """Set playback position action"""
        self.debugLog(u"actionSetPosition called for device: " + dev.name)
        position = int(pluginAction.props.get('position', 0))
        script = f'tell application "Music" to set player position to {position}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionSkipForward(self, pluginAction, dev):
        """Skip forward action"""
        self.debugLog(u"actionSkipForward called for device: " + dev.name)
        seconds = int(pluginAction.props.get('seconds', 10))
        currentPos = int(dev.states.get('playerPosition', 0))
        newPos = currentPos + seconds
        script = f'tell application "Music" to set player position to {newPos}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionSkipBackward(self, pluginAction, dev):
        """Skip backward action"""
        self.debugLog(u"actionSkipBackward called for device: " + dev.name)
        seconds = int(pluginAction.props.get('seconds', 10))
        currentPos = int(dev.states.get('playerPosition', 0))
        newPos = max(0, currentPos - seconds)
        script = f'tell application "Music" to set player position to {newPos}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionSetShuffle(self, pluginAction, dev):
        """Set shuffle action"""
        self.debugLog(u"actionSetShuffle called for device: " + dev.name)
        shuffleState = pluginAction.props.get('shuffleState', 'toggle')
        
        if shuffleState == 'toggle':
            currentShuffle = dev.states.get('shuffleEnabled', False)
            shuffleState = 'off' if currentShuffle else 'on'
        
        shuffleBool = 'true' if shuffleState == 'on' else 'false'
        script = f'tell application "Music" to set shuffle enabled to {shuffleBool}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionSetRepeat(self, pluginAction, dev):
        """Set repeat action"""
        self.debugLog(u"actionSetRepeat called for device: " + dev.name)
        repeatState = pluginAction.props.get('repeatState', 'toggle')
        
        if repeatState == 'toggle':
            currentRepeat = dev.states.get('songRepeat', 'off')
            if currentRepeat == 'off':
                repeatState = 'all'
            elif currentRepeat == 'all':
                repeatState = 'one'
            else:
                repeatState = 'off'
        
        script = f'tell application "Music" to set song repeat to {repeatState}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionPlayPlaylist(self, pluginAction, dev):
        """Play playlist action"""
        self.debugLog(u"actionPlayPlaylist called for device: " + dev.name)
        playlistName = pluginAction.props.get('playlistName', '')
        if playlistName:
            script = f'''
            tell application "Music"
                try
                    play playlist "{playlistName}"
                on error
                    display dialog "Playlist not found: {playlistName}"
                end try
            end tell
            '''
            self.executeAppleScript(script)
            time.sleep(0.5)
            self.updateAppleMusicStatus(dev)
        
    def actionPlayAlbum(self, pluginAction, dev):
        """Play album action"""
        self.debugLog(u"actionPlayAlbum called for device: " + dev.name)
        albumName = pluginAction.props.get('albumName', '')
        artistName = pluginAction.props.get('artistName', '')
        
        if albumName:
            if artistName:
                script = f'''
                tell application "Music"
                    try
                        set theAlbum to first track of library whose album is "{albumName}" and artist is "{artistName}"
                        play theAlbum
                    on error
                        display dialog "Album not found: {albumName} by {artistName}"
                    end try
                end tell
                '''
            else:
                script = f'''
                tell application "Music"
                    try
                        set theAlbum to first track of library whose album is "{albumName}"
                        play theAlbum
                    on error
                        display dialog "Album not found: {albumName}"
                    end try
                end tell
                '''
            self.executeAppleScript(script)
            time.sleep(0.5)
            self.updateAppleMusicStatus(dev)
        
    def actionSearchAndPlay(self, pluginAction, dev):
        """Search and play action"""
        self.debugLog(u"actionSearchAndPlay called for device: " + dev.name)
        searchQuery = pluginAction.props.get('searchQuery', '')
        if searchQuery:
            script = f'''
            tell application "Music"
                try
                    set searchResults to (search library for "{searchQuery}")
                    if (count of searchResults) > 0 then
                        play item 1 of searchResults
                    else
                        display dialog "No results found for: {searchQuery}"
                    end if
                on error
                    display dialog "Search failed for: {searchQuery}"
                end try
            end tell
            '''
            self.executeAppleScript(script)
            time.sleep(0.5)
            self.updateAppleMusicStatus(dev)
    
    def actionSetRating(self, pluginAction, dev):
        """Set rating action"""
        self.debugLog(u"actionSetRating called for device: " + dev.name)
        rating = int(pluginAction.props.get('rating', 0))
        script = f'tell application "Music" to set rating of current track to {rating}'
        self.executeAppleScript(script)
        self.updateAppleMusicStatus(dev)
        
    def actionUpdateNow(self, pluginAction, dev):
        """Force immediate update"""
        self.debugLog(u"actionUpdateNow called for device: " + dev.name)
        self.updateAppleMusicStatus(dev)
