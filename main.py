"""
Main script for the Voice Impersonation Trainer.
Handles recording, playback, and visualization of voice attempts.
"""
import sys
import time
from pathlib import Path
import logging
import matplotlib.pyplot as plt
from typing import Optional

from audio_recorder import AudioRecorder
from audio_processor import AudioProcessor
from visualization import Visualizer
from config import REFERENCE_DIR, USER_RECORDINGS_DIR

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class VoiceImpersonationTrainer:
    """
    Main class for the Voice Impersonation Trainer application.
    Handles the workflow of recording and analyzing voice attempts.
    """
    
    def __init__(self):
        """Initialize the trainer components."""
        self.recorder = AudioRecorder()
        self.processor = AudioProcessor()
        self.visualizer = Visualizer()
        self.current_attempt_path = None
        
        # Ensure directories exist
        REFERENCE_DIR.mkdir(exist_ok=True)
        USER_RECORDINGS_DIR.mkdir(exist_ok=True)

    def list_references(self) -> None:
        """List all available reference recordings."""
        references = list(REFERENCE_DIR.glob('*.wav'))
        if not references:
            print("\nNo reference recordings found in references directory.")
            return
        
        print("\nAvailable reference recordings:")
        for ref in references:
            print(f"- {ref.stem}")

    def show_menu(self) -> str:
        """Display the menu and get user choice."""
        print("\nAvailable commands:")
        print("  listen    - Play the reference recording")
        print("  record    - Start recording your attempt")
        print("  playback  - Play your last recording")
        print("  visualize - Show waveform comparison")
        print("  quit      - Exit the program")
        
        while True:
            choice = input("\nEnter command: ").strip().lower()
            if choice in ['listen', 'record', 'playback', 'visualize', 'quit']:
                return choice
            print("Invalid command. Please try again.")

    def record_attempt(self, reference_name: str) -> Optional[Path]:
        """
        Record a voice attempt with interactive menu.
        
        Args:
            reference_name: Name of the reference recording to use
            
        Returns:
            Path to the recorded attempt file, or None if cancelled
        """
        reference_path = REFERENCE_DIR / f"{reference_name}.wav"
        if not reference_path.exists():
            logger.error(f"Reference file not found: {reference_path}")
            return None
        
        while True:
            choice = self.show_menu()
            
            if choice == 'listen':
                print("\nPlaying reference recording...")
                self.recorder.play_audio(reference_path)
                
            elif choice == 'record':
                print("\nGet ready! Recording will start in:")
                for i in range(3, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)
                
                print("Recording... (Press Ctrl+C to stop)")
                
                try:
                    self.recorder.start_recording()
                    while True:
                        time.sleep(0.1)  # Keep recording until Ctrl+C
                except KeyboardInterrupt:
                    print("\nStopping recording...")
                
                audio_data, sr = self.recorder.stop_recording()
                
                # Generate unique filename
                self.current_attempt_path = USER_RECORDINGS_DIR / f"attempt_{len(list(USER_RECORDINGS_DIR.glob('*.wav'))) + 1}.wav"
                self.recorder.save_recording(self.current_attempt_path)
                print(f"\nRecording saved to: {self.current_attempt_path}")
                
            elif choice == 'playback':
                if self.current_attempt_path and self.current_attempt_path.exists():
                    print("\nPlaying your attempt...")
                    self.recorder.play_audio(self.current_attempt_path)
                else:
                    print("\nNo recording available to play back.")
                    
            elif choice == 'visualize':
                if self.current_attempt_path and self.current_attempt_path.exists():
                    print("\nGenerating visualization...")
                    try:
                        self.analyze_attempt(reference_path, self.current_attempt_path)
                        plt.show()  # This will display the plot window
                    except Exception as e:
                        print(f"\nError generating visualization: {str(e)}")
                        print("Please make sure you have all required packages installed:")
                        print("pip install librosa numpy matplotlib scipy")
                else:
                    print("\nNo recording available to visualize.")
                    
            elif choice == 'quit':
                return self.current_attempt_path

    def analyze_attempt(self, reference_path: Path, attempt_path: Path) -> None:
        """
        Create visualizations comparing the attempt with the reference.
        
        Args:
            reference_path: Path to the reference audio file
            attempt_path: Path to the attempt audio file
        """
        try:
            # Load and process audio files
            ref_audio, ref_sr = self.processor.load_audio(str(reference_path))
            att_audio, att_sr = self.processor.load_audio(str(attempt_path))
            
            # Extract features for visualization
            ref_features = self.processor.extract_features(ref_audio, ref_sr)
            att_features = self.processor.extract_features(att_audio, att_sr)
            
            # Generate visualizations
            self.visualizer.create_comparison_plots(ref_features, att_features)
            
        except ModuleNotFoundError as e:
            if 'aifc' in str(e):
                print("\nMissing required module. Please install the following packages:")
                print("pip install aifc")
                print("\nIf that doesn't work, try installing the complete audio processing stack:")
                print("pip install librosa numpy matplotlib scipy soundfile")
            else:
                raise

def main():
    """Main function to run the Voice Impersonation Trainer."""
    if len(sys.argv) != 3 or sys.argv[1] != '--reference':
        print("Usage: python main.py --reference <reference_name>")
        print("Example: python main.py --reference mr_freeman")
        return

    reference_name = sys.argv[2]
    trainer = VoiceImpersonationTrainer()

    if reference_name == '--list-references':
        trainer.list_references()
        return

    # Start the training session
    attempt_path = trainer.record_attempt(reference_name)
    if attempt_path:
        print("\nTraining session completed!")

if __name__ == '__main__':
    main()
