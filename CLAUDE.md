# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anti-Idle Mouse Mover application - a desktop utility that prevents computers from going idle by making tiny, imperceptible mouse movements at user-defined intervals. The project consists of a Python GUI application built with Pygame and a promotional website.

## Core Architecture

### Main Application (`anti_idle_mouse_mover.py`)
- **GUI Framework**: Pygame-based desktop application with modern UI design
- **Threading**: Uses Python threading for non-blocking mouse movement in background
- **Configuration**: Centralized CONFIG dictionary for colors, fonts, window settings, and donation URL
- **Resource Handling**: Includes `resource_path()` function for PyInstaller compatibility
- **Core Classes**:
  - `App` class: Main application controller handling UI, events, and mouse movement logic

### Key Components
- **Mouse Movement Logic**: Moves mouse 1 pixel and immediately back to prevent visible movement
- **Input Validation**: Interval input restricted to 1-3600 seconds with real-time validation
- **Status Management**: Real-time status updates with countdown display during operation
- **UI State Management**: Proper button/input disabling during active operation

### Website (`index.html`)
- Bilingual (Traditional Chinese/English) promotional website
- Tailwind CSS for responsive design
- Features download links and application screenshots

## Development Commands

### Running the Application
```bash
python anti_idle_mouse_mover.py
```

### Building Executable
Uses PyInstaller with spec files for Windows executable creation:
```bash
pyinstaller anti_idle_mover_v1.0.spec
```

The build creates:
- `build/` directory with build artifacts
- `dist/anti_idle_mover_v1.0.exe` - Final executable

### Dependencies
Set up virtual environment and install required packages:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Key dependencies include:
- `pygame` - GUI framework and mouse control
- `pywin32` - Windows-specific functionality
- Various packaging/build tools for PyInstaller

## File Structure Notes

- `.spec` files: PyInstaller configuration files for different build variants
- `.ico`/`.png` files: Application icons and assets
- `build/` and `dist/`: PyInstaller output directories
- Website assets are self-contained in `index.html`

## Development Notes

- The application is designed as a portable, no-install utility
- Mouse movement is intentionally minimal (1px) to avoid user disruption
- Threading ensures UI remains responsive during mouse movement operations
- Resource paths use PyInstaller-compatible path resolution
- UI follows modern design principles with hover states and visual feedback