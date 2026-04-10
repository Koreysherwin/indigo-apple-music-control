

## Version 1.0.7
- Replaced the non-ASCII placeholder character in the AppleScript path with an ASCII-safe token.
- Resolved errors like: `ascii' codec can't encode character '\xa7'`.
- Removed cached compiled files from the packaged bundle.

## Version 1.0.6
- Added serialized AppleScript execution so overlapping calls cannot pile up.
- Added AppleScript timeouts to reduce the chance of hung polling calls.
- Removed `System Events` process checks from the normal polling path.
- Increased the default polling interval to 5 seconds.
- Enforced a 2-second minimum polling interval in code.
- Reduced the risk of GUI/session instability caused by aggressive AppleScript polling.# Changelog

## [1.0.2] - 2025-01-09

### Fixed
- Fixed error when Music app has no current track (stopped state)
- Properly handle empty/stopped state without errors

## [1.0.1] - 2025-01-09

### Fixed
- Fixed AppleScript error with reserved keyword 'error'

## [1.0.0] - 2025-01-09

### Added
- Initial release
- Complete playback control (play, pause, stop, next, previous)
- Volume control with mute/unmute
- Position seeking (jump to time, skip forward/backward)
- Shuffle and three-mode repeat (off, one, all)
- Play playlists and albums by name
- Library search functionality
- 5-star rating support
- Rich metadata tracking (genre, composer, year, rating)
- Comprehensive state monitoring
- Variable integration for Control Pages
