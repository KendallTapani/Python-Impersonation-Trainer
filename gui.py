"""
GUI implementation of the Voice Impersonation Trainer using PyQt6.
This module provides a graphical interface for recording, playing, and visualizing voice attempts.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pyaudio

from audio_recorder import AudioRecorder
from audio_processor import AudioProcessor
from visualization import Visualizer
from config import REFERENCE_DIR, USER_RECORDINGS_DIR

class VoiceTrainerGUI(QMainWindow):
    """Main window for the Voice Impersonation Trainer GUI."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Impersonation Trainer")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize audio system
        self.pa = pyaudio.PyAudio()
        
        # Initialize components
        self.audio_processor = AudioProcessor()
        self.audio_recorder = AudioRecorder()
        self.visualizer = Visualizer()
        
        # Setup paths
        self.reference_path = REFERENCE_DIR / "mr_freeman.wav"
        self.attempt_path = None
        
        # Create status check timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.check_playback_status)
        self.playback_timer.setInterval(100)  # Check every 100ms
        
        # Setup UI
        self.setup_ui()
        
        # Enable buttons if reference exists
        if self.reference_path.exists():
            self.listen_btn.setEnabled(True)
            self.record_btn.setEnabled(True)
            self.status_label.setText(f"Reference loaded: {self.reference_path.name}")
        else:
            self.status_label.setText("Error: Reference file not found")
        
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create device selection panel
        device_panel = self.create_device_panel()
        main_layout.addWidget(device_panel)
        
        # Create control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Create visualization panel
        self.viz_panel = self.create_visualization_panel()
        main_layout.addWidget(self.viz_panel)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
    def create_device_panel(self):
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Input devices
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("Input Device:"))
        self.input_combo = QComboBox()
        self.populate_input_devices()
        self.input_combo.currentIndexChanged.connect(self.on_input_device_changed)
        input_layout.addWidget(self.input_combo)
        layout.addLayout(input_layout)
        
        # Output devices
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Output Device:"))
        self.output_combo = QComboBox()
        self.populate_output_devices()
        self.output_combo.currentIndexChanged.connect(self.on_output_device_changed)
        output_layout.addWidget(self.output_combo)
        layout.addLayout(output_layout)
        
        return panel
    
    def populate_input_devices(self):
        """Populate the input device dropdown."""
        self.input_combo.clear()
        current_input_idx = self.audio_recorder.selected_input['index']
        
        for i in range(self.pa.get_device_count()):
            device_info = self.pa.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:  # It's an input device
                name = device_info.get('name')
                # Add arrow indicator for current device
                display_name = f"► {name}" if i == current_input_idx else f"  {name}"
                self.input_combo.addItem(display_name, i)  # Store device index as user data
    
    def populate_output_devices(self):
        """Populate the output device dropdown."""
        self.output_combo.clear()
        # Get current output device index, default to system default if none selected
        current_output_idx = (self.audio_recorder.selected_output['index'] 
                            if self.audio_recorder.selected_output 
                            else self.pa.get_default_output_device_info()['index'])
        
        for i in range(self.pa.get_device_count()):
            device_info = self.pa.get_device_info_by_index(i)
            if device_info.get('maxOutputChannels') > 0:  # It's an output device
                name = device_info.get('name')
                # Add arrow indicator for current device
                display_name = f"► {name}" if i == current_output_idx else f"  {name}"
                self.output_combo.addItem(display_name, i)  # Store device index as user data
    
    def on_input_device_changed(self, index):
        """Handle input device selection."""
        if index >= 0:
            device_index = self.input_combo.currentData()
            self.audio_recorder.set_input_device(device_index)
            self.status_label.setText(f"Input device changed to: {self.input_combo.currentText().strip('► ')}")
            # Update the indicators
            self.populate_input_devices()
            # Restore the selection
            for i in range(self.input_combo.count()):
                if self.input_combo.itemData(i) == device_index:
                    self.input_combo.setCurrentIndex(i)
                    break
    
    def on_output_device_changed(self, index):
        """Handle output device selection."""
        if index >= 0:
            device_index = self.output_combo.currentData()
            self.audio_recorder.set_output_device(device_index)
            self.status_label.setText(f"Output device changed to: {self.output_combo.currentText().strip('► ')}")
            # Update the indicators
            self.populate_output_devices()
            # Restore the selection
            for i in range(self.output_combo.count()):
                if self.output_combo.itemData(i) == device_index:
                    self.output_combo.setCurrentIndex(i)
                    break
        
    def create_control_panel(self):
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Create buttons
        self.listen_btn = QPushButton("Listen")
        self.stop_listen_btn = QPushButton("Stop")
        self.record_btn = QPushButton("Record")
        self.stop_btn = QPushButton("Stop")
        self.playback_btn = QPushButton("Playback")
        self.stop_playback_btn = QPushButton("Stop")
        
        # Add buttons to layout
        layout.addWidget(self.listen_btn)
        layout.addWidget(self.stop_listen_btn)
        layout.addWidget(self.record_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.playback_btn)
        layout.addWidget(self.stop_playback_btn)
        
        # Connect signals
        self.listen_btn.clicked.connect(self.listen_reference)
        self.stop_listen_btn.clicked.connect(self.stop_playback)
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.playback_btn.clicked.connect(self.play_attempt)
        self.stop_playback_btn.clicked.connect(self.stop_playback)
        
        # Initially disable some buttons
        self.listen_btn.setEnabled(False)
        self.stop_listen_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.playback_btn.setEnabled(False)
        self.stop_playback_btn.setEnabled(False)
        
        return panel
    
    def check_playback_status(self):
        """Check if playback has finished and update UI accordingly."""
        if not self.audio_recorder.is_playing:
            self.playback_timer.stop()
            self.listen_btn.setEnabled(True)
            self.stop_listen_btn.setEnabled(False)
            self.playback_btn.setEnabled(True)
            self.stop_playback_btn.setEnabled(False)
            self.status_label.setText("Ready")
    
    def create_visualization_panel(self):
        """Create the panel for displaying visualizations."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        return panel
    
    def listen_reference(self):
        """Play the reference audio file."""
        if self.reference_path:
            try:
                self.audio_recorder.play_audio(self.reference_path)
                self.status_label.setText("Playing reference...")
                self.listen_btn.setEnabled(False)
                self.stop_listen_btn.setEnabled(True)
                self.playback_timer.start()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to play reference: {str(e)}")
    
    def start_recording(self):
        try:
            self.attempt_path = Path("attempt.wav")
            self.audio_recorder.start_recording()
            self.status_label.setText("Recording...")
            self.record_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start recording: {str(e)}")
    
    def stop_recording(self):
        try:
            audio_data, sr = self.audio_recorder.stop_recording()
            self.audio_recorder.save_recording(self.attempt_path)
            self.status_label.setText("Recording stopped")
            self.record_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.playback_btn.setEnabled(True)
            self.update_visualization()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop recording: {str(e)}")
    
    def play_attempt(self):
        """Play the recorded attempt audio file."""
        if self.attempt_path and self.attempt_path.exists():
            try:
                self.audio_recorder.play_audio(self.attempt_path)
                self.status_label.setText("Playing attempt...")
                self.playback_btn.setEnabled(False)
                self.stop_playback_btn.setEnabled(True)
                self.playback_timer.start()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to play attempt: {str(e)}")
    
    def stop_playback(self):
        """Stop any ongoing playback."""
        try:
            self.audio_recorder.stop_playback()
            self.playback_timer.stop()
            self.status_label.setText("Playback stopped")
            self.listen_btn.setEnabled(True)
            self.stop_listen_btn.setEnabled(False)
            self.playback_btn.setEnabled(True)
            self.stop_playback_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop playback: {str(e)}")
    
    def update_visualization(self):
        if not (self.reference_path and self.attempt_path):
            return
        
        try:
            # Clear the figure
            self.figure.clear()
            
            # Load audio data first
            ref_audio, ref_sr = self.audio_processor.load_audio(str(self.reference_path))
            attempt_audio, attempt_sr = self.audio_processor.load_audio(str(self.attempt_path))
            
            # Extract features
            ref_features = self.audio_processor.extract_features(ref_audio, ref_sr)
            attempt_features = self.audio_processor.extract_features(attempt_audio, attempt_sr)
            
            # Create subplots
            ax1 = self.figure.add_subplot(311)
            ax2 = self.figure.add_subplot(312)
            ax3 = self.figure.add_subplot(313)
            
            # Plot waveforms
            ax1.plot(ref_features['waveform'], label='Reference', alpha=0.7)
            ax1.plot(attempt_features['waveform'], label='Attempt', alpha=0.7)
            ax1.set_title('Waveform Comparison')
            ax1.legend()
            ax1.grid(True)
            
            # Plot envelopes
            ax2.plot(ref_features['envelope'], label='Reference', alpha=0.7)
            ax2.plot(attempt_features['envelope'], label='Attempt', alpha=0.7)
            ax2.set_title('Amplitude Envelope')
            ax2.legend()
            ax2.grid(True)
            
            # Plot energy
            ax3.plot(ref_features['energy'], label='Reference', alpha=0.7)
            ax3.plot(attempt_features['energy'], label='Attempt', alpha=0.7)
            ax3.set_title('Energy Contour')
            ax3.legend()
            ax3.grid(True)
            
            # Adjust layout and redraw
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Visualization Error", str(e))

def main():
    """Run the Voice Impersonation Trainer GUI."""
    app = QApplication(sys.argv)
    window = VoiceTrainerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 