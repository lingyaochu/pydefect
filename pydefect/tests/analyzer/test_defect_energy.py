# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

import pytest

from pydefect.analyzer.defect_energy import DefectEnergy, CrossPoints, \
    DefectEnergies


@pytest.fixture
def defect_energy():
    return DefectEnergy(name="Va_O1",
                        charges=[0, 1, 2],
                        energies=[5, 3, -4],
                        corrections=[1, 0, 0],
                        shallow=[False, False, False],
                        )


def test_corrected_energies(defect_energy):
    assert defect_energy.corrected_energies == [6, 3, -4]


def test_defect_energy_cross_points(defect_energy):
    actual = defect_energy.cross_points(1, 6)
    expected = ([[1.0, -2.0], [5.0, 6.0], [6.0, 6.0]],
                [[5.0, 6.0]],
                [[1.0, -2.0], [6.0, 6.0]])
    assert actual == expected


def test_cross_points():
    inner_cross_points = [[2, 20], [3, 30], [4, 40]]
    boundary_points = [[1, 10], [5, 50]]
    cross_points = CrossPoints(inner_cross_points, boundary_points)

    assert cross_points.all_points == [[1, 10], [2, 20], [3, 30], [4, 40], [5, 50]]
    assert cross_points.t_inner_cross_points == [[2, 3, 4], [20, 30, 40]]
    assert cross_points.t_boundary_points == [[1, 5], [10, 50]]


def test_defect_energies(defect_energy):
    defect_energies = DefectEnergies([defect_energy],
                                     vbm=1.0,
                                     cbm=6.0,
                                     supercell_vbm=1.5,
                                     supercell_cbm=5.5)
    plt = defect_energies.plot()
    plt.show()


"""
TODO
- Correction.

- Evaluate the crossing points at given Fermi level range.

- Draw a single defect

DONE
"""