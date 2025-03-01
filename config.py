"""
Configuration settings for the Voice Impersonation Trainer.
This module contains all the configurable parameters used throughout the application.
"""
import os
from pathlib import Path

# Audio Recording Settings
# These settings determine the quality and format of the audio recordings
SAMPLE_RATE = 44100  # Number of samples per second (Hz) - CD quality audio
CHANNELS = 1         # Mono audio recording
DURATION = 5         # Default recording duration in seconds
CHUNK_SIZE = 1024    # Size of audio chunks for processing - affects latency/performance

# Audio Processing Settings
# Parameters used for audio analysis and visualization
FRAME_LENGTH = 2048  # Length of each frame for FFT analysis
HOP_LENGTH = 512     # Number of samples between frames - affects time resolution
N_MELS = 128        # Number of Mel frequency bands for spectral analysis
F_MIN = 20          # Minimum frequency for analysis (Hz) - human hearing lower limit
F_MAX = 8000        # Maximum frequency for analysis (Hz) - covers most voice frequencies

# Paths
# Directory structure for storing files
BASE_DIR = Path(__file__).parent                  # Root directory of the application
REFERENCE_DIR = BASE_DIR / "references"           # Store reference voice recordings
TEMP_DIR = BASE_DIR / "temp"                      # Temporary files (visualizations, etc.)
USER_RECORDINGS_DIR = BASE_DIR / "user_recordings"  # Store user's recorded attempts

# Create required directories if they don't exist
for directory in [REFERENCE_DIR, TEMP_DIR, USER_RECORDINGS_DIR]:
    directory.mkdir(exist_ok=True)

# Feature Extraction Settings
# Parameters for voice feature analysis
PITCH_MIN = 50    # Minimum pitch to detect (Hz) - covers low male voices
PITCH_MAX = 1000  # Maximum pitch to detect (Hz) - covers high female voices

# Visualization Settings
# Parameters for generating visual feedback
PLOT_DPI = 100          # Resolution of saved plots
FIGURE_SIZE = (10, 6)   # Default size for visualization figures (width, height)
