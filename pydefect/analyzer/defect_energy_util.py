# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from itertools import combinations
from typing import Dict

from pydefect.analyzer.defect_energy import DefectEnergies


def u_values_from_defect_energies(defect_energy_dict: Dict[str, DefectEnergies],
                                  correction: bool = False) -> dict:
    return {name: calc_u_values(de, correction)
            for name, de in defect_energy_dict.items()}


def calc_u_values(defect_energies: DefectEnergies, correction):
    result = {}
    for triple in combinations(defect_energies.charge_energy_pairs, 3):
        sorted_triple = sorted(triple, key=lambda x: x[0])
        charges = tuple(i[0] for i in sorted_triple)
        net_charge = charges[0] + charges[2] - charges[1] * 2
        charge_diff = charges[1] - charges[0]
        if net_charge != 0 or charge_diff != 1:
            continue
        energies = [i[1].energy(correction) for i in sorted_triple]
        result[charges] = energies[0] + energies[2] - energies[1] * 2
    return result
