# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python application for building honeycomb carbon models from `.dat` or `.pdb` files, with capabilities for intercalation with other structures. The application is built using a GUI with CustomTkinter and follows an MVP (Model-View-Presenter) architecture pattern.

## Development Commands

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building the Application

```bash
# For macOS
./build_app_for_mac.sh

# For Windows
build_app_for_windows.bat
```

### Environment Configuration

- Set `DEV_MODE=true` in `.env` file to enable development mode with error tracebacks
- No `.env` file is currently present in the repository

## Architecture Overview

### MVP Pattern Implementation

The application follows a strict MVP (Model-View-Presenter) architecture:

- **Models**: Located in `src/mvp/*/` - Handle data management and business logic
- **Views**: Located in `src/mvp/*/` - Handle UI components using CustomTkinter
- **Presenters**: Located in `src/mvp/*/` - Handle communication between Model and View
- **Interfaces**: Located in `src/interfaces/mvp/` - Define contracts for MVP components

### Key Architecture Components

#### Core MVP Structure

- `GeneralModel`: Base model class with MVP parameter management
- `GeneralView`: Base view class extending `customtkinter.CTk`
- `GeneralPresenter`: Base presenter class (currently minimal)
- All MVP components follow interface contracts defined in `src/interfaces/`

#### Configuration Management

- `MvpParams`: Main configuration dataclass with comprehensive parameters
- `CoordinateLimits`: Nested configuration for coordinate boundaries
- Configuration files stored in `data/configs/mvp_params/` as JSON
- Constants centralized in `src/services/utils/constants.py`

#### Project Structure

- `src/entities/`: Data structures and models
- `src/services/`: Business logic and utilities
- `src/interfaces/`: All interface definitions
- `src/ui/`: UI components and styling
- `old_gui_logic/`: Legacy GUI implementation (being refactored)

### Data Management

- Project data stored in `data/projects/` and `project_data/`
- Supports multiple file formats: `.xlsx`, `.dat`, `.pdb`
- Structure: `projects/{project_type}/{element}/{data_type}/{structure_name}/`

### Key Dependencies

- **CustomTkinter**: Modern GUI framework
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation
- **MDAnalysis**: Molecular dynamics analysis
- **Matplotlib**: Plotting and visualization
- **OpenPyXL**: Excel file handling

## Common Development Patterns

### Adding New MVP Components

1. Create interfaces in `src/interfaces/mvp/{component_name}/`
2. Implement concrete classes in `src/mvp/{component_name}/`
3. Follow existing naming conventions:
   - for interfaces: `I{Name}Model`, `I{Name}View`, `I{Name}Presenter`;
   - for protocols: `P{Name}Params`, `P{Name}Limits`.

### Configuration Management

- Use `MvpParams` dataclass for configuration
- Load/save configurations via `GeneralModel.get_mvp_params()` and `GeneralModel.set_mvp_params()`
- Configuration files are automatically managed as JSON in `data/configs/mvp_params/`

### File Operations

- Use `FileReader` and `FileWriter` services from `src/services/utils/files_manager/`
- Path constants defined in `Constants.path` class
- Support for multiple formats through `file_format` parameter

### Error Handling

- Logger available via `src.services.utils.logger.Logger`
- Development mode enables detailed error tracebacks
- Use try-catch blocks for configuration parsing with fallback to defaults

## Important Development Notes

## Code Style & Quality Guidelines

When using Claude for code generation or refactoring, follow these quality standards to ensure maintainability, consistency, and correctness.

### General Expectations

Claude should always:

- Ensure all code runs without errors
- Check that all used variables and methods exist and are correctly typed
- Validate that all functions include accurate return type annotations
- Avoid deprecated or outdated practices
- If the class inherits an interface or protocol - check
if the interface or protocol has all the required methods and attributes.

### Code Linting

**Default linter:** Pylance (via Pyright)

Code must pass without lint errors.

**Ensure:**

- No unused imports or variables
- No missing or mismatched types
- No shadowed or ambiguous names
- Explicit visibility of function return types and argument types

**Claude should:**

- Automatically fix or point out linting issues when generating or editing Python code

### Type Annotations

Use PEP 484-style type hints throughout the codebase.

**All functions must include:**

- Argument types
- Return types

**Example:**

```python
def fetch_data(url: str, timeout: int = 5) -> dict:
    """Fetch data from the given URL."""
    ...
```

**Claude should:**

- Never leave initialized variable, function arguments or return types untyped

### Docstrings

Use short, informative docstrings for all functions and classes.

**Follow this format:**

```python
def process_data(data: list[str]) -> dict:
    """Process a list of strings into a dictionary."""
    ...
```

If there are several parameters and the line is too long:

```python
def process_data(
        data: list[str],
        some_param: str,
        another_param: int | None,
) -> dict:
    """Process a list of strings into a dictionary."""
    ...
```

**Claude should:**

- Prefer single-line summaries unless a longer explanation is necessary

### 🔍 Error Checking

Claude must verify that the code works by:

- Ensuring all method calls reference valid objects
- All variables are initialized and typed
- All functions and modules used are imported or defined

**Claude should simulate running the code (or dry-run reasoning) to ensure correctness before returning a response.**

## Current Development Status

The project is in transition from legacy GUI (`old_gui_logic/`) to new MVP architecture. The main entry point still references `src_1.AppGui` which appears to be missing, indicating active refactoring.

### Known Issues (from todo_list.md)

- Replace `np.ndarray` with `NDArray` type hints
- Replace `np.floating` with correct types
- Set interfaces for classes like `ConstantsAtomParams`
