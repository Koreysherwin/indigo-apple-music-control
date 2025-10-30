# Apple Music Control Plugin for Indigo

A comprehensive Indigo plugin for controlling Apple Music and monitoring all playback data in real-time.

## Features

### Device States (Auto-Updated)
The plugin tracks and updates the following Apple Music information:

#### Playback Status
- **Player State**: playing, paused, or stopped
- **Is Playing**: Boolean indicator
- **Is Paused**: Boolean indicator  
- **Is Stopped**: Boolean indicator

#### Track Information
- **Track Name**: Current track title
- **Artist**: Track artist(s)
- **Album**: Album name
- **Album Artist**: Album artist
- **Track Number**: Track number on album
- **Disc Number**: Disc number for multi-disc albums
- **Genre**: Music genre
- **Composer**: Track composer
- **Rating**: Track rating (0-100)
- **Year**: Release year

#### Playback Position
- **Player Position**: Current position in seconds
- **Player Position (Formatted)**: Position as MM:SS
- **Duration**: Track length in seconds
- **Duration (Formatted)**: Duration as MM:SS
- **Progress Percentage**: Playback progress (0-100%)

#### Audio Settings
- **Volume**: Current volume (0-100)
- **Muted**: Boolean mute status
- **Shuffle Enabled**: Shuffle mode on/off
- **Song Repeat**: Repeat mode (off, one, all)

#### Display
- **Status**: Human-readable status (e.g., "▶ Artist - Track Name")

### Actions

#### Playback Control
- **Play**: Start playback
- **Pause**: Pause playback
- **Play/Pause Toggle**: Toggle between play and pause
- **Stop**: Stop playback and reset position
- **Next Track**: Skip to next track
- **Previous Track**: Go to previous track

#### Volume Control
- **Set Volume**: Set specific volume level (0-100)
- **Volume Up**: Increase volume by specified amount
- **Volume Down**: Decrease volume by specified amount
- **Mute**: Mute audio (remembers previous volume)
- **Unmute**: Restore previous volume

#### Position Control
- **Set Playback Position**: Jump to specific second in track
- **Skip Forward**: Jump forward by seconds
- **Skip Backward**: Jump backward by seconds

#### Playback Options
- **Set Shuffle**: Turn shuffle on, off, or toggle
- **Set Repeat**: Set repeat mode (off, one track, all tracks)

#### Content Selection
- **Play Playlist**: Play playlist by name
- **Play Album**: Play album by name (optionally filter by artist)
- **Search and Play**: Search your library and play first result

#### Rating
- **Set Rating**: Rate current track (0-5 stars)

#### Utility
- **Update Now**: Force immediate status update

## Installation

1. **Download** the `AppleMusic.indigoPlugin` package
2. **Double-click** the plugin file to install in Indigo
3. **Restart** the Indigo server if prompted

## Setup

### Creating an Apple Music Device

1. In Indigo, go to **Devices** → **New...**
2. Set Type: **Plugin** → **Apple Music Control**
3. Select Model: **Apple Music Player**
4. Configure settings:
   - **Update Frequency**: How often to poll Apple Music (0.5-10 seconds)
   - **Update Indigo Variables**: Enable to create/update variables
   - **Variable Prefix**: Prefix for variable names (default: "AppleMusic")

### Device Settings

#### Update Frequency
Choose how often the plugin checks Apple Music status:
- **0.5 seconds**: Smoothest updates, higher CPU usage
- **1 second**: Recommended for most uses
- **2-5 seconds**: Good for background monitoring
- **10 seconds**: Minimal CPU usage

#### Variable Updates
If enabled, the plugin will create and update Indigo variables with all Apple Music data:
- Variables are named: `{Prefix}{StateName}` (e.g., `AppleMusicTrackName`)
- Useful for Control Pages and other integrations
- Variables are created automatically if they don't exist

## Usage Examples

### Basic Playback Control
```applescript
-- In Indigo Actions
Execute Action "Apple Music Player - Play"
Execute Action "Apple Music Player - Pause"
Execute Action "Apple Music Player - Next Track"
```

### Volume Control
```applescript
-- Set volume to 50%
Execute Action "Apple Music Player - Set Volume" with value "50"

-- Increase volume by 10
Execute Action "Apple Music Player - Volume Up" with value "10"

-- Mute/Unmute
Execute Action "Apple Music Player - Mute"
Execute Action "Apple Music Player - Unmute"
```

### Play Specific Content
```applescript
-- Play a playlist
Execute Action "Apple Music Player - Play Playlist"
  Playlist Name: "My Favorites"

-- Play an album
Execute Action "Apple Music Player - Play Album"
  Album Name: "Abbey Road"
  Artist Name: "The Beatles"

-- Search and play
Execute Action "Apple Music Player - Search and Play"
  Search Query: "Bohemian Rhapsody"
```

### Rating Songs
```applescript
-- Rate current track 5 stars
Execute Action "Apple Music Player - Set Rating"
  Rating: "100"
```

### Triggers Based on Apple Music State

Create triggers based on device state changes:
- Trigger when playback starts: `isPlaying` becomes `true`
- Trigger when specific artist plays: `artist` contains "The Beatles"
- Trigger when volume changes: `soundVolume` changes
- Trigger when shuffle enabled: `shuffleEnabled` becomes `true`
- Trigger when specific genre plays: `genre` contains "Classical"

