import numpy as np

from src.services import (
    Constants,
    ConstantsAtomParams,
    Logger,
    FileReader,
)
from src.entities import Points
from src.interfaces import ICarbonHoneycombChannel, IPoints

from .based_on_planes_configs import InterChannelBuilderBasedOnPlaneConfigs


logger = Logger("IntercalatedChannelBuilder")


class IntercalatedChannelBuilder:
    @staticmethod
    def build_carbon_coordinates(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str | None = None,
    ) -> Points:
        if file_name is None:
            file_name = Constants.file_names.INIT_DAT_FILE

        carbon_points: np.ndarray = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        if len(carbon_points) == 0:
            raise ValueError(f"No carbon atoms found in {file_name} file.")

        carbon_points = np.round(carbon_points, 3)

        return Points(points=carbon_points)

    # @staticmethod
    # def build_inter_coordinates_for_cell(
    #         project_dir: str,
    #         subproject_dir: str,
    #         structure_dir: str,
    #         file_name: str,
    #         to_translate_inter: bool,
    #         coordinate_limits: CoordinateLimits = CoordinateLimits(),
    # ) -> IPoints:
    #     path_to_inter_atoms_pdb_file: Path = PathBuilder.build_path_to_init_data_file(
    #         project_dir=project_dir,
    #         subproject_dir=subproject_dir,
    #         structure_dir=structure_dir,
    #         file_name=file_name,
    #     )
    #     inter_points: Points = AtomsUniverseBuilder.builds_atoms_coordinates(path_to_inter_atoms_pdb_file)

    #     if to_translate_inter:
    #         return StructureTranslator.translate_cell(
    #             cell_coordinates=inter_points,
    #             translation_limits=coordinate_limits)

    #     return inter_points

    # @staticmethod
    # def build_inter_coordinates_for_close_packed(
    #         inter_atoms_lattice_type: LatticeType,
    #         coordinate_limits: CoordinateLimits,
    #         atom_params: ConstantsAtomParams,
    #         # to_translate_inter: bool,  # TODO
    # ) -> Points:

    #     dist_between_atoms: float = atom_params.DIST_BETWEEN_ATOMS

    #     if inter_atoms_lattice_type.is_fcc:
    #         return AtomsUniverseBuilder.build_fcc_lattice_type(
    #             dist_between_atoms=dist_between_atoms,
    #             coordinate_limits=coordinate_limits,
    #         )

    #     if inter_atoms_lattice_type.is_hcp:
    #         return AtomsUniverseBuilder.build_hcp_lattice_type(
    #             dist_between_atoms=dist_between_atoms,
    #             coordinate_limits=coordinate_limits,
    #         )

    #     logger.warning("No intercalated atoms built for closed packed structure.")
    #     return Points(points=np.array([]))

    # @classmethod
    # def build_inter_in_carbon_by_variance(
    #     cls,
    #     carbon_channel: CarbonHoneycombChannel,
    #     inter_points: Points,
    #     to_filter_inter_atoms: bool = True,
    #     equidistant_inter_points: bool = True
    # ) -> Points:
    #     return InterChannelBuilderByVariance.build_inter_atoms_in_carbon(
    #         carbon_channel,
    #         inter_points,
    #         to_filter_inter_atoms,
    #         equidistant_inter_points,
    #     )

    @classmethod
    def build_inter_in_carbon(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        inter_points: IPoints,
        atom_params: ConstantsAtomParams,
        to_filter_inter_atoms: bool = True,
        equidistant_inter_points: bool = True,
    ) -> IPoints:
        # return InterChannelBuilderByVariance.build_inter_atoms_in_carbon(
        #     carbon_channel,
        #     inter_points,
        #     structure_settings,
        #     to_filter_inter_atoms,
        #     equidistant_inter_atoms,
        # )
        return InterChannelBuilderBasedOnPlaneConfigs.build_inter_in_carbon(
            carbon_channel,
            atom_params,
            equidistant_inter_points,
        )

    @staticmethod
    def translate_inter_points_through_channels(
            inter_atoms: np.ndarray,
            carbon_channels: list[ICarbonHoneycombChannel],
    ) -> np.ndarray:
        """ Translate the built structure to all channels. """

        if not carbon_channels:
            raise ValueError("The list of carbon_channels must not be empty.")

        filled_channel_center: np.ndarray = carbon_channels[0].channel_center

        result_inter_points: np.ndarray = inter_atoms.copy()

        for channel in carbon_channels[1:]:
            channel_center: np.ndarray = channel.channel_center
            vector: np.ndarray = channel_center - filled_channel_center

            translated_inter_points: np.ndarray = inter_atoms + vector

            result_inter_points = np.concatenate([result_inter_points, translated_inter_points])

        return result_inter_points
