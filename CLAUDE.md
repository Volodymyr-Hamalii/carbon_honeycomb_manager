# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python application for building honeycomb carbon models from `.dat` or `.pdb` files, with capabilities for intercalation with other structures. The application is built using a GUI with CustomTkinter and follows a strict MVP (Model-View-Presenter) architecture pattern with comprehensive interface contracts.

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

## Architecture Overview

### MVP Pattern Implementation

The application follows a strict MVP (Model-View-Presenter) architecture with complete interface segregation:

- **Models**: Located in `src/mvp/*/` - Handle data management and business logic
- **Views**: Located in `src/mvp/*/` - Handle UI components using CustomTkinter with centralized styling
- **Presenters**: Located in `src/mvp/*/` - Handle communication between Model and View, parameter binding
- **Interfaces**: Located in `src/interfaces/mvp/` - Define complete contracts for all MVP components

### Current MVP Modules

1. **`main`** - Main application window with project navigation
2. **`init_data`** - Initial carbon structure visualization and analysis
3. **`intercalation_and_sorption`** - Complex intercalation modeling with channel analysis
4. **`data_converter`** - Data format conversion utilities

### Project Structure

```
src/
├── entities/           # Data models and parameter classes
│   ├── figures/       # Geometric entities (points, lattices)
│   └── params/        # Configuration dataclasses (MvpParams, CoordinateLimits)
├── interfaces/        # Complete interface definitions
│   ├── entities/      # Data model protocols
│   ├── mvp/          # MVP component interfaces
│   ├── projects/     # Project logic interfaces
│   ├── services/     # Service layer interfaces
│   └── ui/           # UI component interfaces
├── mvp/              # MVP implementation modules
├── projects/         # Domain-specific business logic
│   ├── carbon_honeycomb_actions/    # Core carbon structure operations
│   ├── intercalation_and_sorption/  # Intercalation algorithms
│   └── data_manipulation/           # Data processing
├── services/         # Utility services
│   ├── coordinate_operations/       # Geometric calculations
│   ├── structure_visualizer/       # Visualization engine
│   └── utils/                      # File I/O, logging, constants
└── ui/               # UI infrastructure
    ├── components/   # Reusable UI widgets
    ├── styles/       # Centralized styling system
    └── templates/    # UI templates and mixins
```

### Data Structure

```
data/
├── configs/mvp_params/      # JSON configuration files per MVP module
├── constants/               # Physical and mathematical constants
└── projects/               # Project data organized by element and type
    └── {element}/
        ├── init_data/      # Initial structure files (.pdb, .dat)
        ├── result_data/    # Generated analysis results (.xlsx)
        └── al-inter-fixed/ # Intercalated structure data
```

### Key Dependencies

- **CustomTkinter**: Modern GUI framework with dark/light themes
- **NumPy**: Numerical computations and array operations
- **Pandas**: Data manipulation and Excel I/O
- **Matplotlib**: Scientific plotting and visualization
- **OpenPyXL**: Excel file handling
- **MDAnalysis**: Molecular dynamics analysis

## Development Patterns

### MVP Component Creation

1. **Define Interfaces First**: Create complete interface contracts in `src/interfaces/mvp/{component_name}/`
2. **Follow Naming Conventions**:
   - Interfaces: `I{Name}Model`, `I{Name}View`, `I{Name}Presenter`
   - Protocols: `P{Name}Params`, `P{Name}Limits`
3. **Implement Concrete Classes**: Create implementations in `src/mvp/{component_name}/`
4. **Ensure Complete Interface Compliance**: All methods used must be defined in interfaces

### Configuration Management

- **Central Configuration**: Use `MvpParams` dataclass for all MVP parameters
- **Automatic Persistence**: Configurations saved as JSON in `data/configs/mvp_params/`
- **Parameter Binding**: Full bidirectional binding between UI components and MVP state
- **State Restoration**: UI loads from saved MVP parameters on window open

### UI Development

- **Centralized Styling**: All styles defined in `src/ui/styles/` (colors, spacing, themes)
- **Component Reuse**: Use components from `src/ui/components/` with consistent styling
- **Scrolling Support**: Use `ScrollableMixin` for keyboard and touchpad scrolling
- **Template Inheritance**: Extend `GeneralView` and `ScrollableToplevel` for consistent behavior