### Control Page Examples

Add Apple Music controls to your Control Pages:
- Display current track: Use `status` state
- Display progress: Use `playerPositionFormatted` and `durationFormatted`
- Volume slider: Control via Set Volume action
- Play/Pause button: Use Play/Pause Toggle action
- Show genre/rating: Use `genre` and `rating` states

## Scripting Examples

### Python Script
```python
# Get current track info
applemusic_dev = indigo.devices[12345]  # Your device ID
track = applemusic_dev.states['trackName']
artist = applemusic_dev.states['artist']
genre = applemusic_dev.states['genre']
indigo.server.log(f"Now playing: {artist} - {track} ({genre})")

# Control playback
indigo.device.execute("Apple Music Player", action="play")
indigo.device.execute("Apple Music Player", action="nextTrack")

# Rate current track
indigo.device.execute("Apple Music Player", action="setRating", props={"rating": "100"})
```

### AppleScript
```applescript
tell application "IndigoServer"
    -- Get current track
    set trackName to value of variable "AppleMusicTrackName"
    
    -- Execute actions
    execute action "Play/Pause Toggle" of device "Apple Music Player"
    
    -- Check if playing
    set isPlaying to value of state "isPlaying" of device "Apple Music Player"
end tell
```

## Automation Ideas

### Smart Playlists by Time of Day
```python
# Morning energetic music
if time is 7:00 AM:
    play playlist "Morning Energy"
    set volume to 50

# Evening calm music
if time is 8:00 PM:
    play playlist "Evening Chill"
    set volume to 30
```

### Auto-Rate Frequently Played Songs
- Track play counts via triggers
- Auto-rate songs you skip through
- Build "favorites" based on listening patterns

### Genre-Based Lighting
- Trigger: When `genre` changes
- Action: Set room lighting based on genre
  - Classical → Warm dim lighting
  - Rock → Bright cool lighting
  - Jazz → Warm medium lighting

### Volume Management
- Auto-lower volume during phone calls
- Restore volume when calls end
- Time-based volume limits (quiet hours)

## Troubleshooting

### Plugin Not Updating
- Ensure Music app is running
- Check that Update Frequency is set appropriately
- Try "Update Now" action to force refresh
- Check Indigo log for errors

### Actions Not Working
- Verify Music app is running and responsive
- Some actions require active playback
- Check that Music has proper macOS permissions
- Try controlling Music directly to verify it's working

### Variables Not Created
- Enable "Update Indigo Variables" in device settings
- Check variable prefix doesn't conflict with existing variables
- Variables are created on first update after enabling

### Music Not Responding
The plugin uses AppleScript to communicate with Music:
- Music must be the native macOS Music app
- macOS may prompt for accessibility permissions
- Grant permissions in System Preferences → Security & Privacy

### Playlist/Album Not Found
- Ensure the playlist/album name exactly matches what's in your library
- Names are case-sensitive
- Check for special characters or extra spaces
- Try searching directly in Music app first

## Technical Details

### Requirements
- Indigo 2022.1 or later
- macOS with Music app (formerly iTunes)
- Python 3.7+ (included with Indigo)

### How It Works
- Uses AppleScript to communicate with Music application
- Polls Music at configurable intervals
- No network requests required (all local)
- No Apple Music API credentials needed
- Works with both Apple Music subscription and local library

### Performance
- Minimal CPU usage with 1-2 second update frequency
- No impact on Music app performance
- Updates only when device is active in Indigo

### Differences from Spotify Plugin
- **Ratings**: Apple Music supports 5-star ratings
- **Repeat Modes**: Three modes (off/one/all) vs. Spotify's two
- **Library Focus**: Works with your local library and Apple Music catalog
- **Metadata**: Includes composer, genre, year information
- **No URIs**: Uses playlist/album names instead of Spotify URIs

## Version History

### 1.0.2
- Fixed error when Music app has no current track (stopped state)
- Properly handle empty/stopped state without errors

### 1.0.1
- Fixed AppleScript error with reserved keyword 'error'

### 1.0.0
- Initial release
- Complete playback control
- Comprehensive state monitoring
- Variable integration
- Rating support
- Library search functionality

## Support

For issues or feature requests:
1. Check Indigo plugin log for errors
2. Verify Music app is working
3. Test with different update frequencies
4. Report issues with log excerpts

## Comparison: Apple Music vs Spotify Plugin

| Feature | Apple Music | Spotify |
|---------|-------------|---------|
| Track Info | ✓ | ✓ |
| Playback Control | ✓ | ✓ |
| Volume Control | ✓ | ✓ |
| Position Control | ✓ | ✓ |
| Shuffle/Repeat | ✓ | ✓ |
| Ratings | ✓ (5-star) | ✗ |
| Popularity | ✗ | ✓ |
| Genre/Composer | ✓ | ✗ |
| Play by URI | ✗ | ✓ |
| Library Search | ✓ | ✗ |
| Artwork URL | ✗ | ✓ |

## License

This plugin is provided as-is for use with Indigo home automation.

---

**Note**: This plugin controls the macOS Music application on the Mac running Indigo. It works with your local music library and Apple Music subscription content. For controlling music on other devices, use AirPlay features within the Music app itself.
