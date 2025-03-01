# Voice Impersonation Trainer

A Python application that helps users practice voice impersonations by providing real-time audio analysis and visualization.

I'm doing an actual react app, this was just to test stuff out.

## Features

- Record and playback voice attempts
- Compare your recording with reference audio
- Real-time visualization of audio waveforms
- Amplitude envelope comparison
- Energy contour analysis
- Device selection for input/output
- Modern PyQt6-based GUI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Python-Impersonation-Trainer-1.git
cd Python-Impersonation-Trainer-1
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the GUI version:
```bash
python gui.py
```

2. Run the command-line version:
```bash
python main.py --reference mr_freeman
```

## Controls

- **Listen**: Play the reference recording
- **Record**: Start recording your attempt
- **Stop**: Stop the current recording/playback
- **Playback**: Play your last recording
- **Visualize**: Show comparison between reference and attempt

## Project Structure

```
├── audio_processor.py   # Audio analysis and feature extraction
├── audio_recorder.py    # Recording and playback functionality
├── config.py           # Configuration settings
├── gui.py             # PyQt6 GUI implementation
├── main.py            # Command-line interface
├── utils.py           # Utility functions
├── visualization.py   # Visualization components
└── references/        # Reference audio files
```

## Requirements

- Python 3.8+
- PyQt6
- NumPy
- SoundFile
- Matplotlib
- PyAudio
- Scipy

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
