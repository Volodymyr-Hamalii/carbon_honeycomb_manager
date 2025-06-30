import numpy as np

from src_1.utils import Logger, ConstantsAtomParams, execution_time_logger
from src_1.data_preparation import StructureSettings
from src_1.base_structure_classes import Points
from src_1.projects.carbon_honeycomb_actions import CarbonHoneycombChannel
from src_1.structure_visualizer import StructureVisualizer
from src_1.coordinate_operations import DistanceMeasure

from .inter_atoms_builder import InterAtomsBuilder
from .inter_atoms_filter import InterAtomsFilter
from .inter_atom_configurator import InterAtomConfigurator


logger = Logger("IntercalatedChannelBuilder")


class InterChannelBuilderBasedOnPlaneConfigs:
    @classmethod
    def build_inter_in_carbon(
            cls,
            carbon_channel: CarbonHoneycombChannel,
            atom_params: ConstantsAtomParams,
            equidistant_inter_points: bool = True,
    ) -> Points:
        """ Returns atoms_inter """

        atoms_inter: Points = InterAtomsBuilder.build_inter_atoms_near_planes(
            carbon_channel, atom_params, equidistant_inter_points)
        atoms_inter = InterAtomsFilter.replace_nearby_atoms_with_one_atom(atoms_inter, atom_params)
        atoms_inter = InterAtomsFilter.remove_too_close_atoms(atoms_inter, atom_params)

        # StructureVisualizer.show_two_structures(
        #     coordinates_first=carbon_channel.points, coordinates_second=atoms_inter.points, to_build_bonds=True)

        # atoms_inter = InterAtomConfigurator.reorganize_inter_atoms_atoms(atoms_inter, carbon_channel)
        cls._print_statistics(atoms_inter, carbon_channel)

        return atoms_inter

    @staticmethod
    def _print_statistics(
        atoms_inter: Points,
        carbon_channel: CarbonHoneycombChannel,
    ) -> None:

        inter: np.ndarray = atoms_inter.points
        carbon: np.ndarray = carbon_channel.points

        min_between_inter_atoms: np.float64 = np.min(DistanceMeasure.calculate_min_distances_between_points(inter))
        max_between_inter_atoms: np.float64 = np.max(DistanceMeasure.calculate_min_distances_between_points(inter))
        # mean_between_inter_atoms: np.float64 = np.mean(DistanceMeasure.calculate_min_distances_between_points(inter))

        min_between_c_and_inter_atoms: np.float64 = np.min(DistanceMeasure.calculate_min_distances(inter, carbon))
        max_between_c_and_inter_atoms: np.float64 = np.max(DistanceMeasure.calculate_min_distances(inter, carbon))
        # mean_between_c_and_inter_atoms: np.float64 = np.mean(DistanceMeasure.calculate_min_distances(inter, carbon))

        logger.info(
            "Final stats:\n",
            f"min_between_inter_atoms: {round(min_between_inter_atoms, 3)}\n",
            f"max_between_inter_atoms: {round(max_between_inter_atoms, 3)}\n",
            # f"mean_between_inter_atoms: {round(mean_between_inter_atoms, 3)}\n",
            f"min_between_c_and_inter_atoms: {round(min_between_c_and_inter_atoms, 3)}\n",
            f"max_between_c_and_inter_atoms: {round(max_between_c_and_inter_atoms, 3)}\n",
            # f"mean_between_c_and_inter_atoms: {round(mean_between_c_and_inter_atoms, 3)}\n",
        )