### File Operations

- **Service Layer**: Use `FileReader` and `FileWriter` from `src/services/utils/files_manager/`
- **Path Management**: Constants defined in `src/services/utils/constants.py`
- **Multi-Format Support**: Handle `.xlsx`, `.dat`, `.pdb` files through unified interface

### Error Handling

- **Structured Logging**: Use `src.services.utils.logger.Logger` throughout
- **Graceful Degradation**: Try-catch blocks with fallback to default values
- **User Feedback**: Consistent error messaging through `GeneralView` base methods

## Code Style & Quality Guidelines

**CRITICAL: Claude must automatically follow these guidelines for ALL code work. No exceptions.**

### Mandatory Pre-Work Checklist

Claude MUST always:

1. **Read CLAUDE.md First**: Automatically apply all project-specific guidelines
2. **Check Interface Compliance**: Verify all methods exist in their respective interfaces
3. **Validate Type Safety**: Ensure all method signatures match exactly
4. **Run Mental Compilation**: Simulate code execution to catch errors before responding.
    If there are some errors - fix them and run all checks one more time.

### Core Quality Standards

#### Type Safety (Non-Negotiable)

- **Complete Type Annotations**: Every function, variable, and parameter must be typed
- **Interface Compliance**: All methods used must exist in their respective interfaces
- **No Type Mismatches**: Method signatures must match interface definitions exactly

```python
# ✅ Correct
def process_data(data: list[str], config: PMvpParams) -> dict[str, Any]:
    """Process data using MVP parameters."""
    ...

# ❌ Incorrect - missing types
def process_data(data, config):
    ...
```

#### Linting (Zero Tolerance)

**Default linter:** Pylance (via Pyright)

**Must have:**

- No unused imports or variables
- No missing or mismatched types
- No shadowed or ambiguous names
- Explicit return types on all functions

#### Interface-First Development

- **Check Interface Definition**: Before using any method, verify it exists in the interface
- **Add Missing Methods**: If a method is needed but not in interface, add it first
- **Complete Implementation**: All interface methods must be implemented

#### Documentation Standards

- **Concise Docstrings**: Single-line summaries preferred
- **Clear Parameter Description**: For complex functions only
- **No Redundant Comments**: Code should be self-documenting

```python
def load_ui_from_params(self) -> None:
    """Load UI components from current MVP parameters."""
    # Implementation here - no additional comments needed
```

### MVP-Specific Rules

#### Parameter Binding

- **Bidirectional Binding**: UI ↔ MVP parameter synchronization required
- **State Persistence**: All UI state must be restorable from MVP parameters
- **Complete Coverage**: Every UI component must map to an MVP parameter

#### UI Consistency

- **Use Centralized Styles**: Import from `src/ui/styles/`
- **Extend Base Classes**: Inherit from `GeneralView`, use `ScrollableMixin`
- **Consistent Error Handling**: Use `GeneralView` messaging methods

### Quality Verification Process

Claude MUST perform this verification before any response:

1. **Interface Check**: ✅ All used methods exist in interfaces
2. **Type Safety**: ✅ All functions have complete type annotations
3. **Import Validation**: ✅ All imports are available and correct
4. **Method Signatures**: ✅ All calls match interface definitions
5. **Mental Execution**: ✅ Code logic flows correctly
6. **MVP Compliance**: ✅ Parameter binding is bidirectional and complete

### Error Recovery Protocol

If Claude detects any quality issues:

1. **Fix Interface First**: Add missing methods to interfaces
2. **Update Implementation**: Ensure all methods are properly implemented
3. **Verify Types**: Check all type annotations are correct
4. **Test Compilation**: Simulate import and execution
5. **Document Changes**: Explain what was fixed and why

### Current Architecture Status

- **MVP Modules**: `main`, `init_data`, `intercalation_and_sorption`, `data_converter`
- **Interface Segregation**: Complete separation of concerns with full contracts
- **Centralized Styling**: All UI styling managed through `src/ui/styles/`
- **Scrolling Infrastructure**: `ScrollableMixin` provides universal scrolling support
- **Parameter Binding**: Full bidirectional UI ↔ MVP state synchronization
