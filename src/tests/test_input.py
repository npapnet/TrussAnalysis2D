import pytest
from npp_2d_truss_analysis.truss_input import Mesh, Displacements, Forces
from npp_2d_truss_analysis.truss_input import integer_to_latin_sequence

@pytest.fixture
def mesh_data():
    return [[5.0],
        [0.0, 0.0],
        [0.0, 2.0],
        [0.0, 4.0],
        [4.0, 4.0],
        [4.0, 2.0],
        [7.0],
        [4.0, 3.0, 1.0],
        [3.0, 2.0, 1.0],
        [2.0, 4.0, 1.0],
        [4.0, 5.0, 1.0],
        [5.0, 2.0, 1.0],
        [2.0, 1.0, 1.0],
        [1.0, 5.0, 1.0],
        [1.0],
        [200000000000.0, 1.0]]

@pytest.fixture
def displ_data():
    return [[1.0], [4.0, 0.0, 0.0, 0.0], [1.0], [1.0, 2.0, 26.5651, 0.0], []]

@pytest.fixture
def forces_data():
    return  [[2.0], [5.0, -180.0, 40000.0, 0.0], [3.0, 200.0, 20000.0, 0.0]]


def test_mesh(mesh_data):
    mesh = Mesh()
    mesh.process_mesh(mesh_data)
    assert mesh.number_nodes == 5
    assert mesh.number_elements == 7
    assert mesh.node_coordinates == [(0.0, 0.0), (0.0, 2.0), (0.0, 4.0), (4.0, 4.0), (4.0, 2.0)]
    assert mesh.element_connectivity == [(4, 3), (3, 2), (2, 4), (4, 5), (5, 2), (2, 1), (1, 5)]
    assert mesh.young_modulus == [200e9, 200e9, 200e9, 200e9, 200e9, 200e9, 200e9]
    assert mesh.area == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

def test_displ(displ_data):
    displ = Displacements()
    displ.process_displacements(displ_data)
    assert displ.number_pin == 1
    assert displ.pin_nodes == [4]   
    assert displ.pin_displacements == [(0.0, 0.0)]
    assert displ.pin_angles == [0.0]
    assert displ.number_roller == 1
    assert displ.roller_nodes == [1]   
    assert displ.roller_directions == [2]
    assert displ.roller_angles == [26.5651]
    assert displ.roller_displacements == [0.0]
    assert displ.number_support == 2
    assert displ.support_nodes == [4,1]



def test_forces(forces_data):
    forces = Forces()
    forces.process_forces(forces_data)
    assert forces.number_forces == 2
    assert forces.force_nodes == [5, 3]
    assert forces.force_components ==  [(40000.0, 0.0), (20000.0, 0.0)]
    assert forces.force_angles == [-180.0, 200.0]


def test_integer_to_latin_sequence():
    assert integer_to_latin_sequence(1) == 'A'
    assert integer_to_latin_sequence(2) == 'B'
    assert integer_to_latin_sequence(26) == 'Z'
    assert integer_to_latin_sequence(27) == 'AA'
    assert integer_to_latin_sequence(28) == 'AB'
    assert integer_to_latin_sequence(52) == 'AZ'
    assert integer_to_latin_sequence(53) == 'BA'
    assert integer_to_latin_sequence(54) == 'BB'
    assert integer_to_latin_sequence(702) == 'ZZ'
