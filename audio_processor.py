"""
Audio processing functionality for the Voice Impersonation Trainer.
This module handles audio feature extraction and analysis.
"""
import wave
import numpy as np
from pathlib import Path
import librosa
import soundfile as sf
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import logging

from config import (
    SAMPLE_RATE, FRAME_LENGTH, HOP_LENGTH,
    N_MELS, F_MIN, F_MAX, PITCH_MIN, PITCH_MAX, CHANNELS
)

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@dataclass
class AudioFeatures:
    """
    Container for extracted audio features used in visualization.
    
    Attributes:
        pitch_contour: Array of pitch values over time (for melody visualization)
        mfcc: Mel-frequency cepstral coefficients (for timbre visualization)
        spectral_centroid: Measure of the "brightness" of the sound
        tempo: Estimated tempo in beats per minute
        energy_envelope: Array of energy values over time (for volume visualization)
    """
    pitch_contour: np.ndarray
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    tempo: float
    energy_envelope: np.ndarray

class AudioProcessor:
    """
    Handles the processing and analysis of audio signals.
    Extracts features useful for visualizing voice characteristics.
    """
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load an audio file and return the audio data and sample rate.
        
        Args:
            file_path: Path to the audio file to load
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sr = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if necessary
            if sr != SAMPLE_RATE:
                # For now, we'll just warn about sample rate mismatch
                logger.warning(f"Sample rate mismatch: file is {sr}Hz, expected {SAMPLE_RATE}Hz")
            
            return audio_data, sr
            
        except Exception as e:
            logger.error(f"Error loading audio file: {str(e)}")
            raise

    def extract_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """
        Extract audio features for visualization.
        
        Args:
            audio_data: Audio time series
            sr: Sampling rate
            
        Returns:
            Dictionary of features including:
            - waveform: The raw audio waveform
            - envelope: The amplitude envelope
            - pitch: Pitch contour
        """
        features = {
            'waveform': audio_data,
            'envelope': self._get_envelope(audio_data),
            'energy': self._get_energy(audio_data)
        }
        return features

    def _get_envelope(self, audio_data: np.ndarray, frame_size: int = 2048) -> np.ndarray:
        """Calculate the amplitude envelope of the audio."""
        return np.array([
            max(abs(audio_data[i:i + frame_size]))
            for i in range(0, len(audio_data), frame_size)
        ])

    def _get_energy(self, audio_data: np.ndarray, frame_size: int = 2048) -> np.ndarray:
        """Calculate the energy contour of the audio."""
        return np.array([
            np.sum(audio_data[i:i + frame_size]**2)
            for i in range(0, len(audio_data), frame_size)
        ])

    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio data to have a maximum amplitude of 1.
        Useful for consistent visualization.
        
        Args:
            audio_data: numpy array of audio samples
            
        Returns:
            Normalized audio data
        """
        return librosa.util.normalize(audio_data)

    @staticmethod
    def trim_silence(audio_data: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
        """
        Remove silence from the beginning and end of the audio.
        Helps create cleaner visualizations.
        
        Args:
            audio_data: numpy array of audio samples
            sr: sample rate of the audio
            
        Returns:
            Audio data with silence removed
        """
        trimmed_audio, _ = librosa.effects.trim(audio_data, top_db=20)
        return trimmed_audio

    @staticmethod
    def match_length(source: np.ndarray, target: np.ndarray) -> np.ndarray:
        """
        Adjust the length of source audio to match the target.
        Either truncates or pads the source audio as needed.
        
        Args:
            source: numpy array of source audio
            target: numpy array of target audio
            
        Returns:
            Length-adjusted source audio
        """
        if len(source) > len(target):
            return source[:len(target)]  # Truncate
        elif len(source) < len(target):
            return np.pad(source, (0, len(target) - len(source)), mode='constant')  # Pad
        return source  # Already matching length
