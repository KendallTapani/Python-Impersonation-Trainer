"""
Visualization functionality for the Voice Impersonation Trainer.
This module handles creating visual comparisons between reference and attempt recordings.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
import logging

from config import PLOT_DPI, FIGURE_SIZE

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Visualizer:
    """
    Creates visual comparisons between reference and attempt recordings.
    """
    
    def create_comparison_plots(self, ref_features: Dict[str, np.ndarray], att_features: Dict[str, np.ndarray]) -> None:
        """
        Create comparison plots between reference and attempt recordings.
        
        Args:
            ref_features: Dictionary of features from reference recording
            att_features: Dictionary of features from attempt recording
        """
        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=FIGURE_SIZE, dpi=PLOT_DPI)
        fig.suptitle('Voice Comparison Visualization', fontsize=14)
        
        # Plot waveforms
        self._plot_waveform_comparison(ax1, ref_features['waveform'], att_features['waveform'])
        
        # Plot amplitude envelopes
        self._plot_envelope_comparison(ax2, ref_features['envelope'], att_features['envelope'])
        
        # Plot energy contours
        self._plot_energy_comparison(ax3, ref_features['energy'], att_features['energy'])
        
        # Adjust layout
        plt.tight_layout()
        
    def _plot_waveform_comparison(self, ax, ref_wave: np.ndarray, att_wave: np.ndarray) -> None:
        """Plot waveform comparison."""
        # Normalize time axis to seconds
        ref_time = np.arange(len(ref_wave)) / len(ref_wave)
        att_time = np.arange(len(att_wave)) / len(att_wave)
        
        ax.plot(ref_time, ref_wave, 'b-', alpha=0.5, label='Reference')
        ax.plot(att_time, att_wave, 'r-', alpha=0.5, label='Your Attempt')
        
        ax.set_title('Waveform Comparison')
        ax.set_xlabel('Time (normalized)')
        ax.set_ylabel('Amplitude')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_envelope_comparison(self, ax, ref_env: np.ndarray, att_env: np.ndarray) -> None:
        """Plot amplitude envelope comparison."""
        # Normalize time axis
        ref_time = np.arange(len(ref_env)) / len(ref_env)
        att_time = np.arange(len(att_env)) / len(att_env)
        
        ax.plot(ref_time, ref_env, 'b-', label='Reference')
        ax.plot(att_time, att_env, 'r-', label='Your Attempt')
        
        ax.set_title('Amplitude Envelope')
        ax.set_xlabel('Time (normalized)')
        ax.set_ylabel('Envelope')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_energy_comparison(self, ax, ref_energy: np.ndarray, att_energy: np.ndarray) -> None:
        """Plot energy contour comparison."""
        # Normalize time axis and energy values
        ref_time = np.arange(len(ref_energy)) / len(ref_energy)
        att_time = np.arange(len(att_energy)) / len(att_energy)
        
        # Normalize energy values
        ref_energy = ref_energy / np.max(ref_energy)
        att_energy = att_energy / np.max(att_energy)
        
        ax.plot(ref_time, ref_energy, 'b-', label='Reference')
        ax.plot(att_time, att_energy, 'r-', label='Your Attempt')
        
        ax.set_title('Energy Contour')
        ax.set_xlabel('Time (normalized)')
        ax.set_ylabel('Normalized Energy')
        ax.legend()
        ax.grid(True, alpha=0.3)
