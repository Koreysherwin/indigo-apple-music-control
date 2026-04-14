## Version 1.0.7
- Replaced non-ASCII delimiter in AppleScript payload with ASCII-safe __PIPE__ to avoid encoding errors in Indigo's current runtime

## [1.0.6] - 2026-04-10

### Changed
- Removed `System Events` process checks from polling
- Added serialized AppleScript execution with timeout protection
- Increased default update frequency to 5 seconds and enforced 2 second minimum

# Changelog

All notable changes to the Apple Music Control Plugin will be documented in this file.

## [1.0.5] - 2024-10-31

### Fixed
- **Device action execution error**: Fixed "'DeviceCmds' object has no attribute 'execute'" error
- Added `actionControlDevice` method to properly handle device actions from Indigo
- Improved error handling for device action execution

### Added
- Device action mapping for TurnOn (Play), TurnOff (Pause), and Toggle (Play/Pause)
- Better debug logging for action execution

## [1.0.4] - 2024-10-28

### Fixed
- **Streaming radio station support**: Fixed "could not convert string to float: 'missing value'" error when playing streaming radio stations
- Added safe handling for all numeric fields that may return 'missing value' from AppleScript
- Duration, position, track number, disc number, rating, year, and volume now handle missing values gracefully

### Added
- Streaming station indicator in status display shows "[Streaming]" tag for radio stations
- Helper function `safe_int()` for robust handling of AppleScript 'missing value' returns

### Changed
- Streaming stations now show duration as 0 instead of causing errors
- Status display enhanced to differentiate between regular tracks and streaming content

## [1.0.3] - 2024-10-28

### Fixed
- **Action visibility in Action Groups**: Changed `deviceFilter="self"` to `deviceFilter="self.appleMusicPlayer"` in Actions.xml for better action registration with Indigo
- Actions now properly appear when selecting "Device Actions" → "Apple Music Player" in Action Groups

### Added
- Debug logging to all action handler methods for better troubleshooting
- Documentation clarification on how to use actions in Action Groups

### Changed
- Updated plugin version to 1.0.3 in Info.plist
- Enhanced README with clearer instructions for using actions

## [1.0.2] - 2024-10-XX

### Fixed
- Fixed error when Music app has no current track (stopped state)
- Properly handle empty/stopped state without errors in AppleScript execution

## [1.0.1] - 2024-10-XX

### Fixed
- Fixed AppleScript error with reserved keyword 'error'
- Improved error handling in AppleScript execution

## [1.0.0] - 2024-10-XX

### Added
- Initial release
- Complete playback control (play, pause, stop, next, previous)
- Comprehensive state monitoring (track info, playback position, volume, etc.)
- Volume control with mute/unmute functionality
- Position control (skip forward/backward, set position)
- Shuffle and repeat controls
- Playlist, album, and search playback
- 5-star rating support
- Library search functionality
- Configurable update frequency
- Optional Indigo variable integration
- Full AppleScript integration with Music app

### Features
- 30+ device states for complete Music app monitoring
- 20+ actions for full playback control
- Real-time status updates
- Works with both Apple Music subscription and local library
- No API credentials required
- Local-only operation (no network requests)
