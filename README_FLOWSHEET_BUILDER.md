# SFILES 2.0 Flowsheet Builder

## Overview

This is a GUI implementation for creating flowsheets using the SFILES 2.0 notation. It allows chemical engineers, wastewater engineers, and other users to build process flowsheets step by step without needing to know the SFILES 2.0 notation directly. The builder integrates with the official SFILES 2.0 library to ensure correct notation and compatibility.

The Flowsheet Builder provides an intuitive interface to create and modify chemical process flowsheets through a web-based interface powered by Streamlit.

## Features

### Unit Management
- Add units with customizable types and names
- Delete units that have no connections
- Edit unit types after creation

### Stream Management
- Connect units with streams (from source to target)
- Add tags to streams (for identifying stream components, conditions, etc.)
- Create branches (multiple outputs from one unit)
- Create joins (multiple inputs to one unit)
- Create recycles (cycles in the flowsheet)
- Delete any stream without affecting the rest of the flowsheet

### Flowsheet Representation
- Real-time visualization of the flowsheet using NetworkX and Matplotlib
- Units are displayed as nodes with their names
- Stream tags are displayed as edge labels

### SFILES 2.0 Integration
- Import SFILES 2.0 strings to recreate existing flowsheets
- Export flowsheets as SFILES 2.0 strings
- Full compatibility with the SFILES 2.0 library

## Installation

### Prerequisites

- Python 3.9+
- SFILES2.0 library
- Streamlit
- NetworkX
- Matplotlib

### Setup

1. Clone or download the SFILES2 repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Navigate to the SFILES2 directory
2. Run the Streamlit app:
   ```
   streamlit run flowsheet_builder.py
   ```
3. Open your web browser and go to `http://localhost:8501`

### Creating Your First Flowsheet

1. **Add Units**: In the left sidebar, enter a unit type (e.g., "Reactor" or "HE" for heat exchanger) and a unique name, then click "Add Unit".
2. **Add Streams**: Select a source unit and a target unit, add optional tags (comma-separated), and click "Add Stream".
3. **Create Branches**: Use the Branch feature to create multiple outputs from a single unit.
4. **Create Joins**: Use the Join feature to direct multiple inputs into a single unit.
5. **Create Recycles**: Connect a downstream unit back to an upstream unit to create a recycle stream.
6. **Export Your Flowsheet**: The SFILES 2.0 string representation is automatically generated and displayed in the right panel. You can also export it to the text area for copying.

### Managing Your Flowsheet

- **Delete Units**: Select a unit and click "Delete Unit" (units with connections cannot be deleted until the connections are removed)
- **Delete Streams**: Click the "Delete" button next to any stream in the Connections list
- **Edit Unit Types**: Select a unit, enter a new type, and click "Update Type"

### Importing Existing Flowsheets

To import an existing SFILES 2.0 string:
1. Paste the SFILES 2.0 string into the Import text area
2. Click "Import"
3. The flowsheet will be rendered and populated in the UI for further editing