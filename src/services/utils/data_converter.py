import numpy as np
import pandas as pd

from .logger import Logger


logger = Logger("DataConverter")


class DataConverter:
    _dat_file_first_line: str = "        {num_of_atoms}         150           3  1.000000000000000E-002       10000\n" + \
        "   5.00000000000000             3023   1.00000000000000\n"

    _pdb_file_first_line: str = "COMPND\tBENS NIEUWE KRISTALLEN\n" + \
        "AUTHOR\tBWVANDEWAAL\t27 04 00\n"

    _pdb_file_end_line: str = "TER\t{num_of_atoms}\nEND\n"

    @classmethod
    def convert_df_to_dat(cls, df: pd.DataFrame) -> list[str]:
        """ Return list of strings with .dat file lines. """
        dat_lines: list[str] = [cls._dat_file_first_line]
        for _, row in df.iterrows():
            dat_lines.append(f"{row[0]:.6f}\t{row[1]:.6f}\t{row[2]:.6f}\n")
        return dat_lines

    @classmethod
    def convert_df_to_pdb(
            cls,
            df: pd.DataFrame,
            atom_name: str = "C",
            residue_seq_num: int = 1,
            chain_id: str = "A",
    ) -> list[str]:
        """ Return list of strings with .pdb file lines. """
        pdb_lines: list[str] = []
        for i, row in df.iterrows():
            pdb_line: str = cls._build_pdb_line(
                row.to_numpy(),
                int(i) + 1,  # type: ignore
                atom_name,
                residue_seq_num,
                chain_id
            )
            pdb_lines.append(pdb_line)
        return pdb_lines

    @classmethod
    def convert_ndarray_to_dat(cls, coordinates: np.ndarray) -> list[str]:
        """ Return list of strings with .dat file lines. """
        first_line: str = cls._dat_file_first_line.format(num_of_atoms=len(coordinates))
        dat_lines: list[str] = [first_line]

        for row in coordinates:
            dat_lines.append(f"{row[0]:.6f}\t{row[1]:.6f}\t{row[2]:.6f}\n")
        return dat_lines

    @classmethod
    def convert_ndarray_to_pdb(
            cls,
            coordinates: np.ndarray,
            atom_name: str = "C",
            residue_seq_num: int = 1,
            chain_id: str = "A",
    ) -> list[str]:
        """ Return list of strings with .pdb file lines. """
        first_line: str = cls._pdb_file_first_line.format(num_of_atoms=len(coordinates))
        pdb_lines: list[str] = [first_line]

        for i, row in enumerate(coordinates):
            pdb_line: str = cls._build_pdb_line(row, i + 1, atom_name, residue_seq_num, chain_id)
            pdb_lines.append(pdb_line)

        num_of_atoms: int = len(coordinates)
        pdb_lines.append(cls._pdb_file_end_line.format(num_of_atoms=num_of_atoms))
        return pdb_lines

    @staticmethod
    def _build_pdb_line(
            row: np.ndarray, index: int, atom_name: str = "C", residue_seq_num: int = 1, chain_id: str = "A") -> str:
        """ Build a PDB line from a row of data. """
        return f"ATOM  {index:5d} {atom_name:<4} {chain_id} {residue_seq_num:4d}    " \
            f"{row[0]:8.3f}{row[1]:8.3f}{row[2]:8.3f}  1.00  0.00\n"
