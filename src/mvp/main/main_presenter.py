from typing import Any
import pandas as pd

from src.interfaces import IMainPresenter, IMainModel, IMainView
from src.services import Logger


logger = Logger("MainPresenter")


class MainPresenter(IMainPresenter):
    """Main application presenter."""

    def __init__(self, model: IMainModel, view: IMainView) -> None:
        self.model: IMainModel = model
        self.view: IMainView = view
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the presenter."""
        self.view.set_selection_callbacks({
            "project": self.set_project_selection,
            "subproject": self.set_subproject_selection,
            "structure": self.set_structure_selection,
        })

        self.view.set_action_callbacks({
            "data_converter": self.open_data_converter,
            "intercalation_and_sorption": self.open_intercalation_and_sorption,
            "show_init_data": self.open_show_init_data,
        })

    def initialize_application(self) -> None:
        """Initialize the application."""
        try:
            self.view.show_status_message("Loading application...")

            # Load projects
            projects: list[str] = self.model.get_projects()
            self.view.set_projects(projects)

            # Restore previous state if available
            self.restore_application_state()

            self.view.show_status_message("Application ready")

        except Exception as e:
            error_message: str = f"Failed to initialize application: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def set_project_selection(self, project_dir: str) -> None:
        """Set project selection and update subprojects."""
        try:
            current_selection = self.model.get_current_selection()
            current_selection["project_dir"] = project_dir
            self.model.set_current_selection(current_selection)

            # Update subprojects
            subprojects = self.model.get_subprojects(project_dir)
            self.view.set_subprojects(subprojects)

            # Clear structure selection
            self.view.set_structures([])

            # Select first subproject if available
            if subprojects:
                self.set_subproject_selection(subprojects[0])

        except Exception as e:
            error_message = f"Failed to set project selection: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def set_subproject_selection(self, subproject_dir: str) -> None:
        """Set subproject selection and update structures."""
        try:
            current_selection = self.model.get_current_selection()
            current_selection["subproject_dir"] = subproject_dir
            self.model.set_current_selection(current_selection)

            # Update structures
            project_dir = current_selection.get("project_dir", "")
            if project_dir:
                structures = self.model.get_structures(project_dir, subproject_dir)
                self.view.set_structures(structures)

                # Select first structure if available
                if structures:
                    self.set_structure_selection(structures[0])

        except Exception as e:
            error_message = f"Failed to set subproject selection: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def set_structure_selection(self, structure_dir: str) -> None:
        """Set structure selection."""
        try:
            current_selection = self.model.get_current_selection()
            current_selection["structure_dir"] = structure_dir
            self.model.set_current_selection(current_selection)

            # Enable actions if we have a complete selection
            if all(current_selection.get(key) for key in ["project_dir", "subproject_dir", "structure_dir"]):
                self.view.enable_actions(True)
            else:
                self.view.enable_actions(False)

        except Exception as e:
            error_message = f"Failed to set structure selection: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def get_available_projects(self) -> list[str]:
        """Get available projects."""
        return self.model.get_projects()

    def get_available_subprojects(self) -> list[str]:
        """Get available subprojects for current project."""
        current_selection = self.model.get_current_selection()
        project_dir = current_selection.get("project_dir", "")
        if project_dir:
            return self.model.get_subprojects(project_dir)
        return []

    def get_available_structures(self) -> list[str]:
        """Get available structures for current project/subproject."""
        current_selection = self.model.get_current_selection()
        project_dir = current_selection.get("project_dir", "")
        subproject_dir = current_selection.get("subproject_dir", "")
        if project_dir and subproject_dir:
            return self.model.get_structures(project_dir, subproject_dir)
        return []

    def open_data_converter(self) -> None:
        """Open data converter window."""
        try:
            self.view.show_status_message("Opening data converter...")
            
            # Get current selection for window context
            current_selection = self.model.get_current_selection()
            project_dir = current_selection.get("project_dir", "")
            subproject_dir = current_selection.get("subproject_dir", "")
            structure_dir = current_selection.get("structure_dir", "")
            
            if not all([project_dir, subproject_dir, structure_dir]):
                self.view.show_error_message("Please select project, subproject, and structure first")
                return
            
            # Import and create MVP triad
            from src.mvp.data_converter import DataConverterModel, DataConverterPresenter, DataConverterView
            
            # Create MVP instances
            model = DataConverterModel()
            view = DataConverterView()
            presenter = DataConverterPresenter(model, view)
            
            # Set up the view with current context
            view.set_context(project_dir, subproject_dir, structure_dir)
            view.set_ui()
            
            # Load available files after context is set
            presenter.load_available_files(project_dir, subproject_dir, structure_dir)
            
            # Show the window
            view.mainloop()
            
            logger.info("Data converter window opened")
        except Exception as e:
            error_message = f"Failed to open data converter: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def open_intercalation_and_sorption(self) -> None:
        """Open intercalation and sorption window."""
        try:
            self.view.show_status_message("Opening intercalation and sorption...")
            
            # Get current selection for window context
            current_selection = self.model.get_current_selection()
            project_dir = current_selection.get("project_dir", "")
            subproject_dir = current_selection.get("subproject_dir", "")
            structure_dir = current_selection.get("structure_dir", "")
            
            if not all([project_dir, subproject_dir, structure_dir]):
                self.view.show_error_message("Please select project, subproject, and structure first")
                return
            
            # Import and create MVP triad
            from src.mvp.intercalation_and_sorption import IntercalationAndSorptionModel, IntercalationAndSorptionPresenter, IntercalationAndSorptionView
            
            # Create MVP instances
            model = IntercalationAndSorptionModel()
            view = IntercalationAndSorptionView()
            presenter = IntercalationAndSorptionPresenter(model, view)
            
            # Set up the view with current context
            view.set_context(project_dir, subproject_dir, structure_dir)
            view.set_ui()
            
            # Load available files after context is set (if presenter has this method)
            if hasattr(presenter, 'load_available_files'):
                presenter.load_available_files(project_dir, subproject_dir, structure_dir)
            
            # Show the window
            view.mainloop()
            
            logger.info("Intercalation and sorption window opened")
        except Exception as e:
            error_message = f"Failed to open intercalation and sorption: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def open_show_init_data(self) -> None:
        """Open show init data window."""
        try:
            self.view.show_status_message("Opening show init data...")
            
            # Get current selection for window context
            current_selection = self.model.get_current_selection()
            project_dir = current_selection.get("project_dir", "")
            subproject_dir = current_selection.get("subproject_dir", "")
            structure_dir = current_selection.get("structure_dir", "")
            
            if not all([project_dir, subproject_dir, structure_dir]):
                self.view.show_error_message("Please select project, subproject, and structure first")
                return
            
            # Import and create MVP triad
            from src.mvp.init_data import InitDataModel, InitDataPresenter, InitDataView
            
            # Create MVP instances
            model = InitDataModel()
            view = InitDataView()
            presenter = InitDataPresenter(model, view)
            
            # Set up the view with current context
            view.set_context(project_dir, subproject_dir, structure_dir)
            view.set_ui()
            
            # Load available files after context is set (if presenter has this method)
            if hasattr(presenter, 'load_available_files'):
                presenter.load_available_files(project_dir, subproject_dir, structure_dir)
            
            # Show the window
            view.mainloop()
            
            logger.info("Show init data window opened")
        except Exception as e:
            error_message = f"Failed to open show init data: {str(e)}"
            self.view.show_error_message(error_message)
            logger.error(error_message)

    def save_application_state(self) -> None:
        """Save current application state."""
        try:
            current_selection = self.model.get_current_selection()
            session_state = {
                "selection": current_selection,
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            self.model.save_session_state(session_state)
            logger.info("Application state saved")
        except Exception as e:
            logger.warning(f"Failed to save application state: {e}")

    def restore_application_state(self) -> None:
        """Restore saved application state."""
        try:
            # First try to restore from current_selection (persistent state)
            current_selection = self.model.get_current_selection()
            if current_selection:
                project_dir = current_selection.get("project_dir", "")
                subproject_dir = current_selection.get("subproject_dir", "")
                structure_dir = current_selection.get("structure_dir", "")
                
                # Restore project selection and update UI
                if project_dir:
                    # Set project selection in UI
                    self.view.set_selected_project(project_dir)
                    # Load subprojects for this project
                    subprojects = self.model.get_subprojects(project_dir)
                    self.view.set_subprojects(subprojects)
                    
                    # Restore subproject selection
                    if subproject_dir and subproject_dir in subprojects:
                        self.view.set_selected_subproject(subproject_dir)
                        # Load structures for this subproject
                        structures = self.model.get_structures(project_dir, subproject_dir)
                        self.view.set_structures(structures)
                        
                        # Restore structure selection and enable buttons
                        if structure_dir and structure_dir in structures:
                            self.view.set_selected_structure(structure_dir)
                            # Call the selection method to trigger button enabling logic
                            self.set_structure_selection(structure_dir)
                            
                logger.info(f"Application state restored: {project_dir}/{subproject_dir}/{structure_dir}")
            else:
                logger.info("No previous application state to restore")
                
        except Exception as e:
            logger.warning(f"Failed to restore application state: {e}")

    def on_application_closing(self) -> None:
        """Handle application closing."""
        try:
            self.save_application_state()
            logger.info("Application closing")
        except Exception as e:
            logger.warning(f"Error during application closing: {e}")
