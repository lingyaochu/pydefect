# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.

import argparse
import sys
import warnings
from pathlib import Path

from monty.serialization import loadfn
from pydefect import __version__
from pydefect.analyzer.unitcell import Unitcell
from pydefect.chem_pot_diag.chem_pot_diag import StandardEnergies
from pydefect.cli.main_functions import plot_defect_energy, \
    make_standard_and_relative_energies, make_cpd_and_vertices, \
    plot_chem_pot_diag, make_supercell, append_interstitial_to_supercell_info, \
    pop_interstitial_from_supercell_info, make_defect_set, \
    make_efnv_correction_main_func, make_band_edge_states_main_func, \
    make_defect_energy_infos_main_func, make_defect_energy_summary_main_func, \
    calc_defect_structure_info, make_calc_summary_main_func
from pydefect.cli.main_tools import str_int_to_int
from pydefect.defaults import defaults
from pymatgen.core import IStructure, Structure
from pymatgen.io.vasp.inputs import UnknownPotcarWarning

warnings.simplefilter('ignore', UnknownPotcarWarning)


description = """pydefect is a package that helps researchers to 
do first-principles point defect calculations with the VASP code."""

epilog = f"Author: Yu Kumagai Version: {__version__}"


def add_sub_parser(_argparse, name: str):
    result = _argparse.ArgumentParser(description="", add_help=False)
    if name == "dirs":
        result.add_argument(
            "-d", "--dirs", nargs="+", type=Path, required=True,
            help="Directory paths to be parsed.")
    elif name == "unitcell":
        result.add_argument(
            "-u", "--unitcell", type=Unitcell.from_yaml, required=True,
            help="Path to the unitcell.yaml file.")
    elif name == "supercell_info":
        result.add_argument(
            "-s", "--supercell_info", required=True, type=loadfn,
            default="supercell_info.json",
            help="Path to the supercell_info.json file.")
    elif name == "perfect_calc_results":
        result.add_argument(
            "-pcr", "--perfect_calc_results", required=True, type=loadfn,
            help="Path to the calc_results.json for the perfect supercell.")
    elif name == "perfect_band_edge_state":
        result.add_argument(
            "-pbes", "--p_state", required=True, type=loadfn,
            help="Path to the perfect_band_edge_state.json.")

    else:
        raise ValueError
    return result


