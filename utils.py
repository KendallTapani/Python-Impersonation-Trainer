"""
Utility functions for the Voice Impersonation Trainer.
This module provides helper functions for file operations, error handling,
and other common tasks used throughout the application.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List
import wave
import contextlib
import numpy as np

# Configure logging with timestamp and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories(directories: List[Path]) -> None:
    """
    Create necessary directories if they don't exist.
    Ensures all required directories are available for file operations.
    
    Args:
        directories: List of directory paths to create
        
    Raises:
        Exception: If directory creation fails
    """
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created/verified: {directory}")
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {str(e)}")
            raise

def get_audio_duration(file_path: Path) -> float:
    """
    Get the duration of an audio file in seconds.
    Uses wave module to read audio file properties.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Duration of the audio in seconds
        
    Raises:
        Exception: If file reading fails
    """
    try:
        with contextlib.closing(wave.open(str(file_path), 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        logger.error(f"Error getting audio duration for {file_path}: {str(e)}")
        raise

def clean_temp_files(temp_dir: Path) -> None:
    """
    Remove temporary files and directories.
    Cleans up old temporary files and recreates the directory.
    
    Args:
        temp_dir: Path to temporary directory
        
    Raises:
        Exception: If cleanup fails
    """
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            logger.info(f"Cleaned temporary directory: {temp_dir}")
    except Exception as e:
        logger.error(f"Error cleaning temporary directory {temp_dir}: {str(e)}")
        raise

def save_numpy_audio(audio_data: np.ndarray, file_path: Path, sample_rate: int) -> None:
    """
    Save numpy array audio data to a WAV file.
    Converts numpy array to audio file format.
    
    Args:
        audio_data: Numpy array containing audio samples
        file_path: Path where to save the audio file
        sample_rate: Sample rate of the audio
        
    Raises:
        Exception: If saving fails
    """
    try:
        import soundfile as sf
        sf.write(str(file_path), audio_data, sample_rate)
        logger.info(f"Audio saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving audio to {file_path}: {str(e)}")
        raise

def load_reference_list(reference_dir: Path) -> List[str]:
    """
    Load list of available reference recordings.
    Scans the reference directory for WAV files.
    
    Args:
        reference_dir: Path to directory containing reference recordings
        
    Returns:
        List of reference recording names (without extension)
        
    Raises:
        Exception: If directory reading fails
    """
    try:
        reference_files = list(reference_dir.glob("*.wav"))
        references = [f.stem for f in reference_files]
        logger.info(f"Found {len(references)} reference recordings")
        return references
    except Exception as e:
        logger.error(f"Error loading reference list from {reference_dir}: {str(e)}")
        raise

def validate_audio_file(file_path: Path) -> bool:
    """
    Validate if a file is a proper audio file.
    Checks basic WAV file properties to ensure file is valid.
    
    Args:
        file_path: Path to audio file to validate
        
    Returns:
        True if file is valid, False otherwise
    """
    try:
        with wave.open(str(file_path), 'r') as wav_file:
            # Check basic WAV file properties
            if wav_file.getnchannels() == 0:
                return False
            if wav_file.getsampwidth() == 0:
                return False
            if wav_file.getframerate() == 0:
                return False
            return True
    except Exception as e:
        logger.error(f"Error validating audio file {file_path}: {str(e)}")
        return False

def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format.
    Converts float seconds to human-readable time string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (MM:SS)
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def ensure_valid_filename(filename: str) -> str:
    """
    Ensure filename is valid and safe.
    Removes invalid characters and ensures non-empty name.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    filename = ''.join(c for c in filename if c in valid_chars)
    # Ensure it's not empty
    if not filename:
        filename = "recording"
    return filename

def get_unique_filename(base_path: Path, base_name: str, extension: str = ".wav") -> Path:
    """
    Generate a unique filename by appending a number if necessary.
    Prevents overwriting existing files by adding incrementing numbers.
    
    Args:
        base_path: Directory path for the file
        base_name: Desired base filename
        extension: File extension (default: .wav)
        
    Returns:
        Path object with unique filename
    """
    counter = 1
    file_path = base_path / f"{base_name}{extension}"
    while file_path.exists():
        file_path = base_path / f"{base_name}_{counter}{extension}"
        counter += 1
    return file_path
