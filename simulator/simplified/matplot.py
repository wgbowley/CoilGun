"""
Filename: matplot.py
Author: William Bowley
Version: 0.1

Description:
    Graphing script for the analytical lumped
    parameter coil-gun simulation using picounits
"""

from typing import Sequence
import matplotlib.pyplot as plt


def plot(
    time_series: Sequence[float],
    current_series: Sequence[float],
    force_series: Sequence[float],
    velocity_series: Sequence[float]
) -> None:
    """ Plots the coil-gun simulation results """
    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    # Set window title
    fig.canvas.manager.set_window_title("Coilgun Simulation Results")

    # Current vs Time
    axes[0].plot(time_series, current_series, color="#00BFFF", linewidth=2)
    axes[0].set_ylabel("Current (A)", color="white")
    axes[0].set_title("Line Current vs Time", color="white")
    axes[0].tick_params(colors="white")

    # Force vs Time
    axes[1].plot(time_series, force_series, color="#FF4500", linewidth=2)
    axes[1].set_ylabel("Force (N)", color="white")
    axes[1].set_title("Projectile Force vs Time", color="white")
    axes[1].tick_params(colors="white")

    # Velocity vs Time
    axes[2].plot(time_series, velocity_series, color="#7CFC00", linewidth=2)
    axes[2].set_xlabel("Time (s)", color="white")
    axes[2].set_ylabel("Velocity (m/s)", color="white")
    axes[2].set_title("Projectile Velocity vs Time", color="white")
    axes[2].tick_params(colors="white")

    fig.tight_layout(pad=2.0)
    plt.show()
