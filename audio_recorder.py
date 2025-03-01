"""
Audio recording functionality for the Voice Impersonation Trainer.
This module handles all audio recording operations, including playback of reference audio,
and recording of user attempts.
"""
import wave
import pyaudio
import numpy as np
import logging
import time
import threading
from pathlib import Path
from typing import Optional, Tuple, Dict

from config import SAMPLE_RATE, CHANNELS, CHUNK_SIZE, TEMP_DIR, REFERENCE_DIR

# Set up logging - only show important messages
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AudioRecorder:
    """
    Handles audio playback and recording functionality using PyAudio.
    Provides methods for playing reference audio and recording user attempts.
    """
    def __init__(self):
        """Initialize the audio system."""
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.playback_stream = None
        self.frames = []
        self.is_recording = False
        self.is_playing = False
        self.playback_thread = None
        
        # List and select input device
        self.input_devices = self._get_input_devices()
        self.selected_input = self._select_best_device()
        self.selected_output = None  # Will be set when playing
        
        logger.info(f"Using input device: {self.selected_input['name']}")

    def _get_input_devices(self) -> Dict[int, dict]:
        """Get all available input devices."""
        devices = {}
        for i in range(self.audio.get_device_count()):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    devices[i] = device_info
            except Exception as e:
                logger.warning(f"Error getting device {i} info: {str(e)}")
        return devices

    def _select_best_device(self) -> dict:
        """Select the best available input device."""
        # First try to find a device with "mic" in the name
        for idx, device in self.input_devices.items():
            if 'mic' in device['name'].lower():
                return {'index': idx, 'name': device['name']}
        
        # Otherwise, use the default input device
        try:
            default_device = self.audio.get_default_input_device_info()
            return {'index': default_device['index'], 'name': default_device['name']}
        except:
            # If all else fails, use the first available input device
            first_device = next(iter(self.input_devices.items()))
            return {'index': first_device[0], 'name': first_device[1]['name']}

    def set_input_device(self, device_index: int) -> None:
        """Set the input device for recording."""
        try:
            device_info = self.audio.get_device_info_by_index(device_index)
            if device_info.get('maxInputChannels') > 0:
                self.selected_input = {'index': device_index, 'name': device_info['name']}
                logger.info(f"Input device set to: {self.selected_input['name']}")
            else:
                raise ValueError("Selected device has no input channels")
        except Exception as e:
            logger.error(f"Error setting input device: {str(e)}")
            raise

    def set_output_device(self, device_index: int) -> None:
        """Set the output device for playback."""
        try:
            device_info = self.audio.get_device_info_by_index(device_index)
            if device_info.get('maxOutputChannels') > 0:
                self.selected_output = {'index': device_index, 'name': device_info['name']}
                logger.info(f"Output device set to: {self.selected_output['name']}")
            else:
                raise ValueError("Selected device has no output channels")
        except Exception as e:
            logger.error(f"Error setting output device: {str(e)}")
            raise

    def play_audio(self, audio_path: Path) -> None:
        """Play any audio file in a separate thread."""
        try:
            # Stop any ongoing playback
            self.stop_playback()
            
            # Start playback in a new thread
            self.playback_thread = threading.Thread(target=self._playback_worker, args=(audio_path,))
            self.playback_thread.daemon = True  # Thread will be terminated when main program exits
            self.is_playing = True
            self.playback_thread.start()
                
        except Exception as e:
            logger.error(f"Error during playback: {str(e)}")
            raise

    def _playback_worker(self, audio_path: Path) -> None:
        """Worker function to handle audio playback in a separate thread."""
        try:
            with wave.open(str(audio_path), 'rb') as wf:
                # Get default output device if none selected
                if not self.selected_output:
                    default_output = self.audio.get_default_output_device_info()
                    self.selected_output = {'index': default_output['index'], 'name': default_output['name']}
                
                self.playback_stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=self.selected_output['index']
                )
                
                data = wf.readframes(CHUNK_SIZE)
                while data and self.is_playing:
                    self.playback_stream.write(data)
                    data = wf.readframes(CHUNK_SIZE)
                
                self.stop_playback()
                
        except Exception as e:
            logger.error(f"Error in playback worker: {str(e)}")
            self.is_playing = False

    def stop_playback(self) -> None:
        """Stop any ongoing playback."""
        self.is_playing = False
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)  # Wait for thread to finish
        
        if self.playback_stream:
            try:
                self.playback_stream.stop_stream()
                self.playback_stream.close()
                self.playback_stream = None
            except Exception as e:
                logger.error(f"Error stopping playback: {str(e)}")
                raise

    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        self.frames = []
        self.is_recording = True
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=self.selected_input['index'],
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=self._callback
            )
            
            self.stream.start_stream()
            
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            raise

    def stop_recording(self) -> Tuple[np.ndarray, int]:
        """Stop recording and return the recorded audio data."""
        if self.stream:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
            if len(self.frames) == 0:
                logger.warning("No audio frames were captured!")
                return np.array([]), SAMPLE_RATE
            
            try:
                audio_data = np.concatenate([np.frombuffer(frame, dtype=np.float32) 
                                           for frame in self.frames])
                
                if len(audio_data) > 0:
                    max_val = np.max(np.abs(audio_data))
                    if max_val < 0.01:
                        logger.warning("Very low audio levels detected!")
                
                return audio_data, SAMPLE_RATE
            except Exception as e:
                logger.error(f"Error processing audio data: {str(e)}")
                raise
        
        return np.array([]), SAMPLE_RATE

    def save_recording(self, filepath: Path) -> None:
        """Save the recorded audio to a WAV file."""
        if not self.frames:
            logger.error("No audio data to save")
            raise ValueError("No audio data to save")

        try:
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paFloat32))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(b''.join(self.frames))
            
        except Exception as e:
            logger.error(f"Error saving recording: {str(e)}")
            raise

    def _callback(self, in_data, frame_count, time_info, status) -> Tuple[None, int]:
        """Process each chunk of recorded audio."""
        if status:
            logger.warning(f"Stream callback status: {status}")
            
        if self.is_recording:
            self.frames.append(in_data)
        return (None, pyaudio.paContinue)

    def __del__(self):
        """Clean up audio resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