def parse_args_main(args):

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    subparsers = parser.add_subparsers()

    dirs_parser = add_sub_parser(argparse, name="dirs")
    unitcell_parser = add_sub_parser(argparse, name="unitcell")
    si_parser = add_sub_parser(argparse, name="supercell_info")
    pcr_parser = add_sub_parser(argparse, name="perfect_calc_results")
    pbes_parser = add_sub_parser(argparse, name="perfect_band_edge_state")
    # -- make_standard_and_relative_energies -----------------------------------
    parser_make_standard_and_relative_energies = subparsers.add_parser(
        name="standard_and_relative_energies",
        description="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['sre'])

    parser_make_standard_and_relative_energies.add_argument(
        "-y", "--composition_energies_yaml", type=str,
        default="composition_energies.yaml",
        help="composition_energies.yaml file name.")
    parser_make_standard_and_relative_energies.set_defaults(
        func=make_standard_and_relative_energies)

    # -- make_cpd_and_vertices -------------------------------------------------
    parser_cv = subparsers.add_parser(
        name="cpd_and_vertices",
        description="Make chemical potential diagram.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['cv'])

    parser_cv.add_argument(
        "-y", "--rel_energy_yaml", type=str, default="relative_energies.yaml",
        help=" yaml file name.")
    parser_cv.add_argument(
        # this must be string as keys of RelativeEnergies are strings.
        "-t", "--target", type=str, required=True,
        help="Target composition, e.g., MgO.")
    parser_cv.add_argument(
        "-e", "--elements", type=str, nargs="+",
        help="Element names considered in chemical potential diagram. Used for "
             "creating the diagram.")
    parser_cv.set_defaults(func=make_cpd_and_vertices)

    # -- plot_cpd ------------------------------------------------
    parser_pcpd = subparsers.add_parser(
        name="plot_cpd",
        description="Plot chemical potential diagram and make pdf file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['pc'])
    parser_pcpd.add_argument(
        "-cpd", "--chem_pot_diag", default="chem_pot_diag.json", type=loadfn,
        help="Path to the chem_pot_diag.json file.")
    parser_pcpd.set_defaults(func=plot_chem_pot_diag)

    # -- supercell ------------------------------------------------
    parser_supercell = subparsers.add_parser(
        name="supercell",
        description="Make SPOSCAR file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['s'])

    parser_supercell.add_argument(
        "-p", "--unitcell", type=IStructure.from_file, required=True,
        help="Base structure file, which must be the standardized primitive "
             "cell.")
    parser_supercell.add_argument(
        "--matrix", nargs="+", type=int,
        help="Supercell matrix applied to the conventional cell. "
             "1, 3 or 9 components are accepted.")
    parser_supercell.add_argument(
        "--min_atoms", dest="min_num_atoms", default=50, type=int,
        help="Minimum number of atoms")
    parser_supercell.add_argument(
        "--max_atoms", dest="max_num_atoms", default=300, type=int,
        help="Maximum number of atoms")

    parser_supercell.set_defaults(func=make_supercell)

    # -- append_interstitial ------------------------------------------------
    parser_append_interstitial = subparsers.add_parser(
        name="append_interstitial",
        description="Append interstitial information to supercell_info.yaml",
        parents=[si_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['ai'])

    parser_append_interstitial.add_argument(
        "-p", "--base_structure", required=True, type=Structure.from_file,
        help="Structure file defining the fractional coordinates such as the "
             "standardized primitive cell.")
    parser_append_interstitial.add_argument(
        "-c", "--frac_coords", required=True, nargs=3, type=float,
        help="Fractional coordinates in the standardized primitive cell added "
             "as an interstitial ")
    parser_append_interstitial.add_argument(
        "-i", "--info", type=str, default="None",
        help="Information related to the appended interstitial site if exists.")

    parser_append_interstitial.set_defaults(
        func=append_interstitial_to_supercell_info)

    # -- pop_interstitial ------------------------------------------------
    parser_pop_interstitial = subparsers.add_parser(
        name="pop",
        description="Pop interstitial site from supercell_info.json. ",
        parents=[si_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['pi'])

    parser_pop_interstitial.add_argument(
        "-i", "--index", type=int,
        help="Popped interstitial index. Note that the indices begin from 1.")
    parser_pop_interstitial.add_argument(
        "--pop_all", action="store_true",
        help="Pop all interstitials. If this is set, index option is ignored.")

    parser_pop_interstitial.set_defaults(
        func=pop_interstitial_from_supercell_info)

    # -- defect_set ------------------------------------------------
    parser_defect_set = subparsers.add_parser(
        name="defect_set",
        description="Make defect_in.yaml file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['ds'])

    parser_defect_set.add_argument(
        "-o", "--oxi_states", nargs="+", type=str_int_to_int,
        help="Oxidation states in integers, e.g., Mg 2 O -2.")
    parser_defect_set.add_argument(
        "-d", "--dopants", nargs="+", type=str,
        help="Names of dopant element, e.g., Al Ga.")
    parser_defect_set.add_argument(
        "-k", "--kwargs", nargs="+", type=str,
        help="Keywords used to screen the target defects. "
             "Regular expression can be used.")

    parser_defect_set.set_defaults(func=make_defect_set)

    # -- defect structure info ------------------------------------------------
    parser_defect_structure_info = subparsers.add_parser(
        name="defect_structure_info",
        description="Defect structure info.",
        parents=[dirs_parser, si_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['dsi'])

    parser_defect_structure_info.add_argument(
        "-dt", "--dist_tolerance", type=float, default=defaults.dist_tol,
        help="Tolerance in Angstrom for distance to judge if the "
             "atoms in initial and final structures are same ones.")
    parser_defect_structure_info.add_argument(
        "--symprec", type=float, default=defaults.symmetry_length_tolerance,
        help="Tolerance for determining point groups in the final "
             "structures. Note that point groups in the initial structures are "
             "set via defect_entry.json files.")
    parser_defect_structure_info.set_defaults(func=calc_defect_structure_info)

    # -- efnv correction ------------------------------------------------
    parser_efnv = subparsers.add_parser(
        name="efnv",
        description="Generate extended FNV-correction related efnv_correction "
                    "files. ",
        parents=[dirs_parser, pcr_parser, unitcell_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['efnv'])

    parser_efnv.set_defaults(func=make_efnv_correction_main_func)

    # -- band edge states ------------------------------------------------
    parser_band_edge_states = subparsers.add_parser(
        name="band_edge_states",
        description="Show edge state for each spin channel.",
        parents=[dirs_parser, pbes_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['bes'])

    parser_band_edge_states.set_defaults(func=make_band_edge_states_main_func)

    # -- defect energy infos ---------------------------------------------------
    parser_defect_energy_infos = subparsers.add_parser(
        name="defect_energy_infos",
        description="",
        parents=[dirs_parser, pcr_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['dei'])
    parser_defect_energy_infos.add_argument(
        "-s", "--std_energies", required=True, type=StandardEnergies.from_yaml,
        help="Path to the StandardEnergies.yaml file.")

    parser_defect_energy_infos.set_defaults(
        func=make_defect_energy_infos_main_func)

    # -- defect energy summary -------------------------------------------------
    parser_defect_energy_summary = subparsers.add_parser(
        name="defect_energy_summary",
        description="",
        parents=[dirs_parser, unitcell_parser, pbes_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['des'])
    parser_defect_energy_summary.add_argument(
        "-t", "--target_vertices_yaml", required=True, type=str,
        help="Path to the target_vertices.yaml file.")

    parser_defect_energy_summary.set_defaults(
        func=make_defect_energy_summary_main_func)

    # -- calc summary -------------------------------------------------
    parser_calc_summary = subparsers.add_parser(
        name="calc_summary",
        description="",
        parents=[dirs_parser, pcr_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['cs'])

    parser_calc_summary.set_defaults(
        func=make_calc_summary_main_func)

    # -- plot defect formation energy ------------------------------------------
    parser_plot_energy = subparsers.add_parser(
        name="plot_defect_formation_energy",
        description="Show and plot defect formation energies.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['pe'])

    parser_plot_energy.add_argument(
        "-d", "--defect_energy_summary", required=True, type=loadfn,
        help="defect_energy_summary.json file path.")
    parser_plot_energy.add_argument(
        "-l", "--label", type=str, help="Label")
    parser_plot_energy.add_argument(
        "-y", "--y_range", nargs=2, type=float,
        help="Energy range in y-axis")
    parser_plot_energy.add_argument(
        "--allow_shallow", action="store_true",
        help="Set when the energies of shallow defects are allowed.")
    parser_plot_energy.add_argument(
        "--no_corrections", dest="with_corrections", action="store_false",
        help="Set when corrections are switched off.")
    parser_plot_energy.add_argument(
        "--no_label_line", dest="label_line", action="store_false",
        help="Set the labels not to locate on the lines.")
    parser_plot_energy.add_argument(
        "--no_add_charges", dest="add_charges", action="store_false",
        help="Set the charges not to appear.")
    parser_plot_energy.set_defaults(func=plot_defect_energy)
    # ------------------------------------------------------------------------
    return parser.parse_args(args)


def main():
    args = parse_args_main(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()


