from pathlib import Path
from tkinter import messagebox

from src.utils import Logger, Constants, FileReader, PathBuilder

from ..viewmodels import VMDataConverter
from ..components import Button, DropdownList
from .windows_template import WindowsTemplate


logger = Logger("DataOperationsWindow")


class DataConverterWindow(WindowsTemplate):
    def __init__(
            self,
            view_model: VMDataConverter,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        super().__init__()
        self.view_model: VMDataConverter = view_model
        self.project_dir: str = project_dir
        self.subproject_dir: str = subproject_dir
        self.structure_dir: str = structure_dir

        self.file_names: list[str] = []
        self._refresh_file_name_lists()

        self.create_window(
            title=f"Data converter ({self.structure_dir})",
        )
        self.create_ui()

    def create_ui(self) -> None:
        self.data_dir_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=[Constants.file_names.RESULT_DATA_DIR],
            command=self.update_data_dir,
            title="Data directory",
            is_disabled=True,
        )

        self.file_names_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=self.file_names,
            command=self.update_file_name,
            title="File to convert",
        )

        self.formats_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=self.view_model.available_formats,
            command=self.update_formats,
            title="Target file format",
        )

        self.next_btn: Button = self.pack_button(
            self.window,
            text="Convert",
            command=self.convert_file,
            pady=(10, 25),
        )

    def update_data_dir(self, value: str) -> None:
        self.view_model.set_data_dir(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
            structure_data_dir=value,
        )
        self._refresh_file_name_lists()

    def update_file_name(self, value: str) -> None:
        self.view_model.set_file_name(value)

    def update_formats(self, value: str) -> None:
        self.view_model.set_file_format(value)

    def _refresh_file_name_lists(self) -> None:
        path: Path = PathBuilder.build_path_to_result_data_dir(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )
        self.file_names: list[str] = FileReader.read_list_of_files(path, to_include_nested_files=True) or ["None"]

        if (not self.view_model.file_name) or (
                self.view_model.file_name == "None") or (
                self.view_model.file_name not in self.file_names):
            self.view_model.set_file_name(self.file_names[0])

        if self.view_model.file_format == "None":
            self.view_model.set_file_format(self.view_model.available_formats[0])

    def convert_file(self) -> None:
        try:
            if self.view_model.file_name.endswith(self.view_model.file_format):
                messagebox.showinfo("Info", "File already in the correct format.")
                return

            converted_file_path: Path = self.view_model.convert_file(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
                file_name=self.view_model.file_name,
                target_format=self.view_model.file_format,
            )
            messagebox.showinfo("Success", f"File converted successfully and saved to\n{converted_file_path}.")

        except Exception as e:
            logger.error(f"Error converting file: {e}")
            messagebox.showerror("Error", str(e))
