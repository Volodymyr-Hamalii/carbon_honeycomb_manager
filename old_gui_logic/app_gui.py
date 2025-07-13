from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

from src.interface.gui.components.dropdown_list import DropdownList
from src.utils import Constants, FileReader

from .components import *
from .viewmodels import *
from .windows import *


class AppGui(ctk.CTk, WindowsTemplate):
    def __init__(self):
        super().__init__()
        self.title("Carbon Honeycomb Manager")
        self.pack_propagate(True)
        self.grid_propagate(True)

        self.list_of_projects: list[str] = []
        self.list_of_subprojects: list[str] = []
        self.list_of_structure_dirs: list[str] = []

        self.set_list_of_projects()
        self.project_dir: str = self.list_of_projects[0] if self.list_of_projects else "None"
        self.set_list_of_subprojects()
        self.subproject_dir: str = self.list_of_subprojects[0] if self.list_of_subprojects else "None"
        self.set_list_of_structure_dirs()
        self.structure_dir: str = self.list_of_structure_dirs[0] if self.list_of_structure_dirs else "None"

        # Create GUI components
        # self.projects_dropdown: DropdownList = self.pack_dropdown_list(
        #     self,
        #     options=self.list_of_projects,
        #     command=self.set_project_dir,
        #     title="Select project",
        #     is_disabled=True,  # TEMP untill there is an only one project
        # )

        self.subprojects_dropdown: DropdownList = self.pack_dropdown_list(
            self,
            options=self.list_of_subprojects,
            command=self.set_subproject_dir,
            title="Select subproject",
        )

        self.structure_dirs_dropdown: DropdownList = self.pack_dropdown_list(
            self,
            options=self.list_of_structure_dirs,
            command=self.set_structure_dir,
            title="Select structure folder",
            pady=(0, 10),
        )

        # Set project, subproject and structure folder
        self.set_project_dir()
        self.set_subproject_dir()
        self.set_structure_dir()

        # Initialize ViewModels
        self.view_model_show_init_data = VMShowInitData()
        self._create_init_data_info_frame()

        self.view_model_data_operations = VMDataConverter()
        self._create_data_operations_frame()

        self.view_model_intercalation_and_sorption = VMIntercalationAndSorption()
        self._create_intercalation_and_sorption_frame()

    def set_list_of_projects(self) -> None:
        projects_dir_path: Path = Constants.path.PROJECT_DATA_PATH
        projects_dirs: list[str] = FileReader.read_list_of_dirs(projects_dir_path)
        self.list_of_projects: list[str] = projects_dirs

    def set_list_of_subprojects(self) -> None:
        subprojects_dir_path: Path = Constants.path.PROJECT_DATA_PATH / self.project_dir
        subproject_dirs: list[str] = FileReader.read_list_of_dirs(subprojects_dir_path)
        self.list_of_subprojects: list[str] = subproject_dirs

    def set_list_of_structure_dirs(self) -> None:
        data_path: Path = Constants.path.PROJECT_DATA_PATH
        init_data_dir: str = Constants.file_names.INIT_DATA_DIR

        structure_dirs_dir_path: Path = data_path / self.project_dir / self.subproject_dir / init_data_dir
        structure_dirs: list[str] = FileReader.read_list_of_dirs(structure_dirs_dir_path)
        self.list_of_structure_dirs: list[str] = structure_dirs

    def set_project_dir(self, project_dir: str = "") -> None:
        if project_dir:
            self.project_dir: str = project_dir

        else:
            projects_dir_path: Path = Constants.path.PROJECT_DATA_PATH
            projects_dirs: list[str] = FileReader.read_list_of_dirs(projects_dir_path)

            if not projects_dirs:
                messagebox.showerror(
                    "Error",
                    "Projects data folders not found. Please, put 'project_data' folder with projects data to the root directory:\n"
                    f"{projects_dir_path}."
                )
                self.project_dir: str = "None"
            else:
                self.project_dir: str = projects_dirs[0]

        # Refresh dropdown list
        self.set_list_of_subprojects()
        self.set_subproject_dir()
        self.subprojects_dropdown.set_options(self.list_of_subprojects, self.subproject_dir)

    def set_subproject_dir(self, subproject_dir: str = "") -> None:
        if subproject_dir:
            self.subproject_dir: str = subproject_dir

        else:
            if not self.list_of_subprojects:
                messagebox.showerror(
                    "Error",
                    "Subprojects data folders not found."
                )
                self.subproject_dir: str = "None"
            else:
                self.subproject_dir: str = self.list_of_subprojects[0]

        # Refresh dropdown list
        self.set_list_of_structure_dirs()
        self.set_structure_dir()
        self.structure_dirs_dropdown.set_options(self.list_of_structure_dirs, self.structure_dir)

    def set_structure_dir(self, structure_dir: str = "") -> None:
        if structure_dir:
            self.structure_dir: str = structure_dir

        else:
            data_path: Path = Constants.path.PROJECT_DATA_PATH
            init_data_dir: str = Constants.file_names.INIT_DATA_DIR

            structure_dirs_dir_path: Path = data_path / self.project_dir / self.subproject_dir / init_data_dir
            structure_dirs: list[str] = FileReader.read_list_of_dirs(structure_dirs_dir_path)

            if not structure_dirs:
                messagebox.showerror(
                    "Error",
                    "Structure folders not found. Please, put 'structure_dirs' folder with structure folders data to the root directory:\n"
                    f"{structure_dirs_dir_path}.")
                self.structure_dir: str = "None"
            else:
                self.structure_dir: str = structure_dirs[0]

    ######### Init data info #########

    def _create_init_data_info_frame(self) -> None:
        """ Create a frame for "Init data info" section """
        init_data_info_frame = ctk.CTkFrame(self)
        init_data_info_frame.pack(pady=10, padx=10, fill="x")

        # Add a label for the section
        init_data_info_label = ctk.CTkLabel(init_data_info_frame, text="CH channel general info")
        init_data_info_label.pack(pady=5)

        # Button to show init structure
        self.show_init_structure_btn = Button(
            init_data_info_frame, text="Show initial CH structure", command=self.open_show_init_structure_window
        )
        self.show_init_structure_btn.pack(pady=10, padx=10)

        # Button to show channel parameters
        self.show_channel_parameters_btn = Button(
            init_data_info_frame, text="Get channel parameters", command=self.open_get_channel_details_window
        )
        self.show_channel_parameters_btn.pack(pady=10, padx=10)

    def open_show_init_structure_window(self) -> None:
        InitDataWindow(
            view_model=self.view_model_show_init_data,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def open_show_one_channel_structure_window(self) -> None:
        InitDataWindow(
            view_model=self.view_model_show_init_data,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def open_get_channel_details_window(self) -> None:
        ChannelDetailsWindow(
            view_model=self.view_model_show_init_data,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    ######### Data operations #########

    def _create_data_operations_frame(self) -> None:
        """ Create a frame for "Data operations" section """
        data_operations_frame = ctk.CTkFrame(self)
        data_operations_frame.pack(pady=10, padx=10, fill="x")

        # Add a label for the section
        data_operations_label = ctk.CTkLabel(data_operations_frame, text="Data operations")
        data_operations_label.pack(pady=5)

        # Button to show data converter
        self.show_data_converter_btn = Button(
            data_operations_frame, text="Files converter", command=self.open_data_converter_window
        )
        self.show_data_converter_btn.pack(pady=10, padx=10)

    def open_data_converter_window(self) -> None:
        DataConverterWindow(
            view_model=self.view_model_data_operations,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    ######### Intercalation and sorption #########

    def _create_intercalation_and_sorption_frame(self) -> None:
        """ Create a frame for "Intercalation and sorption" section """
        intercalation_and_sorption_frame = ctk.CTkFrame(self)
        intercalation_and_sorption_frame.pack(pady=10, padx=10, fill="x")

        # Add a label for the section
        intercalation_and_sorption_label = ctk.CTkLabel(
            intercalation_and_sorption_frame, text="Intercalation and sorption")
        intercalation_and_sorption_label.pack(pady=5)

        # Button to show intercalation and sorption
        self.show_intercalation_and_sorption_btn = Button(
            intercalation_and_sorption_frame, text="Build intercalated atoms in the CH channel",
            command=self.open_update_inter_atoms_coordinates_table_window)
        self.show_intercalation_and_sorption_btn.pack(pady=10, padx=10)

        # Button to show intercalation and sorption
        self.show_intercalation_and_sorption_btn = Button(
            intercalation_and_sorption_frame, text="Translate intercalated atoms to other planes",
            command=self.open_translate_inter_atoms_to_other_planes_window)
        self.show_intercalation_and_sorption_btn.pack(pady=10, padx=10)

        # Button to show intercalation and sorption
        self.show_intercalation_and_sorption_btn = Button(
            intercalation_and_sorption_frame, text="Translate intercalated atoms to all channels",
            command=self.open_translate_inter_atoms_to_all_channels_window)
        self.show_intercalation_and_sorption_btn.pack(pady=10, padx=10)

        # Add a label for the subsection
        model_analysis_label = ctk.CTkLabel(
            intercalation_and_sorption_frame, text="Model analysis")
        model_analysis_label.pack(pady=5)

        # Button to show intercalation and sorption
        self.show_intercalation_and_sorption_btn = Button(
            intercalation_and_sorption_frame, text="Get intercalated CH channel details table",
            command=self.open_get_inter_chc_details_tbl_window)
        self.show_intercalation_and_sorption_btn.pack(pady=10, padx=10)

        # Button to show intercalation and sorption constants
        self.show_intercalation_and_sorption_btn = Button(
            intercalation_and_sorption_frame, text="Get intercalated CH channel constants",
            command=self.open_get_inter_chc_constants_window)
        self.show_intercalation_and_sorption_btn.pack(pady=10, padx=10)

    def open_update_inter_atoms_coordinates_table_window(self) -> None:
        UpdateInterCoordinatesTableWindow(
            view_model=self.view_model_intercalation_and_sorption,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def open_translate_inter_atoms_to_other_planes_window(self) -> None:
        TranslateInterToOtherPlanesWindow(
            view_model=self.view_model_intercalation_and_sorption,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def open_translate_inter_atoms_to_all_channels_window(self) -> None:
        TranslateInterToAllChannelsWindow(
            view_model=self.view_model_intercalation_and_sorption,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def open_get_inter_chc_details_tbl_window(self) -> None:
        GetInterChcDetailsTblWindow(
            view_model=self.view_model_intercalation_and_sorption,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def open_get_inter_chc_constants_window(self) -> None:
        GetInterChcConstantsWindow(
            view_model=self.view_model_intercalation_and_sorption,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )
