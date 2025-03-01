from openff.toolkit.typing.engines.smirnoff import ForceField
from openff.toolkit.topology import Molecule, Topology
from biopandas.pdb import PandasPdb
import matplotlib.pyplot as plt
from operator import itemgetter
from mendeleev import element
from simtk.openmm import app
from scipy import optimize
import subprocess as sp
from sys import stdout
import pandas as pd
import numpy as np
import statistics
import itertools
import parmed
import pickle
import shutil
import simtk
import scipy
import time
import math
import sys
import ast
import re
import os

BOHRS_PER_ANGSTROM = 0.529
HARTREE_PER_KCAL_MOL = 627.509391
#kcal/mol * A^2 to kJ/mol * nm^2
KCAL_MOL_PER_KJ_MOL = 4.184
ANGSTROMS_PER_NM = 10.0
RADIANS_PER_DEGREE = np.pi / 180.0


method_basis_scale_dict = {
    "HF STO-3G": 0.817,
    "HF 3-21G": 0.906,
    "HF 3-21G*": 0.903,
    "HF 6-31G": 0.903,
    "HF 6-31G*": 0.899,
    "HF 6-31G**": 0.903,
    "HF 6-31+G**": 0.904,
    "HF 6-311G*": 0.904,
    "HF 6-311G**": 0.909,
    "HF TZVP": 0.909,
    "HF cc-pVDZ": 0.908,
    "HF cc-pVTZ": 0.91,
    "HF cc-pVQZ": 0.908,
    "HF aug-cc-pVDZ": 0.911,
    "HF aug-cc-pVTZ": 0.91,
    "HF aug-cc-pVQZ": 0.909,
    "HF daug-cc-pVDZ": 0.912,
    "HF daug-cc-pVTZ": 0.905,
    "ROHF 3-21G": 0.907,
    "ROHF 3-21G*": 0.909,
    "ROHF 6-31G": 0.895,
    "ROHF 6-31G*": 0.89,
    "ROHF 6-31G**": 0.855,
    "ROHF 6-31+G**": 0.856,
    "ROHF 6-311G*": 0.856,
    "ROHF 6-311G**": 0.913,
    "ROHF cc-pVDZ": 0.861,
    "ROHF cc-pVTZ": 0.901,
    "LSDA STO-3G": 0.896,
    "LSDA 3-21G": 0.984,
    "LSDA 3-21G*": 0.982,
    "LSDA 6-31G": 0.98,
    "LSDA 6-31G*": 0.981,
    "LSDA 6-31G**": 0.981,
    "LSDA 6-31+G**": 0.985,
    "LSDA 6-311G*": 0.984,
    "LSDA 6-311G**": 0.988,
    "LSDA TZVP": 0.988,
    "LSDA cc-pVDZ": 0.989,
    "LSDA cc-pVTZ": 0.989,
    "LSDA aug-cc-pVDZ": 0.989,
    "LSDA aug-cc-pVTZ": 0.991,
    "BLYP STO-3G": 0.925,
    "BLYP 3-21G": 0.995,
    "BLYP 3-21G*": 0.994,
    "BLYP 6-31G": 0.992,
    "BLYP 6-31G*": 0.992,
    "BLYP 6-31G**": 0.992,
    "BLYP 6-31+G**": 0.995,
    "BLYP 6-311G*": 0.998,
    "BLYP 6-311G**": 0.996,
    "BLYP TZVP": 0.998,
    "BLYP cc-pVDZ": 1.002,
    "BLYP cc-pVTZ": 0.997,
    "BLYP aug-cc-pVDZ": 0.998,
    "BLYP aug-cc-pVTZ": 0.997,
    "B1B95 STO-3G": 0.883,
    "B1B95 3-21G": 0.957,
    "B1B95 3-21G*": 0.955,
    "B1B95 6-31G": 0.954,
    "B1B95 6-31G*": 0.949,
    "B1B95 6-31G**": 0.955,
    "B1B95 6-31+G**": 0.957,
    "B1B95 6-311G*": 0.959,
    "B1B95 6-311G**": 0.96,
    "B1B95 TZVP": 0.957,
    "B1B95 cc-pVDZ": 0.961,
    "B1B95 cc-pVTZ": 0.957,
    "B1B95 aug-cc-pVDZ": 0.958,
    "B1B95 aug-cc-pVTZ": 0.959,
    "B3LYP STO-3G": 0.892,
    "B3LYP 3-21G": 0.965,
    "B3LYP 3-21G*": 0.962,
    "B3LYP 6-31G": 0.962,
    "B3LYP 6-31G*": 0.96,
    "B3LYP 6-31G**": 0.961,
    "B3LYP 6-31+G**": 0.964,
    "B3LYP 6-311G*": 0.966,
    "B3LYP 6-311G**": 0.967,
    "B3LYP TZVP": 0.965,
    "B3LYP cc-pVDZ": 0.97,
    "B3LYP cc-pVTZ": 0.967,
    "B3LYP cc-pVQZ": 0.969,
    "B3LYP aug-cc-pVDZ": 0.97,
    "B3LYP aug-cc-pVTZ": 0.968,
    "B3LYP aug-cc-pVQZ": 0.969,
    "B3PW91 STO-3G": 0.885,
    "B3PW91 3-21G": 0.961,
    "B3PW91 3-21G*": 0.959,
    "B3PW91 6-31G": 0.958,
    "B3PW91 6-31G*": 0.957,
    "B3PW91 6-31G**": 0.958,
    "B3PW91 6-31+G**": 0.96,
    "B3PW91 6-311G*": 0.963,
    "B3PW91 6-311G**": 0.963,
    "B3PW91 TZVP": 0.964,
    "B3PW91 cc-pVDZ": 0.965,
    "B3PW91 cc-pVTZ": 0.962,
    "B3PW91 aug-cc-pVDZ": 0.965,
    "B3PW91 aug-cc-pVTZ": 0.965,
    "mPW1PW91 STO-3G": 0.879,
    "mPW1PW91 3-21G": 0.955,
    "mPW1PW91 3-21G*": 0.95,
    "mPW1PW91 6-31G": 0.947,
    "mPW1PW91 6-31G*": 0.948,
    "mPW1PW91 6-31G**": 0.952,
    "mPW1PW91 6-31+G**": 0.952,
    "mPW1PW91 6-311G*": 0.954,
    "mPW1PW91 6-311G**": 0.957,
    "mPW1PW91 TZVP": 0.954,
    "mPW1PW91 cc-pVDZ": 0.958,
    "mPW1PW91 cc-pVTZ": 0.959,
    "mPW1PW91 aug-cc-pVDZ": 0.958,
    "mPW1PW91 aug-cc-pVTZ": 0.958,
    "PBEPBE STO-3G": 0.914,
    "PBEPBE 3-21G": 0.991,
    "PBEPBE 3-21G*": 0.954,
    "PBEPBE 6-31G": 0.986,
    "PBEPBE 6-31G*": 0.986,
    "PBEPBE 6-31G**": 0.986,
    "PBEPBE 6-31+G**": 0.989,
    "PBEPBE 6-311G*": 0.99,
    "PBEPBE 6-311G**": 0.991,
    "PBEPBE TZVP": 0.989,
    "PBEPBE cc-pVDZ": 0.994,
    "PBEPBE cc-pVTZ": 0.993,
    "PBEPBE aug-cc-pVDZ": 0.994,
    "PBEPBE aug-cc-pVTZ": 0.994,
    "PBE1PBE STO-3G": 0.882,
    "PBE1PBE 3-21G": 0.96,
    "PBE1PBE 3-21G*": 0.96,
    "PBE1PBE 6-31G": 0.956,
    "PBE1PBE 6-31G*": 0.95,
    "PBE1PBE 6-31G**": 0.953,
    "PBE1PBE 6-31+G**": 0.955,
    "PBE1PBE 6-311G*": 0.959,
    "PBE1PBE 6-311G**": 0.959,
    "PBE1PBE TZVP": 0.96,
    "PBE1PBE cc-pVDZ": 0.962,
    "PBE1PBE cc-pVTZ": 0.961,
    "PBE1PBE aug-cc-pVDZ": 0.962,
    "PBE1PBE aug-cc-pVTZ": 0.962,
    "HSEh1PBE STO-3G": 0.883,
    "HSEh1PBE 3-21G": 0.963,
    "HSEh1PBE 3-21G*": 0.96,
    "HSEh1PBE 6-31G": 0.957,
    "HSEh1PBE 6-31G*": 0.951,
    "HSEh1PBE 6-31G**": 0.954,
    "HSEh1PBE 6-31+G**": 0.955,
    "HSEh1PBE 6-311G*": 0.96,
    "HSEh1PBE 6-311G**": 0.96,
    "HSEh1PBE TZVP": 0.96,
    "HSEh1PBE cc-pVDZ": 0.962,
    "HSEh1PBE cc-pVTZ": 0.961,
    "HSEh1PBE aug-cc-pVDZ": 0.962,
    "HSEh1PBE aug-cc-pVTZ": 0.962,
    "TPSSh 3-21G": 0.969,
    "TPSSh 3-21G*": 0.966,
    "TPSSh 6-31G": 0.962,
    "TPSSh 6-31G*": 0.959,
    "TPSSh 6-31G**": 0.959,
    "TPSSh 6-31+G**": 0.963,
    "TPSSh 6-311G*": 0.963,
    "TPSSh TZVP": 0.964,
    "TPSSh cc-pVDZ": 0.972,
    "TPSSh cc-pVTZ": 0.968,
    "TPSSh aug-cc-pVDZ": 0.967,
    "TPSSh aug-cc-pVTZ": 0.965,
    "B97D3 3-21G": 0.983,
    "B97D3 6-31G*": 0.98,
    "B97D3 6-31+G**": 0.983,
    "B97D3 6-311G**": 0.986,
    "B97D3 TZVP": 0.986,
    "B97D3 cc-pVDZ": 0.992,
    "B97D3 cc-pVTZ": 0.986,
    "B97D3 aug-cc-pVTZ": 0.985,
    "MP2 STO-3G": 0.872,
    "MP2 3-21G": 0.955,
    "MP2 3-21G*": 0.951,
    "MP2 6-31G": 0.957,
    "MP2 6-31G*": 0.943,
    "MP2 6-31G**": 0.937,
    "MP2 6-31+G**": 0.941,
    "MP2 6-311G*": 0.95,
    "MP2 6-311G**": 0.95,
    "MP2 TZVP": 0.948,
    "MP2 cc-pVDZ": 0.953,
    "MP2 cc-pVTZ": 0.95,
    "MP2 cc-pVQZ": 0.948,
    "MP2 aug-cc-pVDZ": 0.959,
    "MP2 aug-cc-pVTZ": 0.953,
    "MP2 aug-cc-pVQZ": 0.95,
    "MP2=FULL STO-3G": 0.889,
    "MP2=FULL 3-21G": 0.955,
    "MP2=FULL 3-21G*": 0.948,
    "MP2=FULL 6-31G": 0.95,
    "MP2=FULL 6-31G*": 0.942,
    "MP2=FULL 6-31G**": 0.934,
    "MP2=FULL 6-31+G**": 0.939,
    "MP2=FULL 6-311G*": 0.947,
    "MP2=FULL 6-311G**": 0.949,
    "MP2=FULL TZVP": 0.953,
    "MP2=FULL cc-pVDZ": 0.95,
    "MP2=FULL cc-pVTZ": 0.949,
    "MP2=FULL cc-pVQZ": 0.957,
    "MP2=FULL aug-cc-pVDZ": 0.969,
    "MP2=FULL aug-cc-pVTZ": 0.951,
    "MP2=FULL aug-cc-pVQZ": 0.956,
    "MP3 STO-3G": 0.894,
    "MP3 3-21G": 0.968,
    "MP3 3-21G*": 0.965,
    "MP3 6-31G": 0.966,
    "MP3 6-31G*": 0.939,
    "MP3 6-31G**": 0.935,
    "MP3 6-31+G**": 0.931,
    "MP3 TZVP": 0.935,
    "MP3 cc-pVDZ": 0.948,
    "MP3 cc-pVTZ": 0.945,
    "MP3=FULL 6-31G*": 0.938,
    "MP3=FULL 6-31+G**": 0.932,
    "MP3=FULL TZVP": 0.934,
    "MP3=FULL cc-pVDZ": 0.94,
    "MP3=FULL cc-pVTZ": 0.933,
    "B2PLYP 6-31G*": 0.949,
    "B2PLYP 6-31+G**": 0.952,
    "B2PLYP TZVP": 0.954,
    "B2PLYP cc-pVDZ": 0.958,
    "B2PLYP cc-pVTZ": 0.959,
    "B2PLYP cc-pVQZ": 0.957,
    "B2PLYP aug-cc-pVTZ": 0.961,
    "B2PLYP=FULL 3-21G": 0.952,
    "B2PLYP=FULL 6-31G*": 0.948,
    "B2PLYP=FULL 6-31+G**": 0.951,
    "B2PLYP=FULL TZVP": 0.954,
    "B2PLYP=FULL cc-pVDZ": 0.959,
    "B2PLYP=FULL cc-pVTZ": 0.956,
    "B2PLYP=FULL aug-cc-pVDZ": 0.962,
    "B2PLYP=FULL aug-cc-pVTZ": 0.959,
    "CID 3-21G": 0.932,
    "CID 3-21G*": 0.931,
    "CID 6-31G": 0.935,
    "CID 6-31G*": 0.924,
    "CID 6-31G**": 0.924,
    "CID 6-31+G**": 0.924,
    "CID 6-311G*": 0.929,
    "CID cc-pVDZ": 0.924,
    "CID cc-pVTZ": 0.927,
    "CISD 3-21G": 0.941,
    "CISD 3-21G*": 0.934,
    "CISD 6-31G": 0.938,
    "CISD 6-31G*": 0.926,
    "CISD 6-31G**": 0.918,
    "CISD 6-31+G**": 0.922,
    "CISD 6-311G*": 0.925,
    "CISD cc-pVDZ": 0.922,
    "CISD cc-pVTZ": 0.93,
    "QCISD 3-21G": 0.969,
    "QCISD 3-21G*": 0.961,
    "QCISD 6-31G": 0.964,
    "QCISD 6-31G*": 0.952,
    "QCISD 6-31G**": 0.941,
    "QCISD 6-31+G**": 0.945,
    "QCISD 6-311G*": 0.957,
    "QCISD 6-311G**": 0.954,
    "QCISD TZVP": 0.955,
    "QCISD cc-pVDZ": 0.959,
    "QCISD cc-pVTZ": 0.956,
    "QCISD aug-cc-pVDZ": 0.969,
    "QCISD aug-cc-pVTZ": 0.962,
    "CCD 3-21G": 0.972,
    "CCD 3-21G*": 0.957,
    "CCD 6-31G": 0.96,
    "CCD 6-31G*": 0.947,
    "CCD 6-31G**": 0.938,
    "CCD 6-31+G**": 0.942,
    "CCD 6-311G*": 0.955,
    "CCD 6-311G**": 0.955,
    "CCD TZVP": 0.948,
    "CCD cc-pVDZ": 0.957,
    "CCD cc-pVTZ": 0.934,
    "CCD aug-cc-pVDZ": 0.965,
    "CCD aug-cc-pVTZ": 0.957,
    "CCSD 3-21G": 0.943,
    "CCSD 3-21G*": 0.943,
    "CCSD 6-31G": 0.943,
    "CCSD 6-31G*": 0.944,
    "CCSD 6-31G**": 0.933,
    "CCSD 6-31+G**": 0.934,
    "CCSD 6-311G*": 0.954,
    "CCSD TZVP": 0.954,
    "CCSD cc-pVDZ": 0.947,
    "CCSD cc-pVTZ": 0.941,
    "CCSD cc-pVQZ": 0.951,
    "CCSD aug-cc-pVDZ": 0.963,
    "CCSD aug-cc-pVTZ": 0.956,
    "CCSD aug-cc-pVQZ": 0.953,
    "CCSD=FULL 6-31G*": 0.95,
    "CCSD=FULL TZVP": 0.948,
    "CCSD=FULL cc-pVTZ": 0.948,
    "CCSD=FULL aug-cc-pVTZ": 0.951,
}

element_list = [
    ["1 ", "H ", "Hydrogen"],
    ["2 ", "He", "Helium"],
    ["3 ", "Li", "Lithium"],
    ["4 ", "Be", "Beryllium"],
    ["5 ", "B ", "Boron"],
    ["6 ", "C ", "Carbon"],
    ["7 ", "N ", "Nitrogen"],
    ["8 ", "O ", "Oxygen"],
    ["9 ", "F ", "Fluorine"],
    ["10", "Ne", "Neon"],
    ["11", "Na", "Sodium"],
    ["12", "Mg", "Magnesium"],
    ["13", "Al", "Aluminum"],
    ["14", "Si", "Silicon"],
    ["15", "P ", "Phosphorus"],
    ["16", "S ", "Sulfur"],
    ["17", "Cl", "Chlorine"],
    ["18", "Ar", "Argon"],
    ["19", "K ", "Potassium"],
    ["20", "Ca", "Calcium"],
    ["21", "Sc", "Scandium"],
    ["22", "Ti", "Titanium"],
    ["23", "V ", "Vanadium"],
    ["24", "Cr", "Chromium"],
    ["25", "Mn", "Manganese"],
    ["26", "Fe", "Iron"],
    ["27", "Co", "Cobalt"],
    ["28", "Ni", "Nickel"],
    ["29", "Cu", "Copper"],
    ["30", "Zn", "Zinc"],
    ["31", "Ga", "Gallium"],
    ["32", "Ge", "Germanium"],
    ["33", "As", "Arsenic"],
    ["34", "Se", "Selenium"],
    ["35", "Br", "Bromine"],
    ["36", "Kr", "Krypton"],
    ["37", "Rb", "Rubidium"],
    ["38", "Sr", "Strontium"],
    ["39", "Y ", "Yttrium"],
    ["40", "Zr", "Zirconium"],
    ["41", "Nb", "Niobium"],
    ["42", "Mo", "Molybdenum"],
    ["43", "Tc", "Technetium"],
    ["44", "Ru", "Ruthenium"],
    ["45", "Rh", "Rhodium"],
    ["46", "Pd", "Palladium"],
    ["47", "Ag", "Silver"],
    ["48", "Cd", "Cadmium"],
    ["49", "In", "Indium"],
    ["50", "Sn", "Tin"],
    ["51", "Sb", "Antimony"],
    ["52", "Te", "Tellurium"],
    ["53", "I ", "Iodine"],
    ["54", "Xe", "Xenon"],
    ["55", "Cs", "Cesium"],
    ["56", "Ba", "Barium"],
    ["57", "La", "Lanthanum"],
    ["58", "Ce", "Cerium"],
    ["59", "Pr", "Praseodymium"],
    ["60", "Nd", "Neodymium"],
    ["61", "Pm", "Promethium"],
    ["62", "Sm", "Samarium"],
    ["63", "Eu", "Europium"],
    ["64", "Gd", "Gadolinium"],
    ["65", "Tb", "Terbium"],
    ["66", "Dy", "Dysprosium"],
    ["67", "Ho", "Holmium"],
    ["68", "Er", "Erbium"],
    ["69", "Tm", "Thulium"],
    ["70", "Yb", "Ytterbium"],
    ["71", "Lu", "Lutetium"],
    ["72", "Hf", "Hafnium"],
    ["73", "Ta", "Tantalum"],
    ["74", "W ", "Tungsten"],
    ["75", "Re", "Rhenium"],
    ["76", "Os", "Osmium"],
    ["77", "Ir", "Iridium"],
    ["78", "Pt", "Platinum"],
    ["79", "Au", "Gold"],
    ["80", "Hg", "Mercury"],
    ["81", "Tl", "Thallium"],
    ["82", "Pb", "Lead"],
    ["83", "Bi", "Bismuth"],
    ["84", "Po", "Polonium"],
    ["85", "At", "Astatine"],
    ["86", "Rn", "Radon"],
    ["87", "Fr", "Francium"],
    ["88", "Ra", "Radium"],
    ["89", "Ac", "Actinium"],
    ["90", "Th", "Thorium"],
    ["91", "Pa", "Protactinium"],
    ["92", "U ", "Uranium"],
    ["93", "Np", "Neptunium"],
    ["94", "Pu", "Plutonium"],
    ["95", "Am", "Americium"],
    ["96", "Cm", "Curium"],
    ["97", "Bk", "Berkelium"],
    ["98", "Cf", "Californium"],
    ["99", "Es", "Einsteinium"],
]


def get_vibrational_scaling(functional, basis_set):

    """
    Returns vibrational scaling factor given the functional
    and the basis set for the QM engine.

    Parameters
    ----------
    functional: str
        Functional

    basis_set: str
        Basis set

    Returns
    -------
    vib_scale: float
        Vibrational scaling factor corresponding to the given
        the basis_set and the functional.

    Examples
    --------
    >>> get_vibrational_scaling("QCISD", "6-311G*")
    0.957

    """
    vib_scale = method_basis_scale_dict.get(functional + " " + basis_set)
    return vib_scale


def unit_vector_N(u_BC, u_AB):

    """
    Calculates unit normal vector perpendicular to plane ABC.

    Parameters
    ----------
    u_BC : (.. , 1, 3) array
        Unit vector from atom B to atom C.

    u_AB : (..., 1, 3) array
        Unit vector from atom A to atom B.

    Returns
    -------
    u_N : (..., 1, 3) array
        Unit normal vector perpendicular to plane ABC.

    Examples
    --------
    >>> u_BC = [0.34040355, 0.62192853, 0.27011169]
    >>> u_AB = [0.28276792, 0.34232697, 0.02370306]
    >>> unit_vector_N(u_BC, u_AB)
    array([-0.65161629,  0.5726879 , -0.49741811])
    """
    cross_product = np.cross(u_BC, u_AB)
    norm_u_N = np.linalg.norm(cross_product)
    u_N = cross_product / norm_u_N
    return u_N


def delete_guest_angle_params(guest_qm_params_file="guest_qm_params.txt"):
    """
    
    """
    f_params = open(guest_qm_params_file, "r")
    lines_params = f_params.readlines()
    for i in range(len(lines_params)):
        if "Begin writing the Angle Parameters" in lines_params[i]:
            to_begin = int(i)
        if "Finish writing the Angle Parameters" in lines_params[i]:
            to_end = int(i)
    lines_selected = lines_params[:to_begin] + lines_params[to_end + 1 :]
    with open(guest_qm_params_file, "w") as f_:
        f_.write("".join(lines_selected))
    return


def remove_bad_angle_params(
        guest_qm_params_file="guest_qm_params.txt", angle=1.00, k_angle=500):
    with open(guest_qm_params_file, "r") as f_params:
        lines_params = f_params.readlines()
    for i in range(len(lines_params)):
        if "Begin writing the Angle Parameters" in lines_params[i]:
            to_begin = int(i)
        if "Finish writing the Angle Parameters" in lines_params[i]:
            to_end = int(i)
    angle_params = lines_params[to_begin + 1 : to_end]
    lines_to_omit = []
    for i in angle_params:
        if float(re.findall(r"[-+]?\d+[.]?\d*", i)[0]) < float(angle) or float(
            re.findall(r"[-+]?\d+[.]?\d*", i)[1]
        ) > float(k_angle):
            lines_to_omit.append(i)
    for b in lines_to_omit:
        lines_params.remove(b)
    with open(guest_qm_params_file, "w") as file:
        for j in lines_params:
            file.write(j)


def get_num_host_atoms(host_pdb):

    """
    Reads the host PDB file and returns the
    total number of atoms.
    """

    ppdb = PandasPdb()
    ppdb.read_pdb(host_pdb)
    no_host_atoms = ppdb.df["ATOM"].shape[0]
    return no_host_atoms


def change_names(inpcrd_file, prmtop_file, pdb_file):
    command = "cp -r " + inpcrd_file + " system_qmmmrebind.inpcrd"
    os.system(command)
    command = "cp -r " + prmtop_file + " system_qmmmrebind.prmtop"
    os.system(command)
    command = "cp -r " + pdb_file + " system_qmmmrebind.pdb"
    os.system(command)


def copy_file(source, destination):

    """
    Copies a file from a source to the destination.
    """
    shutil.copy(source, destination)


def get_openmm_energies(system_pdb, system_xml):

    """
    Returns decomposed OPENMM energies for the
    system.

    Parameters
    ----------
    system_pdb : str
        Input PDB file

    system_xml : str
        Forcefield file in XML format

    """

    pdb = simtk.openmm.app.PDBFile(system_pdb)
    ff_xml_file = open(system_xml, "r")
    system = simtk.openmm.XmlSerializer.deserialize(ff_xml_file.read())
    integrator = simtk.openmm.LangevinIntegrator(
        300 * simtk.unit.kelvin,
        1 / simtk.unit.picosecond,
        0.002 * simtk.unit.picoseconds,
    )
    simulation = simtk.openmm.app.Simulation(pdb.topology, system, integrator)
    simulation.context.setPositions(pdb.positions)
    state = simulation.context.getState(
        getEnergy=True, getParameters=True, getForces=True
    )
    force_group = []
    for i, force in enumerate(system.getForces()):
        force_group.append(force.__class__.__name__)
    forcegroups = {}
    for i in range(system.getNumForces()):
        force = system.getForce(i)
        force.setForceGroup(i)
        forcegroups[force] = i
    energies = {}
    for f, i in forcegroups.items():
        energies[f] = (
            simulation.context.getState(getEnergy=True, groups=2 ** i)
            .getPotentialEnergy()
            ._value
        )
    decomposed_energy = []
    for key, val in energies.items():
        decomposed_energy.append(val)
    df_energy_openmm = pd.DataFrame(
        list(zip(force_group, decomposed_energy)),
        columns=["Energy_term", "Energy_openmm_params"],
    )
    energy_values = [
        list(
            df_energy_openmm.loc[
                df_energy_openmm["Energy_term"] == "HarmonicBondForce"
            ].values[0]
        )[1],
        list(
            df_energy_openmm.loc[
                df_energy_openmm["Energy_term"] == "HarmonicAngleForce"
            ].values[0]
        )[1],
        list(
            df_energy_openmm.loc[
                df_energy_openmm["Energy_term"] == "PeriodicTorsionForce"
            ].values[0]
        )[1],
        list(
            df_energy_openmm.loc[
                df_energy_openmm["Energy_term"] == "NonbondedForce"
            ].values[0]
        )[1],
    ]
    energy_group = [
        "HarmonicBondForce",
        "HarmonicAngleForce",
        "PeriodicTorsionForce",
        "NonbondedForce",
    ]
    df_energy_open_mm = pd.DataFrame(
        list(zip(energy_group, energy_values)),
        columns=["Energy_term", "Energy_openmm_params"],
    )
    df_energy_open_mm = df_energy_open_mm.set_index("Energy_term")
    print(df_energy_open_mm)


def u_PA_from_angles(atom_A, atom_B, atom_C, coords):

    """
    Returns the vector in the plane A,B,C and perpendicular to AB.

    Parameters
    ----------
    atom_A : int
        Index of atom A (left, starting from 0).

    atom_B : int
        Index of atom B (center, starting from 0).

    atom_C : int
        Index of atom C (right, starting from 0).

    coords : (..., N, 3) array
        An array which contains the coordinates of all
        the N atoms.

    """
    diff_AB = coords[atom_B, :] - coords[atom_A, :]
    norm_diff_AB = np.linalg.norm(diff_AB)
    u_AB = diff_AB / norm_diff_AB
    diff_CB = coords[atom_B, :] - coords[atom_C, :]
    norm_diff_CB = np.linalg.norm(diff_CB)
    u_CB = diff_CB / norm_diff_CB
    u_N = unit_vector_N(u_CB, u_AB)
    u_PA = np.cross(u_N, u_AB)
    norm_PA = np.linalg.norm(u_PA)
    u_PA = u_PA / norm_PA
    return u_PA


def force_angle_constant(
    atom_A,
    atom_B,
    atom_C,
    bond_lengths,
    eigenvalues,
    eigenvectors,
    coords,
    scaling_1,
    scaling_2,
):

    """
    Calculates force constant according to Equation 14 of
    Seminario calculation paper; returns angle (in kcal/mol/rad^2)
    and equilibrium angle (in degrees).

    Parameters
    ----------
    atom_A : int
        Index of atom A (left, starting from 0).

    atom_B : int
        Index of atom B (center, starting from 0).

    atom_C : int
        Index of atom C (right, starting from 0).

    bond_lengths : (N, N) array
        An N * N array containing the bond lengths for
        all the possible pairs of atoms.

    eigenvalues : (N, N, 3) array
        A numpy array of shape (N, N, 3) containing
        eigenvalues of the hessian matrix, where N
        is the total number of atoms.

    eigenvectors : (3, 3, N, N) array
        A numpy array of shape (3, 3, N, N) containing
        eigenvectors of the hessian matrix.

    coords : (N, 3) array
        A numpy array of shape (N, 3) having the X, Y and Z
        coordinates of all N atoms.

    scaling_1 : float
        Factor to scale the projections of eigenvalues for AB.

    scaling_2 : float
        Factor to scale the projections of eigenvalues for BC.

    Returns
    -------
    k_theta : float
        Force angle constant calculated using modified
        seminario method.

    k_0 : float
        Equilibrium angle between AB and BC.

    """
    # Vectors along bonds calculated
    diff_AB = coords[atom_B, :] - coords[atom_A, :]
    norm_diff_AB = np.linalg.norm(diff_AB)
    u_AB = diff_AB / norm_diff_AB
    diff_CB = coords[atom_B, :] - coords[atom_C, :]
    norm_diff_CB = np.linalg.norm(diff_CB)
    u_CB = diff_CB / norm_diff_CB
    # Bond lengths and eigenvalues found
    bond_length_AB = bond_lengths[atom_A, atom_B]
    eigenvalues_AB = eigenvalues[atom_A, atom_B, :]
    eigenvectors_AB = eigenvectors[0:3, 0:3, atom_A, atom_B]
    bond_length_BC = bond_lengths[atom_B, atom_C]
    eigenvalues_CB = eigenvalues[atom_C, atom_B, :]
    eigenvectors_CB = eigenvectors[0:3, 0:3, atom_C, atom_B]
    # Normal vector to angle plane found
    u_N = unit_vector_N(u_CB, u_AB)
    u_PA = np.cross(u_N, u_AB)
    norm_u_PA = np.linalg.norm(u_PA)
    u_PA = u_PA / norm_u_PA
    u_PC = np.cross(u_CB, u_N)
    norm_u_PC = np.linalg.norm(u_PC)
    u_PC = u_PC / norm_u_PC
    sum_first = 0
    sum_second = 0
    # Projections of eigenvalues
    for i in range(0, 3):
        eig_AB_i = eigenvectors_AB[:, i]
        eig_BC_i = eigenvectors_CB[:, i]
        sum_first = sum_first + (
            eigenvalues_AB[i] * abs(dot_product(u_PA, eig_AB_i))
        )
        sum_second = sum_second + (
            eigenvalues_CB[i] * abs(dot_product(u_PC, eig_BC_i))
        )
    # Scaling due to additional angles - Modified Seminario Part
    sum_first = sum_first / scaling_1
    sum_second = sum_second / scaling_2
    # Added as two springs in series
    k_theta = (1 / ((bond_length_AB ** 2) * sum_first)) + (
        1 / ((bond_length_BC ** 2) * sum_second)
    )
    k_theta = 1 / k_theta
    k_theta = -k_theta  # Change to OPLS form
    k_theta = abs(k_theta * 0.5)  # Change to OPLS form
    # Equilibrium Angle
    theta_0 = math.degrees(math.acos(np.dot(u_AB, u_CB)))
    # If the vectors u_CB and u_AB are linearly dependent u_N cannot be defined.
    # This case is dealt with here :
    if abs(sum((u_CB) - (u_AB))) < 0.01 or (
        abs(sum((u_CB) - (u_AB))) > 1.99 and abs(sum((u_CB) - (u_AB))) < 2.01
    ):
        scaling_1 = 1
        scaling_2 = 1
        [k_theta, theta_0] = force_angle_constant_special_case(
            atom_A,
            atom_B,
            atom_C,
            bond_lengths,
            eigenvalues,
            eigenvectors,
            coords,
            scaling_1,
            scaling_2,
        )
    return k_theta, theta_0


def dot_product(u_PA, eig_AB):

    """
    Returns the dot product of two vectors.

    Parameters
    ----------
    u_PA : (..., 1, 3) array
        Unit vector perpendicular to AB and in the
        plane of A, B, C.

    eig_AB : (..., 3, 3) array
        Eigenvectors of the hessian matrix for
        the bond AB.

    """
    x = 0
    for i in range(0, 3):
        x = x + u_PA[i] * eig_AB[i].conjugate()
    return x


def force_angle_constant_special_case(
    atom_A,
    atom_B,
    atom_C,
    bond_lengths,
    eigenvalues,
    eigenvectors,
    coords,
    scaling_1,
    scaling_2,
):

    """
    Calculates force constant according to Equation 14
    of Seminario calculation paper when the vectors
    u_CB and u_AB are linearly dependent and u_N cannot
    be defined. It instead takes samples of u_N across a
    unit sphere for the calculation; returns angle
    (in kcal/mol/rad^2) and equilibrium angle in degrees.

    Parameters
    ----------
    atom_A : int
        Index of atom A (left, starting from 0).

    atom_B : int
        Index of atom B (center, starting from 0).

    atom_C : int
        Index of atom C (right, starting from 0).

    bond_lengths : (N, N) array
        An N * N array containing the bond lengths for
        all the possible pairs of atoms.

    eigenvalues : (N, N, 3) array
        A numpy array of shape (N, N, 3) containing
        eigenvalues of the  hessian matrix, where N
        is the total number of atoms.

    eigenvectors : (3, 3, N, N) array
        A numpy array of shape (3, 3, N, N) containing
        eigenvectors of the hessian matrix.

    coords : (N, 3) array
        A numpy array of shape (N, 3) having the X, Y,
        and Z coordinates of all N atoms.

    scaling_1 : float
        Factor to scale the projections of eigenvalues for AB.

    scaling_2 : float
        Factor to scale the projections of eigenvalues for BC.

    Returns
    -------
    k_theta : float
        Force angle constant calculated using modified
        seminario method.
    k_0 : float
        Equilibrium angle between AB and BC.

    """
    # Vectors along bonds calculated
    diff_AB = coords[atom_B, :] - coords[atom_A, :]
    norm_diff_AB = np.linalg.norm(diff_AB)
    u_AB = diff_AB / norm_diff_AB
    diff_CB = coords[atom_B, :] - coords[atom_C, :]
    norm_diff_CB = np.linalg.norm(diff_CB)
    u_CB = diff_CB / norm_diff_CB
    # Bond lengths and eigenvalues found
    bond_length_AB = bond_lengths[atom_A, atom_B]
    eigenvalues_AB = eigenvalues[atom_A, atom_B, :]
    eigenvectors_AB = eigenvectors[0:3, 0:3, atom_A, atom_B]
    bond_length_BC = bond_lengths[atom_B, atom_C]
    eigenvalues_CB = eigenvalues[atom_C, atom_B, :]
    eigenvectors_CB = eigenvectors[0:3, 0:3, atom_C, atom_B]
    k_theta_array = np.zeros((180, 360))
    # Find force constant with varying u_N (with vector uniformly
    # sampled across a sphere)
    for theta in range(0, 180):
        for phi in range(0, 360):
            r = 1
            u_N = [
                r
                * math.sin(math.radians(theta))
                * math.cos(math.radians(theta)),
                r
                * math.sin(math.radians(theta))
                * math.sin(math.radians(theta)),
                r * math.cos(math.radians(theta)),
            ]
            u_PA = np.cross(u_N, u_AB)
            u_PA = u_PA / np.linalg.norm(u_PA)
            u_PC = np.cross(u_CB, u_N)
            u_PC = u_PC / np.linalg.norm(u_PC)
            sum_first = 0
            sum_second = 0
            # Projections of eigenvalues
            for i in range(0, 3):
                eig_AB_i = eigenvectors_AB[:, i]
                eig_BC_i = eigenvectors_CB[:, i]
                sum_first = sum_first + (
                    eigenvalues_AB[i] * abs(dot_product(u_PA, eig_AB_i))
                )
                sum_second = sum_second + (
                    eigenvalues_CB[i] * abs(dot_product(u_PC, eig_BC_i))
                )
            # Added as two springs in series
            k_theta_ij = (1 / ((bond_length_AB ** 2) * sum_first)) + (
                1 / ((bond_length_BC ** 2) * sum_second)
            )
            k_theta_ij = 1 / k_theta_ij
            k_theta_ij = -k_theta_ij  # Change to OPLS form
            k_theta_ij = abs(k_theta_ij * 0.5)  # Change to OPLS form
            k_theta_array[theta, phi] = k_theta_ij
    # Removes cases where u_N was linearly dependent of u_CB or u_AB.
    # Force constant used is taken as the mean.
    k_theta = np.mean(np.mean(k_theta_array))
    # Equilibrium Angle independent of u_N
    theta_0 = math.degrees(math.cos(np.dot(u_AB, u_CB)))
    return k_theta, theta_0


def force_constant_bond(atom_A, atom_B, eigenvalues, eigenvectors, coords):

    """
    Calculates the bond force constant for the bonds in the
    molecule according to equation 10 of seminario paper,
    given the bond atoms' indices and the corresponding
    eigenvalues, eigenvectors and coordinates matrices.

    Parameters
    ----------
    atom_A : int
        Index of Atom A.

    atom_B : int
        Index of Atom B.

    eigenvalues : (N, N, 3) array
        A numpy array of shape (N, N, 3) containing eigenvalues
        of the hessian matrix, where N is the total number
        of atoms.

    eigenvectors : (3, 3, N, N) array
        A numpy array of shape (3, 3, N, N) containing the
        eigenvectors of the hessian matrix.

    coords : (N, 3) array
        A numpy array of shape (N, 3) having the X, Y, and
        Z  coordinates of all N atoms.

    Returns
    --------
    k_AB : float
        Bond Force Constant value for the bond with atoms A and B.

    """
    # Eigenvalues and eigenvectors calculated
    eigenvalues_AB = eigenvalues[atom_A, atom_B, :]
    eigenvectors_AB = eigenvectors[:, :, atom_A, atom_B]
    # Vector along bond
    diff_AB = np.array(coords[atom_B, :]) - np.array(coords[atom_A, :])
    norm_diff_AB = np.linalg.norm(diff_AB)
    unit_vectors_AB = diff_AB / norm_diff_AB
    k_AB = 0
    # Projections of eigenvalues
    for i in range(0, 3):
        dot_product = abs(np.dot(unit_vectors_AB, eigenvectors_AB[:, i]))
        k_AB = k_AB + (eigenvalues_AB[i] * dot_product)
    k_AB = -k_AB * 0.5  # Convert to OPLS form
    return k_AB


def u_PA_from_angles(atom_A, atom_B, atom_C, coords):

    """
    Returns the vector in the plane A,B,C and perpendicular to AB.

    Parameters
    ----------
    atom_A : int
        Index of atom A (left, starting from 0).

    atom_B : int
        Index of atom B (center, starting from 0).

    atom_C : int
        Index of atom C (right, starting from 0).

    coords : (..., N, 3) array
        An array containing the coordinates of all the N atoms.

    Returns
    -------
    u_PA : (..., 1, 3) array
        Unit vector perpendicular to AB and in the plane of A, B, C.

    """
    diff_AB = coords[atom_B, :] - coords[atom_A, :]
    norm_diff_AB = np.linalg.norm(diff_AB)
    u_AB = diff_AB / norm_diff_AB
    diff_CB = coords[atom_B, :] - coords[atom_C, :]
    norm_diff_CB = np.linalg.norm(diff_CB)
    u_CB = diff_CB / norm_diff_CB
    u_N = unit_vector_N(u_CB, u_AB)
    u_PA = np.cross(u_N, u_AB)
    norm_PA = np.linalg.norm(u_PA)
    u_PA = u_PA / norm_PA
    return u_PA


def reverse_list(lst):

    """
    Returns the reversed form of a given list.

    Parameters
    ----------
    lst : list
        Input list.

    Returns
    -------
    reversed_list : list
        Reversed input list.

    Examples
    --------
    >>> lst = [5, 4, 7, 2]
    >>> reverse_list(lst)
    [2, 7, 4, 5]

    """
    reversed_list = lst[::-1]
    return reversed_list


def uniq(input_):

    """
    Returns a list with only unique elements from a list
    containing duplicate / repeating elements.

    Parameters
    ----------
    input_ : list
        Input list.

    Returns
    -------
    output : list
        List with only unique elements.

    Examples
    --------
    >>> lst = [2, 4, 2, 9, 10, 35, 10]
    >>> uniq(lst)
    [2, 4, 9, 10, 35]

    """
    output = []
    for x in input_:
        if x not in output:
            output.append(x)
    return output


def search_in_file(file: str, word: str) -> list:

    """
    Search for the given string in file and return lines
    containing that string along with line numbers.

    Parameters
    ----------
    file : str
        Input file.

    word : str
        Search word.

    Returns
    -------
    list_of_results : list
        List of lists with each element representing the
        line number and the line contents.

    """
    line_number = 0
    list_of_results = []
    with open(file, "r") as f:
        for line in f:
            line_number += 1
            if word in line:
                list_of_results.append((line_number, line.rstrip()))
    return list_of_results


def list_to_dict(lst):

    """
    Converts an input list with mapped characters (every
    odd entry is the key of the dictionary and every
    even entry adjacent to the odd entry is its correponding
    value)  to a dictionary.

    Parameters
    ----------
    lst : list
        Input list.

    Returns
    -------
    res_dct : dict
        A dictionary with every element mapped with
        its successive element starting from index 0.

    Examples
    --------
    >>> lst = [5, 9, 3, 6, 2, 7]
    >>> list_to_dict(lst)
    {5: 9, 3: 6, 2: 7}

    """

    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct


def scale_list(list_):

    """
    Returns a scaled list with the minimum value
    subtracted from each element of the corresponding list.

    Parameters
    ----------
    list_ : list
        Input list.

    Returns
    -------
    scaled_list : list
        Scaled list.

    Examples
    --------
    >>> list_ = [6, 3, 5, 11, 3, 2, 8, 6]
    >>> scale_list(list_)
    [4, 1, 3, 9, 1, 0, 6, 4]

    """
    scaled_list = [i - min(list_) for i in list_]
    return scaled_list


def list_kJ_kcal(list_):

    """
    Convert the elements in the list from
    kiloJoules units to kiloCalories units.

    Parameters
    ----------
    list_ : list
        List with elements in units of kJ.

    Returns
    -------
    converted_list : list
        List with elements in units of kcal.

    Examples
    --------
    >>> list_ = [6, 3, 5]
    >>> list_kJ_kcal(list_)
    [1.4340344168260037, 0.7170172084130019, 1.1950286806883366]

    """
    converted_list = [i / 4.184 for i in list_]
    return converted_list


def list_hartree_kcal(list_):
    """
    Convert the elements in the list from
    hartree units to kiloCalories units.

    Parameters
    ----------
    list_ : list
        List with elements in units of hartree.

    Returns
    -------
    converted_list : list
        List with elements in units of kcal.

    Examples
    --------
    >>> list_ = [6, 3, 5]
    >>> list_hartree_kcal(list_)
    [3765.0564000000004, 1882.5282000000002, 3137.547]

    """
    converted_list = [i * 627.5094 for i in list_]
    return converted_list


def torsiondrive_input_to_xyz(psi_input_file, xyz_file):

    """
    Returns an xyz file from a torsiondrive formatted
    input file.

    Parameters
    ----------
    psi_input_file : str
        Input file for the psi4 QM engine.

    xyz_file : str
        XYZ format file to write the coords of the system.

    """
    with open(psi_input_file, "r") as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if "molecule {" in lines[i]:
            to_begin = int(i)
        if "set {" in lines[i]:
            to_end = int(i)
    xyz_lines = lines[to_begin + 2 : to_end - 1]
    with open(xyz_file, "w") as f:
        f.write(str(len(xyz_lines)) + "\n")
        f.write(xyz_file + "\n")
        for i in xyz_lines:
            f.write(i)


def xyz_to_pdb(xyz_file, coords_file, template_pdb, system_pdb):
    """
    Converts a XYZ file to a PDB file.

    Parameters
    ----------
    xyz_file : str
        XYZ file containing the coordinates of the system.

    coords_file : str
        A text file containing the coordinates part of XYZ file.

    template_pdb : str
        A pdb file to be used as a template for the required PDB.

    system_pdb : str
        Output PDB file with the coordinates updated in the
        template pdb using XYZ file.

    """
    with open(xyz_file, "r") as f:
        lines = f.readlines()
    needed_lines = lines[2:]
    with open(coords_file, "w") as f:
        for i in needed_lines:
            f.write(i)
    df = pd.read_csv(coords_file, header=None, delimiter=r"\s+")
    df.columns = ["atom", "x", "y", "z"]
    ppdb = PandasPdb()
    ppdb.read_pdb(template_pdb)
    ppdb.df["ATOM"]["x_coord"] = df["x"]
    ppdb.df["ATOM"]["y_coord"] = df["y"]
    ppdb.df["ATOM"]["z_coord"] = df["z"]
    ppdb.to_pdb(system_pdb)


def generate_xml_from_pdb_sdf(system_pdb, system_sdf, system_xml):
    """
    Generates an openforcefield xml file from the pdb file.

    Parameters
    ----------
    system_pdb : str
        Input PDB file.

    system_sdf : str
        SDF file of the system.

    system_xml : str
        XML force field file generated using PDB and SDF files.

    """
    # command = "babel -ipdb " + system_pdb + " -osdf " + system_sdf
    command = "obabel -ipdb " + system_pdb + " -osdf -O " + system_sdf
    os.system(command)
    # off_molecule = openforcefield.topology.Molecule(system_sdf)
    off_molecule = Molecule(system_sdf)
    # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
    force_field = ForceField("openff_unconstrained-1.0.0.offxml")
    system = force_field.create_openmm_system(off_molecule.to_topology())
    pdbfile = simtk.openmm.app.PDBFile(system_pdb)
    structure = parmed.openmm.load_topology(
        pdbfile.topology, system, xyz=pdbfile.positions
    )
    with open(system_xml, "w") as f:
        f.write(simtk.openmm.XmlSerializer.serialize(system))


def generate_xml_from_charged_pdb_sdf(
    system_pdb,
    system_init_sdf,
    system_sdf,
    num_charge_atoms,
    index_charge_atom_1,
    charge_atom_1,
    system_xml,
):
    """
    Generates an openforcefield xml file from the pdb
    file via SDF file and openforcefield.

    Parameters
    ----------
    system_pdb : str
        Input PDB file.

    system_init_sdf : str
        SDF file for the system excluding charge information.

    system_sdf : str
        SDF file of the system.

    num_charge_atoms : int
        Total number of charged atoms in the PDB.

    index_charge_atom_1 : int
        Index of the first charged atom.

    charge_atom_1 : float
        Charge on first charged atom.
    system_xml : str
        XML force field file generated using PDB and SDF files.

    """
    # command = "babel -ipdb " + system_pdb + " -osdf " + system_init_sdf
    command = "obabel -ipdb " + system_pdb + " -osdf -O " + system_init_sdf
    os.system(command)
    with open(system_init_sdf, "r") as f1:
        filedata = f1.readlines()
        filedata = filedata[:-2]
    with open(system_sdf, "w+") as out:
        for i in filedata:
            out.write(i)
        line_1 = (
            "M  CHG  "
            + str(num_charge_atoms)
            + "   "
            + str(index_charge_atom_1)
            + "   "
            + str(charge_atom_1)
            + "\n"
        )
        line_2 = "M  END" + "\n"
        line_3 = "$$$$"
        out.write(line_1)
        out.write(line_2)
        out.write(line_3)
    # off_molecule = openforcefield.topology.Molecule(system_sdf)
    off_molecule = Molecule(system_sdf)
    # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
    force_field = ForceField("openff_unconstrained-1.0.0.offxml")
    system = force_field.create_openmm_system(off_molecule.to_topology())
    pdbfile = simtk.openmm.app.PDBFile(system_pdb)
    structure = parmed.openmm.load_topology(
        pdbfile.topology, system, xyz=pdbfile.positions
    )
    with open(system_xml, "w") as f:
        f.write(simtk.openmm.XmlSerializer.serialize(system))


def get_dihedrals(qm_scan_file):

    """
    Returns dihedrals from the torsiondrive scan file.

    Parameters
    ----------
    qm_scan_file : str
        Output scan file containing torsiondrive scans.

    Returns
    -------
    dihedrals : list
        List of all the dihedral values from the qm scan file.

    """
    with open(qm_scan_file, "r") as f:
        lines = f.readlines()
    energy_dihedral_lines = []
    for i in range(len(lines)):
        if "Dihedral" in lines[i]:
            energy_dihedral_lines.append(lines[i])
    dihedrals = []
    for i in energy_dihedral_lines:
        energy_dihedral = i
        energy_dihedral = re.findall(r"[-+]?\d+[.]?\d*", energy_dihedral)
        dihedral = float(energy_dihedral[0])
        dihedrals.append(dihedral)
    return dihedrals


def get_qm_energies(qm_scan_file):

    """
    Returns QM optimized energies from the torsiondrive
    scan file.

    Parameters
    ----------
    qm_scan_file : str
        Output scan file containing torsiondrive scans.

    Returns
    -------
    qm_energies : list
        List of all the qm optimiseed energies extracted from the torsiondrive
        scan file.
    """
    with open(qm_scan_file, "r") as f:
        lines = f.readlines()
    energy_dihedral_lines = []
    for i in range(len(lines)):
        if "Dihedral" in lines[i]:
            energy_dihedral_lines.append(lines[i])
    qm_energies = []
    for i in energy_dihedral_lines:
        energy_dihedral = i
        energy_dihedral = re.findall(r"[-+]?\d+[.]?\d*", energy_dihedral)
        energy = float(energy_dihedral[1])
        qm_energies.append(energy)
    return qm_energies


def generate_mm_pdbs(qm_scan_file, template_pdb):

    """
    Generate PDBs from the torsiondrive scan file
    based on a template PDB.

    """
    with open(qm_scan_file, "r") as f:
        lines = f.readlines()
    energy_dihedral_lines = []
    for i in range(len(lines)):
        if "Dihedral" in lines[i]:
            energy_dihedral_lines.append(lines[i])
    dihedrals = []
    for i in energy_dihedral_lines:
        energy_dihedral = i
        energy_dihedral = re.findall(r"[-+]?\d+[.]?\d*", energy_dihedral)
        dihedral = float(energy_dihedral[0])
        dihedrals.append(dihedral)
    lines_markers = []
    for i in range(len(lines)):
        if "Dihedral" in lines[i]:
            lines_markers.append(i)
    lines_markers.append(len(lines) + 1)
    for i in range(len(lines_markers) - 1):
        # pdb_file_to_write = str(dihedrals[i]) + ".pdb"
        if dihedrals[i] > 0:
            pdb_file_to_write = "plus_" + str(abs(dihedrals[i])) + ".pdb"
        if dihedrals[i] < 0:
            pdb_file_to_write = "minus_" + str(abs(dihedrals[i])) + ".pdb"
        to_begin = lines_markers[i]
        to_end = lines_markers[i + 1]
        lines_to_write = lines[to_begin + 1 : to_end - 1]
        x_coords = []
        y_coords = []
        z_coords = []
        for i in lines_to_write:
            coordinates = i
            coordinates = re.findall(r"[-+]?\d+[.]?\d*", coordinates)
            x = float(coordinates[0])
            y = float(coordinates[1])
            z = float(coordinates[2])
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
        ppdb = PandasPdb()
        ppdb.read_pdb(template_pdb)
        ppdb.df["ATOM"]["x_coord"] = x_coords
        ppdb.df["ATOM"]["y_coord"] = y_coords
        ppdb.df["ATOM"]["z_coord"] = z_coords
        ppdb.to_pdb(pdb_file_to_write)


def remove_mm_files(qm_scan_file):
    """
    Delete all generated PDB files.

    Parameters
    ----------
    qm_scan_file : str
        Output scan file containing torsiondrive scans.

    """
    mm_pdb_list = []
    for i in get_dihedrals(qm_scan_file):
        if i > 0:
            pdb_file = "plus_" + str(abs(i)) + ".pdb"
        if i < 0:
            pdb_file = "minus_" + str(abs(i)) + ".pdb"
        mm_pdb_list.append(pdb_file)
    for i in mm_pdb_list:
        command = "rm -rf  " + i
        os.system(command)
        command = "rm -rf  " + i[:-4] + ".inpcrd"
        os.system(command)
        command = "rm -rf  " + i[:-4] + ".prmtop"
        os.system(command)


def get_non_torsion_mm_energy(system_pdb, load_topology, system_xml):

    """
    Returns sum of all the non-torsional energies (that
    includes HarmonicBondForce, HarmonicAngleForce
    and NonBondedForce) of the system from the PDB
    file given the topology and the forcefield file.

    Parameters
    ----------
    system_pdb : str
        System PDB file to load the openmm system topology
        and coordinates.

    load_topology : {"openmm", "parmed"}
        Argument to specify how to load the topology.

    system_xml : str
        XML force field file for the openmm system.

    Returns
    -------
    Sum of all the non-torsional energies of the system.

    """
    system_prmtop = system_pdb[:-4] + ".prmtop"
    system_inpcrd = system_pdb[:-4] + ".inpcrd"
    if load_topology == "parmed":
        openmm_system = parmed.openmm.load_topology(
            parmed.load_file(system_pdb, structure=True).topology,
            parmed.load_file(system_xml),
        )
    if load_topology == "openmm":
        openmm_system = parmed.openmm.load_topology(
            simtk.openmm.app.PDBFile(system_pdb).topology,
            parmed.load_file(system_xml),
        )
    openmm_system.save(system_prmtop, overwrite=True)
    openmm_system.coordinates = parmed.load_file(
        system_pdb, structure=True
    ).coordinates
    openmm_system.save(system_inpcrd, overwrite=True)
    parm = parmed.load_file(system_prmtop, system_inpcrd)
    prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
        parm, parm.createSystem()
    )
    # print(prmtop_energy_decomposition)
    prmtop_energy_decomposition_value_no_torsion = [
        list_to_dict(
            [
                item
                for sublist in [
                    list(elem) for elem in prmtop_energy_decomposition
                ]
                for item in sublist
            ]
        ).get("HarmonicBondForce"),
        list_to_dict(
            [
                item
                for sublist in [
                    list(elem) for elem in prmtop_energy_decomposition
                ]
                for item in sublist
            ]
        ).get("HarmonicAngleForce"),
        list_to_dict(
            [
                item
                for sublist in [
                    list(elem) for elem in prmtop_energy_decomposition
                ]
                for item in sublist
            ]
        ).get("NonbondedForce"),
    ]
    return sum(prmtop_energy_decomposition_value_no_torsion)


def get_mm_potential_energies(qm_scan_file, load_topology, system_xml):

    """
    Returns potential energy of the system from the PDB file
    given the topology and the forcefield file.

    Parameters
    ----------
    qm_scan_file : str
        Output scan file containing torsiondrive scans.

    load_topology : {"openmm", "parmed"}
        Argument to spcify how to load the topology.

    system_xml : str
        XML file to load the openmm system.

    Returns
    -------
    mm_potential_energies : list
        List of all the non torsion mm energies for the
        generated PDB files.

    """
    mm_pdb_list = []
    for i in get_dihedrals(qm_scan_file):
        if i > 0:
            pdb_file = "plus_" + str(abs(i)) + ".pdb"
        if i < 0:
            pdb_file = "minus_" + str(abs(i)) + ".pdb"
        mm_pdb_list.append(pdb_file)
    for i in mm_pdb_list:
        mm_pdb_file = i
    mm_potential_energies = []
    for i in mm_pdb_list:
        mm_pdb_file = i
        mm_energy = get_non_torsion_mm_energy(
            system_pdb=i, load_topology=load_topology, system_xml=system_xml,
        )
        mm_potential_energies.append(mm_energy)
    return mm_potential_energies


def list_diff(list_1, list_2):

    """
    Returns the difference between two lists as a list.

    Parameters
    ----------
    list_1 : list
        First list

    list_2 : list
        Second list.

    Returns
    -------
    diff_list : list
        List containing the diferences between the elements of
        the two lists.
    Examples
    --------
    >>> list_1 = [4, 2, 8, 3, 0, 6, 7]
    >>> list_2 = [5, 3, 1, 5, 6, 0, 4]
    >>> list_diff(list_1, list_2)
    [-1, -1, 7, -2, -6, 6, 3]

    """
    diff_list = []
    zipped_list = zip(list_1, list_2)
    for list1_i, list2_i in zipped_list:
        diff_list.append(list1_i - list2_i)
    return diff_list


def dihedral_energy(x, k1, k2, k3, k4=0):
    """
    Expression for the dihedral energy.
    """
    energy_1 = k1 * (1 + np.cos(1 * x * 0.01745))
    energy_2 = k2 * (1 - np.cos(2 * x * 0.01745))
    energy_3 = k3 * (1 + np.cos(3 * x * 0.01745))
    energy_4 = k4 * (1 - np.cos(4 * x * 0.01745))
    dihedral_energy = energy_1 + energy_2 + energy_3 + energy_4
    return dihedral_energy


def error_function(delta_qm, delta_mm):
    """
    Root Mean Squared Error.
    """
    squared_error = np.square(np.subtract(delta_qm, delta_mm))
    mean_squared_error = squared_error.mean()
    root_mean_squared_error = math.sqrt(mean_squared_error)
    return root_mean_squared_error


def error_function_boltzmann(delta_qm, delta_mm, T):
    """
    Boltzmann Root Mean Squared Error.
    """
    kb = 3.297623483 * 10 ** (-24)  # in cal/K
    delta_qm_boltzmann_weighted = [np.exp(-i / (kb * T)) for i in delta_qm]
    squared_error = (
        np.square(np.subtract(delta_qm, delta_mm))
        * delta_qm_boltzmann_weighted
    )
    mean_squared_error = squared_error.mean()
    root_mean_squared_error = math.sqrt(mean_squared_error)
    return root_mean_squared_error


def gen_init_guess(qm_scan_file, load_topology, system_xml):

    """
    Initial guess for the torsional parameter.

    Parameters
    ----------
    qm_scan_file : str
        Output scan file containing torsiondrive scans.

    load_topology : {"openmm", "parmed"}
        Argument to speify how to load the topology.

    system_xml : str
        XML force field file for the system.

    Returns
    -------
    k_init_guess : list
        Initial guess for the torsional parameters.

    """
    x = get_dihedrals(qm_scan_file)
    y = scale_list(
        list_=get_mm_potential_energies(
            qm_scan_file=qm_scan_file,
            load_topology=load_topology,
            system_xml=system_xml,
        )
    )
    init_vals = [0.0, 0.0, 0.0, 0.0]
    k_init_guess, covar = scipy.optimize.curve_fit(
        dihedral_energy, x, y, p0=init_vals
    )
    for i in range(len(k_init_guess)):
        if k_init_guess[i] < 0:
            k_init_guess[i] = 0
    return k_init_guess


def objective_function(k_array, x, delta_qm):
    """
    Objective function for the torsional parameter fitting.
    """
    delta_mm = dihedral_energy(
        x, k1=k_array[0], k2=k_array[1], k3=k_array[2], k4=k_array[3]
    )
    loss_function = error_function(delta_qm, delta_mm)
    return loss_function


def fit_params(qm_scan_file, load_topology, system_xml, method):
    """
    Optimization of the objective function.
    """
    k_guess = gen_init_guess(
        qm_scan_file=qm_scan_file,
        load_topology=load_topology,
        system_xml=system_xml,
    )
    x_data = np.array(get_dihedrals(qm_scan_file))
    delta_qm = np.array(
        scale_list(list_hartree_kcal(list_=get_qm_energies(qm_scan_file)))
    )
    optimise = scipy.optimize.minimize(
        objective_function,
        k_guess,
        args=(x_data, delta_qm),
        method=method,
        bounds=[(0.00, None), (0.00, None), (0.00, None), (0.00, None),],
    )
    return optimise.x


def get_tor_params(
    qm_scan_file, template_pdb, load_topology, system_xml, method
):
    """
    Returns the fitted torsional parameters.
    """
    qm_e = get_qm_energies(qm_scan_file=qm_scan_file)
    qm_e_kcal = list_hartree_kcal(qm_e)
    delta_qm = scale_list(qm_e_kcal)
    generate_mm_pdbs(qm_scan_file=qm_scan_file, template_pdb=template_pdb)
    mm_pe_no_torsion_kcal = get_mm_potential_energies(
        qm_scan_file=qm_scan_file,
        load_topology=load_topology,
        system_xml=system_xml,
    )
    delta_mm = scale_list(mm_pe_no_torsion_kcal)
    opt_param = fit_params(
        qm_scan_file=qm_scan_file,
        load_topology=load_topology,
        system_xml=system_xml,
        method=method,
    )
    return opt_param


def get_torsional_lines(
    template_pdb,
    system_xml,
    qm_scan_file,
    load_topology,
    method,
    dihedral_text_file,
):
    """
    Returns the torsional lines for the XML forcefield file.
    """
    opt_param = get_tor_params(
        qm_scan_file=qm_scan_file,
        template_pdb=template_pdb,
        load_topology=load_topology,
        system_xml=system_xml,
        method=method,
    )
    dihedral_text = open(dihedral_text_file, "r")
    dihedral_text_lines = dihedral_text.readlines()
    atom_numbers = dihedral_text_lines[-1]
    atom_index_from_1 = [
        int(re.findall(r"\d+", atom_numbers)[0]),
        int(re.findall(r"\d+", atom_numbers)[1]),
        int(re.findall(r"\d+", atom_numbers)[2]),
        int(re.findall(r"\d+", atom_numbers)[3]),
    ]
    atom_index = [i - 1 for i in atom_index_from_1]
    atom_index_lines = (
        " "
        + "p1="
        + '"'
        + str(atom_index[0])
        + '"'
        + " "
        + "p2="
        + '"'
        + str(atom_index[1])
        + '"'
        + " "
        + "p3="
        + '"'
        + str(atom_index[2])
        + '"'
        + " "
        + "p4="
        + '"'
        + str(atom_index[3])
        + '"'
        + " "
    )
    tor_lines = []
    for i in range(len(opt_param)):
        line_to_append = (
            "                "
            + "<Torsion "
            + "k="
            + '"'
            + str(round(opt_param[i], 8))
            + '"'
            + atom_index_lines
            + "periodicity="
            + '"'
            + str(i + 1)
            + '"'
            + " "
            + "phase="
            + '"'
            + "0"
            + '"'
            + "/>"
        )
        # print(line_to_append)
        tor_lines.append(line_to_append)
    return tor_lines


def singular_resid(pdbfile, qmmmrebind_init_file):

    """
    Returns a PDB file with chain ID = A

    Parameters
    ----------
    pdbfile: str
        Input PDB file

    qmmmrebind_init_file: str
        Output PDB file

    """

    ppdb = PandasPdb().read_pdb(pdbfile)
    ppdb.df["HETATM"]["chain_id"] = "A"
    ppdb.df["ATOM"]["chain_id"] = "A"
    ppdb.to_pdb(
        path=qmmmrebind_init_file, records=None, gz=False, append_newline=True
    )


def relax_init_structure(
    pdbfile,
    prmtopfile,
    qmmmrebindpdb,
    sim_output="output.pdb",
    sim_steps=100000,
):

    """
    Minimizing the initial PDB file with the given topology
    file

    Parameters
    ----------
    pdbfile: str
        Input PDB file.

    prmtopfile : str
        Input prmtop file.

    qmmmrebind_init_file: str
        Output PDB file.

    sim_output: str
        Simulation output trajectory file.

    sim_steps: int
        MD simulation steps.

    """

    prmtop = simtk.openmm.app.AmberPrmtopFile(prmtopfile)
    pdb = simtk.openmm.app.PDBFile(pdbfile)
    system = prmtop.createSystem(
        nonbondedMethod=simtk.openmm.app.PME,
        nonbondedCutoff=1 * simtk.unit.nanometer,
        constraints=simtk.openmm.app.HBonds,
    )
    integrator = simtk.openmm.LangevinIntegrator(
        300 * simtk.unit.kelvin,
        1 / simtk.unit.picosecond,
        0.002 * simtk.unit.picoseconds,
    )
    simulation = simtk.openmm.app.Simulation(
        prmtop.topology, system, integrator
    )
    simulation.context.setPositions(pdb.positions)
    print(simulation.context.getState(getEnergy=True).getPotentialEnergy())
    simulation.minimizeEnergy(maxIterations=10000000)
    print(simulation.context.getState(getEnergy=True).getPotentialEnergy())
    simulation.reporters.append(
        simtk.openmm.app.PDBReporter(sim_output, int(sim_steps / 10))
    )
    simulation.reporters.append(
        simtk.openmm.app.StateDataReporter(
            stdout,
            int(sim_steps / 10),
            step=True,
            potentialEnergy=True,
            temperature=True,
        )
    )
    simulation.reporters.append(
        simtk.openmm.app.PDBReporter(qmmmrebindpdb, sim_steps)
    )
    simulation.step(sim_steps)
    command = "rm -rf " + sim_output
    os.system(command)


def truncate(x):

    """
    Returns a float or an integer with an exact number
    of characters.

    Parameters
    ----------
    x: str
       input value

    """
    if len(str(int(float(x)))) == 1:
        x = format(x, ".8f")
    if len(str(int(float(x)))) == 2:
        x = format(x, ".7f")
    if len(str(int(float(x)))) == 3:
        x = format(x, ".6f")
    if len(str(int(float(x)))) == 4:
        x = format(x, ".5f")
    if len(str(x)) > 10:
        x = round(x, 10)
    return x


def add_vectors_inpcrd(pdbfile, inpcrdfile):

    """
    Adds periodic box dimensions to the inpcrd file

    Parameters
    ----------
    pdbfile: str
       PDB file containing the periodic box information.

    inpcrdfile: str
       Input coordinate file.

    """

    pdbfilelines = open(pdbfile, "r").readlines()
    for i in pdbfilelines:
        if "CRYST" in i:
            vector_list = re.findall(r"[-+]?\d*\.\d+|\d+", i)
            vector_list = [float(i) for i in vector_list]
            vector_list = vector_list[1 : 1 + 6]
            line_to_add = (
                "  "
                + truncate(vector_list[0])
                + "  "
                + truncate(vector_list[1])
                + "  "
                + truncate(vector_list[2])
                + "  "
                + truncate(vector_list[3])
                + "  "
                + truncate(vector_list[4])
                + "  "
                + truncate(vector_list[5])
            )
            print(line_to_add)
    with open(inpcrdfile, "a+") as f:
        f.write(line_to_add)


def add_dim_prmtop(pdbfile, prmtopfile):

    """
    Adds periodic box dimensions flag in the prmtop file.

    Parameters
    ----------
    prmtopfile: str
       Input prmtop file.

    pdbfile: str
       PDB file containing the periodic box information.

    """
    pdbfilelines = open(pdbfile, "r").readlines()
    for i in pdbfilelines:
        if "CRYST" in i:
            vector_list = re.findall(r"[-+]?\d*\.\d+|\d+", i)
            vector_list = [float(i) for i in vector_list]
            vector_list = vector_list[1 : 1 + 6]
            vector_list = [i / 10 for i in vector_list]
            vector_list = [truncate(i) for i in vector_list]
            vector_list = [i + "E+01" for i in vector_list]
            line3 = (
                "  "
                + vector_list[3]
                + "  "
                + vector_list[0]
                + "  "
                + vector_list[1]
                + "  "
                + vector_list[2]
            )
            print(line3)
    line1 = "%FLAG BOX_DIMENSIONS"
    line2 = "%FORMAT(5E16.8)"
    with open(prmtopfile) as f1, open("intermediate.prmtop", "w") as f2:
        for line in f1:
            if line.startswith("%FLAG RADIUS_SET"):
                line = line1 + "\n" + line2 + "\n" + line3 + "\n" + line
            f2.write(line)
    command = "rm -rf " + prmtopfile
    os.system(command)
    command = "mv  intermediate.prmtop " + prmtopfile
    os.system(command)


def add_period_prmtop(parm_file, ifbox):

    """
    Changes the value of IFBOX if needed for the prmtop / parm file.
    Set to 1 if standard periodic box and 2 when truncated octahedral.
    """
    with open(parm_file) as f:
        parm_lines = f.readlines()
    lines_contain = []
    for i in range(len(parm_lines)):
        if parm_lines[i].startswith("%FLAG POINTERS"):
            lines_contain.append(i + 4)
    line = parm_lines[lines_contain[0]]
    line_new = "%8s  %6s  %6s  %6s  %6s  %6s  %6s  %6s  %6s  %6s" % (
        re.findall(r"\d+", line)[0],
        re.findall(r"\d+", line)[1],
        re.findall(r"\d+", line)[2],
        re.findall(r"\d+", line)[3],
        re.findall(r"\d+", line)[4],
        re.findall(r"\d+", line)[5],
        re.findall(r"\d+", line)[6],
        str(ifbox),
        re.findall(r"\d+", line)[8],
        re.findall(r"\d+", line)[9],
    )
    parm_lines[lines_contain[0]] = line_new + "\n"
    with open(parm_file, "w") as f:
        for i in parm_lines:
            f.write(i)

def add_solvent_pointers_prmtop(non_reparams_file, reparams_file):

    """
    Adds the flag solvent pointers to the topology file.
    """
    f_non_params = open(non_reparams_file, "r")
    lines_non_params = f_non_params.readlines()
    for i in range(len(lines_non_params)):
        if "FLAG SOLVENT_POINTERS" in lines_non_params[i]:
            to_begin = int(i)
    solvent_pointers = lines_non_params[to_begin : to_begin + 3]
    file = open(reparams_file, "a") 
    for i in solvent_pointers:
        file.write(i)

def prmtop_calibration(
    prmtopfile="system_qmmmrebind.prmtop",
    inpcrdfile="system_qmmmrebind.inpcrd",
):

    """
    Standardizes the topology files

    Parameters
    ----------

    prmtopfile: str
       Input prmtop file.

    inpcrdfile: str
       Input coordinate file.

    """
    parm = parmed.load_file(prmtopfile, inpcrdfile)
    parm_1 = parmed.tools.actions.changeRadii(parm, "mbondi3")
    parm_1.execute()
    parm_2 = parmed.tools.actions.setMolecules(parm)
    parm_2.execute()
    parm.save(prmtopfile, overwrite=True)


def run_openmm_prmtop_inpcrd(
    pdbfile="system_qmmmrebind.pdb",
    prmtopfile="system_qmmmrebind.prmtop",
    inpcrdfile="system_qmmmrebind.inpcrd",
    sim_output="output.pdb",
    sim_steps=10000,
):

    """
    Runs OpenMM simulation with inpcrd and prmtop files.

    Parameters
    ----------
    pdbfile: str
       Input PDB file.

    prmtopfile: str
       Input prmtop file.

    inpcrdfile: str
       Input coordinate file.

    sim_output: str
       Output trajectory file.

    sim_steps: int
       Simulation steps.

    """

    prmtop = simtk.openmm.app.AmberPrmtopFile(prmtopfile)
    inpcrd = simtk.openmm.app.AmberInpcrdFile(inpcrdfile)
    system = prmtop.createSystem(
        nonbondedCutoff=1 * simtk.unit.nanometer,
        constraints=simtk.openmm.app.HBonds,
    )
    integrator = simtk.openmm.LangevinIntegrator(
        300 * simtk.unit.kelvin,
        1 / simtk.unit.picosecond,
        0.002 * simtk.unit.picoseconds,
    )
    simulation = simtk.openmm.app.Simulation(
        prmtop.topology, system, integrator
    )
    if inpcrd.boxVectors is None:
        add_vectors_inpcrd(
            pdbfile=pdbfile, inpcrdfile=inpcrdfile,
        )
    if inpcrd.boxVectors is not None:
        simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)
        print(inpcrd.boxVectors)
    simulation.context.setPositions(inpcrd.positions)
    print(simulation.context.getState(getEnergy=True).getPotentialEnergy())
    simulation.minimizeEnergy(maxIterations=1000000)
    print(simulation.context.getState(getEnergy=True).getPotentialEnergy())
    simulation.reporters.append(
        simtk.openmm.app.PDBReporter(sim_output, int(sim_steps / 10))
    )
    simulation.reporters.append(
        simtk.openmm.app.StateDataReporter(
            stdout,
            int(sim_steps / 10),
            step=True,
            potentialEnergy=True,
            temperature=True,
        )
    )
    simulation.step(sim_steps)


def run_openmm_prmtop_pdb(
    pdbfile="system_qmmmrebind.pdb",
    prmtopfile="system_qmmmrebind.prmtop",
    sim_output="output.pdb",
    sim_steps=10000,
):

    """
    Runs OpenMM simulation with pdb and prmtop files.

    Parameters
    ----------
    pdbfile: str
       Input PDB file.

    prmtopfile: str
       Input prmtop file.

    sim_output: str
       Output trajectory file.

    sim_steps: int
       Simulation steps.

    """
    prmtop = simtk.openmm.app.AmberPrmtopFile(prmtopfile)
    pdb = simtk.openmm.app.PDBFile(pdbfile)
    system = prmtop.createSystem(
        nonbondedCutoff=1 * simtk.unit.nanometer,
        constraints=simtk.openmm.app.HBonds,
    )
    integrator = simtk.openmm.LangevinIntegrator(
        300 * simtk.unit.kelvin,
        1 / simtk.unit.picosecond,
        0.002 * simtk.unit.picoseconds,
    )
    simulation = simtk.openmm.app.Simulation(
        prmtop.topology, system, integrator
    )
    simulation.context.setPositions(pdb.positions)
    print(simulation.context.getState(getEnergy=True).getPotentialEnergy())
    simulation.minimizeEnergy(maxIterations=1000000)
    print(simulation.context.getState(getEnergy=True).getPotentialEnergy())
    simulation.reporters.append(
        simtk.openmm.app.PDBReporter(sim_output, int(sim_steps / 10))
    )
    simulation.reporters.append(
        simtk.openmm.app.StateDataReporter(
            stdout,
            int(sim_steps / 10),
            step=True,
            potentialEnergy=True,
            temperature=True,
        )
    )
    simulation.step(sim_steps)


def move_qmmmmrebind_files(
    prmtopfile="system_qmmmrebind.prmtop",
    inpcrdfile="system_qmmmrebind.inpcrd",
    pdbfile="system_qmmmrebind.pdb",
):

    """
    Moves QMMMReBind generated topology and parameter files
    to a new directory .

    Parameters
    ----------
    prmtopfile: str
       QMMMReBind generated prmtop file.

    inpcrdfile: str
        QMMMReBind generated inpcrd file.

    pdbfile: str
        QMMMReBind generated PDB file.

    """
    current_pwd = os.getcwd()
    command = "rm -rf reparameterized_files"
    os.system(command)
    command = "mkdir reparameterized_files"
    os.system(command)
    shutil.copy(
        current_pwd + "/" + prmtopfile,
        current_pwd + "/" + "reparameterized_files" + "/" + prmtopfile,
    )
    shutil.copy(
        current_pwd + "/" + inpcrdfile,
        current_pwd + "/" + "reparameterized_files" + "/" + inpcrdfile,
    )
    shutil.copy(
        current_pwd + "/" + pdbfile,
        current_pwd + "/" + "reparameterized_files" + "/" + pdbfile,
    )


def move_qm_files():

    """
    Moves QM engine generated files to a new directory .

    """
    current_pwd = os.getcwd()
    command = "rm -rf qm_data"
    os.system(command)
    command = "mkdir qm_data"
    os.system(command)
    command = "cp -r " + "*.com* " + current_pwd + "/" + "qm_data"
    os.system(command)
    command = "cp -r " + "*.log* " + current_pwd + "/" + "qm_data"
    os.system(command)
    command = "cp -r " + "*.chk* " + current_pwd + "/" + "qm_data"
    os.system(command)
    command = "cp -r " + "*.fchk* " + current_pwd + "/" + "qm_data"
    os.system(command)


def move_qmmmrebind_files():

    """
    Moves all QMMMREBind files to a new directory.

    """
    current_pwd = os.getcwd()
    command = "rm -rf qmmmrebind_data"
    os.system(command)
    command = "mkdir qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.sdf* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.txt* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.pdb* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.xml* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.chk* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.fchk* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.com* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.log* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.inpcrd* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.prmtop* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.parm7* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.out* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*run_command* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.dat* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)
    command = "mv " + "*.xyz* " + current_pwd + "/" + "qmmmrebind_data"
    os.system(command)


class PrepareQMMM:

    """
    A class used to segregate the QM and MM regions.

    This class contain methods to remove the solvent, ions and all
    entities that are exclusive of receptor and the ligand. It also
    defines the Quantum Mechanical (QM) region and the Molecular
    Mechanical (MM) region based upon the distance of the ligand
    from the receptor and the chosen number of receptor residues. It
    is also assumed that the initial PDB file will have the receptor
    followed by the ligand.

    ...

    Attributes
    ----------
    init_pdb : str
        Initial PDB file containing the receptor-ligand complex with
        solvent, ions, etc.

    cleaned_pdb : str
        Formatted PDB file containing only the receptor and the ligand.

    guest_init_pdb : str
        A separate ligand PDB file with atom numbers not beginning from 1.

    host_pdb : str
        A separate receptor PDB file with atom numbers beginning from 1.

    guest_resname : str
        Three letter residue ID for the ligand.

    guest_pdb : str, optional
        Ligand PDB file with atom numbers beginning from 1.

    guest_xyz : str, optional
        A text file of the XYZ coordinates of the ligand.

    distance : float, optional
        The distance required to define the QM region of the receptor.
        This is the distance between the atoms of the ligand and the
        atoms of the receptor.

    residue_list : str, optional
        A text file of the residue numbers of the receptor within the
        proximity (as defined by the distance) from the ligand.

    host_qm_atoms : str, optional
        A text file of the atom numbers of the receptors in the QM
        region.

    host_mm_atoms : str, optional
        A text file of the atom numbers of the receptors in the MM
        region (all atoms except atoms in the QM region)

    host_qm_pdb : str, optional
        PDB file for the receptor's QM region.

    host_mm_pdb : str, optional
        PDB file for the receptor's MM region.

    qm_pdb : str, optional
        PDB file for the QM region (receptor's QM region and the
        ligand).

    mm_pdb : str, optional
        PDB file for the MM region.

    host_mm_region_I_atoms : str, optional
        A text file of the atom numbers of the receptors in the MM
        region preceeding the QM region.

    host_mm_region_II_atoms : str, optional
        A text file of the atom numbers of the receptors in the MM
        region following the QM region.

    host_mm_region_I_pdb : str, optional
        PDB file of the receptor in the MM region preceeding the
        QM region.

    host_mm_region_II_pdb : str, optional
        PDB file of the receptor in the MM region following the
        QM region.

    num_residues : int, optional
        Number of residues required in the QM region of the receptor.
    """

    def __init__(
        self,
        init_pdb,
        distance,
        num_residues,
        guest_resname,
        cleaned_pdb="system.pdb",
        guest_init_pdb="guest_init.pdb",
        host_pdb="host.pdb",
        guest_pdb="guest_init_II.pdb",
        guest_xyz="guest_coord.txt",
        residue_list="residue_list.txt",
        host_qm_atoms="host_qm.txt",
        host_mm_atoms="host_mm.txt",
        host_qm_pdb="host_qm.pdb",
        host_mm_pdb="host_mm.pdb",
        qm_pdb="qm.pdb",
        mm_pdb="mm.pdb",
        host_mm_region_I_atoms="host_mm_region_I.txt",
        host_mm_region_II_atoms="host_mm_region_II.txt",
        host_mm_region_I_pdb="host_mm_region_I.pdb",
        host_mm_region_II_pdb="host_mm_region_II.pdb",
    ):

        self.init_pdb = init_pdb
        self.distance = distance
        self.num_residues = num_residues
        self.guest_resname = guest_resname
        self.cleaned_pdb = cleaned_pdb
        self.guest_init_pdb = guest_init_pdb
        self.host_pdb = host_pdb
        self.guest_pdb = guest_pdb
        self.guest_xyz = guest_xyz
        self.residue_list = residue_list
        self.host_qm_atoms = host_qm_atoms
        self.host_mm_atoms = host_mm_atoms
        self.host_qm_pdb = host_qm_pdb
        self.host_mm_pdb = host_mm_pdb
        self.qm_pdb = qm_pdb
        self.mm_pdb = mm_pdb
        self.host_mm_region_I_atoms = host_mm_region_I_atoms
        self.host_mm_region_II_atoms = host_mm_region_II_atoms
        self.host_mm_region_I_pdb = host_mm_region_I_pdb
        self.host_mm_region_II_pdb = host_mm_region_II_pdb

    def clean_up(self):
        """
        Reads the given PDB file, removes all entities except the
        receptor and ligand and saves a new pdb file.
        """
        ions = [
            "Na+",
            "Cs+",
            "K+",
            "Li+",
            "Rb+",
            "Cl-",
            "Br-",
            "F-",
            "I-",
            "Ca2",
        ]
        intermediate_file_1 = self.cleaned_pdb[:-4] + "_intermediate_1.pdb"
        intermediate_file_2 = self.cleaned_pdb[:-4] + "_intermediate_2.pdb"
        command = (
            "pdb4amber -i "
            + self.init_pdb
            + " -o "
            + intermediate_file_1
            + " --noter --dry"
        )
        os.system(command)
        to_delete = (
            intermediate_file_1[:-4] + "_nonprot.pdb",
            intermediate_file_1[:-4] + "_renum.txt",
            intermediate_file_1[:-4] + "_sslink",
            intermediate_file_1[:-4] + "_water.pdb",
        )
        os.system("rm -rf " + " ".join(to_delete))
        with open(intermediate_file_1) as f1, open(
                intermediate_file_2, "w") as f2:
            for line in f1:
                if not any(ion in line for ion in ions):
                    f2.write(line)
        with open(intermediate_file_2, "r") as f1:
            filedata = f1.read()
        filedata = filedata.replace("HETATM", "ATOM  ")
        with open(self.cleaned_pdb, "w") as f2:
            f2.write(filedata)
        command = "rm -rf " + intermediate_file_1 + " " + intermediate_file_2
        os.system(command)

    def create_host_guest(self):
        """
        Saves separate receptor and ligand PDB files.
        """
        with open(self.cleaned_pdb) as f1, open(self.host_pdb, "w") as f2:
            for line in f1:
                if not self.guest_resname in line and not "CRYST1" in line:
                    f2.write(line)
        with open(self.cleaned_pdb) as f1, open(
            self.guest_init_pdb, "w"
        ) as f2:
            for line in f1:
                if self.guest_resname in line or "END" in line:
                    f2.write(line)

    def realign_guest(self):
        """
        Saves a ligand PDB file with atom numbers beginning from 1.
        """
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_init_pdb)
        to_subtract = min(ppdb.df["ATOM"]["atom_number"]) - 1
        ppdb.df["ATOM"]["atom_number"] = (
            ppdb.df["ATOM"]["atom_number"] - to_subtract
        )
        intermediate_file_1 = self.guest_pdb[:-4] + "_intermediate_1.pdb"
        intermediate_file_2 = self.guest_pdb[:-4] + "_intermediate_2.pdb"
        ppdb.to_pdb(path=intermediate_file_1)
        command = (
            "pdb4amber -i "
            + intermediate_file_1
            + " -o "
            + intermediate_file_2
        )
        os.system(command)
        to_delete = (
            intermediate_file_2[:-4] + "_nonprot.pdb",
            intermediate_file_2[:-4] + "_renum.txt",
            intermediate_file_2[:-4] + "_sslink",
        )
        os.system("rm -rf " + " ".join(to_delete))
        with open(intermediate_file_2, "r") as f1:
            filedata = f1.read()
        filedata = filedata.replace("HETATM", "ATOM  ")
        with open(self.guest_pdb, "w") as f2:
            f2.write(filedata)
        command = "rm -rf " + intermediate_file_1 + " " + intermediate_file_2
        os.system(command)

    def get_guest_coord(self):
        """
        Saves a text file of the XYZ coordinates of the ligand.
        """
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_pdb)
        xyz = ppdb.df["ATOM"][["x_coord", "y_coord", "z_coord"]]
        xyz_to_list = xyz.values.tolist()
        np.savetxt(self.guest_xyz, xyz_to_list)

    def get_qm_resids(self):
        """
        Saves a text file of the residue numbers of the receptor within the
        proximity (as defined by the distance) from the ligand.
        """
        guest_coord_list = np.loadtxt(self.guest_xyz)
        host_atom_list = []
        for i in range(len(guest_coord_list)):
            reference_point = guest_coord_list[i]
            # TODO: move reads outside of loop
            ppdb = PandasPdb()
            ppdb.read_pdb(self.host_pdb) 
            distances = ppdb.distance(xyz=reference_point, records=("ATOM"))
            all_within_distance = ppdb.df["ATOM"][
                distances < float(self.distance)
            ]
            host_df = all_within_distance["atom_number"]
            host_list = host_df.values.tolist()
            host_atom_list.append(host_list)
        host_atom_list = list(itertools.chain(*host_atom_list))
        host_atom_list = set(host_atom_list)
        host_atom_list = list(host_atom_list)
        host_atom_list.sort()
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_pdb)
        df = ppdb.df["ATOM"][["atom_number", "residue_number", "residue_name"]]
        index_list = []
        for i in host_atom_list:
            indices = np.where(df["atom_number"] == i)
            indices = list(indices)[0]
            indices = list(indices)
            index_list.append(indices)
        index_list = list(itertools.chain.from_iterable(index_list))
        df1 = df.iloc[
            index_list,
        ]
        # TODO: make it write list of integers
        resid_num = list(df1.residue_number.unique())
        np.savetxt(self.residue_list, resid_num, fmt="%i")

    def get_host_qm_mm_atoms(self):
        """
        Saves a text file of the atom numbers of the receptors in the QM
        region and MM region separately.
        """
        resid_num = np.loadtxt(self.residue_list)
        # approximated_res_list = [int(i) for i in resid_num]
        approximated_res_list = []
        # TODO: what is this doing?
        for i in range(
            int(statistics.median(resid_num))
            - int(int(self.num_residues) / 2),
            int(statistics.median(resid_num))
            + int(int(self.num_residues) / 2),
        ):
            approximated_res_list.append(i)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_pdb)
        df = ppdb.df["ATOM"][["atom_number", "residue_number", "residue_name"]]
        host_index_nested_list = []
        for i in approximated_res_list:
            indices = np.where(df["residue_number"] == i)
            #TODO: the program seems to error when this line is removed, which
            # makes no sense.
            indices = list(indices)[0]
            indices = list(indices)
            host_index_nested_list.append(indices)
        host_index_list = list(
            itertools.chain.from_iterable(host_index_nested_list)
        )
        df_atom = df.iloc[host_index_list]
        df_atom_number = df_atom["atom_number"]
        host_atom_list = df_atom_number.values.tolist()
        selected_atoms = []
        selected_atoms.extend(host_atom_list)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_pdb)
        len_atoms = []
        for i in range(len(ppdb.df["ATOM"])):
            len_atoms.append(i + 1)
        non_selected_atoms = list(set(len_atoms).difference(selected_atoms))
        assert len(non_selected_atoms) + len(selected_atoms) == len(len_atoms),\
            "Sum of the atoms in the selected and non-selected region "\
            "does not equal the length of list of total atoms."
        np.savetxt(self.host_qm_atoms, selected_atoms, fmt="%i")
        np.savetxt(self.host_mm_atoms, non_selected_atoms, fmt="%i")

    def save_host_pdbs(self):
        """
        Saves a PDB file for the receptor's QM region and MM
        region separately.
        """
        selected_atoms = np.loadtxt(self.host_qm_atoms)
        # TODO: not necessary if savetxt writes in integers
        selected_atoms = [int(i) for i in selected_atoms]
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_pdb)
        for i in selected_atoms:
            ppdb.df["ATOM"] = ppdb.df["ATOM"][
                ppdb.df["ATOM"]["atom_number"] != i
            ]
        ppdb.to_pdb(
            path=self.host_mm_pdb, records=None, gz=False, append_newline=True,
        )
        non_selected_atoms = np.loadtxt(self.host_mm_atoms)
        non_selected_atoms = [int(i) for i in non_selected_atoms]
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_pdb)
        for i in non_selected_atoms:
            ppdb.df["ATOM"] = ppdb.df["ATOM"][
                ppdb.df["ATOM"]["atom_number"] != i
            ]
        ppdb.to_pdb(
            path=self.host_qm_pdb, records=None, gz=False, append_newline=True,
        )

    def get_host_mm_region_atoms(self):
        """
        Saves a text file for the atoms of the receptor's MM region
        preceding the QM region and saves another text file for the
        atoms of the receptor's MM region folllowing the QM region.
        """
        resid_num = np.loadtxt(self.residue_list)
        approximated_res_list = []
        for i in range(
            int(statistics.median(resid_num))
            - int(int(self.num_residues) / 2),
            int(statistics.median(resid_num))
            + int(int(self.num_residues) / 2),
        ):
            approximated_res_list.append(i)
        # print(approximated_res_list)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_pdb)
        df = ppdb.df["ATOM"][["residue_number"]]
        res_list = list(set(df["residue_number"].to_list()))
        res_mm_list = list(set(res_list).difference(approximated_res_list))
        # print(res_mm_list)
        res_mm_region_I_list = []
        # TODO: This can probably be made into a single loop by comparing i
        # to the maximum value within approximated_res_list
        for i in res_mm_list:
            for j in approximated_res_list:
                if i < j:
                    res_mm_region_I_list.append(i)
        res_mm_region_I_list = list(set(res_mm_region_I_list))
        res_mm_region_II_list = list(
            set(res_mm_list).difference(res_mm_region_I_list)
        )
        # print(res_mm_region_II_list)
        ppdb.read_pdb(self.host_mm_pdb)
        df = ppdb.df["ATOM"][["atom_number", "residue_number", "residue_name"]]
        mm_region_I_index_nested_list = []
        for i in res_mm_region_I_list:
            indices = np.where(df["residue_number"] == i)
            # TODO: again, this is strange code
            indices = list(indices)[0]
            indices = list(indices)
            mm_region_I_index_nested_list.append(indices)
        mm_region_I_index_list = list(
            itertools.chain.from_iterable(mm_region_I_index_nested_list)
        )
        df_atom = df.iloc[mm_region_I_index_list]
        df_atom_number = df_atom["atom_number"]
        mm_region_I_atom_list = df_atom_number.values.tolist()
        mm_region_I_atoms = []
        mm_region_I_atoms.extend(mm_region_I_atom_list)
        mm_region_II_index_nested_list = []
        for i in res_mm_region_II_list:
            indices = np.where(df["residue_number"] == i)
            # TODO: again, this is strange code
            indices = list(indices)[0]
            indices = list(indices)
            mm_region_II_index_nested_list.append(indices)
        mm_region_II_index_list = list(
            itertools.chain.from_iterable(mm_region_II_index_nested_list)
        )
        df_atom = df.iloc[mm_region_II_index_list]
        df_atom_number = df_atom["atom_number"]
        mm_region_II_atom_list = df_atom_number.values.tolist()
        mm_region_II_atoms = []
        mm_region_II_atoms.extend(mm_region_II_atom_list)
        ppdb.read_pdb(self.host_mm_pdb)
        len_atoms = []
        for i in range(len(ppdb.df["ATOM"])):
            len_atoms.append(i + 1)
        assert len(mm_region_I_atoms) + len(mm_region_II_atoms) == len(len_atoms),\
            "Sum of the atoms in the selected and non-selected region "\
            "does not equal the length of list of total atoms."
        np.savetxt(self.host_mm_region_I_atoms, mm_region_I_atoms, fmt="%i")
        np.savetxt(self.host_mm_region_II_atoms, mm_region_II_atoms, fmt="%i")

    def save_host_mm_regions_pdbs(self):
        """
        Saves a PDB file for the receptor's MM region preceding
        the QM region and saves another PDB file for the receptor's
        MM region folllowing the QM region.
        """
        mm_region_I_atoms = np.loadtxt(self.host_mm_region_I_atoms)
        mm_region_I_atoms = [int(i) for i in mm_region_I_atoms]
        mm_region_II_atoms = np.loadtxt(self.host_mm_region_II_atoms)
        mm_region_II_atoms = [int(i) for i in mm_region_II_atoms]
        
        # NOTE: this is a slightly confusing way to define the atoms to 
        # write to a PDB - the members that are *not* in a section, rather
        # than the members that are.
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_mm_pdb)
        for i in mm_region_II_atoms:
            ppdb.df["ATOM"] = ppdb.df["ATOM"][
                ppdb.df["ATOM"]["atom_number"] != i
            ]
        ppdb.to_pdb(
            path=self.host_mm_region_I_pdb,
            records=None,
            gz=False,
            append_newline=True,
        )
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_mm_pdb)
        for i in mm_region_I_atoms:
            ppdb.df["ATOM"] = ppdb.df["ATOM"][
                ppdb.df["ATOM"]["atom_number"] != i
            ]
        ppdb.to_pdb(
            path=self.host_mm_region_II_pdb,
            records=None,
            gz=False,
            append_newline=True,
        )

    def get_qm_mm_regions(self):
        """
        Saves separate PDB files for the QM and MM regions.
        QM regions comprise the QM region of the receptor
        and the entire ligand where the MM region comprise
        the non-selected QM regions of the receptor.
        """
        with open(self.host_qm_pdb) as f1, open(self.qm_pdb, "w") as f2:
            for line in f1:
                if "ATOM" in line:
                    f2.write(line)
        with open(self.guest_pdb) as f1, open(self.qm_pdb, "a") as f2:
            for line in f1:
                if "ATOM" in line:
                    f2.write(line)
            f2.write("END")
        with open(self.host_mm_pdb) as f1, open(self.mm_pdb, "w") as f2:
            for line in f1:
                if "ATOM" in line:
                    f2.write(line)
            f2.write("END")


class PrepareGaussianGuest:

    """
    A class used to prepare the QM engine input file (Gaussian)
    for the ligand and run QM calculations with appropriate
    keywords.

    This class contain methods to write an input file (.com extension)
    for the QM engine. It then runs a QM calculation with the given
    basis set and functional. Checkpoint file is then converted to
    a formatted checkpoint file. Output files (.log, .chk, and .fhck)
    will then be used to extract ligand's force field parameters.

    ...

    Attributes
    ----------
    charge : int, optional
        Charge of the ligand.

    multiplicity: int, optional
        Spin Multiplicity (2S+1) of the ligand where S represents
        the total spin of the ligand.

    guest_pdb: str, optional
        Ligand PDB file with atom numbers beginning from 1.

    n_processors : int, optional
        Number of processors to be used for Gaussian program to run and
        set in %NProcShared command of Gaussian.

    memory : int, optional
        Memory (in GB) to be used set in %Mem command of Gaussian.

    functional: str, optional
        Exchange/Correlation or hybrid functional to use in the Gaussian
        QM calculation.

    basis_set: str, optional
        Basis set to use for the Gaussian QM calculation.

    optimisation: str, optional
        set to "OPT" to perform a geometry optimization on the ligand
        specified in the system; else set to an empty string.

    frequency: str, optional
        set to "FREQ" for Gaussian to perform a frequency calculation;
        else set to an empty string.

    add_keywords_I: str, optional
        Specifies the integration grid.

    add_keywords_II: str, optional
        Specifies the QM engine to select one of the methods for
        analyzing the electron density of the system. Methods used
        are based on fitting the molecular electrostatic potential.
        Methods used are : POP=CHELPG (Charges from Electrostatic
        Potentials using a Grid based method) and POP=MK
        (Merz-Singh-Kollman scheme)

    add_keywords_III: str, optional
        Used to include the IOp keyword (to set the internal options to
        specific values) in the Gaussian command.

    gauss_out_file: str, optional
        This file contains the output script obtained after running
        the Gaussian QM calculation.

    fchk_out_file: str, optional
        Formatted checkpoint file obtained from the checkpoint file
        using formchk command.


    """

    def __init__(
        self,
        charge=0,
        multiplicity=1,
        guest_pdb="guest_init_II.pdb",
        n_processors=12,
        memory=50,
        functional="B3LYP",
        basis_set="6-31G",
        optimisation="OPT",
        frequency="FREQ",
        add_keywords_I="INTEGRAL=(GRID=ULTRAFINE)",
        add_keywords_II="POP(MK,READRADII)",
        add_keywords_III="IOP(6/33=2,6/42=6)",
        gauss_out_file="guest.out",
        fchk_out_file="guest_fchk.out",
    ):

        self.charge = charge
        self.multiplicity = multiplicity
        self.guest_pdb = guest_pdb
        self.n_processors = n_processors
        self.memory = memory
        self.functional = functional
        self.basis_set = basis_set
        self.optimisation = optimisation
        self.frequency = frequency
        self.gauss_out_file = gauss_out_file
        self.fchk_out_file = fchk_out_file
        self.add_keywords_I = add_keywords_I
        self.add_keywords_II = add_keywords_II
        self.add_keywords_III = add_keywords_III

    def write_input(self):
        """
        Writes a Gaussian input file for the ligand.
        """

        command_line_1 = "%Chk = " + self.guest_pdb[:-4] + ".chk"
        command_line_2 = "%Mem = " + str(self.memory) + "GB"
        command_line_3 = "%NProcShared = " + str(self.n_processors)
        command_line_4 = (
            "# "
            + self.functional
            + " "
            + self.basis_set
            + " "
            + self.optimisation
            + " "
            + self.frequency
            + " "
            + self.add_keywords_I
            + " "
            + self.add_keywords_II
            + " "
            + self.add_keywords_III
        )
        command_line_5 = " "
        command_line_6 = self.guest_pdb[:-4] + " " + "gaussian input file"
        command_line_7 = " "
        command_line_8 = str(self.charge) + " " + str(self.multiplicity)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_pdb)
        df = ppdb.df["ATOM"]
        df_1 = ppdb.df["ATOM"]["element_symbol"]
        df_1.columns = ["atom"]
        df_2 = df[["x_coord", "y_coord", "z_coord"]]
        df_merged = pd.concat([df_1, df_2], axis=1)
        command_line_9 = df_merged.to_string(header=False, index=False)
        command_line_10 = " "
        command = [
            command_line_1,
            command_line_2,
            command_line_3,
            command_line_4,
            command_line_5,
            command_line_6,
            command_line_7,
            command_line_8,
            command_line_9,
            command_line_10,
        ]
        commands = "\n".join(command)
        with open(self.guest_pdb[:-4] + ".com", "w") as f:
            f.write(commands)

    def run_gaussian(self):
        """
        Runs the Gaussian QM calculation for the ligand locally.
        """
        execute_command = (
            "g16"
            + " < "
            + self.guest_pdb[:-4]
            + ".com"
            + " > "
            + self.guest_pdb[:-4]
            + ".log"
        )
        with open(self.gauss_out_file, "w+") as f:
            sp.run(
                execute_command, shell=True, stdout=f, stderr=sp.STDOUT,
            )

    def get_fchk(self):
        """
        Converts the Gaussian checkpoint file (.chk) to a formatted checkpoint
        file (.fchk).
        """
        execute_command = (
            "formchk"
            + " "
            + self.guest_pdb[:-4]
            + ".chk"
            + " "
            + self.guest_pdb[:-4]
            + ".fchk"
        )
        with open(self.fchk_out_file, "w+") as f:
            sp.run(
                execute_command, shell=True, stdout=f, stderr=sp.STDOUT,
            )


class PrepareGaussianHostGuest:

    """
    A class used to prepare the QM engine input file (Gaussian) for
    the receptor - ligand complex and run the QM calculations with
    the appropriate keywords.

    This class contain methods to write an input file (.com extension)
    for the QM engine for the receptor - ligand complex. It then runs
    a QM calculation with the given basis set and functional. Checkpoint
    file is then converted to a formatted checkpoint file. Output files
    (.log, .chk, and .fhck) will then be used to extract charges for the
    ligand and the receptor.

    ...

    Attributes
    ----------
    charge : int, optional
        Total charge of the receptor - ligand complex.

    multiplicity : int, optional
        Spin Multiplicity (2S+1) of the ligand where S represents
        the total spin of the ligand.

    guest_pdb : str, optional
        Ligand PDB file with atom numbers beginning from 1.

    host_qm_pdb : str, optional
        PDB file for the receptor's QM region.

    n_processors : int, optional
        Number of processors to be used for Gaussian program to run and
        set in %NProcShared command of Gaussian.

    memory : int, optional
        Memory (in GB) to be used set in %Mem command of Gaussian.

    functional: str, optional
        Exchange/Correlation or hybrid functional to use in the Gaussian
        QM calculation.

    basis_set: str, optional
        Basis set to use for the Gaussian QM calculation.

    optimisation: str, optional
        set to "OPT" to perform a geometry optimization on the ligand
        specified in the system; else set to an empty string.

    frequency: str, optional
        set to "FREQ" for Gaussian to perform a frequency calculation;
        else set to an empty string.

    add_keywords_I: str, optional
        Specifies the integration grid.

    add_keywords_II: str, optional
        Specifies the QM engine to select one of the methods for
        analyzing the electron density of the system. Methods used
        are based on fitting the molecular electrostatic potential.
        Methods used are : POP=CHELPG (Charges from Electrostatic
        Potentials using a Grid based method) and POP=MK
        (Merz-Singh-Kollman scheme)

    add_keywords_III: str, optional
        Used to include the IOp keyword (to set the internal options to
        specific values) in the Gaussian command.

    gauss_system_out_file : str, optional
        This file contains the output script obtained after running
        the Gaussian QM calculation.

    fchk_system_out_file : str, optional
        Formatted checkpoint file obtained from the checkpoint file
        using formchk command.

    host_guest_input : str, optional
        Gaussian input file (.com extension) for the receptor - ligand
        QM region.

    qm_guest_charge_parameter_file : str, optional
        File containing the charges of ligand atoms and their corresponding
        atoms. Charge obtained are the polarised charged due to the
        surrounding receptor's region.

    qm_host_charge_parameter_file : str, optional
        File containing the charges of the QM region of the receptor.

    qm_guest_atom_charge_parameter_file : str, optional
        File containing the charges of ligand atoms. Charge obtained
        are the polarised charged due to the surrounding receptor's region.

    """

    def __init__(
        self,
        charge=0,
        multiplicity=1,
        guest_pdb="guest_init_II.pdb",
        host_qm_pdb="host_qm.pdb",
        n_processors=12,
        memory=50,
        functional="B3LYP",
        basis_set="6-31G",
        optimisation="",
        frequency="",
        add_keywords_I="INTEGRAL=(GRID=ULTRAFINE)",
        add_keywords_II="POP(MK,READRADII)",
        add_keywords_III="IOP(6/33=2,6/42=6) SCRF=PCM",
        gauss_system_out_file="system_qm.out",
        fchk_system_out_file="system_qm_fchk.out",
        host_guest_input="host_guest.com",
        qm_guest_charge_parameter_file="guest_qm_surround_charges.txt",
        qm_host_charge_parameter_file="host_qm_surround_charges.txt",
        qm_guest_atom_charge_parameter_file="guest_qm_atom_surround_charges.txt",
    ):

        self.charge = charge
        self.multiplicity = multiplicity
        self.guest_pdb = guest_pdb
        self.host_qm_pdb = host_qm_pdb
        self.n_processors = n_processors
        self.memory = memory
        self.functional = functional
        self.basis_set = basis_set
        self.optimisation = optimisation
        self.frequency = frequency
        self.add_keywords_I = add_keywords_I
        self.add_keywords_II = add_keywords_II
        self.add_keywords_III = add_keywords_III
        self.gauss_system_out_file = gauss_system_out_file
        self.fchk_system_out_file = fchk_system_out_file
        self.host_guest_input = host_guest_input
        self.qm_guest_charge_parameter_file = qm_guest_charge_parameter_file
        self.qm_host_charge_parameter_file = qm_host_charge_parameter_file
        self.qm_guest_atom_charge_parameter_file = (
            qm_guest_atom_charge_parameter_file
        )

    def write_input(self):
        """
        Writes a Gaussian input file for the receptor - ligand QM region.
        """
        command_line_1 = "%Chk = " + self.host_guest_input[:-4] + ".chk"
        command_line_2 = "%Mem = " + str(self.memory) + "GB"
        command_line_3 = "%NProcShared = " + str(self.n_processors)
        command_line_4 = (
            "# "
            + self.functional
            + " "
            + self.basis_set
            + " "
            + self.optimisation
            + " "
            + self.frequency
            + " "
            + self.add_keywords_I
            + " "
            + self.add_keywords_II
            + " "
            + self.add_keywords_III
        )
        command_line_5 = " "
        command_line_6 = "Gaussian Input File"
        command_line_7 = " "
        command_line_8 = str(self.charge) + " " + str(self.multiplicity)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_pdb)
        df = ppdb.df["ATOM"]
        df_1 = ppdb.df["ATOM"]["element_symbol"]
        df_1.columns = ["atom"]
        df_3 = df[["x_coord", "y_coord", "z_coord"]]
        df_2 = pd.Series(["0"] * len(df), name="decide_freeze")
        df_merged_1 = pd.concat([df_1, df_2, df_3], axis=1)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_qm_pdb)
        df = ppdb.df["ATOM"]
        df_1 = ppdb.df["ATOM"]["element_symbol"]
        df_1.columns = ["atom"]
        df_3 = df[["x_coord", "y_coord", "z_coord"]]
        df_2 = pd.Series(["0"] * len(df), name="decide_freeze")
        df_merged_2 = pd.concat([df_1, df_2, df_3], axis=1)
        df_merged = pd.concat([df_merged_1, df_merged_2], axis=0)
        command_line_9 = df_merged.to_string(header=False, index=False)
        command_line_10 = " "
        command = [
            command_line_1,
            command_line_2,
            command_line_3,
            command_line_4,
            command_line_5,
            command_line_6,
            command_line_7,
            command_line_8,
            command_line_9,
            command_line_10,
        ]
        commands = "\n".join(command)

        with open(self.host_guest_input, "w") as f:
            f.write(commands)

    def run_gaussian(self):
        """
        Runs the Gaussian QM calculation for the ligand - receptor region
        locally.
        """
        execute_command = (
            "g16"
            + " < "
            + self.host_guest_input
            + " > "
            + self.host_guest_input[:-4]
            + ".log"
        )
        with open(self.gauss_system_out_file, "w+") as f:
            sp.run(
                execute_command, shell=True, stdout=f, stderr=sp.STDOUT,
            )

    def get_fchk(self):
        """
        Converts the Gaussian checkpoint file (.chk) to a formatted checkpoint
        file (.fchk).
        """
        execute_command = (
            "formchk"
            + " "
            + self.host_guest_input[:-4]
            + ".chk"
            + " "
            + self.host_guest_input[:-4]
            + ".fchk"
        )
        with open(self.fchk_system_out_file, "w+") as f:
            sp.run(
                execute_command, shell=True, stdout=f, stderr=sp.STDOUT,
            )

    def get_qm_host_guest_charges(self):
        """
        Extract charge information for the receptor - ligand QM region.
        """
        log_file = self.host_guest_input[:-4] + ".log"
        with open(log_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Fitting point charges to electrostatic potential" in lines[i]:
                to_begin = int(i)
            if " Sum of ESP charges =" in lines[i]:
                to_end = int(i)
        
        # Why + 4?
        charges = lines[to_begin + 4 : to_end]
        charge_list = []
        for i in range(len(charges)):
            charge_list.append(charges[i].strip().split())
        charge_list_value = []
        atom_list = []
        for i in range(len(charge_list)):
            charge_list_value.append(charge_list[i][2])
            atom_list.append(charge_list[i][1])
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_pdb)
        df_guest = ppdb.df["ATOM"]
        number_guest_atoms = df_guest.shape[0]
        data_tuples = list(zip(atom_list, charge_list_value))
        df_charge = pd.DataFrame(data_tuples, columns=["Atom", "Charge"])
        number_host_atoms = df_charge.shape[0] - number_guest_atoms
        df_charge_guest = df_charge.head(number_guest_atoms)
        df_charge_host = df_charge.tail(number_host_atoms)
        df_charge_only_guest = df_charge_guest["Charge"]
        df_charge_guest.to_csv(
            self.qm_guest_charge_parameter_file,
            index=False,
            header=False,
            sep=" ",
        )
        df_charge_host.to_csv(
            self.qm_host_charge_parameter_file,
            index=False,
            header=False,
            sep=" ",
        )
        df_charge_only_guest.to_csv(
            self.qm_guest_atom_charge_parameter_file,
            index=False,
            header=False,
            sep=" ",
        )


class ParameterizeGuest:

    """
    A class used to obtain force field parameters for the ligand (bond,
    angle and charge parameters) from QM calculations.

    This class contain methods to process the output files of the
    Gaussian QM output files (.chk, .fchk and .log files). Methods
    in the class extract the unprocessed hessian matrix from the
    Gaussian QM calculations, processes it and uses the Modified
    Seminario Method to ontain the bond and angle parameters. The
    class also extracts the QM charges from the log file.

    ...

    Attributes
    ----------
    xyz_file: str, optional
        XYZ file for ligand coordinates obtained from its corresponding
        formatted checkpoint file.

    coordinate_file: str, optional
        Text file containing the ligand coordinates (extracted
        from the formatted checkpoint file).

    unprocessed_hessian_file: str, optional
        Unprocessed hessian matrix of the ligand obtained from the
        formatted checkpoint file.

    bond_list_file: str, optional
        Text file containing the bond information of the ligand extracted
        from the log file.

    angle_list_file: str, optional
        Text file containing the angle information of the ligand extracted
        from the log file.

    hessian_file: str, optional
        Processed hessian matrix of the ligand.

    atom_names_file: str, optional
        Text file containing the list of atom names from the fchk file.

    bond_parameter_file: str, optional
        Text file containing the bond parameters for the ligand obtained
        using the Modified Seminario method.

    angle_parameter_file: str, optional
        Text file containing the angle parameters of the ligand obtained
        using the Modified Seminario method..

    charge_parameter_file: str, optional
        Text file containing the QM charges of the ligand.

    guest_pdb: str, optional
        Ligand PDB file with atom numbers beginning from 1.

    proper_dihedral_file: str, optional
        A text file containing proper dihedral angles of the ligand.

    functional: str, optional
        Exchange/Correlation or hybrid functional to use in the Gaussian
        QM calculation.

    basis_set: str, optional
        Basis set to use for the Gaussian QM calculation.

    """

    def __init__(
        self,
        xyz_file="guest_coords.xyz",
        coordinate_file="guest_coordinates.txt",
        unprocessed_hessian_file="guest_unprocessed_hessian.txt",
        bond_list_file="guest_bond_list.txt",
        angle_list_file="guest_angle_list.txt",
        hessian_file="guest_hessian.txt",
        atom_names_file="guest_atom_names.txt",
        bond_parameter_file="guest_bonds.txt",
        angle_parameter_file="guest_angles.txt",
        charge_parameter_file="guest_qm_surround_charges.txt",
        guest_pdb="guest_init_II.pdb",
        proper_dihedral_file="proper_dihedrals.txt",
        functional="B3LYP",
        basis_set="6-31G",
    ):

        self.xyz_file = xyz_file
        self.coordinate_file = coordinate_file
        self.unprocessed_hessian_file = unprocessed_hessian_file
        self.bond_list_file = bond_list_file
        self.angle_list_file = angle_list_file
        self.hessian_file = hessian_file
        self.atom_names_file = atom_names_file
        self.bond_parameter_file = bond_parameter_file
        self.angle_parameter_file = angle_parameter_file
        self.charge_parameter_file = charge_parameter_file
        self.guest_pdb = guest_pdb
        self.proper_dihedral_file = proper_dihedral_file
        self.functional = functional
        self.basis_set = basis_set

    def get_xyz(self):
        """
        Saves XYZ file from the formatted checkpoint file.
        """
        fchk_file = self.guest_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                no_coordinates = re.findall(r"\d+|\d+.\d+", lines[i])
                no_coordinates = int(no_coordinates[0])
                to_begin = int(i)
                
        cartesian_coords = lines[
            to_begin + 1 : to_begin + 1 + int(math.ceil(no_coordinates / 5))
        ]
        cartesian_list = []
        for i in range(len(cartesian_coords)):
            cartesian_list.append(cartesian_coords[i].strip().split())
        
        coordinates_list = [
            item for sublist in cartesian_list for item in sublist
        ]
        # Converted from Atomic units (Bohrs) to Angstroms
        list_coords = [float(x) * BOHRS_PER_ANGSTROM for x in coordinates_list]
        for i in range(len(lines)):
            if "Atomic numbers" in lines[i]:
                to_begin = int(i)
            if "Nuclear charges" in lines[i]:
                to_end = int(i)
        atomic_number_strings = lines[to_begin + 1 : to_end]
        atom_numbers_nested = []
        for i in range(len(atomic_number_strings)):
            atom_numbers_nested.append(atomic_number_strings[i].strip().split())
        numbers = [item for sublist in atom_numbers_nested for item in sublist]
        N = int(no_coordinates / 3)
        # Opens the new xyz file
        with open(self.xyz_file, "w") as file:
            file.write(str(N) + "\n \n")
            coords = np.zeros((N, 3))
            n = 0
            names = []
            # Gives name for atomic number
            for x in range(0, len(numbers)):
                names.append(element_list[int(numbers[x]) - 1][1])
            # Print coordinates to new input_coords.xyz file
            for i in range(0, N):
                for j in range(0, 3):
                    coords[i][j] = list_coords[n]
                    n = n + 1
                file.write(
                    names[i]
                    + str(round(coords[i][0], 3))
                    + " "
                    + str(round(coords[i][1], 3))
                    + " "
                    + str(round(coords[i][2], 3))
                    + "\n"
                )
            
        np.savetxt(self.coordinate_file, coords, fmt="%s")

    def get_unprocessed_hessian(self):
        """
        Saves a text file of the unprocessed hessian matrix from the
        formatted checkpoint file.
        """
        fchk_file = self.guest_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Cartesian Force Constants" in lines[i]:
                no_hessian = re.findall(r"\d+|\d+.\d+", lines[i])
                no_hessian = int(no_hessian[0])
                to_begin = int(i)
        hessian = lines[
            to_begin + 1 : to_begin + 1 + int(math.ceil(no_hessian / 5))
        ]
        hessian_list = []
        for i in range(len(hessian)):
            hessian_list.append(hessian[i].strip().split())
        unprocessed_Hessian = [
            item for sublist in hessian_list for item in sublist
        ]
        np.savetxt(
            self.unprocessed_hessian_file, unprocessed_Hessian, fmt="%s",
        )

    def get_bond_angles(self):
        """
        Saves a text file containing bonds and angles from the gaussian
        log file.
        """
        log_file = self.guest_pdb[:-4] + ".log"
        with open(log_file, "r") as fid:
            tline = fid.readline()
            bond_list = []
            angle_list = []
            tmp = "R"  # States if bond or angle
            # Finds the bond and angles from the .log file
            while tline:
                tline = fid.readline()
                # Line starts at point when bond and angle list occurs
                if (
                    len(tline) > 80
                    and tline[0:81].strip()
                    == "! Name  Definition              Value          Derivative Info.                !"
                ):
                    tline = fid.readline()
                    tline = fid.readline()
                    # Stops when all bond and angles recorded
                    while (tmp[0] == "R") or (tmp[0] == "A"):
                        line = tline.split()
                        tmp = line[1]
                        # Bond or angles listed as string
                        list_terms = line[2][2:-1]
                        # Bond List
                        if tmp[0] == "R":
                            x = list_terms.split(",")
                            # Subtraction due to python array indexing at 0
                            x = [(int(i) - 1) for i in x]
                            bond_list.append(x)
                            # Angle List
                        if tmp[0] == "A":
                            x = list_terms.split(",")
                            # Subtraction due to python array indexing at 0
                            x = [(int(i) - 1) for i in x]
                            angle_list.append(x)
                        tline = fid.readline()
                    # Leave loop
                    tline = -1
            np.savetxt(self.bond_list_file, bond_list, fmt="%s")
            np.savetxt(self.angle_list_file, angle_list, fmt="%s")
        
    def get_hessian(self):
        """
        Extracts hessian matrix from the unprocessed hessian matrix
        and saves into a new file.
        """
        unprocessed_Hessian = np.loadtxt(self.unprocessed_hessian_file)
        fchk_file = self.guest_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                no_coordinates = re.findall(r"\d+|\d+.\d+", lines[i])
                no_coordinates = int(no_coordinates[0])
        
        N = int(no_coordinates / 3)
        length_hessian = 3 * N
        hessian = np.zeros((length_hessian, length_hessian))
        m = 0
        # Write the hessian in a 2D array format
        for i in range(0, length_hessian):
            for j in range(0, (i + 1)):
                hessian[i][j] = unprocessed_Hessian[m]
                hessian[j][i] = unprocessed_Hessian[m]
                m = m + 1
        hessian = (hessian * HARTREE_PER_KCAL_MOL) / (
            BOHRS_PER_ANGSTROM ** 2
        )  # Change from Hartree/bohr to kcal/mol/ang
        np.savetxt(self.hessian_file, hessian, fmt="%s")

    def get_atom_names(self):
        """
        Saves a list of atom names from the formatted checkpoint file.
        """
        fchk_file = self.guest_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Atomic numbers" in lines[i]:
                to_begin = int(i)
            if "Nuclear charges" in lines[i]:
                to_end = int(i)
        atomic_numbers = lines[to_begin + 1 : to_end]
        atom_numbers = []
        for i in range(len(atomic_numbers)):
            atom_numbers.append(atomic_numbers[i].strip().split())
        numbers = [item for sublist in atom_numbers for item in sublist]
        names = []
        # Gives name for atomic number
        for x in range(0, len(numbers)):
            names.append(element_list[int(numbers[x]) - 1][1])
        atom_names = []
        for i in range(0, len(names)):
            atom_names.append(names[i].strip() + str(i + 1))
        np.savetxt(self.atom_names_file, atom_names, fmt="%s")

    def get_bond_angle_params(self):
        """
        Saves the bond and angle parameter files obtained from
        the formatted checkpoint file.
        """
        fchk_file = self.guest_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                no_coordinates = re.findall(r"\d+|\d+.\d+", lines[i])
                no_coordinates = int(no_coordinates[0])
        N = int(no_coordinates / 3)
        coords = np.loadtxt(self.coordinate_file)
        hessian = np.loadtxt(self.hessian_file)
        bond_list = np.loadtxt(self.bond_list_file, dtype=int)
        atom_names = np.loadtxt(self.atom_names_file, dtype=str)
        # Find bond lengths
        bond_lengths = np.zeros((N, N))
        for i in range(0, N):
            for j in range(0, N):
                diff_i_j = np.array(coords[i, :]) - np.array(coords[j, :])
                bond_lengths[i][j] = np.linalg.norm(diff_i_j)
        eigenvectors = np.empty((3, 3, N, N), dtype=complex)
        eigenvalues = np.empty((N, N, 3), dtype=complex)
        partial_hessian = np.zeros((3, 3))
        for i in range(0, N):
            for j in range(0, N):
                partial_hessian = hessian[
                    (i * 3) : ((i + 1) * 3), (j * 3) : ((j + 1) * 3)
                ]
                [a, b] = np.linalg.eig(partial_hessian)
                eigenvalues[i, j, :] = a
                eigenvectors[:, :, i, j] = b
        # Modified Seminario method to find the bond parameters and
        # print them to file
        file_bond = open(self.bond_parameter_file, "w")
        k_b = np.zeros(len(bond_list))
        bond_length_list = np.zeros(len(bond_list))
        unique_values_bonds = []  # Used to find average values
        for i in range(0, len(bond_list)):
            AB = force_constant_bond(
                bond_list[i][0],
                bond_list[i][1],
                eigenvalues,
                eigenvectors,
                coords,
            )
            BA = force_constant_bond(
                bond_list[i][1],
                bond_list[i][0],
                eigenvalues,
                eigenvectors,
                coords,
            )
            # Order of bonds sometimes causes slight differences,
            # find the mean
            k_b[i] = np.real((AB + BA) / 2)
            # Vibrational_scaling takes into account DFT deficities /
            # anharmocity
            vibrational_scaling = get_vibrational_scaling(
                functional=self.functional, basis_set=self.basis_set
            )
            vibrational_scaling_squared = vibrational_scaling ** 2
            k_b[i] = k_b[i] * vibrational_scaling_squared
            bond_length_list[i] = bond_lengths[bond_list[i][0]][
                bond_list[i][1]
            ]
            file_bond.write(
                atom_names[bond_list[i][0]]
                + "-"
                + atom_names[bond_list[i][1]]
                + "  "
            )
            file_bond.write(
                str("%#.5g" % k_b[i])
                + "   "
                + str("%#.4g" % bond_length_list[i])
                + "   "
                + str(bond_list[i][0] + 1)
                + "   "
                + str(bond_list[i][1] + 1)
            )
            file_bond.write("\n")
            unique_values_bonds.append(
                [
                    atom_names[bond_list[i][0]],
                    atom_names[bond_list[i][1]],
                    k_b[i],
                    bond_length_list[i],
                    1,
                ]
            )
        file_bond.close()
        angle_list = np.loadtxt(self.angle_list_file, dtype=int)
        # Modified Seminario method to find the angle parameters
        # and print them to file
        file_angle = open(self.angle_parameter_file, "w")
        k_theta = np.zeros(len(angle_list))
        theta_0 = np.zeros(len(angle_list))
        unique_values_angles = []  # Used to find average values
        # Modified Seminario part goes here ...
        # Connectivity information for Modified Seminario Method
        central_atoms_angles = []
        # A structure is created with the index giving the central
        # atom of the angle,
        # an array then lists the angles with that central atom.
        # i.e. central_atoms_angles{3} contains an array of angles
        # with central atom 3
        for i in range(0, len(coords)):
            central_atoms_angles.append([])
            for j in range(0, len(angle_list)):
                if i == angle_list[j][1]:
                    # For angle ABC, atoms A C are written to array
                    AC_array = [angle_list[j][0], angle_list[j][2], j]
                    central_atoms_angles[i].append(AC_array)
                    # For angle ABC, atoms C A are written to array
                    CA_array = [angle_list[j][2], angle_list[j][0], j]
                    central_atoms_angles[i].append(CA_array)
        # Sort rows by atom number
        for i in range(0, len(coords)):
            central_atoms_angles[i] = sorted(
                central_atoms_angles[i], key=itemgetter(0)
            )
        # Find normals u_PA for each angle
        unit_PA_all_angles = []
        for i in range(0, len(central_atoms_angles)):
            unit_PA_all_angles.append([])
            for j in range(0, len(central_atoms_angles[i])):
                # For the angle at central_atoms_angles[i][j,:] the
                # corresponding u_PA value
                # is found for the plane ABC and bond AB, where ABC
                # corresponds to the order
                # of the arguements. This is why the reverse order
                # was also added
                unit_PA_all_angles[i].append(
                    u_PA_from_angles(
                        central_atoms_angles[i][j][0],
                        i,
                        central_atoms_angles[i][j][1],
                        coords,
                    )
                )
        # Finds the contributing factors from the other angle terms
        # scaling_factor_all_angles
        # = cell(max(max(angle_list))); %This array will contain
        # scaling factor and angle list position
        scaling_factor_all_angles = []
        for i in range(0, len(central_atoms_angles)):
            scaling_factor_all_angles.append([])
            for j in range(0, len(central_atoms_angles[i])):
                n = 1
                m = 1
                angles_around = 0
                additional_contributions = 0
                scaling_factor_all_angles[i].append([0, 0])
                # Position in angle list
                scaling_factor_all_angles[i][j][1] = central_atoms_angles[i][
                    j
                ][2]
                # Goes through the list of angles with the same central atom
                # and computes the
                # term need for the modified Seminario method
                # Forwards directions, finds the same bonds with the central atom i
                while (
                    ((j + n) < len(central_atoms_angles[i]))
                    and central_atoms_angles[i][j][0]
                    == central_atoms_angles[i][j + n][0]
                ):
                    additional_contributions = (
                        additional_contributions
                        + (
                            abs(
                                np.dot(
                                    unit_PA_all_angles[i][j][:],
                                    unit_PA_all_angles[i][j + n][:],
                                )
                            )
                        )
                        ** 2
                    )
                    n = n + 1
                    angles_around = angles_around + 1
                # Backwards direction, finds the same bonds with the central atom i
                while ((j - m) >= 0) and central_atoms_angles[i][j][
                    0
                ] == central_atoms_angles[i][j - m][0]:
                    additional_contributions = (
                        additional_contributions
                        + (
                            abs(
                                np.dot(
                                    unit_PA_all_angles[i][j][:],
                                    unit_PA_all_angles[i][j - m][:],
                                )
                            )
                        )
                        ** 2
                    )
                    m = m + 1
                    angles_around = angles_around + 1
                if n != 1 or m != 1:
                    # Finds the mean value of the additional contribution to
                    # change to normal
                    # Seminario method comment out + part
                    scaling_factor_all_angles[i][j][0] = 1 + (
                        additional_contributions / (m + n - 2)
                    )
                else:
                    scaling_factor_all_angles[i][j][0] = 1
        scaling_factors_angles_list = []
        for i in range(0, len(angle_list)):
            scaling_factors_angles_list.append([])
        # Orders the scaling factors according to the angle list
        for i in range(0, len(central_atoms_angles)):
            for j in range(0, len(central_atoms_angles[i])):
                scaling_factors_angles_list[
                    scaling_factor_all_angles[i][j][1]
                ].append(scaling_factor_all_angles[i][j][0])
        # Finds the angle force constants with the scaling factors
        # included for each angle
        for i in range(0, len(angle_list)):
            # Ensures that there is no difference when the
            # ordering is changed
            [AB_k_theta, AB_theta_0] = force_angle_constant(
                angle_list[i][0],
                angle_list[i][1],
                angle_list[i][2],
                bond_lengths,
                eigenvalues,
                eigenvectors,
                coords,
                scaling_factors_angles_list[i][0],
                scaling_factors_angles_list[i][1],
            )
            [BA_k_theta, BA_theta_0] = force_angle_constant(
                angle_list[i][2],
                angle_list[i][1],
                angle_list[i][0],
                bond_lengths,
                eigenvalues,
                eigenvectors,
                coords,
                scaling_factors_angles_list[i][1],
                scaling_factors_angles_list[i][0],
            )
            k_theta[i] = (AB_k_theta + BA_k_theta) / 2
            theta_0[i] = (AB_theta_0 + BA_theta_0) / 2
            # Vibrational_scaling takes into account DFT
            # deficities/ anharmonicity
            k_theta[i] = k_theta[i] * vibrational_scaling_squared
            file_angle.write(
                atom_names[angle_list[i][0]]
                + "-"
                + atom_names[angle_list[i][1]]
                + "-"
                + atom_names[angle_list[i][2]]
                + "  "
            )
            file_angle.write(
                str("%#.4g" % k_theta[i])
                + "   "
                + str("%#.4g" % theta_0[i])
                + "   "
                + str(angle_list[i][0] + 1)
                + "   "
                + str(angle_list[i][1] + 1)
                + "   "
                + str(angle_list[i][2] + 1)
            )
            file_angle.write("\n")
            unique_values_angles.append(
                [
                    atom_names[angle_list[i][0]],
                    atom_names[angle_list[i][1]],
                    atom_names[angle_list[i][2]],
                    k_theta[i],
                    theta_0[i],
                    1,
                ]
            )
        file_angle.close()

    def get_charges(self):
        """
        Saves the atomic charges in a text file obtained from
        the Gaussian log file.
        """
        log_file = self.guest_pdb[:-4] + ".log"
        with open(log_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Fitting point charges to electrostatic potential" in lines[i]:
                to_begin = int(i)
            if " Sum of ESP charges =" in lines[i]:
                to_end = int(i)
        charges = lines[to_begin + 4 : to_end]
        charge_list = []
        for i in range(len(charges)):
            charge_list.append(charges[i].strip().split())
        charge_list_value = []
        atom_list = []
        for i in range(len(charge_list)):
            charge_list_value.append(charge_list[i][2])
            atom_list.append(charge_list[i][1])
        data_tuples = list(zip(atom_list, charge_list_value))
        df_charge = pd.DataFrame(data_tuples, columns=["Atom", "Charge"])
        df_charge.to_csv(
            self.charge_parameter_file, index=False, header=False, sep=" ",
        )

    def get_proper_dihedrals(self):
        """
        Saves proper dihedral angles of the ligand in a text file.
        """
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_pdb)
        no_atoms = len(ppdb.df["ATOM"])
        atom_index_list = []
        for i in range(no_atoms):
            atom_index_list.append(i + 1)
        possible_dihedrals = []
        for dihed in itertools.permutations(atom_index_list, 4):
            possible_dihedrals.append(dihed)
        df_bonds = pd.read_csv(
            self.bond_parameter_file, header=None, delimiter=r"\s+"
        )
        df_bonds.columns = [
            "bond",
            "k_bond",
            "bond_length",
            "bond_1",
            "bond_2",
        ]
        bond1 = df_bonds["bond_1"].values.tolist()
        bond2 = df_bonds["bond_2"].values.tolist()
        bond_list_list = []
        for i in range(len(bond1)):
            args = (bond1[i], bond2[i])
            bond_list_list.append(list(args))
        reverse_bond_list_list = []
        for bonds in bond_list_list:
            reverse_bond_list_list.append(reverse_list(bonds))
        bond_lists = bond_list_list + reverse_bond_list_list
        proper_dihed_repeated = []
        for i in range(len(possible_dihedrals)):
            dihed_frag = (
                [possible_dihedrals[i][0], possible_dihedrals[i][1]],
                [possible_dihedrals[i][1], possible_dihedrals[i][2]],
                [possible_dihedrals[i][2], possible_dihedrals[i][3]],
            )
            a = [
                dihed_frag[0] in bond_lists,
                dihed_frag[1] in bond_lists,
                dihed_frag[2] in bond_lists,
            ]
            if a == [True, True, True]:
                proper_dihed_repeated.append(possible_dihedrals[i])

        len_repeated_dihed_list = len(proper_dihed_repeated)
        proper_dihedrals = proper_dihed_repeated
        for x in proper_dihedrals:
            z = x[::-1]
            if z in proper_dihedrals:
                proper_dihedrals.remove(z)
        len_non_repeated_dihed_list = len(proper_dihedrals)
        # print(len_repeated_dihed_list == len_non_repeated_dihed_list * 2)
        np.savetxt(self.proper_dihedral_file, proper_dihedrals, fmt="%s")
        # return(proper_dihedrals)


class PrepareGaussianHost:

    """
    A class used to prepare the QM engine input file (Gaussian)
    for the receptor and run QM calculations with appropriate keywords.

    This class contain methods to write an input file (.com extension)
    for the QM engine. It then runs a QM calculation with the given
    basis set and functional. Checkpoint file is then converted to
    a formatted checkpoint file. Output files (.log, .chk, and .fhck)
    will then be used to extract receptors's force field parameters.

    ...

    Attributes
    ----------
    charge : int, optional
        Charge of the receptor.

    multiplicity: int, optional
        Spin Multiplicity (2S+1) of the receptor where S represents
        the total spin of the receptor.

    host_qm_pdb: str, optional
        PDB file of the receptor's QM region with atom numbers
        beginning from 1.

    n_processors : int, optional
        Number of processors to be used for Gaussian program to run and
        set in %NProcShared command of Gaussian.

    memory : int, optional
        Memory (in GB) to be used set in %Mem command of Gaussian.

    functional: str, optional
        Exchange/Correlation or hybrid functional to use in the Gaussian
        QM calculation.

    basis_set: str, optional
        Basis set to use for the Gaussian QM calculation.

    optimisation: str, optional
        set to "OPT" to perform a geometry optimization on the receptor
        specified in the system; else set to an empty string.

    frequency: str, optional
        set to "FREQ" for Gaussian to perform a frequency calculation;
        else set to an empty string.

    add_keywords_I: str, optional
        Specifies the integration grid.

    add_keywords_II: str, optional
        Specifies the QM engine to select one of the methods for
        analyzing the electron density of the system. Methods used
        are based on fitting the molecular electrostatic potential.
        Methods used are : POP=CHELPG (Charges from Electrostatic
        Potentials using a Grid based method) and POP=MK
        (Merz-Singh-Kollman scheme)

    add_keywords_III: str, optional
        Used to include the IOp keyword (to set the internal options to
        specific values) in the Gaussian command.

    gauss_out_file: str, optional
        This file contains the output script obtained after running
        the Gaussian QM calculation.

    fchk_out_file: str, optional
        Formatted checkpoint file obtained from the checkpoint file
        using formchk command.

    """

    def __init__(
        self,
        charge=0,
        multiplicity=1,
        host_qm_pdb="host_qm.pdb",
        n_processors=12,
        memory=50,
        functional="B3LYP",
        basis_set="6-31G",
        optimisation="OPT",
        frequency="FREQ",
        add_keywords_I="INTEGRAL=(GRID=ULTRAFINE) SCF=(maxcycles=4000) SYMMETRY=NONE",
        add_keywords_II="POP(MK,READRADII)",
        add_keywords_III="IOP(6/33=2,6/42=6)",
        gauss_out_file="host_qm.out",
        fchk_out_file="host_qm_fchk.out",
    ):

        self.charge = charge
        self.multiplicity = multiplicity
        self.host_qm_pdb = host_qm_pdb
        self.n_processors = n_processors
        self.memory = memory
        self.functional = functional
        self.basis_set = basis_set
        self.optimisation = optimisation
        self.frequency = frequency
        self.gauss_out_file = gauss_out_file
        self.fchk_out_file = fchk_out_file
        self.add_keywords_I = add_keywords_I
        self.add_keywords_II = add_keywords_II
        self.add_keywords_III = add_keywords_III

    def write_input(self):
        """
        Writes a Gaussian input file for the receptor QM region.
        """
        # TODO: create generic function for Gaussian Input file (DRY principle)
        command_line_1 = "%Chk = " + self.host_qm_pdb[:-4] + ".chk"
        command_line_2 = "%Mem = " + str(self.memory) + "GB"
        command_line_3 = "%NProcShared = " + str(self.n_processors)
        command_line_4 = (
            "# "
            + self.functional
            + " "
            + self.basis_set
            + " "
            + self.optimisation
            + " "
            + self.frequency
            + " "
            + self.add_keywords_I
            + " "
            + self.add_keywords_II
            + " "
            + self.add_keywords_III
        )
        command_line_5 = " "
        command_line_6 = self.host_qm_pdb[:-4] + " " + "gaussian input file"
        command_line_7 = " "
        command_line_8 = str(self.charge) + " " + str(self.multiplicity)
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_qm_pdb)
        df = ppdb.df["ATOM"]
        df_1 = ppdb.df["ATOM"]["element_symbol"]
        df_1.columns = ["atom"]
        df_2 = df[["x_coord", "y_coord", "z_coord"]]
        df_merged = pd.concat([df_1, df_2], axis=1)
        command_line_9 = df_merged.to_string(header=False, index=False)
        command_line_10 = " "
        command = [
            command_line_1,
            command_line_2,
            command_line_3,
            command_line_4,
            command_line_5,
            command_line_6,
            command_line_7,
            command_line_8,
            command_line_9,
            command_line_10,
        ]
        commands = "\n".join(command)
        with open(self.host_qm_pdb[:-4] + ".com", "w") as f:
            f.write(commands)

    def run_gaussian(self):
        """
        Runs the Gaussian QM calculation for the receptor locally.
        """
        execute_command = (
            "g16"
            + " < "
            + self.host_qm_pdb[:-4]
            + ".com"
            + " > "
            + self.host_qm_pdb[:-4]
            + ".log"
        )
        with open(self.gauss_out_file, "w+") as f:
            sp.run(
                execute_command, shell=True, stdout=f, stderr=sp.STDOUT,
            )

    def get_fchk(self):
        """
        Converts the Gaussian checkpoint file (.chk) to a formatted checkpoint
        file (.fchk).
        """
        execute_command = (
            "formchk"
            + " "
            + self.host_qm_pdb[:-4]
            + ".chk"
            + " "
            + self.host_qm_pdb[:-4]
            + ".fchk"
        )
        with open(self.fchk_out_file, "w+") as f:
            sp.run(
                execute_command, shell=True, stdout=f, stderr=sp.STDOUT,
            )


class ParameterizeHost:

    """
    A class used to obtain force field parameters for the QM region
    of the receptor (bond, angle and charge parameters) from QM
    calculations.

    This class contain methods to process the output files of the
    Gaussian QM output files (.chk, .fchk and .log files). Methods
    in the class extract the unprocessed hessian matrix from the
    Gaussian QM calculations, processes it and uses the Modified
    Seminario Method to ontain the bond and angle parameters. The
    class also extracts the QM charges from the log file.

    ...

    Attributes
    ----------
    xyz_file: str, optional
        XYZ file for ligand coordinates obtained from its corresponding
        formatted checkpoint file.

    coordinate_file: str, optional
        Text file containing the receptor coordinates (extracted
        from the formatted checkpoint file).

    unprocessed_hessian_file: str, optional
        Unprocessed hessian matrix of the receptor obtained from the
        formatted checkpoint file.

    bond_list_file: str, optional
        Text file containing the bond information of the receptor
        extracted from the log file.

    angle_list_file: str, optional
        Text file containing the angle information of the receptor
        extracted from the log file.

    hessian_file: str, optional
        Processed hessian matrix of the receptor.

    atom_names_file: str, optional
        Text file containing the list of atom names from the fchk file.

    bond_parameter_file: str, optional
        Text file containing the bond parameters for the receptor
        obtained using the Modified Seminario method.

    angle_parameter_file: str, optional
        Text file containing the angle parameters of the receptor.

    charge_parameter_file: str, optional
        Text file containing the QM charges of the receptor.

    host_qm_pdb: str, optional
        PDB file for the receptor's QM region.

    functional: str, optional
        Exchange/Correlation or hybrid functional to use in the Gaussian
        QM calculation.

    basis_set: str, optional
        Basis set to use for the Gaussian QM calculation.

    """

    def __init__(
        self,
        xyz_file="host_qm_coords.xyz",
        coordinate_file="host_qm_coordinates.txt",
        unprocessed_hessian_file="host_qm_unprocessed_hessian.txt",
        bond_list_file="host_qm_bond_list.txt",
        angle_list_file="host_qm_angle_list.txt",
        hessian_file="host_qm_hessian.txt",
        atom_names_file="host_qm_atom_names.txt",
        bond_parameter_file="host_qm_bonds.txt",
        angle_parameter_file="host_qm_angles.txt",
        charge_parameter_file="host_qm_surround_charges.txt",
        host_qm_pdb="host_qm.pdb",
        functional="B3LYP",
        basis_set="6-31G",
    ):

        self.xyz_file = xyz_file
        self.coordinate_file = coordinate_file
        self.unprocessed_hessian_file = unprocessed_hessian_file
        self.bond_list_file = bond_list_file
        self.angle_list_file = angle_list_file
        self.hessian_file = hessian_file
        self.atom_names_file = atom_names_file
        self.bond_parameter_file = bond_parameter_file
        self.angle_parameter_file = angle_parameter_file
        self.charge_parameter_file = charge_parameter_file
        self.host_qm_pdb = host_qm_pdb
        self.functional = functional
        self.basis_set = basis_set

    def get_xyz(self):
        """
        Saves XYZ file from the formatted checkpoint file.
        """
        fchk_file = self.host_qm_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                no_coordinates = re.findall(r"\d+|\d+.\d+", lines[i])
                no_coordinates = int(no_coordinates[0])
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                to_begin = int(i)
        cartesian_coords = lines[
            to_begin + 1 : to_begin + 1 + int(math.ceil(no_coordinates / 5))
        ]
        cartesian_list = []
        for i in range(len(cartesian_coords)):
            cartesian_list.append(cartesian_coords[i].strip().split())
        coordinates_list = [
            item for sublist in cartesian_list for item in sublist
        ]
        list_coords = [float(x) * float(0.529) for x in coordinates_list]
        for i in range(len(lines)):
            if "Atomic numbers" in lines[i]:
                to_begin = int(i)
            if "Nuclear charges" in lines[i]:
                to_end = int(i)
        atomic_numbers = lines[to_begin + 1 : to_end]
        atom_numbers = []
        for i in range(len(atomic_numbers)):
            atom_numbers.append(atomic_numbers[i].strip().split())
        numbers = [item for sublist in atom_numbers for item in sublist]
        N = int(no_coordinates / 3)
        # Opens the new xyz file
        file = open(self.xyz_file, "w")
        file.write(str(N) + "\n \n")
        coords = np.zeros((N, 3))
        n = 0
        names = []
        # Gives name for atomic number
        for x in range(0, len(numbers)):
            names.append(element_list[int(numbers[x]) - 1][1])
        # Print coordinates to new input_coords.xyz file
        for i in range(0, N):
            for j in range(0, 3):
                coords[i][j] = list_coords[n]
                n = n + 1
            file.write(
                names[i]
                + str(round(coords[i][0], 3))
                + " "
                + str(round(coords[i][1], 3))
                + " "
                + str(round(coords[i][2], 3))
                + "\n"
            )
        file.close()
        np.savetxt(self.coordinate_file, coords, fmt="%s")

    def get_unprocessed_hessian(self):
        """
        Saves a text file of the unprocessed hessian matrix from the
        formatted checkpoint file.
        """
        fchk_file = self.host_qm_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Cartesian Force Constants" in lines[i]:
                no_hessian = re.findall(r"\d+|\d+.\d+", lines[i])
                no_hessian = int(no_hessian[0])
        for i in range(len(lines)):
            if "Cartesian Force Constants" in lines[i]:
                to_begin = int(i)
        hessian = lines[
            to_begin + 1 : to_begin + 1 + int(math.ceil(no_hessian / 5))
        ]
        hessian_list = []
        for i in range(len(hessian)):
            hessian_list.append(hessian[i].strip().split())
        unprocessed_Hessian = [
            item for sublist in hessian_list for item in sublist
        ]
        np.savetxt(
            self.unprocessed_hessian_file, unprocessed_Hessian, fmt="%s",
        )

    def get_bond_angles(self):
        """
        Saves a text file containing bonds and angles from the gaussian
        log file.
        """
        log_file = self.host_qm_pdb[:-4] + ".log"
        fid = open(log_file, "r")
        tline = fid.readline()
        bond_list = []
        angle_list = []
        n = 1
        n_bond = 1
        n_angle = 1
        tmp = "R"  # States if bond or angle
        B = []
        # Finds the bond and angles from the .log file
        while tline:
            tline = fid.readline()
            # Line starts at point when bond and angle list occurs
            if (
                len(tline) > 80
                and tline[0:81].strip()
                == "! Name  Definition              Value          Derivative Info.                !"
            ):
                tline = fid.readline()
                tline = fid.readline()
                # Stops when all bond and angles recorded
                while (tmp[0] == "R") or (tmp[0] == "A"):
                    line = tline.split()
                    tmp = line[1]
                    # Bond or angles listed as string
                    list_terms = line[2][2:-1]
                    # Bond List
                    if tmp[0] == "R":
                        x = list_terms.split(",")
                        # Subtraction due to python array indexing at 0
                        x = [(int(i) - 1) for i in x]
                        bond_list.append(x)
                        # Angle List
                    if tmp[0] == "A":
                        x = list_terms.split(",")
                        # Subtraction due to python array indexing at 0
                        x = [(int(i) - 1) for i in x]
                        angle_list.append(x)
                    tline = fid.readline()
                # Leave loop
                tline = -1
        np.savetxt(self.bond_list_file, bond_list, fmt="%s")
        np.savetxt(self.angle_list_file, angle_list, fmt="%s")

    def get_hessian(self):
        """
        Extracts hessian matrix from the unprocessed hessian matrix
        and saves into a new file.
        """
        unprocessed_Hessian = np.loadtxt(self.unprocessed_hessian_file)
        fchk_file = self.host_qm_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                no_coordinates = re.findall(r"\d+|\d+.\d+", lines[i])
                no_coordinates = int(no_coordinates[0])
        N = int(no_coordinates / 3)
        length_hessian = 3 * N
        hessian = np.zeros((length_hessian, length_hessian))
        m = 0
        # Write the hessian in a 2D array format
        for i in range(0, (length_hessian)):
            for j in range(0, (i + 1)):
                hessian[i][j] = unprocessed_Hessian[m]
                hessian[j][i] = unprocessed_Hessian[m]
                m = m + 1
        hessian = (hessian * (627.509391)) / (
            0.529 ** 2
        )  # Change from Hartree/bohr to kcal/mol/ang
        np.savetxt(self.hessian_file, hessian, fmt="%s")

    def get_atom_names(self):
        """
        Saves a list of atom names from the formatted checkpoint file.
        """
        fchk_file = self.host_qm_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Atomic numbers" in lines[i]:
                to_begin = int(i)
            if "Nuclear charges" in lines[i]:
                to_end = int(i)
        atomic_numbers = lines[to_begin + 1 : to_end]
        atom_numbers = []
        for i in range(len(atomic_numbers)):
            atom_numbers.append(atomic_numbers[i].strip().split())
        numbers = [item for sublist in atom_numbers for item in sublist]
        names = []
        # Gives name for atomic number
        for x in range(0, len(numbers)):
            names.append(element_list[int(numbers[x]) - 1][1])
        atom_names = []
        for i in range(0, len(names)):
            atom_names.append(names[i].strip() + str(i + 1))
        np.savetxt(self.atom_names_file, atom_names, fmt="%s")

    def get_bond_angle_params(self):
        """
        Saves the bond and angle parameter files obtained from
        the formatted checkpoint file.
        """
        fchk_file = self.host_qm_pdb[:-4] + ".fchk"
        with open(fchk_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Current cartesian coordinates" in lines[i]:
                no_coordinates = re.findall(r"\d+|\d+.\d+", lines[i])
                no_coordinates = int(no_coordinates[0])
        N = int(no_coordinates / 3)
        coords = np.loadtxt(self.coordinate_file)
        hessian = np.loadtxt(self.hessian_file)
        bond_list = np.loadtxt(self.bond_list_file, dtype=int)
        atom_names = np.loadtxt(self.atom_names_file, dtype=str)
        # Find bond lengths
        bond_lengths = np.zeros((N, N))
        for i in range(0, N):
            for j in range(0, N):
                diff_i_j = np.array(coords[i, :]) - np.array(coords[j, :])
                bond_lengths[i][j] = np.linalg.norm(diff_i_j)
        eigenvectors = np.empty((3, 3, N, N), dtype=complex)
        eigenvalues = np.empty((N, N, 3), dtype=complex)
        partial_hessian = np.zeros((3, 3))
        for i in range(0, N):
            for j in range(0, N):
                partial_hessian = hessian[
                    (i * 3) : ((i + 1) * 3), (j * 3) : ((j + 1) * 3)
                ]
                [a, b] = np.linalg.eig(partial_hessian)
                eigenvalues[i, j, :] = a
                eigenvectors[:, :, i, j] = b
        # Modified Seminario method to find the bond parameters
        # and print them to file
        file_bond = open(self.bond_parameter_file, "w")
        k_b = np.zeros(len(bond_list))
        bond_length_list = np.zeros(len(bond_list))
        unique_values_bonds = []  # Used to find average values
        for i in range(0, len(bond_list)):
            AB = force_constant_bond(
                bond_list[i][0],
                bond_list[i][1],
                eigenvalues,
                eigenvectors,
                coords,
            )
            BA = force_constant_bond(
                bond_list[i][1],
                bond_list[i][0],
                eigenvalues,
                eigenvectors,
                coords,
            )
            # Order of bonds sometimes causes slight differences,
            # find the mean
            k_b[i] = np.real((AB + BA) / 2)
            # Vibrational_scaling takes into account DFT deficities
            # / anharmocity
            vibrational_scaling = get_vibrational_scaling(
                functional=self.functional, basis_set=self.basis_set
            )
            vibrational_scaling_squared = vibrational_scaling ** 2
            k_b[i] = k_b[i] * vibrational_scaling_squared
            bond_length_list[i] = bond_lengths[bond_list[i][0]][
                bond_list[i][1]
            ]
            file_bond.write(
                atom_names[bond_list[i][0]]
                + "-"
                + atom_names[bond_list[i][1]]
                + "  "
            )
            file_bond.write(
                str("%#.5g" % k_b[i])
                + "   "
                + str("%#.4g" % bond_length_list[i])
                + "   "
                + str(bond_list[i][0] + 1)
                + "   "
                + str(bond_list[i][1] + 1)
            )
            file_bond.write("\n")
            unique_values_bonds.append(
                [
                    atom_names[bond_list[i][0]],
                    atom_names[bond_list[i][1]],
                    k_b[i],
                    bond_length_list[i],
                    1,
                ]
            )
        file_bond.close()
        angle_list = np.loadtxt(self.angle_list_file, dtype=int)
        # Modified Seminario method to find the angle parameters
        # and print them to file
        file_angle = open(self.angle_parameter_file, "w")
        k_theta = np.zeros(len(angle_list))
        theta_0 = np.zeros(len(angle_list))
        unique_values_angles = []  # Used to find average values
        # Modified Seminario part goes here ...
        # Connectivity information for Modified Seminario Method
        central_atoms_angles = []
        # A structure is created with the index giving the central
        # atom of the angle, an array then lists the angles with
        # that central atom.
        # i.e. central_atoms_angles{3} contains an array of angles
        # with central atom 3
        for i in range(0, len(coords)):
            central_atoms_angles.append([])
            for j in range(0, len(angle_list)):
                if i == angle_list[j][1]:
                    # For angle ABC, atoms A C are written to array
                    AC_array = [angle_list[j][0], angle_list[j][2], j]
                    central_atoms_angles[i].append(AC_array)
                    # For angle ABC, atoms C A are written to array
                    CA_array = [angle_list[j][2], angle_list[j][0], j]
                    central_atoms_angles[i].append(CA_array)
        # Sort rows by atom number
        for i in range(0, len(coords)):
            central_atoms_angles[i] = sorted(
                central_atoms_angles[i], key=itemgetter(0)
            )
        # Find normals u_PA for each angle
        unit_PA_all_angles = []
        for i in range(0, len(central_atoms_angles)):
            unit_PA_all_angles.append([])
            for j in range(0, len(central_atoms_angles[i])):
                # For the angle at central_atoms_angles[i][j,:] the corresponding
                # u_PA value is found for the plane ABC and bond AB,
                # where ABC corresponds to the order of the arguements.
                # This is why the reverse order was also added
                unit_PA_all_angles[i].append(
                    u_PA_from_angles(
                        central_atoms_angles[i][j][0],
                        i,
                        central_atoms_angles[i][j][1],
                        coords,
                    )
                )
        # Finds the contributing factors from the other angle terms
        # scaling_factor_all_angles = cell(max(max(angle_list)));
        # This array will contain scaling factor and angle list position
        scaling_factor_all_angles = []
        for i in range(0, len(central_atoms_angles)):
            scaling_factor_all_angles.append([])
            for j in range(0, len(central_atoms_angles[i])):
                n = 1
                m = 1
                angles_around = 0
                additional_contributions = 0
                scaling_factor_all_angles[i].append([0, 0])
                # Position in angle list
                scaling_factor_all_angles[i][j][1] = central_atoms_angles[i][
                    j
                ][2]
                # Goes through the list of angles with the same central
                # atom and computes the term need for the modified Seminario method
                # Forwards directions, finds the same bonds with the central atom i
                while (
                    ((j + n) < len(central_atoms_angles[i]))
                    and central_atoms_angles[i][j][0]
                    == central_atoms_angles[i][j + n][0]
                ):
                    additional_contributions = (
                        additional_contributions
                        + (
                            abs(
                                np.dot(
                                    unit_PA_all_angles[i][j][:],
                                    unit_PA_all_angles[i][j + n][:],
                                )
                            )
                        )
                        ** 2
                    )
                    n = n + 1
                    angles_around = angles_around + 1
                # Backwards direction, finds the same bonds with the central atom i
                while ((j - m) >= 0) and central_atoms_angles[i][j][
                    0
                ] == central_atoms_angles[i][j - m][0]:
                    additional_contributions = (
                        additional_contributions
                        + (
                            abs(
                                np.dot(
                                    unit_PA_all_angles[i][j][:],
                                    unit_PA_all_angles[i][j - m][:],
                                )
                            )
                        )
                        ** 2
                    )
                    m = m + 1
                    angles_around = angles_around + 1
                if n != 1 or m != 1:
                    # Finds the mean value of the additional contribution to
                    # change to normal Seminario method comment out + part
                    scaling_factor_all_angles[i][j][0] = 1 + (
                        additional_contributions / (m + n - 2)
                    )
                else:
                    scaling_factor_all_angles[i][j][0] = 1
        scaling_factors_angles_list = []
        for i in range(0, len(angle_list)):
            scaling_factors_angles_list.append([])
        # Orders the scaling factors according to the angle list
        for i in range(0, len(central_atoms_angles)):
            for j in range(0, len(central_atoms_angles[i])):
                scaling_factors_angles_list[
                    scaling_factor_all_angles[i][j][1]
                ].append(scaling_factor_all_angles[i][j][0])
        # Finds the angle force constants with the scaling factors
        # included for each angle
        for i in range(0, len(angle_list)):
            # Ensures that there is no difference when the
            # ordering is changed
            [AB_k_theta, AB_theta_0] = force_angle_constant(
                angle_list[i][0],
                angle_list[i][1],
                angle_list[i][2],
                bond_lengths,
                eigenvalues,
                eigenvectors,
                coords,
                scaling_factors_angles_list[i][0],
                scaling_factors_angles_list[i][1],
            )
            [BA_k_theta, BA_theta_0] = force_angle_constant(
                angle_list[i][2],
                angle_list[i][1],
                angle_list[i][0],
                bond_lengths,
                eigenvalues,
                eigenvectors,
                coords,
                scaling_factors_angles_list[i][1],
                scaling_factors_angles_list[i][0],
            )
            k_theta[i] = (AB_k_theta + BA_k_theta) / 2
            theta_0[i] = (AB_theta_0 + BA_theta_0) / 2
            # Vibrational_scaling takes into account DFT
            # deficities / anharmonicity
            k_theta[i] = k_theta[i] * vibrational_scaling_squared
            file_angle.write(
                atom_names[angle_list[i][0]]
                + "-"
                + atom_names[angle_list[i][1]]
                + "-"
                + atom_names[angle_list[i][2]]
                + "  "
            )
            file_angle.write(
                str("%#.4g" % k_theta[i])
                + "   "
                + str("%#.4g" % theta_0[i])
                + "   "
                + str(angle_list[i][0] + 1)
                + "   "
                + str(angle_list[i][1] + 1)
                + "   "
                + str(angle_list[i][2] + 1)
            )
            file_angle.write("\n")
            unique_values_angles.append(
                [
                    atom_names[angle_list[i][0]],
                    atom_names[angle_list[i][1]],
                    atom_names[angle_list[i][2]],
                    k_theta[i],
                    theta_0[i],
                    1,
                ]
            )
        file_angle.close()

    def get_charges(self):
        """
        Saves the atomic charges in a text file obtained from
        the Gaussian log file.
        """
        log_file = self.host_qm_pdb[:-4] + ".log"
        with open(log_file, "r") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "Fitting point charges to electrostatic potential" in lines[i]:
                to_begin = int(i)
            if " Sum of ESP charges =" in lines[i]:
                to_end = int(i)
        charges = lines[to_begin + 4 : to_end]
        charge_list = []
        for i in range(len(charges)):
            charge_list.append(charges[i].strip().split())
        charge_list_value = []
        atom_list = []
        for i in range(len(charge_list)):
            charge_list_value.append(charge_list[i][2])
            atom_list.append(charge_list[i][1])
        data_tuples = list(zip(atom_list, charge_list_value))
        df_charge = pd.DataFrame(data_tuples, columns=["Atom", "Charge"])
        df_charge.to_csv(
            self.charge_parameter_file, index=False, header=False, sep=" ",
        )


class GuestAmberXMLAmber:

    """
    A class used to generate a template force field XML file for the ligand
    in order regenerate the reparameterised forcefield XML file.

    This class contain methods to generate a template XML force field through
    openforcefield. XML template generation can be obtained through different
    file formats such as PDB, SDF, and SMI. Methods support charged ligands as
    well. Re-parameterized XML force field files are then generated from the
    template files. Different energy components such as the bond, angle,
    torsional and non-bonded energies are computed for the non-reparametrized
    and the reparameterized force fields. Difference between the
    non-reparameterized and reparameterized force field energies can then be
    analyzed.
    ...

    Attributes
    ----------
    charge : int
        Charge of the ligand.

    num_charge_atoms: int, optional
        Number of charged atoms in the molecule.

    charge_atom_1: int, optional
        Charge on the first charged atom.

    index_charge_atom_1: int, optional
        Index of the first charged atom.

    system_pdb: str, optional
        Ligand PDB file with atom numbers beginning from 1.

    system_mol2: str, optional
        Ligand Mol2 file obtained from PDB file.

    system_in: str, optional
        Prepi file as required by antechamber.

    system_frcmod: str, optional
        FRCMOD file as required by antechamber.

    prmtop_system : str, optional
        Topology file obtained from the ligand PDB.

    inpcrd_system : str, optional
        Coordinate file obtained from the ligand PDB using the
        command saveamberparm.

    system_leap : str, optional
        Amber generated leap file for generating and saving topology
        and coordinate files.

    system_xml: str, optional
        Serialized XML force field file of the ligand.

    system_smi: str, optional
        Ligand SMILES format file.

    system_sdf: str, optional
        Ligand SDF (structure-data) format file.

    system_init_sdf: str, optional
        Ligand SDF (structure-data) format file. This file will be
        generated only if the ligand is charged.

    index_charge_atom_2: int, optional
        Index of the second charged atom of the ligand.

    charge_atom_2: int, optional
        Charge on the second charged atom of the ligand.

    charge_parameter_file: str, optional
        File containing the charges of ligand atoms and their corresponding
        atoms.

    system_qm_pdb: str, optional
        Ligand PDB file with atom numbers beginning from 1.

    bond_parameter_file: str, optional
        Text file containing the bond parameters for the ligand.

    angle_parameter_file: str, optional
        Text file containing the angle parameters of the ligand.

    system_qm_params_file: str, optional
        A text file containing the QM obtained parameters for the
        ligand.

    reparameterised_intermediate_system_xml_file: str, optional
        XML foce field file with bond and angle parameter lines replaced by
        corresponding values obtained from the QM calculations.

    system_xml_non_bonded_file: str, optional
        Text file to write the NonBondedForce Charge Parameters from
        the non-parameterised system XML file.

    system_xml_non_bonded_reparams_file: str, optional
        Text file containing the non-bonded parameters parsed from the
        XML force field file.

    reparameterised_system_xml_file: str, optional
        Reparameterized force field XML file obtained using
        openforcefield.

    non_reparameterised_system_xml_file: str, optional
        Non-reparameterized force field XML file obtained using
        openforcefield.

    prmtop_system_non_params: str, optional
        Amber generated topology file saved from the non-reparameterized
        force field XML file for the ligand.

    inpcrd_system_non_params: str, optional
        Amber generated coordinate file saved from the non-reparameterized
        force field XML file for the ligand.

    prmtop_system_params: str, optional
        Amber generated topology file saved from the reparameterized
        force field XML file for the ligand.

    inpcrd_system_params: str, optional
        Amber generated coordinate file saved from the reparameterized
        force field XML file for the ligand.

    load_topology: str, optional
        Argument to specify how to load the topology. Can either be "openmm"
        or "parmed".

    """

    def __init__(
        self,
        charge=0,
        # TODO: some of these variables are ints, and shouldn't be initialized as strings
        num_charge_atoms="",
        charge_atom_1="",
        index_charge_atom_1="",
        system_pdb="guest_init_II.pdb",
        system_mol2="guest.mol2",
        system_in="guest.in",
        system_frcmod="guest.frcmod",
        prmtop_system="guest.prmtop",
        inpcrd_system="guest.inpcrd",
        system_leap="guest.leap",
        system_xml="guest_init.xml",
        system_smi="guest.smi",
        system_sdf="guest.sdf",
        system_init_sdf="guest_init.sdf",
        index_charge_atom_2=" ",
        charge_atom_2=" ",
        charge_parameter_file="guest_qm_surround_charges.txt",
        system_qm_pdb="guest_init_II.pdb",
        bond_parameter_file="guest_bonds.txt",
        angle_parameter_file="guest_angles.txt",
        system_qm_params_file="guest_qm_params.txt",
        reparameterised_intermediate_system_xml_file="guest_intermediate_reparameterised.xml",
        system_xml_non_bonded_file="guest_xml_non_bonded.txt",
        system_xml_non_bonded_reparams_file="guest_xml_non_bonded_reparams.txt",
        reparameterised_system_xml_file="guest_reparameterised.xml",
        non_reparameterised_system_xml_file="guest_init.xml",
        prmtop_system_non_params="guest_non_params.prmtop",
        inpcrd_system_non_params="guest_non_params.inpcrd",
        prmtop_system_params="guest_params.prmtop",
        inpcrd_system_params="guest_params.inpcrd",
        load_topology="openmm",
    ):

        self.charge = charge
        self.num_charge_atoms = num_charge_atoms
        self.charge_atom_1 = charge_atom_1
        self.index_charge_atom_1 = index_charge_atom_1
        self.system_pdb = system_pdb
        self.system_mol2 = system_mol2
        self.system_in = system_in
        self.system_frcmod = system_frcmod
        self.prmtop_system = prmtop_system
        self.inpcrd_system = inpcrd_system
        self.system_leap = system_leap
        self.system_xml = system_xml
        self.system_smi = system_smi
        self.system_sdf = system_sdf
        self.system_init_sdf = system_init_sdf
        self.index_charge_atom_2 = index_charge_atom_2
        self.charge_atom_2 = charge_atom_2
        self.charge_parameter_file = charge_parameter_file
        self.system_qm_pdb = system_qm_pdb
        self.bond_parameter_file = bond_parameter_file
        self.angle_parameter_file = angle_parameter_file
        self.system_qm_params_file = system_qm_params_file
        self.reparameterised_intermediate_system_xml_file = (
            reparameterised_intermediate_system_xml_file
        )
        self.system_xml_non_bonded_file = system_xml_non_bonded_file
        self.system_xml_non_bonded_reparams_file = (
            system_xml_non_bonded_reparams_file
        )
        self.reparameterised_system_xml_file = reparameterised_system_xml_file
        self.non_reparameterised_system_xml_file = (
            non_reparameterised_system_xml_file
        )
        self.prmtop_system_non_params = prmtop_system_non_params
        self.inpcrd_system_non_params = inpcrd_system_non_params
        self.prmtop_system_params = prmtop_system_params
        self.inpcrd_system_params = inpcrd_system_params
        self.load_topology = load_topology

    def generate_xml_antechamber(self):
        """
        Generates an XML forcefield file from the PDB file through antechamber.
        """
        command = (
            # "babel -ipdb " + self.system_pdb + " -omol2 " + self.system_mol2
            "obabel -ipdb "
            + self.system_pdb
            + " -omol2 -O "
            + self.system_mol2
        )
        os.system(command)
        command = (
            "antechamber -i "
            + self.system_mol2
            + " -fi mol2 -o "
            + self.system_in
            + " -fo prepi -c bcc -nc "
            + str(self.charge)
        )
        os.system(command)
        command = (
            "parmchk2 -i "
            + self.system_in
            + " -o "
            + self.system_frcmod
            + " -f prepi -a Y"
        )
        os.system(command)
        os.system(
            "rm -rf ANTECHAMBER* leap.log sqm* ATOMTYPE.INF PREP.INF NEWPDB.PDB"
        )
        line_1 = "loadamberprep " + self.system_in
        line_2 = "loadamberparams " + self.system_frcmod
        line_3 = "pdb = loadpdb " + self.system_pdb
        line_4 = (
            "saveamberparm pdb "
            + self.prmtop_system
            + " "
            + self.inpcrd_system
        )
        line_5 = "quit"
        with open(self.system_leap, "w") as f:
            f.write("    " + "\n")
            f.write(line_1 + "\n")
            f.write(line_2 + "\n")
            f.write(line_3 + "\n")
            f.write(line_4 + "\n")
            f.write(line_5 + "\n")
        command = "tleap -f " + self.system_leap
        os.system(command)
        parm = parmed.load_file(self.prmtop_system, self.inpcrd_system)
        system = parm.createSystem()
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def generate_xml_from_pdb_smi(self):
        """
        Generates an XML forcefield file from the SMILES file through
        openforcefield.
        """
        # off_molecule = openforcefield.topology.Molecule(self.system_smi)
        off_molecule = Molecule(self.system_smi)
        # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
        force_field = ForceField("openff_unconstrained-1.0.0.offxml")
        system = force_field.create_openmm_system(off_molecule.to_topology())
        pdbfile = simtk.openmm.app.PDBFile(self.system_pdb)
        structure = parmed.openmm.load_topology(
            pdbfile.topology, system, xyz=pdbfile.positions
        )
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def generate_xml_from_pdb_sdf(self):
        """
        Generates an XML forcefield file from the SDF file through
        openforcefield.
        """
        command = (
            # "babel -ipdb " + self.system_pdb + " -osdf " + self.system_sdf
            "obabel -ipdb "
            + self.system_pdb
            + " -osdf -O "
            + self.system_sdf
        )
        os.system(command)
        # off_molecule = openforcefield.topology.Molecule(self.system_sdf)
        off_molecule = Molecule(self.system_sdf)
        # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
        force_field = ForceField("openff_unconstrained-1.0.0.offxml")
        system = force_field.create_openmm_system(off_molecule.to_topology())
        pdbfile = simtk.openmm.app.PDBFile(self.system_pdb)
        structure = parmed.openmm.load_topology(
            pdbfile.topology, system, xyz=pdbfile.positions
        )
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def generate_xml_from_charged_pdb_sdf(self):
        """
        Generates an XML forcefield file for a singly charged ligand molecule
        from the SDF file through openforcefield.
        """
        command = (
            # "babel -ipdb " + self.system_pdb + " -osdf " + self.system_init_sdf
            "obabel -ipdb "
            + self.system_pdb
            + " -osdf -O "
            + self.system_init_sdf
        )
        os.system(command)
        with open(self.system_init_sdf, "r") as f1:
            filedata = f1.readlines()
            filedata = filedata[:-2]
        with open(self.system_sdf, "w+") as out:
            for i in filedata:
                out.write(i)
            line_1 = (
                "M  CHG  "
                + str(self.num_charge_atoms)
                + "   "
                + str(self.index_charge_atom_1)
                + "   "
                + str(self.charge_atom_1)
                + "\n"
            )
            line_2 = "M  END" + "\n"
            line_3 = "$$$$"
            out.write(line_1)
            out.write(line_2)
            out.write(line_3)
        # off_molecule = openforcefield.topology.Molecule(self.system_sdf)
        off_molecule = Molecule(self.system_sdf)
        # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
        force_field = ForceField("openff_unconstrained-1.0.0.offxml")
        system = force_field.create_openmm_system(off_molecule.to_topology())
        pdbfile = simtk.openmm.app.PDBFile(self.system_pdb)
        structure = parmed.openmm.load_topology(
            pdbfile.topology, system, xyz=pdbfile.positions
        )
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def generate_xml_from_doubly_charged_pdb_sdf(self):
        """
        Generates an XML forcefield file for a singly charged ligand molecule
        from the SDF file through openforcefield.
        """
        command = (
            # "babel -ipdb " + self.system_pdb + " -osdf " + self.system_init_sdf
            "obabel -ipdb "
            + self.system_pdb
            + " -osdf -O "
            + self.system_init_sdf
        )
        os.system(command)
        with open(self.system_init_sdf, "r") as f1:
            filedata = f1.readlines()
            filedata = filedata[:-2]
        with open(self.system_sdf, "w+") as out:
            for i in filedata:
                out.write(i)
            line_1 = (
                "M  CHG  "
                + str(self.num_charge_atoms)
                + "   "
                + str(self.index_charge_atom_1)
                + "   "
                + str(self.charge_atom_1)
                + "   "
                + str(self.index_charge_atom_2)
                + "   "
                + str(self.charge_atom_2)
                + "\n"
            )
            line_2 = "M  END" + "\n"
            line_3 = "$$$$"
            out.write(line_1)
            out.write(line_2)
            out.write(line_3)
        # off_molecule = openforcefield.topology.Molecule(self.system_sdf)
        off_molecule = Molecule(self.system_sdf)
        # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
        force_field = ForceField("openff_unconstrained-1.0.0.offxml")
        system = force_field.create_openmm_system(off_molecule.to_topology())
        pdbfile = simtk.openmm.app.PDBFile(self.system_pdb)
        structure = parmed.openmm.load_topology(
            pdbfile.topology, system, xyz=pdbfile.positions
        )
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def write_system_params(self):
        """
        Saves the parameters obtained from the QM log files in a text file.
        """
        # Charges from QM files
        df_charges = pd.read_csv(
            self.charge_parameter_file, header=None, delimiter=r"\s+"
        )
        df_charges.columns = ["atom", "charges"]
        qm_charges = df_charges["charges"].values.tolist()
        qm_charges = [round(num, 6) for num in qm_charges]
        # print(qm_charges)
        # Bond Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.system_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        atom_name_list = [i - 1 for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.bond_parameter_file, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "bond",
            "k_bond",
            "bond_length",
            "bond_1",
            "bond_2",
        ]
        # print(df.head())
        bond_1_list = df["bond_1"].values.tolist()
        bond_1_list = [x - 1 + min(atom_name_list) for x in bond_1_list]
        bond_2_list = df["bond_2"].values.tolist()
        bond_2_list = [x - 1 + min(atom_name_list) for x in bond_2_list]
        # print(bond_1_list)
        # print(bond_2_list)
        k_bond_list = df["k_bond"].values.tolist()
        #k_bond_list = [
        #    i * 418.40 for i in k_bond_list
        #]  # kcal/mol * A^2 to kJ/mol * nm^2
        
        k_bond_list = [
            i * KCAL_MOL_PER_KJ_MOL * ANGSTROMS_PER_NM**2 for i in k_bond_list
        ]  # kcal/mol * A^2 to kJ/mol * nm^2
        k_bond_list = [round(num, 10) for num in k_bond_list]
        # print(k_bond_list)
        bond_length_list = df["bond_length"].values.tolist()
        # TODO: units here? Anstroms per nm?
        bond_length_list = [i / 10.00 for i in bond_length_list]
        bond_length_list = [round(num, 6) for num in bond_length_list]
        # print(bond_length_list)
        # Angle Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.system_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        atom_name_list = [i - 1 for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.angle_parameter_file, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "angle",
            "k_angle",
            "angle_degrees",
            "angle_1",
            "angle_2",
            "angle_3",
        ]
        # print(df.head())
        angle_1_list = df["angle_1"].values.tolist()
        angle_1_list = [x - 1 + min(atom_name_list) for x in angle_1_list]
        # print(angle_1_list)
        angle_2_list = df["angle_2"].values.tolist()
        angle_2_list = [x - 1 + min(atom_name_list) for x in angle_2_list]
        # print(angle_2_list)
        angle_3_list = df["angle_3"].values.tolist()
        angle_3_list = [x - 1 + min(atom_name_list) for x in angle_3_list]
        # print(angle_3_list)
        k_angle_list = df["k_angle"].values.tolist()
        k_angle_list = [
            i * KCAL_MOL_PER_KJ_MOL for i in k_angle_list
        ]  # kcal/mol * radian^2 to kJ/mol * radian^2
        k_angle_list = [round(num, 6) for num in k_angle_list]
        # print(k_angle_list)
        angle_list = df["angle_degrees"].values.tolist()
        angle_list = [i * RADIANS_PER_DEGREE for i in angle_list]
        angle_list = [round(num, 6) for num in angle_list]
        # print(angle_list)
        xml = open(self.system_qm_params_file, "w")
        xml.write("Begin writing the Bond Parameters" + "\n")
        # TODO: These should use string formatting to become more concise
        for i in range(len(k_bond_list)):
            xml.write(
                "                                "
                + "<Bond"
                + " "
                + "d="
                + '"'
                + str(bond_length_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_bond_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(bond_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(bond_2_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Bond Parameters" + "\n")
        xml.write("Begin writing the Angle Parameters" + "\n")
        for i in range(len(k_angle_list)):
            xml.write(
                "                                "
                + "<Angle"
                + " "
                + "a="
                + '"'
                + str(angle_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_angle_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(angle_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(angle_2_list[i])
                + '"'
                + " "
                + "p3="
                + '"'
                + str(angle_3_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Angle Parameters" + "\n")
        xml.write("Begin writing the Charge Parameters" + "\n")
        for i in range(len(qm_charges)):
            xml.write(
                "<Particle"
                + " "
                + "q="
                + '"'
                + str(qm_charges[i])
                + '"'
                + " "
                + "eps="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "sig="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "atom="
                + '"'
                + str(atom_name_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Charge Parameters" + "\n")
        xml.close()

    def write_intermediate_reparameterised_system_xml(self):
        """
        Writes a reparameterised XML force field file for
        ligand but without the QM obtained charges.
        """
        # Bond Parameters
        f_params = open(self.system_qm_params_file, "r")
        lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [
                comb_1,
                comb_2,
                comb_3,
                comb_4,
                comb_5,
                comb_6,
            ]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()

    def write_reparameterised_system_xml(self):
        """
        Writes a reparameterised XML force field file for the ligand.
        """
        # Bond Parameters
        f_params = open(self.system_qm_params_file, "r")
        lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        # TODO: These should use string formatting to become more concise
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [
                comb_1,
                comb_2,
                comb_3,
                comb_4,
                comb_5,
                comb_6,
            ]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()

        f_params = open(self.system_qm_params_file)
        lines_params = f_params.readlines()
        # Charge Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Charge Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Charge Parameters" in lines_params[i]:
                to_end = int(i)
        charge_params = lines_params[to_begin + 1 : to_end]
        non_bonded_index = []
        for k in charge_params:
            non_bonded_index.append(int(re.findall("[-+]?\d*\.\d+|\d+", k)[3]))
        charge_for_index = []
        for k in charge_params:
            charge_for_index.append(
                float(re.findall("[-+]?\d*\.\d+|\d+", k)[0])
            )

        xml_off = open(self.system_xml)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)
        nonbond_params = xml_off_lines[to_begin + 4 : to_end - 1]
        # print(len(nonbond_params))
        f_non_bonded = open(self.system_xml_non_bonded_file, "w")
        for x in nonbond_params:
            f_non_bonded.write(x)
        f_non_bonded = open(self.system_xml_non_bonded_file)
        lines_non_bonded = f_non_bonded.readlines()
        # print(len(lines_non_bonded))
        lines_non_bonded_to_write = []
        for i in range(len(non_bonded_index)):
            line_ = lines_non_bonded[non_bonded_index[i]]
            # print(line_)
            eps = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[0])
            sig = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[2])
            line_to_replace = (
                "                                "
                + "<Particle "
                + "eps="
                + '"'
                + str(eps)
                + '"'
                + " "
                + "q="
                + '"'
                + str(charge_for_index[i])
                + '"'
                + " "
                + "sig="
                + '"'
                + str(sig)
                + '"'
                + "/>"
            )
            lines_non_bonded_to_write.append(line_to_replace)
        data_ = list(zip(non_bonded_index, lines_non_bonded_to_write))

        df_non_bonded_params = pd.DataFrame(
            data_, columns=["line_index", "line"]
        )
        # print(df_non_bonded_params.head())
        f_non_bonded_ = open(self.system_xml_non_bonded_file)
        lines_non_bonded_ = f_non_bonded_.readlines()
        for i in range(len(lines_non_bonded_)):
            if i in non_bonded_index:
                lines_non_bonded_[i] = (
                    df_non_bonded_params.loc[
                        df_non_bonded_params.line_index == i, "line"
                    ].values[0]
                ) + "\n"
        # print(len(lines_non_bonded_))
        f_write_non_bonded_reparams = open(
            self.system_xml_non_bonded_reparams_file, "w"
        )
        for p in range(len(lines_non_bonded_)):
            f_write_non_bonded_reparams.write(lines_non_bonded_[p])
        f_write_non_bonded_reparams.close()
        f_ = open(self.system_xml_non_bonded_reparams_file)
        lines_ = f_.readlines()
        print(len(lines_) == len(lines_non_bonded))

        xml_off = open(self.reparameterised_intermediate_system_xml_file)
        # TODO: implement function(s) to read certain types of files. DRY principle
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)

        lines_before_params = xml_off_lines[: to_begin + 4]
        f__ = open(self.system_xml_non_bonded_reparams_file)
        lines_params_non_bonded = f__.readlines()
        lines_after_params = xml_off_lines[to_end - 1 :]
        f_reparams_xml = open(self.reparameterised_system_xml_file, "w")
        for x in lines_before_params:
            f_reparams_xml.write(x)
        for x in lines_params_non_bonded:
            f_reparams_xml.write(x)
        for x in lines_after_params:
            f_reparams_xml.write(x)
        f_reparams_xml.close()

    def save_amber_params_non_qm_charges(self):
        """
        Saves amber generated topology files for the ligand
        without the QM charges.
        """
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params,
        )

        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(
                    self.reparameterised_intermediate_system_xml_file
                ),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(
                    self.reparameterised_intermediate_system_xml_file
                ),
            )
        openmm_system.save(self.prmtop_system_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )

        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(
                self.reparameterised_intermediate_system_xml_file
            ),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")

        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

    def save_amber_params(self):
        """
        Saves amber generated topology files for the ligand.
        """
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params,
        )

        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")

        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")

        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )

        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")

        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")

        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

    def analyze_diff_energies(self):
        """
        Compares the energies of the ligand obtained from the non-parameterized
        and the parameterized force field files.
        """
        parm_non_params = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params,
        )
        prmtop_energy_decomposition_non_params = parmed.openmm.energy_decomposition_system(
            parm_non_params, parm_non_params.createSystem()
        )
        prmtop_energy_decomposition_non_params_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_non_params_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_non_params = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_non_params_list,
                    prmtop_energy_decomposition_non_params_value,
                )
            ),
            columns=["Energy_term", "Energy_parm_non_params"],
        )
        df_energy_non_params = df_energy_non_params.set_index("Energy_term")
        # print(df_energy_non_params)
        parm_params = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )
        prmtop_energy_decomposition_params = parmed.openmm.energy_decomposition_system(
            parm_params, parm_params.createSystem()
        )
        prmtop_energy_decomposition_params_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_params_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_params = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_params_list,
                    prmtop_energy_decomposition_params_value,
                )
            ),
            columns=["Energy_term", "Energy_parm_params"],
        )
        df_energy_params = df_energy_params.set_index("Energy_term")
        # print(df_energy_params)
        df_compare = pd.concat(
            [df_energy_non_params, df_energy_params], axis=1
        )
        df_compare["Energy_difference"] = df_compare[
            "Energy_parm_non_params"
        ].sub(df_compare["Energy_parm_params"], axis=0)
        print(df_compare)


class HostAmberXMLAmber:

    """
    A class used to generate a template force field XML file for the receptor
    in order regenerate the reparameterised forcefield XML file.

    This class contain methods to generate a template XML force field through
    openforcefield. Re-parameterized XML force field files are then
    generated from the template files. Different energy components such as
    bond, angle, torsional and non-bonded energies are computed for the
    non-reparametrized and the reparameterized force fields. Difference
    between the non-reparameterized and reparameterized force field energies
    can then be analyzed.
    ...

    Attributes
    ----------

    system_pdb: str, optional
        Receptor PDB file with atom numbers beginning from 1.

    system_sdf: str, optional
        Receptor SDF (structure-data) format file.

    charge : int
        Charge of the ligand.

    system_mol2: str, optional
        Receptor Mol2 file obtained from PDB file.

    system_in: str, optional
        Prepi file as required by antechamber.

    system_frcmod: str, optional
        FRCMOD file as required by antechamber.

    prmtop_system : str, optional
        Topology file obtained from the receptor PDB.

    inpcrd_system : str, optional
        Coordinate file obtained from the receptor PDB using the
        command saveamberparm.

    system_leap : str, optional
        Amber generated leap file for generating and saving topology
        and coordinate files.

    system_xml: str, optional
        Serilazed XML force field file of the receptor.

    sim_output: str, optional
        PDB file containing the trajectory coordinates for the OpenMM
        simulation.

    sim_steps: str, optional
        Number of steps in the OpenMM MD simulation.

    charge_parameter_file: str, optional
        File containing the charges of receptor atoms and their
        corresponding atoms.

    system_qm_pdb: str, optional
        Receptor QM region's PDB file with atom numbers beginning from 1.

    bond_parameter_file: str, optional
        Text file containing the bond parameters for the receptor.

    angle_parameter_file: str, optional
        Text file containing the angle parameters of the receptor.

    system_qm_params_file: str, optional
        A text file containing the QM obtained parameters for the
        receptor.

    reparameterised_intermediate_system_xml_file: str, optional
        XML force field file with bond and angle parameter lines replaced by
        corresponding values obtained from the QM calculations.

    system_xml_non_bonded_file: str, optional
        Text file to write the NonBondedForce Charge Parameters from
        the non-parameterised system XML file.

    system_xml_non_bonded_reparams_file: str, optional
        Text file containing the non-bonded parameters parsed from the
        XML force field file.

    reparameterised_system_xml_file: str, optional
        Reparameterized force field XML file obtained using
        openforcefield.

    non_reparameterised_system_xml_file: str, optional
        Non-reparameterized force field XML file obtained using
        openforcefield.

    prmtop_system_non_params: str, optional
        Amber generated topology file saved from the non-reparameterized
        force field XML file for the receptor.

    inpcrd_system_non_params: str, optional
        Amber generated coordinate file saved from the non-reparameterized
        force field XML file for the receptor.

    prmtop_system_params: str, optional
        Amber generated topology file saved from the reparameterized
        force field XML file for the receptor.

    inpcrd_system_params: str, optional
        Amber generated coordinate file saved from the reparameterized
        force field XML file for the receptor.

    load_topology: str, optional
        Argument to specify how to load the topology. Can either be "openmm"
        or "parmed".

    """

    def __init__(
        self,
        system_pdb="host.pdb",
        system_sdf="host.sdf",
        charge=0,
        system_mol2="host.mol2",
        system_in="host.in",
        system_frcmod="host.frcmod",
        prmtop_system="host.prmtop",
        inpcrd_system="host.inpcrd",
        system_leap="host.leap",
        system_xml="host.xml",
        sim_output="sim_output.pdb",
        sim_steps=1000,
        charge_parameter_file="host_qm_surround_charges.txt",
        system_qm_pdb="host_qm.pdb",
        bond_parameter_file="host_qm_bonds.txt",
        angle_parameter_file="host_qm_angles.txt",
        system_qm_params_file="host_qm_params.txt",
        reparameterised_intermediate_system_xml_file="host_intermediate_reparameterised.xml",
        system_xml_non_bonded_file="host_xml_non_bonded.txt",
        system_xml_non_bonded_reparams_file="host_xml_non_bonded_reparams.txt",
        reparameterised_system_xml_file="host_reparameterised.xml",
        non_reparameterised_system_xml_file="host.xml",
        prmtop_system_non_params="host_non_params.prmtop",
        inpcrd_system_non_params="host_non_params.inpcrd",
        prmtop_system_params="host_params.prmtop",
        inpcrd_system_params="host_params.inpcrd",
        load_topology="openmm",
    ):
        self.system_pdb = system_pdb
        self.system_sdf = system_sdf
        self.charge = charge
        self.system_mol2 = system_mol2
        self.system_in = system_in
        self.system_frcmod = system_frcmod
        self.prmtop_system = prmtop_system
        self.inpcrd_system = inpcrd_system
        self.system_leap = system_leap
        self.system_xml = system_xml
        self.sim_output = sim_output
        self.sim_steps = sim_steps
        self.charge_parameter_file = charge_parameter_file
        self.system_qm_pdb = system_qm_pdb
        self.bond_parameter_file = bond_parameter_file
        self.angle_parameter_file = angle_parameter_file
        self.system_qm_params_file = system_qm_params_file
        self.reparameterised_intermediate_system_xml_file = (
            reparameterised_intermediate_system_xml_file
        )
        self.system_xml_non_bonded_file = system_xml_non_bonded_file
        self.system_xml_non_bonded_reparams_file = (
            system_xml_non_bonded_reparams_file
        )
        self.reparameterised_system_xml_file = reparameterised_system_xml_file
        self.non_reparameterised_system_xml_file = (
            non_reparameterised_system_xml_file
        )
        self.prmtop_system_non_params = prmtop_system_non_params
        self.inpcrd_system_non_params = inpcrd_system_non_params
        self.prmtop_system_params = prmtop_system_params
        self.inpcrd_system_params = inpcrd_system_params
        self.load_topology = load_topology

    def generate_xml_from_pdb_sdf(self):
        """
        Generates an XML forcefield file from the SDF file through
        openforcefield.
        """
        command = (
            # "babel -ipdb " + self.system_pdb + " -osdf " + self.system_sdf
            "obabel -ipdb "
            + self.system_pdb
            + " -osdf -O "
            + self.system_sdf
        )
        os.system(command)
        # off_molecule = openforcefield.topology.Molecule(self.system_sdf)
        off_molecule = Molecule(self.system_sdf)
        # force_field = openforcefield.typing.engines.smirnoff.ForceField("openff_unconstrained-1.0.0.offxml")
        force_field = ForceField("openff_unconstrained-1.0.0.offxml")
        system = force_field.create_openmm_system(off_molecule.to_topology())
        pdbfile = simtk.openmm.app.PDBFile(self.system_pdb)
        structure = parmed.openmm.load_topology(
            pdbfile.topology, system, xyz=pdbfile.positions
        )
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def generate_xml_antechamber(self):
        """
        Generates an XML forcefield file from the PDB file through antechamber.
        """
        command = (
            # "babel -ipdb " + self.system_pdb + " -omol2 " + self.system_mol2
            "obabel -ipdb "
            + self.system_pdb
            + " -omol2 -O "
            + self.system_mol2
        )
        os.system(command)
        command = (
            "antechamber -i "
            + self.system_mol2
            + " -fi mol2 -o "
            + self.system_in
            + " -fo prepi -c bcc -nc "
            + str(self.charge)
        )
        os.system(command)
        command = (
            "parmchk2 -i "
            + self.system_in
            + " -o "
            + self.system_frcmod
            + " -f prepi -a Y"
        )
        os.system(command)
        os.system(
            "rm -rf ANTECHAMBER* leap.log sqm* ATOMTYPE.INF PREP.INF NEWPDB.PDB"
        )
        line_1 = "loadamberprep " + self.system_in
        line_2 = "loadamberparams " + self.system_frcmod
        line_3 = "pdb = loadpdb " + self.system_pdb
        line_4 = (
            "saveamberparm pdb "
            + self.prmtop_system
            + " "
            + self.inpcrd_system
        )
        line_5 = "quit"
        with open(self.system_leap, "w") as f:
            f.write("    " + "\n")
            f.write(line_1 + "\n")
            f.write(line_2 + "\n")
            f.write(line_3 + "\n")
            f.write(line_4 + "\n")
            f.write(line_5 + "\n")
        command = "tleap -f " + self.system_leap
        os.system(command)
        parm = parmed.load_file(self.prmtop_system, self.inpcrd_system)
        system = parm.createSystem()
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def serialize_system(self):
        pdb = simtk.openmm.app.PDBFile(self.system_pdb)
        forcefield = simtk.openmm.app.ForceField("amber14-all.xml")
        system = forcefield.createSystem(pdb.topology)
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            pdb.topology, system, integrator
        )
        simulation.context.setPositions(pdb.positions)
        simulation.minimizeEnergy(maxIterations=100000)
        state = simulation.context.getState(getEnergy=True)
        energy = state.getPotentialEnergy()
        print(energy)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(self.sim_output, self.sim_steps / 10)
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.sim_output
        os.system(command)
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def write_system_params(self):
        """
        Saves the parameters obtained from the QM log files in a text file.
        """
        # Charges from QM files
        df_charges = pd.read_csv(
            self.charge_parameter_file, header=None, delimiter=r"\s+"
        )
        df_charges.columns = ["atom", "charges"]
        qm_charges = df_charges["charges"].values.tolist()
        qm_charges = [round(num, 6) for num in qm_charges]
        # print(qm_charges)
        # Bond Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.system_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        atom_name_list = [i - 1 for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.bond_parameter_file, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "bond",
            "k_bond",
            "bond_length",
            "bond_1",
            "bond_2",
        ]
        # print(df.head())
        bond_1_list = df["bond_1"].values.tolist()
        bond_1_list = [x - 1 + min(atom_name_list) for x in bond_1_list]
        bond_2_list = df["bond_2"].values.tolist()
        bond_2_list = [x - 1 + min(atom_name_list) for x in bond_2_list]
        # print(bond_1_list)
        # print(bond_2_list)
        k_bond_list = df["k_bond"].values.tolist()
        k_bond_list = [
            i * KCAL_MOL_PER_KJ_MOL * ANGSTROMS_PER_NM**2 for i in k_bond_list
        ]  # kcal/mol * A^2 to kJ/mol * nm^2
        k_bond_list = [round(num, 10) for num in k_bond_list]
        # print(k_bond_list)
        bond_length_list = df["bond_length"].values.tolist()
        bond_length_list = [i / 10.00 for i in bond_length_list]
        bond_length_list = [round(num, 6) for num in bond_length_list]
        # print(bond_length_list)
        # Angle Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.system_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        atom_name_list = [i - 1 for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.angle_parameter_file, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "angle",
            "k_angle",
            "angle_degrees",
            "angle_1",
            "angle_2",
            "angle_3",
        ]
        # print(df.head())
        angle_1_list = df["angle_1"].values.tolist()
        angle_1_list = [x - 1 + min(atom_name_list) for x in angle_1_list]
        # print(angle_1_list)
        angle_2_list = df["angle_2"].values.tolist()
        angle_2_list = [x - 1 + min(atom_name_list) for x in angle_2_list]
        # print(angle_2_list)
        angle_3_list = df["angle_3"].values.tolist()
        angle_3_list = [x - 1 + min(atom_name_list) for x in angle_3_list]
        # print(angle_3_list)
        k_angle_list = df["k_angle"].values.tolist()
        k_angle_list = [
            i * 4.184 for i in k_angle_list
        ]  # kcal/mol * radian^2 to kJ/mol * radian^2
        k_angle_list = [round(num, 6) for num in k_angle_list]
        # print(k_angle_list)
        angle_list = df["angle_degrees"].values.tolist()
        angle_list = [(i * math.pi) / 180.00 for i in angle_list]
        angle_list = [round(num, 6) for num in angle_list]
        # print(angle_list)
        xml = open(self.system_qm_params_file, "w")
        xml.write("Begin writing the Bond Parameters" + "\n")
        for i in range(len(k_bond_list)):
            xml.write(
                "                                "
                + "<Bond"
                + " "
                + "d="
                + '"'
                + str(bond_length_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_bond_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(bond_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(bond_2_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Bond Parameters" + "\n")
        xml.write("Begin writing the Angle Parameters" + "\n")
        for i in range(len(k_angle_list)):
            xml.write(
                "                                "
                + "<Angle"
                + " "
                + "a="
                + '"'
                + str(angle_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_angle_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(angle_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(angle_2_list[i])
                + '"'
                + " "
                + "p3="
                + '"'
                + str(angle_3_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Angle Parameters" + "\n")
        xml.write("Begin writing the Charge Parameters" + "\n")
        for i in range(len(qm_charges)):
            xml.write(
                "<Particle"
                + " "
                + "q="
                + '"'
                + str(qm_charges[i])
                + '"'
                + " "
                + "eps="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "sig="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "atom="
                + '"'
                + str(atom_name_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Charge Parameters" + "\n")
        xml.close()

    def write_reparameterised_system_xml(self):
        """
        Writes a reparameterised XML force field file for the ligand.
        """
        # Bond Parameters
        f_params = open(self.system_qm_params_file, "r")
        lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [
                comb_1,
                comb_2,
                comb_3,
                comb_4,
                comb_5,
                comb_6,
            ]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()

        f_params = open(self.system_qm_params_file)
        lines_params = f_params.readlines()
        # Charge Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Charge Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Charge Parameters" in lines_params[i]:
                to_end = int(i)
        charge_params = lines_params[to_begin + 1 : to_end]
        non_bonded_index = []
        for k in charge_params:
            non_bonded_index.append(int(re.findall("[-+]?\d*\.\d+|\d+", k)[3]))
        charge_for_index = []
        for k in charge_params:
            charge_for_index.append(
                float(re.findall("[-+]?\d*\.\d+|\d+", k)[0])
            )

        xml_off = open(self.system_xml)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)
        nonbond_params = xml_off_lines[to_begin + 4 : to_end - 1]
        # print(len(nonbond_params))
        f_non_bonded = open(self.system_xml_non_bonded_file, "w")
        for x in nonbond_params:
            f_non_bonded.write(x)
        f_non_bonded = open(self.system_xml_non_bonded_file)
        lines_non_bonded = f_non_bonded.readlines()
        # print(len(lines_non_bonded))
        lines_non_bonded_to_write = []
        for i in range(len(non_bonded_index)):
            line_ = lines_non_bonded[non_bonded_index[i]]
            # print(line_)
            eps = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[0])
            sig = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[2])
            line_to_replace = (
                "                                "
                + "<Particle "
                + "eps="
                + '"'
                + str(eps)
                + '"'
                + " "
                + "q="
                + '"'
                + str(charge_for_index[i])
                + '"'
                + " "
                + "sig="
                + '"'
                + str(sig)
                + '"'
                + "/>"
            )
            lines_non_bonded_to_write.append(line_to_replace)
        data_ = list(zip(non_bonded_index, lines_non_bonded_to_write))

        df_non_bonded_params = pd.DataFrame(
            data_, columns=["line_index", "line"]
        )
        # print(df_non_bonded_params.head())
        f_non_bonded_ = open(self.system_xml_non_bonded_file)
        lines_non_bonded_ = f_non_bonded_.readlines()
        for i in range(len(lines_non_bonded_)):
            if i in non_bonded_index:
                lines_non_bonded_[i] = (
                    df_non_bonded_params.loc[
                        df_non_bonded_params.line_index == i, "line"
                    ].values[0]
                ) + "\n"
        # print(len(lines_non_bonded_))
        f_write_non_bonded_reparams = open(
            self.system_xml_non_bonded_reparams_file, "w"
        )
        for p in range(len(lines_non_bonded_)):
            f_write_non_bonded_reparams.write(lines_non_bonded_[p])
        f_write_non_bonded_reparams.close()
        f_ = open(self.system_xml_non_bonded_reparams_file)
        lines_ = f_.readlines()
        print(len(lines_) == len(lines_non_bonded))

        xml_off = open(self.reparameterised_intermediate_system_xml_file)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)

        lines_before_params = xml_off_lines[: to_begin + 4]
        f__ = open(self.system_xml_non_bonded_reparams_file)
        lines_params_non_bonded = f__.readlines()
        lines_after_params = xml_off_lines[to_end - 1 :]
        f_reparams_xml = open(self.reparameterised_system_xml_file, "w")
        for x in lines_before_params:
            f_reparams_xml.write(x)
        for x in lines_params_non_bonded:
            f_reparams_xml.write(x)
        for x in lines_after_params:
            f_reparams_xml.write(x)
        f_reparams_xml.close()

    def save_amber_params(self):
        """
        Saves amber generated topology files for the ligand.
        """
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params,
        )

        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")

        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")

        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )

        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")

        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")

        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

    def analyze_diff_energies(self):
        """
        Compares the energies of the ligand obtained from the non-parameterized
        and the parameterized force field files.
        """
        parm_non_params = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params,
        )
        prmtop_energy_decomposition_non_params = parmed.openmm.energy_decomposition_system(
            parm_non_params, parm_non_params.createSystem()
        )
        prmtop_energy_decomposition_non_params_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_non_params
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_non_params_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_non_params = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_non_params_list,
                    prmtop_energy_decomposition_non_params_value,
                )
            ),
            columns=["Energy_term", "Energy_parm_non_params"],
        )
        df_energy_non_params = df_energy_non_params.set_index("Energy_term")
        # print(df_energy_non_params)
        parm_params = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )
        prmtop_energy_decomposition_params = parmed.openmm.energy_decomposition_system(
            parm_params, parm_params.createSystem()
        )
        prmtop_energy_decomposition_params_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem)
                        for elem in prmtop_energy_decomposition_params
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_params_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_params = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_params_list,
                    prmtop_energy_decomposition_params_value,
                )
            ),
            columns=["Energy_term", "Energy_parm_params"],
        )
        df_energy_params = df_energy_params.set_index("Energy_term")
        # print(df_energy_params)
        df_compare = pd.concat(
            [df_energy_non_params, df_energy_params], axis=1
        )
        df_compare["Energy_difference"] = df_compare[
            "Energy_parm_non_params"
        ].sub(df_compare["Energy_parm_params"], axis=0)
        print(df_compare)


class RunOpenMMSims:

    """
    A class used to run the OpenMM simulation on any specified system.

    This class contain methods to run a MD simulation to confirm the
    proper structure of the reparameterized forcefield files.


    ...

    Attributes
    ----------
    system_prmtop : str
        Topology file of the system (receptor, ligand or
        receptor - ligand complex)

    system_inpcrd : str
        Coordinate file of the system (receptor, ligand or
        receptor - ligand complex)

    system_pdb: str
        PDB file of the system to run MD simulation (receptor,
        ligand or receptor - ligand complex).

    system_xml: str
        Serialised XML file for the system.

    sim_output: str, optional
        PDB file containing the trajectory coordinates for the OpenMM
        simulation.

    sim_steps: str, optional
        Number of steps in the OpenMM MD simulation.

    """

    def __init__(
        self,
        system_prmtop,
        system_inpcrd,
        system_pdb,
        system_xml,
        system_output="sim_output.pdb",
        sim_steps=1000,
    ):

        self.system_prmtop = system_prmtop
        self.system_inpcrd = system_inpcrd
        self.system_pdb = system_pdb
        self.system_xml = system_xml
        self.system_output = system_output
        self.sim_steps = sim_steps

    def run_openmm_prmtop_inpcrd(self):
        """
        Runs OpenMM MD simulation with prmtop and inpcrd file.
        """
        print(
            "Running OpenMM simulation for "
            + self.system_prmtop
            + " and "
            + self.system_inpcrd
        )
        prmtop = simtk.openmm.app.AmberPrmtopFile(self.system_prmtop)
        inpcrd = simtk.openmm.app.AmberInpcrdFile(self.system_inpcrd)
        system = prmtop.createSystem()
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            prmtop.topology, system, integrator
        )
        simulation.context.setPositions(inpcrd.positions)
        if inpcrd.boxVectors is not None:
            simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)

    def run_openmm_prmtop_pdb(self):
        """
        Runs OpenMM MD simulation with prmtop and PDB file.
        """
        print(
            "Running OpenMM simulation for "
            + self.system_prmtop
            + " and "
            + self.system_pdb
        )
        pdb = simtk.openmm.app.PDBFile(self.system_pdb)
        prmtop = simtk.openmm.app.AmberPrmtopFile(self.system_prmtop)
        system = prmtop.createSystem()
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            prmtop.topology, system, integrator
        )
        simulation.context.setPositions(pdb.positions)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)

    def run_openmm_xml_pdb(self):
        """
        Runs OpenMM MD simulation with XML and PDB file.
        """
        print(
            "Running OpenMM simulation for "
            + self.system_xml
            + " and "
            + self.system_pdb
        )
        pdb = simtk.openmm.app.PDBFile(self.system_pdb)
        ff_xml_file = open(self.system_xml, "r")
        system = simtk.openmm.XmlSerializer.deserialize(ff_xml_file.read())
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            pdb.topology, system, integrator
        )
        simulation.context.setPositions(pdb.positions)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)


class MergeHostGuestTopology:

    """
    A class used to merge the host and guest topology and coordinate
    files.

    ...

    Attributes
    ----------
    host_prmtop : str
        Topology file of the receptor.

    guest_prmtop : str
        Topology file of the ligand.

    host_inpcrd : str
        Coordinate file of the receptor.

    guest_inpcrd : str
        Coordinate file of the ligand.

    system_prmtop : str
        Topology file of the receptor - ligand complex.

    system_inpcrd : str
        Coordinate file of the receptor - ligand complex.

    """

    def __init__(
        self,
        host_prmtop,
        guest_prmtop,
        host_inpcrd,
        guest_inpcrd,
        system_prmtop,
        system_inpcrd,
    ):

        self.host_prmtop = host_prmtop
        self.guest_prmtop = guest_prmtop
        self.host_inpcrd = host_inpcrd
        self.guest_inpcrd = guest_inpcrd
        self.system_prmtop = system_prmtop
        self.system_inpcrd = system_inpcrd

    def merge_topology_files(self):
        """
        Merge the host and guest topology and coordinate files.
        """
        print(
            "Merging the "
            + self.host_prmtop
            + " "
            + self.guest_prmtop
            + " files"
        )
        print(
            "Merging the "
            + self.host_inpcrd
            + " "
            + self.guest_inpcrd
            + " files"
        )
        host_system = parmed.load_file(self.host_prmtop, xyz=self.host_inpcrd)
        guest_system = parmed.load_file(
            self.guest_prmtop, xyz=self.guest_inpcrd
        )
        system = host_system + guest_system
        system.save(self.system_prmtop, overwrite=True)
        system.save(self.system_inpcrd, overwrite=True)


class TorsionDriveSims:

    """
    A class used to create a filetree for torsion scan
    using torsionsdrive for the dihedral angles of the ligand.

    This class creates a directory for carrying out torsiondrive
    calculations followed by fitting of torsional parameters. Methods
    in this class are used to run torsiondrive calculations either for
    all of the torsional angles, or for non-hydrogen / heavy atoms
    contributing to the torsional angle.

    ...

    Attributes
    ----------
    charge : int, optional
        Charge of the ligand.

    multiplicity: int, optional
        Spin Multiplicity (2S+1) of the ligand where S represents
        the total spin of the ligand.

    reparameterised_system_xml_file : str, optional
        Reparamaterixed XML force field for the ligand.

    torsion_xml_file : str, optional
        A text file containing torsional parameters from
        reparameterised XML file.

    xyz_file : str, optional
        XYZ file containing the coordinates of the guest molecule.

    psi_input_file : str, optional
        Input file for psi4 QM engine.

    memory : int, optional
        Memory (in GB) to be used.

    basis_set: str, optional
        Basis set to use for the QM engine.

    functional: str, optional
        Exchange/Correlation or hybrid Functional for the QM engine.

    iterations : int, optional
        Maximum number of geometry optimization steps.

    method_torsion_drive : str, optional
        The algorithm/package to use while running the torsiondrive
        scan. Using --native_opt uses QM program native constrained
        optimization algorithm and turns off geomeTRIC package.

    system_bonds_file : str, optional
        Text file containing bond parameters for the ligand.

    tor_dir : str, optional
        Torsiondrive directory containing separate torsiondrive
        folders, each containing files for a separate torsiondrive
        calculation for a particular dihedral angle.

    dihedral_text_file : str, optional
        Dihedral information file for torsiondrive.

    template_pdb : str, optional
        Guest PDB with atoms beginning from 1 to be used as a
        template PDB to retrieve atom indices and symbols.

    torsion_drive_run_file : str, optional
        bash file for torsiondrive calculations.

    dihedral_interval : int, optional
        Grid spacing for dihedral scan, i.e. every n degrees
        (where n is an integer), multiple values will be mapped
        to each dihedral angle.

    engine : str, optional
        Engine for running torsiondrive scan.

    energy_threshold : float, optional
        Only activate grid points if the new optimization is lower than
        the previous lowest energy (in a.u.).

    """

    def __init__(
        self,
        charge=0,
        multiplicity=1,
        reparameterised_system_xml_file="guest_reparameterised.xml",
        torsion_xml_file="guest_torsion_xml.txt",
        xyz_file="guest_coords.xyz",
        psi_input_file="torsion_drive_input.dat",
        memory=50,
        basis_set="6-31G",
        functional="B3LYP",
        iterations=2000,
        method_torsion_drive="native_opt",
        system_bonds_file="guest_bonds.txt",
        tor_dir="torsion_dir",
        dihedral_text_file="dihedrals.txt",
        template_pdb="guest_init_II.pdb",
        torsion_drive_run_file="run_command",
        dihedral_interval=15,
        engine="psi4",
        energy_threshold=0.00001,
    ):

        self.charge = charge
        self.multiplicity = multiplicity
        self.reparameterised_system_xml_file = reparameterised_system_xml_file
        self.torsion_xml_file = torsion_xml_file
        self.xyz_file = xyz_file
        self.psi_input_file = psi_input_file
        self.memory = memory
        self.basis_set = basis_set
        self.functional = functional
        self.iterations = iterations
        self.method_torsion_drive = method_torsion_drive
        self.system_bonds_file = system_bonds_file
        self.tor_dir = tor_dir
        self.dihedral_text_file = dihedral_text_file
        self.template_pdb = template_pdb
        self.torsion_drive_run_file = torsion_drive_run_file
        self.dihedral_interval = dihedral_interval
        self.engine = engine
        self.energy_threshold = energy_threshold

    def write_torsion_drive_run_file(self):
        """
        Saves a bash file for running torsion scans for torsiondrive.
        """
        if self.method_torsion_drive == "geometric":
            torsion_command = (
                "torsiondrive-launch"
                + " "
                + self.psi_input_file
                + " "
                + self.dihedral_text_file
                + " "
                + "-g"
                + " "
                + str(self.dihedral_interval)
                + " "
                + "-e"
                + " "
                + self.engine
                + " "
                + "--energy_thresh"
                + " "
                + str(self.energy_threshold)
                + " "
                + "-v"
            )
        if self.method_torsion_drive == "native_opt":
            torsion_command = (
                "torsiondrive-launch"
                + " "
                + self.psi_input_file
                + " "
                + self.dihedral_text_file
                + " "
                + "-g"
                + " "
                + str(self.dihedral_interval)
                + " "
                + "-e"
                + " "
                + self.engine
                + " "
                + "--energy_thresh"
                + " "
                + str(self.energy_threshold)
                + " "
                + "--"
                + self.method_torsion_drive
                + " "
                + "-v"
            )
        print(torsion_command)
        with open(self.torsion_drive_run_file, "w") as f:
            f.write(torsion_command)

    def write_tor_params_txt(self):
        """
        Saves a text file containing torsional parameters from the reparameterized XML
        force field file.
        """
        xml_off = open(self.reparameterised_system_xml_file, "r")
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<Torsions>" in xml_off_lines[i]:
                to_begin = int(i)
            if "</Torsions>" in xml_off_lines[i]:
                to_end = int(i)
        torsion_params = xml_off_lines[to_begin + 1 : to_end]

        k_list_off = []
        for i in range(len(torsion_params)):
            k_list_off.append(
                float(re.findall("\d*\.?\d+", torsion_params[i])[0])
            )
        k_list_off = [round(num, 10) for num in k_list_off]
        # print(k_list_off)
        p1 = []
        for i in range(len(torsion_params)):
            p1.append(int(re.findall("\d*\.?\d+", torsion_params[i])[2]))
        p1 = [i + 1 for i in p1]
        # print(p1)
        p2 = []
        for i in range(len(torsion_params)):
            p2.append(int(re.findall("\d*\.?\d+", torsion_params[i])[4]))
        p2 = [i + 1 for i in p2]
        # print(p2)
        p3 = []
        for i in range(len(torsion_params)):
            p3.append(int(re.findall("\d*\.?\d+", torsion_params[i])[6]))
        p3 = [i + 1 for i in p3]
        # print(p3)
        p4 = []
        for i in range(len(torsion_params)):
            p4.append(int(re.findall("\d*\.?\d+", torsion_params[i])[8]))
        p4 = [i + 1 for i in p4]
        # print(p4)
        periodicity = []
        for i in range(len(torsion_params)):
            periodicity.append(
                int(re.findall("\d*\.?\d+", torsion_params[i])[9])
            )
        # print(periodicity)
        phase = []
        for i in range(len(torsion_params)):
            phase.append(float(re.findall("\d*\.?\d+", torsion_params[i])[10]))
        phase = [round(num, 8) for num in phase]
        # print(phase)
        data_tuples = list(zip(k_list_off, p1, p2, p3, p4, periodicity, phase))
        df_tor = pd.DataFrame(
            data_tuples,
            columns=["k", "p1", "p2", "p3", "p4", "periodicity", "phase",],
        )
        # print(df_tor.head())
        df_tor.to_csv(
            self.torsion_xml_file, index=False, header=False, sep=" "
        )

    def write_psi4_input(self):
        """
        Writes a psi4 input QM file.
        """
        xyz_lines = open(self.xyz_file, "r").readlines()[2:]
        with open(self.psi_input_file, "w") as f:
            f.write("memory" + " " + str(self.memory) + " " + "GB" + "\n")
            f.write("molecule" + " " + "{" + "\n")
            f.write(str(self.charge) + " " + str(self.multiplicity) + "\n")
            for line in xyz_lines:
                f.write(line)
            f.write("}" + "\n")
            f.write("set" + " " + "{" + "\n")
            f.write("basis" + " " + self.basis_set + "\n")
            if self.method_torsion_drive == "native_opt":
                f.write("GEOM_MAXITER" + " " + str(self.iterations) + "\n")
            f.write("}" + "\n")
            if self.method_torsion_drive == "native_opt":
                f.write(
                    "optimize" + "(" + "'" + self.functional + "'" ")" + "\n"
                )
            if self.method_torsion_drive == "geometric":
                f.write(
                    "gradient" + "(" + "'" + self.functional + "'" ")" + "\n"
                )

    def create_torsion_drive_dir(self):
        """
        Creates a directory for carrying out torsiondrive
        calculations for all the proper dihedral angles.
        """
        df_tor = pd.read_csv(
            self.torsion_xml_file, header=None, delimiter=r"\s+"
        )
        df_tor.columns = [
            "k",
            "p1",
            "p2",
            "p3",
            "p4",
            "periodicity",
            "phase",
        ]
        # print(df_tor.head())
        df_dihedrals = df_tor[["p1", "p2", "p3", "p4"]]
        # print(df_dihedrals.head())
        dihedrals_list_list = []
        for i in range(len(df_dihedrals)):
            dihedrals_list_list.append(df_dihedrals.iloc[i].values.tolist())
        set_list = set()
        unique_dihedrals_list_list = []
        for x in dihedrals_list_list:
            srtd = tuple(sorted(x))
            if srtd not in set_list:
                unique_dihedrals_list_list.append(x)
                set_list.add(srtd)
        # print(unique_dihedrals_list_list)
        os.system("rm -rf " + self.tor_dir)
        os.system("mkdir " + self.tor_dir)
        parent_cwd = os.getcwd()
        shutil.copy(
            parent_cwd + "/" + self.psi_input_file,
            parent_cwd + "/" + self.tor_dir + "/" + self.psi_input_file,
        )
        shutil.copy(
            parent_cwd + "/" + self.template_pdb,
            parent_cwd + "/" + self.tor_dir + "/" + self.template_pdb,
        )
        shutil.copy(
            parent_cwd + "/" + self.torsion_drive_run_file,
            parent_cwd
            + "/"
            + self.tor_dir
            + "/"
            + self.torsion_drive_run_file,
        )
        os.chdir(parent_cwd + "/" + self.tor_dir)
        torsion_drive_dir = os.getcwd()
        for i in range(len(unique_dihedrals_list_list)):
            dir_name = "torsion_drive" + "_" + str(i)
            os.system("rm -rf " + dir_name)
            os.system("mkdir " + dir_name)
            os.chdir(torsion_drive_dir + "/" + dir_name)
            with open(self.dihedral_text_file, "w") as f:
                f.write(
                    "# dihedral definition by atom indices starting from 1"
                    + "\n"
                )
                f.write("# i     j     k     l" + "\n")
                i_ = unique_dihedrals_list_list[i][0]
                j_ = unique_dihedrals_list_list[i][1]
                k_ = unique_dihedrals_list_list[i][2]
                l_ = unique_dihedrals_list_list[i][3]
                f.write(
                    " "
                    + "{:< 6d}".format(i_)
                    + "{:< 6d}".format(j_)
                    + "{:< 6d}".format(k_)
                    + "{:< 6d}".format(l_)
                    + "\n"
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.psi_input_file,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.psi_input_file,
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.template_pdb,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.template_pdb,
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.torsion_drive_run_file,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.torsion_drive_run_file,
                )
                os.chdir(torsion_drive_dir)
        os.system("rm -rf " + self.psi_input_file)
        os.system("rm -rf " + self.template_pdb)
        os.system("rm -rf " + self.torsion_drive_run_file)
        os.chdir(parent_cwd)

    def create_non_H_torsion_drive_dir(self):
        """
        Creates a directory for carrying out torsiondrive
        calculations for all non-hydrogen torsional angles.
        """
        df_tor = pd.read_csv(
            self.torsion_xml_file, header=None, delimiter=r"\s+"
        )
        df_tor.columns = [
            "k",
            "p1",
            "p2",
            "p3",
            "p4",
            "periodicity",
            "phase",
        ]
        # print(df_tor.head())
        ppdb = PandasPdb()
        ppdb.read_pdb(self.template_pdb)
        df_index_symbol = ppdb.df["ATOM"][["atom_number", "element_symbol"]]
        # print(df_index_symbol.head())
        df_dihedrals = df_tor[["p1", "p2", "p3", "p4"]]
        # print(df_dihedrals.head())
        dihedrals_list_list = []
        for i in range(len(df_dihedrals)):
            dihedrals_list_list.append(df_dihedrals.iloc[i].values.tolist())
        set_list = set()
        unique_dihedrals_list_list = []
        for x in dihedrals_list_list:
            srtd = tuple(sorted(x))
            if srtd not in set_list:
                unique_dihedrals_list_list.append(x)
                set_list.add(srtd)
        # print(unique_dihedrals_list_list)
        atom_dihedral_list = []
        for sub_list in unique_dihedrals_list_list:
            atom_dihedral_list.append(
                [
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[0]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[1]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[2]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[3]
                    ]["element_symbol"].to_list()[0],
                ]
            )
        # print(atom_dihedral_list)
        index_to_include = []
        for i in range(len(atom_dihedral_list)):
            if "H" not in atom_dihedral_list[i]:
                index_to_include.append(i)
        non_H_dihedrals = []
        for i in index_to_include:
            non_H_dihedrals.append(unique_dihedrals_list_list[i])
        # print(non_H_dihedrals)
        non_H_atom_dihedral_list = []
        for sub_list in non_H_dihedrals:
            non_H_atom_dihedral_list.append(
                [
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[0]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[1]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[2]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[3]
                    ]["element_symbol"].to_list()[0],
                ]
            )
        print(non_H_atom_dihedral_list)
        os.system("rm -rf " + self.tor_dir)
        os.system("mkdir " + self.tor_dir)
        parent_cwd = os.getcwd()
        shutil.copy(
            parent_cwd + "/" + self.psi_input_file,
            parent_cwd + "/" + self.tor_dir + "/" + self.psi_input_file,
        )
        shutil.copy(
            parent_cwd + "/" + self.template_pdb,
            parent_cwd + "/" + self.tor_dir + "/" + self.template_pdb,
        )
        shutil.copy(
            parent_cwd + "/" + self.torsion_drive_run_file,
            parent_cwd
            + "/"
            + self.tor_dir
            + "/"
            + self.torsion_drive_run_file,
        )
        os.chdir(parent_cwd + "/" + self.tor_dir)
        torsion_drive_dir = os.getcwd()
        for i in range(len(non_H_dihedrals)):
            dir_name = "torsion_drive" + "_" + str(i)
            os.system("rm -rf " + dir_name)
            os.system("mkdir " + dir_name)
            os.chdir(torsion_drive_dir + "/" + dir_name)
            with open(self.dihedral_text_file, "w") as f:
                f.write(
                    "# dihedral definition by atom indices starting from 1"
                    + "\n"
                )
                f.write("# i     j     k     l" + "\n")
                i_ = non_H_dihedrals[i][0]
                j_ = non_H_dihedrals[i][1]
                k_ = non_H_dihedrals[i][2]
                l_ = non_H_dihedrals[i][3]
                f.write(
                    " "
                    + "{:< 6d}".format(i_)
                    + "{:< 6d}".format(j_)
                    + "{:< 6d}".format(k_)
                    + "{:< 6d}".format(l_)
                    + "\n"
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.psi_input_file,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.psi_input_file,
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.template_pdb,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.template_pdb,
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.torsion_drive_run_file,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.torsion_drive_run_file,
                )
                os.chdir(torsion_drive_dir)
        os.system("rm -rf " + self.psi_input_file)
        os.system("rm -rf " + self.template_pdb)
        os.system("rm -rf " + self.torsion_drive_run_file)
        os.chdir(parent_cwd)

    def create_non_H_bonded_torsion_drive_dir(self):
        """
        Creates a directory for carrying out torsiondrive
        calculations for all non-hydrogen bonded torsional angles.
        """
        df_tor = pd.read_csv(
            self.torsion_xml_file, header=None, delimiter=r"\s+"
        )
        df_tor.columns = [
            "k",
            "p1",
            "p2",
            "p3",
            "p4",
            "periodicity",
            "phase",
        ]
        # print(df_tor.head())
        ppdb = PandasPdb()
        ppdb.read_pdb(self.template_pdb)
        df_index_symbol = ppdb.df["ATOM"][["atom_number", "element_symbol"]]
        # print(df_index_symbol.head())
        df_dihedrals = df_tor[["p1", "p2", "p3", "p4"]]
        # print(df_dihedrals.head())
        dihedrals_list_list = []
        for i in range(len(df_dihedrals)):
            dihedrals_list_list.append(df_dihedrals.iloc[i].values.tolist())
        set_list = set()
        unique_dihedrals_list_list = []
        for x in dihedrals_list_list:
            srtd = tuple(sorted(x))
            if srtd not in set_list:
                unique_dihedrals_list_list.append(x)
                set_list.add(srtd)
        # print(unique_dihedrals_list_list)
        atom_dihedral_list = []
        for sub_list in unique_dihedrals_list_list:
            atom_dihedral_list.append(
                [
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[0]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[1]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[2]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[3]
                    ]["element_symbol"].to_list()[0],
                ]
            )
        # print(atom_dihedral_list)
        index_to_include = []
        for i in range(len(atom_dihedral_list)):
            if "H" not in atom_dihedral_list[i]:
                index_to_include.append(i)
        non_H_dihedrals = []
        for i in index_to_include:
            non_H_dihedrals.append(unique_dihedrals_list_list[i])
        # print(non_H_dihedrals)
        non_H_atom_dihedral_list = []
        for sub_list in non_H_dihedrals:
            non_H_atom_dihedral_list.append(
                [
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[0]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[1]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[2]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[3]
                    ]["element_symbol"].to_list()[0],
                ]
            )
        # print(non_H_atom_dihedral_list)
        df_bonds_all = pd.read_csv(
            self.system_bonds_file, header=None, delimiter=r"\s+"
        )
        df_bonds_all.columns = [
            "bond_names",
            "k",
            "angle",
            "b1",
            "b2",
        ]
        df_bonds = df_bonds_all[["b1", "b2"]]
        bonds_list_list = []
        for i in range(len(df_bonds)):
            bonds_list_list.append(df_bonds.iloc[i].values.tolist())
        # print(bonds_list_list)
        reverse_bond_list_list = []
        for i in bonds_list_list:
            reverse_bond_list_list.append(reverse_list(i))
        # print(reverse_bond_list_list)
        bond_list = bonds_list_list + reverse_bond_list_list
        # print(bond_list)
        non_H_dihedral_bonds_list = []
        for i in non_H_dihedrals:
            non_H_dihedral_bonds_list.append(
                [[i[0], i[1]], [i[1], i[2]], [i[2], i[3]]]
            )
        # print(non_H_dihedral_bonds_list)
        bonded_index_to_include = []
        for i in range(len(non_H_dihedral_bonds_list)):
            if [
                non_H_dihedral_bonds_list[i][0] in bond_list,
                non_H_dihedral_bonds_list[i][1] in bond_list,
                non_H_dihedral_bonds_list[i][2] in bond_list,
            ] == [True, True, True]:
                bonded_index_to_include.append(i)
        # print(bonded_index_to_include)
        non_H_bonded_dihedrals = []
        for i in bonded_index_to_include:
            non_H_bonded_dihedrals.append(non_H_dihedrals[i])
        # print(non_H_bonded_dihedrals)
        non_H_bonded_atom_dihedral_list = []
        for sub_list in non_H_bonded_dihedrals:
            non_H_bonded_atom_dihedral_list.append(
                [
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[0]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[1]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[2]
                    ]["element_symbol"].to_list()[0],
                    df_index_symbol.loc[
                        df_index_symbol["atom_number"] == sub_list[3]
                    ]["element_symbol"].to_list()[0],
                ]
            )
        print(non_H_bonded_atom_dihedral_list)
        os.system("rm -rf " + self.tor_dir)
        os.system("mkdir " + self.tor_dir)
        parent_cwd = os.getcwd()
        shutil.copy(
            parent_cwd + "/" + self.psi_input_file,
            parent_cwd + "/" + self.tor_dir + "/" + self.psi_input_file,
        )
        shutil.copy(
            parent_cwd + "/" + self.template_pdb,
            parent_cwd + "/" + self.tor_dir + "/" + self.template_pdb,
        )
        shutil.copy(
            parent_cwd + "/" + self.torsion_drive_run_file,
            parent_cwd
            + "/"
            + self.tor_dir
            + "/"
            + self.torsion_drive_run_file,
        )
        os.chdir(parent_cwd + "/" + self.tor_dir)
        torsion_drive_dir = os.getcwd()
        for i in range(len(non_H_bonded_dihedrals)):
            dir_name = "torsion_drive" + "_" + str(i)
            os.system("rm -rf " + dir_name)
            os.system("mkdir " + dir_name)
            os.chdir(torsion_drive_dir + "/" + dir_name)
            with open(self.dihedral_text_file, "w") as f:
                f.write(
                    "# dihedral definition by atom indices starting from 1"
                    + "\n"
                )
                f.write("# i     j     k     l" + "\n")
                i_ = non_H_bonded_dihedrals[i][0]
                j_ = non_H_bonded_dihedrals[i][1]
                k_ = non_H_bonded_dihedrals[i][2]
                l_ = non_H_bonded_dihedrals[i][3]
                f.write(
                    " "
                    + "{:< 6d}".format(i_)
                    + "{:< 6d}".format(j_)
                    + "{:< 6d}".format(k_)
                    + "{:< 6d}".format(l_)
                    + "\n"
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.psi_input_file,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.psi_input_file,
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.template_pdb,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.template_pdb,
                )
                shutil.copy(
                    torsion_drive_dir + "/" + self.torsion_drive_run_file,
                    torsion_drive_dir
                    + "/"
                    + dir_name
                    + "/"
                    + self.torsion_drive_run_file,
                )
                os.chdir(torsion_drive_dir)
        os.system("rm -rf " + self.psi_input_file)
        os.system("rm -rf " + self.template_pdb)
        os.system("rm -rf " + self.torsion_drive_run_file)
        os.chdir(parent_cwd)

    def run_torsion_sim(self):
        """
        Run torsion scans using torsiondrive locally.
        """
        parent_cwd = os.getcwd()
        target_dir = parent_cwd + "/" + self.tor_dir
        num_folders = 0
        for _, dirnames, filenames in os.walk(target_dir):
            num_folders += len(dirnames)
        for i in range(num_folders):
            dir_ = "torsion_drive" + "_" + str(i)
            os.chdir(parent_cwd + "/" + self.tor_dir + "/" + dir_)
            run_command = "bash" + " " + self.torsion_drive_run_file
            # os.system(run_command)
            print(run_command)
            os.chdir(parent_cwd)


class TorsionDriveParams:

    """

    A class used to parameterize the torsional parameters
    of the ligand by fitting the torsional parameters obtained
    from torsiondrive calculations.

    Previously obtained reparameterized XML forcefield file did
    not have the torsional parameters obtained from QM calculations.
    The torsional parameters obtained from torsiondrive scans are
    fitted and a new XML forcefield file is generated.

    ...

    Attributes
    ----------
    num_charge_atoms : int, optional
        Number of charged atoms in the molecule.

    index_charge_atom_1: int, optional
        Index of the first charged atom.

    charge_atom_1 : int, optional
        Charge on the first charged atom.

    tor_dir : str, optional
        Torsiondrive directory containing separate torsiondrive folders,
        each containing files for a separate torsiondrive calculation
        for a particular dihedral angle.

    reparameterized_torsional_params_file : str, optional
        Text file containing the forcefield parameters for the
        ligand previously obtained without torsional reparameterization.

    psi_input_file : str, optional
        Input file for psi4 QM engine.

    xyz_file : str, optional
        XYZ file for ligand coordinates.

    coords_file : str, optional
        Text file containing the XYZ coordinates of the ligand.

    template_pdb: str, optional
        Ligand PDB with atoms beginning from 1 to be used as a template PDB
        to retrieve atom indices and symbols.

    system_pdb: str, optional
        PDB file for the torsiondrive torsion scans

    system_sdf : str, optional
        Maximum number of geometry optimization steps.

    system_xml : str, optional
        XML force field file for the ligand.

    qm_scan_file : str, optional
        Output scan file for the torsiondrive scans.

    load_topology : str, optional
        Argument to specify how to load the topology. Can either
        be "openmm" or "parmed".

    method : str, optional
        Minimization method for fitting of torsional
        parameters.

    dihedral_text_file : str, optional
        Dihedral information file for torsiondrive.

    system_init_sdf : str, optional
        Ligand SDF (structure-data) format file. This file will be generated
        only if the ligand is charged.

    reparameterised_system_xml_file : str, optional
        Reparameterized force field XML file obtained using
        openforcefield without torsional reparamaterization.

    reparameterised_torsional_system_xml_file : str, optional
        XML force field file for the ligand obtained with
        torsional reparamaterization.

    """
    
    def __init__(
        self,
        # TODO: some of these variables are ints, and should be initialized as ints
        num_charge_atoms="",
        index_charge_atom_1="",
        charge_atom_1="",
        tor_dir="torsion_dir",
        reparameterized_torsional_params_file="reparameterized_torsional_params.txt",
        psi_input_file="torsion_drive_input.dat",
        xyz_file="torsion_drive_input.xyz",
        coords_file="torsion_drive_input.txt",
        template_pdb="guest_init_II.pdb",
        system_pdb="torsion_drive_input.pdb",
        system_sdf="torsion_drive_input.sdf",
        system_xml="torsion_drive_input.xml",
        qm_scan_file="scan.xyz",
        load_topology="openmm",
        method="L-BFGS-B",
        dihedral_text_file="dihedrals.txt",
        system_init_sdf="torsion_drive_input_init.sdf",
        reparameterised_system_xml_file="guest_reparameterised.xml",
        reparameterised_torsional_system_xml_file="guest_torsional_reparameterized.xml",
    ):

        self.num_charge_atoms = num_charge_atoms
        self.index_charge_atom_1 = index_charge_atom_1
        self.charge_atom_1 = charge_atom_1
        self.tor_dir = tor_dir
        self.reparameterized_torsional_params_file = (
            reparameterized_torsional_params_file
        )
        self.psi_input_file = psi_input_file
        self.xyz_file = xyz_file
        self.coords_file = coords_file
        self.template_pdb = template_pdb
        self.system_pdb = system_pdb
        self.system_sdf = system_sdf
        self.system_xml = system_xml
        self.qm_scan_file = qm_scan_file
        self.method = method
        self.dihedral_text_file = dihedral_text_file
        self.system_init_sdf = system_init_sdf
        self.load_topology = load_topology
        self.reparameterised_system_xml_file = reparameterised_system_xml_file
        self.reparameterised_torsional_system_xml_file = (
            reparameterised_torsional_system_xml_file
        )

    def write_reparams_torsion_lines(self):
        """
        Saves a text file containing torsional parameters for the ligand
        obtained through openforcefield.
        """
        torsional_parameters_list = []
        parent_cwd = os.getcwd()
        # TODO: use os.path.join
        target_dir = os.path.join(parent_cwd, self.tor_dir)
        # TODO: let's use a more informative variable name than 'i'
        for i in os.listdir(target_dir):
            os.chdir(os.path.join(parent_cwd, self.tor_dir, i))
            if os.path.isfile(self.qm_scan_file):
                print("Entering directory" + " : " + os.getcwd())
                torsiondrive_input_to_xyz(
                    psi_input_file=self.psi_input_file, xyz_file=self.xyz_file,
                )
                xyz_to_pdb(
                    xyz_file=self.xyz_file,
                    coords_file=self.coords_file,
                    template_pdb=self.template_pdb,
                    system_pdb=self.system_pdb,
                )
                generate_xml_from_charged_pdb_sdf(
                    system_pdb=self.system_pdb,
                    system_init_sdf=self.system_init_sdf,
                    system_sdf=self.system_sdf,
                    num_charge_atoms=self.num_charge_atoms,
                    index_charge_atom_1=self.index_charge_atom_1,
                    charge_atom_1=self.charge_atom_1,
                    system_xml=self.system_xml,
                )
                torsional_lines = get_torsional_lines(
                    template_pdb=self.template_pdb,
                    system_xml=self.system_xml,
                    qm_scan_file=self.qm_scan_file,
                    load_topology=self.load_topology,
                    method=self.method,
                    dihedral_text_file=self.dihedral_text_file,
                )
                # print(torsional_lines)
                torsional_parameters_list.append(torsional_lines)
                remove_mm_files(qm_scan_file=self.qm_scan_file)
                os.chdir(parent_cwd)
            else:
                print("Entering directory" + " : " + os.getcwd())
                print(
                    "Torsional Scan file not found, optimization may not \
                     be complete. Existing!!"
                )
                os.chdir(parent_cwd)
        torsional_parameters = [
            item for sublist in torsional_parameters_list for item in sublist
        ]
        with open(self.reparameterized_torsional_params_file, "w") as f:
            for i in torsional_parameters:
                f.write(i + "\n")

    def write_reparams_torsion_lines_charged(self):
        """
        Saves a text file containing torsional parameters for a charged ligand
        obtained through openforcefield.
        """
        torsional_parameters_list = []
        parent_cwd = os.getcwd()
        target_dir = os.path.join(parent_cwd, self.tor_dir)
        for i in os.listdir(target_dir):
            os.chdir(os.path.join(parent_cwd, self.tor_dir, i))
            if os.path.isfile(self.qm_scan_file):
                print("Entering directory" + " : " + os.getcwd())
                torsiondrive_input_to_xyz(
                    psi_input_file=self.psi_input_file, xyz_file=self.xyz_file,
                )
                xyz_to_pdb(
                    xyz_file=self.xyz_file,
                    coords_file=self.coords_file,
                    template_pdb=self.template_pdb,
                    system_pdb=self.system_pdb,
                )
                generate_xml_from_charged_pdb_sdf(
                    system_pdb=self.system_pdb,
                    system_init_sdf=self.system_init_sdf,
                    system_sdf=self.system_sdf,
                    num_charge_atoms=self.num_charge_atoms,
                    index_charge_atom_1=self.index_charge_atom_1,
                    charge_atom_1=self.charge_atom_1,
                    system_xml=self.system_xml,
                )
                torsional_lines = get_torsional_lines(
                    template_pdb=self.template_pdb,
                    system_xml=self.system_xml,
                    qm_scan_file=self.qm_scan_file,
                    load_topology=self.load_topology,
                    method=self.method,
                    dihedral_text_file=self.dihedral_text_file,
                )
                # print(torsional_lines)
                torsional_parameters_list.append(torsional_lines)
                remove_mm_files(qm_scan_file=self.qm_scan_file)
                os.chdir(parent_cwd)
            else:
                print("Entering directory" + " : " + os.getcwd())
                print(
                    "Torsional Scan file not found, optimization may not \
                     be complete. Existing!!"
                )
                os.chdir(parent_cwd)
        torsional_parameters = [
            item for sublist in torsional_parameters_list for item in sublist
        ]
        with open(self.reparameterized_torsional_params_file, "w") as f:
            for i in torsional_parameters:
                f.write(i + "\n")

    def write_torsional_reparams(self):
        """
        Generates a XML force field file for the ligand with reparameterized
        torsional parameters.
        """
        with open(self.reparameterized_torsional_params_file, "r") as xml_tor:
            xml_tor_lines = xml_tor.readlines()
        non_zero_k_tor = []
        for i in xml_tor_lines:
            to_find = "k=" + '"' + "0.0" + '"'
            if to_find not in i:
                non_zero_k_tor.append(i)
        # print(non_zero_k_tor)
        p1 = []
        for i in range(len(non_zero_k_tor)):
            p1.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[2]))
        # print(p1)
        p2 = []
        for i in range(len(non_zero_k_tor)):
            p2.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[4]))
        # print(p2)
        p3 = []
        for i in range(len(non_zero_k_tor)):
            p3.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[6]))
        # print(p3)
        p4 = []
        for i in range(len(non_zero_k_tor)):
            p4.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[8]))
        # print(p4)
        periodicity = []
        for i in range(len(non_zero_k_tor)):
            periodicity.append(
                int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[9])
            )
        # print(periodicity)
        # TODO: there may be a way to consolidate the reparametrization of 
        #  the XML file to obey the DRY principle
        xml_tor_reparams = open(self.reparameterised_system_xml_file, "r")
        xml_tor_reparams_lines = xml_tor_reparams.readlines()
        # A string template and formatting should be used here
        for j in range(len(xml_tor_reparams_lines)):
            for i in range(len(non_zero_k_tor)):
                to_find_tor = (
                    "p1="
                    + '"'
                    + str(p1[i])
                    + '"'
                    + " "
                    + "p2="
                    + '"'
                    + str(p2[i])
                    + '"'
                    + " "
                    + "p3="
                    + '"'
                    + str(p3[i])
                    + '"'
                    + " "
                    + "p4="
                    + '"'
                    + str(p4[i])
                    + '"'
                    + " "
                    + "periodicity="
                    + '"'
                    + str(periodicity[i])
                    + '"'
                )
                if to_find_tor in xml_tor_reparams_lines[j]:
                    # print(xml_tor_reparams_lines[j])
                    xml_tor_reparams_lines[j] = non_zero_k_tor[i]
        with open(self.reparameterised_torsional_system_xml_file, "w") as f:
            for i in xml_tor_reparams_lines:
                f.write(i)


class PrepareSolvatedParams:

    """
    A class used to integrate the parameterized topology
    files of the receptor - ligand complex and the solvent.

    This class contain methods to concatanate the solvent (and
    ions ) and the receptor - ligand complex in a single
    parameterized topology file (prmtop and inpcrd).

    ...

    Attributes
    ----------

    init_pdb : str
        Initial PDB file containing the receptor-ligand complex with
        solvent, ions, etc.

    intermediate_pdb : str, optional
        An intermediate PDB file formed during pdb4amber processing.

    solvent_pdb : str, optional
        PDB file containing the water, ions, etc.

    solvent_prmtop : str, optional
        Solvent topology file.

    solvent_inpcrd : str, optional
        Solvent coordinate file.

    solvent_amber_pdb : str, optional
        Solvent PDB file saved from Amber's tleap.

    solvent_leap : str, optional
        Solvent tleap file for parameterizing the solvent.

    system_prmtop : str, optional
        Topology file of the receptor - ligand complex.

    system_inpcrd : str, optional
        Coordinate file of the receptor - ligand complex.

    system_output: str, optional
        PDB file containing the trajectory coordinates for
        the OpenMM simulation.

    sim_steps: str, optional
        Number of steps in the OpenMM MD simulation.

    system_solvent_prmtop : str, optional
        Topology file of the receptor - ligand complex and
        the solvent.

    system_solvent_inpcrd : str, optional
        Coordinate file of the receptor - ligand complex and
        the solvent.

    system_solvent_pdb : str, optional
        PDB file of the receptor - ligand complex and
        the solvent.

    """

    def __init__(
        self,
        init_pdb,
        intermediate_pdb="intermediate.pdb",
        solvent_pdb="solvent.pdb",
        solvent_prmtop="solvent.prmtop",
        solvent_inpcrd="solvent.inpcrd",
        solvent_amber_pdb="solvent_amber.pdb",
        solvent_leap="solvent.leap",
        system_prmtop="system_torsional_params.prmtop",
        system_inpcrd="system_torsional_params.inpcrd",
        system_output="sim_output.pdb",
        sim_steps=1000,
        system_solvent_prmtop="system_qmmmrebind.prmtop",
        system_solvent_inpcrd="system_qmmmrebind.inpcrd",
        system_solvent_pdb="system_qmmmrebind.pdb",
    ):

        self.init_pdb = init_pdb
        self.intermediate_pdb = intermediate_pdb
        self.solvent_pdb = solvent_pdb
        self.solvent_prmtop = solvent_prmtop
        self.solvent_inpcrd = solvent_inpcrd
        self.solvent_amber_pdb = solvent_amber_pdb
        self.solvent_leap = solvent_leap
        self.system_prmtop = system_prmtop
        self.system_inpcrd = system_inpcrd
        self.system_output = system_output
        self.sim_steps = sim_steps
        self.system_solvent_prmtop = system_solvent_prmtop
        self.system_solvent_inpcrd = system_solvent_inpcrd
        self.system_solvent_pdb = system_solvent_pdb

    def create_solvent_pdb(self):
        """
        Generates a PDB file containing the solvent and the ions.
        """
        water_variables = ["HOH", "WAT"]
        ions = [
            "Na+",
            "Cs+",
            "K+",
            "Li+",
            "Rb+",
            "Cl-",
            "Br-",
            "F-",
            "I-",
            "Ca2",
        ]
        pdb_variables = ["END", "CRYST"]
        with open(self.init_pdb) as f1, open(self.intermediate_pdb, "w") as f2:
            for line in f1:
                if (
                    any(
                        water_variable in line
                        for water_variable in water_variables
                    )
                    or any(
                        pdb_variable in line for pdb_variable in pdb_variables
                    )
                    or any(ion in line for ion in ions)
                ):
                    f2.write(line)
        command = (
            "pdb4amber -i " + self.intermediate_pdb + " -o " + self.solvent_pdb
        )
        os.system(command)
        command = (
            "rm -rf "
            + self.solvent_pdb[:-4]
            + "_nonprot.pdb "
            + self.solvent_pdb[:-4]
            + "_renum.txt "
            + self.solvent_pdb[:-4]
            + "_sslink"
        )
        os.system(command)
        command = "rm -rf " + self.intermediate_pdb
        os.system(command)

    def parameterize_solvent_pdb(self):
        """
        Generates a topology file (prmtop) and a coordinate
        file (inpcrd) for the solvent system.
        """
        line_0 = " "
        line_1 = "source leaprc.protein.ff14SB"
        line_2 = "source leaprc.water.tip3p"
        line_3 = "loadAmberParams frcmod.ionsjc_tip3p"
        line_4 = "pdb = loadpdb " + self.solvent_pdb
        line_5 = (
            "saveamberparm pdb "
            + self.solvent_prmtop
            + " "
            + self.solvent_inpcrd
        )
        line_6 = "savepdb pdb " + self.solvent_amber_pdb
        line_7 = "quit"
        with open(self.solvent_leap, "w") as f:
            f.write(line_0 + "\n")
            f.write(line_1 + "\n")
            f.write(line_2 + "\n")
            f.write(line_3 + "\n")
            f.write(line_4 + "\n")
            f.write(line_5 + "\n")
            f.write(line_6 + "\n")
            f.write(line_7 + "\n")
        command = "tleap -f " + self.solvent_leap
        os.system(command)
        command = "rm -rf leap.log " + self.solvent_leap
        os.system(command)

    def run_openmm_solvent_prmtop_inpcrd(self):
        """
        Runs OpenMM MD simulation with prmtop and inpcrd file
        for the solvent.
        """
        print(
            "Running OpenMM simulation for "
            + self.solvent_prmtop
            + " and "
            + self.solvent_inpcrd
        )
        prmtop = simtk.openmm.app.AmberPrmtopFile(self.solvent_prmtop)
        inpcrd = simtk.openmm.app.AmberInpcrdFile(self.solvent_inpcrd)
        system = prmtop.createSystem()
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            prmtop.topology, system, integrator
        )
        simulation.context.setPositions(inpcrd.positions)
        if inpcrd.boxVectors is not None:
            simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)

    def run_openmm_solvent_prmtop_pdb(self):
        """
        Runs OpenMM MD simulation with prmtop and PDB file
        for the solvent.
        """
        print(
            "Running OpenMM simulation for "
            + self.solvent_prmtop
            + " and "
            + self.solvent_amber_pdb
        )
        pdb = simtk.openmm.app.PDBFile(self.solvent_amber_pdb)
        prmtop = simtk.openmm.app.AmberPrmtopFile(self.solvent_prmtop)
        system = prmtop.createSystem()
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            prmtop.topology, system, integrator
        )
        simulation.context.setPositions(pdb.positions)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)

    def merge_topology_files_system_solvent(self):
        """
        Merge the system and solvent topology and coordinate
        files.
        """
        print(
            "Merging the "
            + self.system_prmtop
            + " "
            + self.solvent_prmtop
            + " files"
        )
        print(
            "Merging the "
            + self.system_inpcrd
            + " "
            + self.solvent_inpcrd
            + " files"
        )
        system = parmed.load_file(self.system_prmtop, xyz=self.system_inpcrd)
        solvent = parmed.load_file(
            self.solvent_prmtop, xyz=self.solvent_inpcrd
        )
        system_solvent = system + solvent
        system_solvent.save(self.system_solvent_prmtop, overwrite=True)
        system_solvent.save(self.system_solvent_inpcrd, overwrite=True)
        system_solvent.save(self.system_solvent_pdb, overwrite=True)

    def run_openmm_system_solvent_prmtop_inpcrd(self):
        """
        Runs OpenMM MD simulation with prmtop and inpcrd file
        for the solvent - system complex.
        """
        print(
            "Running OpenMM simulation for "
            + self.system_solvent_prmtop
            + " and "
            + self.system_solvent_inpcrd
        )
        prmtop = simtk.openmm.app.AmberPrmtopFile(self.system_solvent_prmtop)
        inpcrd = simtk.openmm.app.AmberInpcrdFile(self.system_solvent_inpcrd)
        system = prmtop.createSystem()
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            prmtop.topology, system, integrator
        )
        simulation.context.setPositions(inpcrd.positions)
        if inpcrd.boxVectors is not None:
            simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)

    def run_openmm_system_solvent_prmtop_pdb(self):
        """
        Runs OpenMM MD simulation with prmtop and PDB file
        for the solvent - system complex.
        """
        print(
            "Running OpenMM simulation for "
            + self.system_solvent_prmtop
            + " and "
            + self.system_solvent_pdb
        )
        pdb = simtk.openmm.app.PDBFile(self.system_solvent_pdb)
        prmtop = simtk.openmm.app.AmberPrmtopFile(self.system_solvent_prmtop)
        system = prmtop.createSystem()
        integrator = simtk.openmm.LangevinIntegrator(
            300 * simtk.unit.kelvin,
            1 / simtk.unit.picosecond,
            0.002 * simtk.unit.picoseconds,
        )
        simulation = simtk.openmm.app.Simulation(
            prmtop.topology, system, integrator
        )
        simulation.context.setPositions(pdb.positions)
        simulation.minimizeEnergy(maxIterations=100000)
        simulation.reporters.append(
            simtk.openmm.app.PDBReporter(
                self.system_output, self.sim_steps / 10
            )
        )
        simulation.reporters.append(
            simtk.openmm.app.StateDataReporter(
                stdout,
                reportInterval=int(self.sim_steps / 10),
                step=True,
                potentialEnergy=True,
                temperature=True,
            )
        )
        simulation.step(self.sim_steps)
        command = "rm -rf " + self.system_output
        os.system(command)


class SystemAmberSystem:

    """
    A class used to generate a force field XML file for the system
    from the given amber forcefield topology files and
    regenerate the reparameterised forcefield XML file.

    This class contain methods to generate a XML force field through
    parmed if the amber forcefield topology files are given.
    Re-parameterized XML force field files are then generated from
    these XML focefield files. Different energy components such as
    bond, angle, torsional and non-bonded energies are computed for the
    non-reparametrized and the reparameterized force fields. Difference
    between the non-reparameterized and reparameterized force field energies
    can then be analyzed.
    ...

     Attributes
    ----------

    host_pdb: str, optional
        PDB file for the host.

    system_pdb: str, optional
        PDB file for the system (host, guest and solvent).

    prmtop_system: str, optional
        Topology file for the system (host, guest and solvent).

    system_xml: str, optional
        Serialised XML forcefield file generated by parmed.

    charge_parameter_file_guest: str, optional
        Receptor PDB file with atom numbers beginning from 1.

    guest_qm_pdb: str, optional
        Ligand PDB file with atom numbers beginning from 1.

    bond_parameter_file_guest: str, optional
        Text file containing the bond parameters for the ligand.

    angle_parameter_file_guest: str, optional
        Text file containing the angle parameters of the ligand.

    guest_qm_params_file: str, optional
        Text file containing QM obtained parameters for the ligand.

    charge_parameter_file_host: str, optional
        File containing the charges of receptor atoms and their
        corresponding atoms.

    bond_parameter_file_host: str, optional
        Text file containing the bond parameters for the receptor.

    host_qm_pdb: str, optional
        Receptor QM region's PDB file with atom numbers beginning from 1.

    angle_parameter_file_host: str, optional
        Text file containing the angle parameters of the receptor.

    host_qm_params_file: str, optional
        Text file containing QM obtained parameters for the receptor.

    host_guest_qm_params_file: str, optional
        Text file containing QM obtained parameters for the system.

    reparameterised_intermediate_system_xml_file: str, optional
        XML force field file with bond and angle parameter lines replaced by
        corresponding values obtained from the QM calculations.

    system_xml_non_bonded_file: str, optional
        Text file to write the NonBondedForce Charge Parameters from
        the non-parameterised system XML file.

    system_xml_non_bonded_reparams_file: str, optional
        Text file containing the non-bonded parameters parsed from the
        XML force field file.

    reparameterised_system_xml_file: str, optional
        Reparameterized force field XML file obtained using
        openforcefield.

    reparameterized_torsional_params_file : str, optional
        Text file containing the forcefield parameters for the
        ligand previously obtained without torsional reparameterization.

    reparameterised_intermediate_torsional_system_xml_file : str, optional
        XML force field file for the system (without the QM charges) obtained
        with torsional reparamaterization.

    reparameterised_torsional_system_xml_file : str, optional
        XML force field file for the system obtained with
        torsional reparamaterization.

    load_topology: str, optional
        Argument to specify how to load the topology. Can either be "openmm"
        or "parmed".

    non_reparameterised_system_xml_file: str, optional
        Non-reparameterized force field XML file.

    prmtop_system_non_params: str, optional
        Non-reparameterized topology file.

    inpcrd_system_non_params: str, optional
        Non-reparameterized INPCRD file.

    prmtop_system_intermediate_params: str, optional
        Reparameterized topology file but without the QM charges.

    inpcrd_system_intermediate_params: str, optional
        Reparameterized INPCRD file but without the QM charges.

    prmtop_system_params: str, optional
        Reparameterized topology file.

    inpcrd_system_params: str, optional
        Reparameterized INPCRD file.

    """

    def __init__(
        self,
        host_pdb="host.pdb",
        system_pdb="",
        prmtop_system="hostguest.parm7",
        system_xml="hostguest.xml",
        charge_parameter_file_guest="guest_qm_surround_charges.txt",
        guest_qm_pdb="guest_init_II.pdb",
        bond_parameter_file_guest="guest_bonds.txt",
        angle_parameter_file_guest="guest_angles.txt",
        guest_qm_params_file="guest_qm_params.txt",
        charge_parameter_file_host="host_qm_surround_charges.txt",
        bond_parameter_file_host="host_qm_bonds.txt",
        host_qm_pdb="host_qm.pdb",
        angle_parameter_file_host="host_qm_angles.txt",
        host_qm_params_file="host_qm_params.txt",
        host_guest_qm_params_file="host_guest_qm_params.txt",
        reparameterised_intermediate_system_xml_file="hostguest_intermediate.xml",
        system_xml_non_bonded_file="hostguest_non_bonded.txt",
        system_xml_non_bonded_reparams_file="hostguest_non_bonded_reparams.txt",
        reparameterised_system_xml_file="hostguest_reparameterised.xml",
        reparameterized_torsional_params_file="reparameterized_torsional_params.txt",
        reparameterised_intermediate_torsional_system_xml_file="reparameterized_torsional_params.txt",
        reparameterised_torsional_system_xml_file="hostguest_torsional_reparameterised.xml",
        load_topology="openmm",
        non_reparameterised_system_xml_file="hostguest.xml",
        prmtop_system_non_params="hostguest.parm7",
        inpcrd_system_non_params="hostguest_non_params.pdb",
        prmtop_system_intermediate_params="hostguest_intermediate.prmtop",
        inpcrd_system_intermediate_params="hostguest_intermediate.inpcrd",
        prmtop_system_params="hostguest_params.prmtop",
        inpcrd_system_params="hostguest_params.inpcrd",
    ):

        self.host_pdb = host_pdb
        self.system_pdb = system_pdb
        self.prmtop_system = prmtop_system
        self.system_xml = system_xml
        self.charge_parameter_file_guest = charge_parameter_file_guest
        self.guest_qm_pdb = guest_qm_pdb
        self.bond_parameter_file_guest = bond_parameter_file_guest
        self.angle_parameter_file_guest = angle_parameter_file_guest
        self.guest_qm_params_file = guest_qm_params_file
        self.charge_parameter_file_host = charge_parameter_file_host
        self.bond_parameter_file_host = bond_parameter_file_host
        self.host_qm_pdb = host_qm_pdb
        self.angle_parameter_file_host = angle_parameter_file_host
        self.host_qm_params_file = host_qm_params_file
        self.host_guest_qm_params_file = host_guest_qm_params_file
        self.reparameterised_intermediate_system_xml_file = (
            reparameterised_intermediate_system_xml_file
        )
        self.system_xml_non_bonded_file = system_xml_non_bonded_file
        self.system_xml_non_bonded_reparams_file = (
            system_xml_non_bonded_reparams_file
        )
        self.reparameterised_system_xml_file = reparameterised_system_xml_file
        self.reparameterized_torsional_params_file = (
            reparameterized_torsional_params_file
        )
        self.reparameterised_intermediate_torsional_system_xml_file = (
            reparameterised_intermediate_torsional_system_xml_file
        )
        self.reparameterised_torsional_system_xml_file = (
            reparameterised_torsional_system_xml_file
        )
        self.load_topology = load_topology
        self.non_reparameterised_system_xml_file = (
            non_reparameterised_system_xml_file
        )
        self.prmtop_system_non_params = prmtop_system_non_params
        self.inpcrd_system_non_params = inpcrd_system_non_params
        self.prmtop_system_intermediate_params = (
            prmtop_system_intermediate_params
        )
        self.inpcrd_system_intermediate_params = (
            inpcrd_system_intermediate_params
        )
        self.prmtop_system_params = prmtop_system_params
        self.inpcrd_system_params = inpcrd_system_params

    def generate_xml_from_prmtop(self):

        """
        Generates a serialsed XML forcefield file through parmed, given
        the PDB file and its corresponding topology file.
        """

        parm = parmed.load_file(self.prmtop_system, self.system_pdb)
        system = parm.createSystem()
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def write_guest_params_non_zero(self):

        """
        Saves the parameters of the ligand obtained from the QM log files
        in a text file starting from non-zero ( indexing begins from the
        index of the last atom of the receptor ).
        """

        # Charges from QM files
        df_charges = pd.read_csv(
            self.charge_parameter_file_guest, header=None, delimiter=r"\s+"
        )
        df_charges.columns = ["atom", "charges"]
        qm_charges = df_charges["charges"].values.tolist()
        qm_charges = [round(num, 6) for num in qm_charges]
        # print(qm_charges)
        # Bond Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        # atom_name_list = [i - 1 for i in atom_name_list]
        no_host_atoms = get_num_host_atoms(self.host_pdb)
        atom_name_list = [i - 1 + no_host_atoms for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.bond_parameter_file_guest, header=None, delimiter=r"\s+"
        )
        df.columns = ["bond", "k_bond", "bond_length", "bond_1", "bond_2"]
        # print(df.head())
        bond_1_list = df["bond_1"].values.tolist()
        bond_1_list = [x - 1 + min(atom_name_list) for x in bond_1_list]
        bond_2_list = df["bond_2"].values.tolist()
        bond_2_list = [x - 1 + min(atom_name_list) for x in bond_2_list]
        # print(bond_1_list)
        # print(bond_2_list)
        k_bond_list = df["k_bond"].values.tolist()
        k_bond_list = [
            i * KCAL_MOL_PER_KJ_MOL * ANGSTROMS_PER_NM**2 for i in k_bond_list
        ]  # kcal/mol * A^2 to kJ/mol * nm^2
        k_bond_list = [round(num, 10) for num in k_bond_list]
        # print(k_bond_list)
        bond_length_list = df["bond_length"].values.tolist()
        bond_length_list = [i / 10.00 for i in bond_length_list]
        bond_length_list = [round(num, 6) for num in bond_length_list]
        # print(bond_length_list)
        # Angle Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        # atom_name_list = [i - 1 for i in atom_name_list]
        no_host_atoms = get_num_host_atoms(self.host_pdb)
        atom_name_list = [i - 1 + no_host_atoms for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.angle_parameter_file_guest, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "angle",
            "k_angle",
            "angle_degrees",
            "angle_1",
            "angle_2",
            "angle_3",
        ]
        # print(df.head())
        angle_1_list = df["angle_1"].values.tolist()
        angle_1_list = [x - 1 + min(atom_name_list) for x in angle_1_list]
        # print(angle_1_list)
        angle_2_list = df["angle_2"].values.tolist()
        angle_2_list = [x - 1 + min(atom_name_list) for x in angle_2_list]
        # print(angle_2_list)
        angle_3_list = df["angle_3"].values.tolist()
        angle_3_list = [x - 1 + min(atom_name_list) for x in angle_3_list]
        # print(angle_3_list)
        k_angle_list = df["k_angle"].values.tolist()
        k_angle_list = [
            i * 4.184 for i in k_angle_list
        ]  # kcal/mol * radian^2 to kJ/mol * radian^2
        k_angle_list = [round(num, 6) for num in k_angle_list]
        # print(k_angle_list)
        angle_list = df["angle_degrees"].values.tolist()
        angle_list = [(i * math.pi) / 180.00 for i in angle_list]
        angle_list = [round(num, 6) for num in angle_list]
        # print(angle_list)
        xml = open(self.guest_qm_params_file, "w")
        xml.write("Begin writing the Bond Parameters" + "\n")
        for i in range(len(k_bond_list)):
            xml.write(
                "                                "
                + "<Bond"
                + " "
                + "d="
                + '"'
                + str(bond_length_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_bond_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(bond_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(bond_2_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Bond Parameters" + "\n")
        xml.write("Begin writing the Angle Parameters" + "\n")
        for i in range(len(k_angle_list)):
            xml.write(
                "                                "
                + "<Angle"
                + " "
                + "a="
                + '"'
                + str(angle_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_angle_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(angle_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(angle_2_list[i])
                + '"'
                + " "
                + "p3="
                + '"'
                + str(angle_3_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Angle Parameters" + "\n")
        xml.write("Begin writing the Charge Parameters" + "\n")
        for i in range(len(qm_charges)):
            xml.write(
                "<Particle"
                + " "
                + "q="
                + '"'
                + str(qm_charges[i])
                + '"'
                + " "
                + "eps="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "sig="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "atom="
                + '"'
                + str(atom_name_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Charge Parameters" + "\n")
        xml.close()

    def write_host_params(self):

        """
        Saves the parameters obtained from the QM log files of the
        receptor in a text file.
        """

        # Charges from QM files
        df_charges = pd.read_csv(
            self.charge_parameter_file_host, header=None, delimiter=r"\s+"
        )
        df_charges.columns = ["atom", "charges"]
        qm_charges = df_charges["charges"].values.tolist()
        qm_charges = [round(num, 6) for num in qm_charges]
        # print(qm_charges)
        # Bond Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        atom_name_list = [i - 1 for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.bond_parameter_file_host, header=None, delimiter=r"\s+"
        )
        df.columns = ["bond", "k_bond", "bond_length", "bond_1", "bond_2"]
        # print(df.head())
        bond_1_list = df["bond_1"].values.tolist()
        bond_1_list = [x - 1 + min(atom_name_list) for x in bond_1_list]
        bond_2_list = df["bond_2"].values.tolist()
        bond_2_list = [x - 1 + min(atom_name_list) for x in bond_2_list]
        # print(bond_1_list)
        # print(bond_2_list)
        k_bond_list = df["k_bond"].values.tolist()
        k_bond_list = [
            i * KCAL_MOL_PER_KJ_MOL * ANGSTROMS_PER_NM**2 for i in k_bond_list
        ]  # kcal/mol * A^2 to kJ/mol * nm^2
        k_bond_list = [round(num, 10) for num in k_bond_list]
        # print(k_bond_list)
        bond_length_list = df["bond_length"].values.tolist()
        bond_length_list = [i / 10.00 for i in bond_length_list]
        bond_length_list = [round(num, 6) for num in bond_length_list]
        # print(bond_length_list)
        # Angle Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.host_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        atom_name_list = [i - 1 for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.angle_parameter_file_host, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "angle",
            "k_angle",
            "angle_degrees",
            "angle_1",
            "angle_2",
            "angle_3",
        ]
        # print(df.head())
        angle_1_list = df["angle_1"].values.tolist()
        angle_1_list = [x - 1 + min(atom_name_list) for x in angle_1_list]
        # print(angle_1_list)
        angle_2_list = df["angle_2"].values.tolist()
        angle_2_list = [x - 1 + min(atom_name_list) for x in angle_2_list]
        # print(angle_2_list)
        angle_3_list = df["angle_3"].values.tolist()
        angle_3_list = [x - 1 + min(atom_name_list) for x in angle_3_list]
        # print(angle_3_list)
        k_angle_list = df["k_angle"].values.tolist()
        k_angle_list = [
            i * 4.184 for i in k_angle_list
        ]  # kcal/mol * radian^2 to kJ/mol * radian^2
        k_angle_list = [round(num, 6) for num in k_angle_list]
        # print(k_angle_list)
        angle_list = df["angle_degrees"].values.tolist()
        angle_list = [(i * math.pi) / 180.00 for i in angle_list]
        angle_list = [round(num, 6) for num in angle_list]
        # print(angle_list)
        xml = open(self.host_qm_params_file, "w")
        xml.write("Begin writing the Bond Parameters" + "\n")
        for i in range(len(k_bond_list)):
            xml.write(
                "                                "
                + "<Bond"
                + " "
                + "d="
                + '"'
                + str(bond_length_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_bond_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(bond_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(bond_2_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Bond Parameters" + "\n")
        xml.write("Begin writing the Angle Parameters" + "\n")
        for i in range(len(k_angle_list)):
            xml.write(
                "                                "
                + "<Angle"
                + " "
                + "a="
                + '"'
                + str(angle_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_angle_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(angle_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(angle_2_list[i])
                + '"'
                + " "
                + "p3="
                + '"'
                + str(angle_3_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Angle Parameters" + "\n")
        xml.write("Begin writing the Charge Parameters" + "\n")
        for i in range(len(qm_charges)):
            xml.write(
                "<Particle"
                + " "
                + "q="
                + '"'
                + str(qm_charges[i])
                + '"'
                + " "
                + "eps="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "sig="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "atom="
                + '"'
                + str(atom_name_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Charge Parameters" + "\n")
        xml.close()

    def merge_qm_params(self):

        """
        Saves the parameters of the ligand obtained from the QM log files
        in a text file starting from non-zero ( indexing begins from the
        index of the last atom of the receptor ).
        """

        # Bond Parameters Host
        f_params_host = open(self.host_qm_params_file, "r")
        lines_params_host = f_params_host.readlines()
        # Bond Parameters Host
        for i in range(len(lines_params_host)):
            if "Begin writing the Bond Parameters" in lines_params_host[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params_host[i]:
                to_end = int(i)
        bond_params_host = lines_params_host[to_begin + 1 : to_end]
        # Bond Parameters Guest
        f_params_guest = open(self.guest_qm_params_file, "r")
        lines_params_guest = f_params_guest.readlines()
        # Bond Parameters Guest
        for i in range(len(lines_params_guest)):
            if "Begin writing the Bond Parameters" in lines_params_guest[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params_guest[i]:
                to_end = int(i)
        bond_params_guest = lines_params_guest[to_begin + 1 : to_end]
        bond_systems_params = bond_params_host + bond_params_guest
        # Angle Parameters Host
        f_params_host = open(self.host_qm_params_file, "r")
        lines_params_host = f_params_host.readlines()
        # Angle Parameters Host
        for i in range(len(lines_params_host)):
            if "Begin writing the Angle Parameters" in lines_params_host[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params_host[i]:
                to_end = int(i)
        angle_params_host = lines_params_host[to_begin + 1 : to_end]
        # Angle Parameters Guest
        f_params_guest = open(self.guest_qm_params_file, "r")
        lines_params_guest = f_params_guest.readlines()
        # Angle Parameters Guest
        for i in range(len(lines_params_guest)):
            if "Begin writing the Angle Parameters" in lines_params_guest[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params_guest[i]:
                to_end = int(i)
        angle_params_guest = lines_params_guest[to_begin + 1 : to_end]
        angle_systems_params = angle_params_host + angle_params_guest
        # Charge Parameters Host
        f_params_host = open(self.host_qm_params_file, "r")
        lines_params_host = f_params_host.readlines()
        # Charge Parameters Host
        for i in range(len(lines_params_host)):
            if "Begin writing the Charge Parameters" in lines_params_host[i]:
                to_begin = int(i)
            if "Finish writing the Charge Parameters" in lines_params_host[i]:
                to_end = int(i)
        charge_params_host = lines_params_host[to_begin + 1 : to_end]
        # Charge Parameters Guest
        f_params_guest = open(self.guest_qm_params_file, "r")
        lines_params_guest = f_params_guest.readlines()
        # Charge Parameters Guest
        for i in range(len(lines_params_guest)):
            if "Begin writing the Charge Parameters" in lines_params_guest[i]:
                to_begin = int(i)
            if "Finish writing the Charge Parameters" in lines_params_guest[i]:
                to_end = int(i)
        charge_params_guest = lines_params_guest[to_begin + 1 : to_end]
        charge_systems_params = charge_params_host + charge_params_guest
        system_params = open(self.host_guest_qm_params_file, "w")
        system_params.write("Begin writing the Bond Parameters" + "\n")
        for i in range(len(bond_systems_params)):
            system_params.write(bond_systems_params[i])
        system_params.write("Finish writing the Bond Parameters" + "\n")
        system_params.write("Begin writing the Angle Parameters" + "\n")
        for i in range(len(angle_systems_params)):
            system_params.write(angle_systems_params[i])
        system_params.write("Finish writing the Angle Parameters" + "\n")
        system_params.write("Begin writing the Charge Parameters" + "\n")
        for i in range(len(charge_systems_params)):
            system_params.write(charge_systems_params[i])
        system_params.write("Finish writing the Charge Parameters" + "\n")
        system_params.close()

    def write_intermediate_reparameterised_system_xml(self):

        """
        Writes a reparameterised XML force field file for the
        system but without the QM obtained charges.
        """

        # Bond Parameters
        f_params = open(self.host_guest_qm_params_file, "r")
        lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [comb_1, comb_2, comb_3, comb_4, comb_5, comb_6]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()

    def write_reparameterised_system_xml(self):

        """
        Writes a reparameterised XML force field file for the system.
        """

        # Bond Parameters
        f_params = open(self.host_guest_qm_params_file, "r")
        lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [comb_1, comb_2, comb_3, comb_4, comb_5, comb_6]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()
        f_params = open(self.host_guest_qm_params_file)
        lines_params = f_params.readlines()
        # Charge Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Charge Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Charge Parameters" in lines_params[i]:
                to_end = int(i)
        charge_params = lines_params[to_begin + 1 : to_end]
        non_bonded_index = []
        for k in charge_params:
            non_bonded_index.append(int(re.findall("[-+]?\d*\.\d+|\d+", k)[3]))
        charge_for_index = []
        for k in charge_params:
            charge_for_index.append(
                float(re.findall("[-+]?\d*\.\d+|\d+", k)[0])
            )
        xml_off = open(self.system_xml)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)
        nonbond_params = xml_off_lines[to_begin + 4 : to_end - 1]
        # print(len(nonbond_params))
        f_non_bonded = open(self.system_xml_non_bonded_file, "w")
        for x in nonbond_params:
            f_non_bonded.write(x)
        f_non_bonded = open(self.system_xml_non_bonded_file)
        lines_non_bonded = f_non_bonded.readlines()
        # print(len(lines_non_bonded))
        lines_non_bonded_to_write = []
        for i in range(len(non_bonded_index)):
            line_ = lines_non_bonded[non_bonded_index[i]]
            # print(line_)
            eps = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[0])
            sig = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[2])
            line_to_replace = (
                "                                "
                + "<Particle "
                + "eps="
                + '"'
                + str(eps)
                + '"'
                + " "
                + "q="
                + '"'
                + str(charge_for_index[i])
                + '"'
                + " "
                + "sig="
                + '"'
                + str(sig)
                + '"'
                + "/>"
            )
            lines_non_bonded_to_write.append(line_to_replace)
        data_ = list(zip(non_bonded_index, lines_non_bonded_to_write))
        df_non_bonded_params = pd.DataFrame(
            data_, columns=["line_index", "line"]
        )
        # print(df_non_bonded_params.head())
        f_non_bonded_ = open(self.system_xml_non_bonded_file)
        lines_non_bonded_ = f_non_bonded_.readlines()
        for i in range(len(lines_non_bonded_)):
            if i in non_bonded_index:
                lines_non_bonded_[i] = (
                    df_non_bonded_params.loc[
                        df_non_bonded_params.line_index == i, "line"
                    ].values[0]
                ) + "\n"
        # print(len(lines_non_bonded_))
        f_write_non_bonded_reparams = open(
            self.system_xml_non_bonded_reparams_file, "w"
        )
        for p in range(len(lines_non_bonded_)):
            f_write_non_bonded_reparams.write(lines_non_bonded_[p])
        f_write_non_bonded_reparams.close()
        f_ = open(self.system_xml_non_bonded_reparams_file)
        lines_ = f_.readlines()
        print(len(lines_) == len(lines_non_bonded))
        xml_off = open(self.reparameterised_intermediate_system_xml_file)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)
        lines_before_params = xml_off_lines[: to_begin + 4]
        f__ = open(self.system_xml_non_bonded_reparams_file)
        lines_params_non_bonded = f__.readlines()
        lines_after_params = xml_off_lines[to_end - 1 :]
        f_reparams_xml = open(self.reparameterised_system_xml_file, "w")
        for x in lines_before_params:
            f_reparams_xml.write(x)
        for x in lines_params_non_bonded:
            f_reparams_xml.write(x)
        for x in lines_after_params:
            f_reparams_xml.write(x)
        f_reparams_xml.close()

    def write_torsional_reparams_intermediate(self):
        """
        Generates a XML force field file for the system ( without the
        QM charges ) with reparameterized torsional parameters of the ligand.
        """

        no_host_atoms = get_num_host_atoms(self.host_pdb)
        xml_tor = open(self.reparameterized_torsional_params_file, "r")
        xml_tor_lines = xml_tor.readlines()
        xml_tor_lines_renum = []
        for i in xml_tor_lines:
            i = i.replace(
                "p1=" + '"' + str(int(re.findall("\d*\.?\d+", i)[2])) + '"',
                "p1="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[2]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p2=" + '"' + str(int(re.findall("\d*\.?\d+", i)[4])) + '"',
                "p2="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[4]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p3=" + '"' + str(int(re.findall("\d*\.?\d+", i)[6])) + '"',
                "p3="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[6]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p4=" + '"' + str(int(re.findall("\d*\.?\d+", i)[8])) + '"',
                "p4="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[8]) + no_host_atoms))
                + '"',
            )
            xml_tor_lines_renum.append(i)

        non_zero_k_tor = []
        for i in xml_tor_lines_renum:
            to_find = "k=" + '"' + "0.0" + '"'
            if to_find not in i:
                non_zero_k_tor.append(i)
        # print(non_zero_k_tor)
        p1 = []
        for i in range(len(non_zero_k_tor)):
            p1.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[2]))
        # print(p1)
        p2 = []
        for i in range(len(non_zero_k_tor)):
            p2.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[4]))
        # print(p2)
        p3 = []
        for i in range(len(non_zero_k_tor)):
            p3.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[6]))
        # print(p3)
        p4 = []
        for i in range(len(non_zero_k_tor)):
            p4.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[8]))
        # print(p4)
        periodicity = []
        for i in range(len(non_zero_k_tor)):
            periodicity.append(
                int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[9])
            )
        # print(periodicity)
        xml_tor_reparams = open(
            self.reparameterised_intermediate_system_xml_file, "r"
        )
        xml_tor_reparams_lines = xml_tor_reparams.readlines()
        for j in range(len(xml_tor_reparams_lines)):
            for i in range(len(non_zero_k_tor)):
                to_find_tor = (
                    "p1="
                    + '"'
                    + str(p1[i])
                    + '"'
                    + " "
                    + "p2="
                    + '"'
                    + str(p2[i])
                    + '"'
                    + " "
                    + "p3="
                    + '"'
                    + str(p3[i])
                    + '"'
                    + " "
                    + "p4="
                    + '"'
                    + str(p4[i])
                    + '"'
                    + " "
                    + "periodicity="
                    + '"'
                    + str(periodicity[i])
                    + '"'
                )
                if to_find_tor in xml_tor_reparams_lines[j]:
                    print(xml_tor_reparams_lines[j])
                    xml_tor_reparams_lines[j] = non_zero_k_tor[i]
        with open(
            self.reparameterised_intermediate_torsional_system_xml_file, "w"
        ) as f:
            for i in xml_tor_reparams_lines:
                f.write(i)

    def write_torsional_reparams(self):
        """
        Generates a XML force field file for the system with reparameterized
        torsional parameters of the ligand.
        """

        no_host_atoms = get_num_host_atoms(self.host_pdb)
        xml_tor = open(self.reparameterized_torsional_params_file, "r")
        xml_tor_lines = xml_tor.readlines()
        xml_tor_lines_renum = []
        for i in xml_tor_lines:
            i = i.replace(
                "p1=" + '"' + str(int(re.findall("\d*\.?\d+", i)[2])) + '"',
                "p1="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[2]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p2=" + '"' + str(int(re.findall("\d*\.?\d+", i)[4])) + '"',
                "p2="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[4]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p3=" + '"' + str(int(re.findall("\d*\.?\d+", i)[6])) + '"',
                "p3="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[6]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p4=" + '"' + str(int(re.findall("\d*\.?\d+", i)[8])) + '"',
                "p4="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[8]) + no_host_atoms))
                + '"',
            )
            xml_tor_lines_renum.append(i)

        non_zero_k_tor = []
        for i in xml_tor_lines_renum:
            to_find = "k=" + '"' + "0.0" + '"'
            if to_find not in i:
                non_zero_k_tor.append(i)
        # print(non_zero_k_tor)
        p1 = []
        for i in range(len(non_zero_k_tor)):
            p1.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[2]))
        # print(p1)
        p2 = []
        for i in range(len(non_zero_k_tor)):
            p2.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[4]))
        # print(p2)
        p3 = []
        for i in range(len(non_zero_k_tor)):
            p3.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[6]))
        # print(p3)
        p4 = []
        for i in range(len(non_zero_k_tor)):
            p4.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[8]))
        # print(p4)
        periodicity = []
        for i in range(len(non_zero_k_tor)):
            periodicity.append(
                int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[9])
            )
        # print(periodicity)
        xml_tor_reparams = open(self.reparameterised_system_xml_file, "r")
        xml_tor_reparams_lines = xml_tor_reparams.readlines()
        for j in range(len(xml_tor_reparams_lines)):
            for i in range(len(non_zero_k_tor)):
                to_find_tor = (
                    "p1="
                    + '"'
                    + str(p1[i])
                    + '"'
                    + " "
                    + "p2="
                    + '"'
                    + str(p2[i])
                    + '"'
                    + " "
                    + "p3="
                    + '"'
                    + str(p3[i])
                    + '"'
                    + " "
                    + "p4="
                    + '"'
                    + str(p4[i])
                    + '"'
                    + " "
                    + "periodicity="
                    + '"'
                    + str(periodicity[i])
                    + '"'
                )
                if to_find_tor in xml_tor_reparams_lines[j]:
                    print(xml_tor_reparams_lines[j])
                    xml_tor_reparams_lines[j] = non_zero_k_tor[i]
        with open(self.reparameterised_torsional_system_xml_file, "w") as f:
            for i in xml_tor_reparams_lines:
                f.write(i)

    def save_amber_params_non_qm_charges(self):

        """
        Saves amber generated topology files for the system
        without the QM charges.
        """

        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(
                    self.reparameterised_intermediate_torsional_system_xml_file
                ),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(
                    self.reparameterised_intermediate_torsional_system_xml_file
                ),
            )
        openmm_system.save(
            self.prmtop_system_intermediate_params, overwrite=True
        )
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(
            self.inpcrd_system_intermediate_params, overwrite=True
        )
        parm = parmed.load_file(
            self.prmtop_system_intermediate_params,
            self.inpcrd_system_intermediate_params,
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(
                self.reparameterised_intermediate_torsional_system_xml_file
            ),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

    def save_amber_params(self):

        """
        Saves amber generated topology files for the system.
        """

        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(
                    self.reparameterised_torsional_system_xml_file
                ),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(
                    self.reparameterised_torsional_system_xml_file
                ),
            )
        openmm_system.save(self.prmtop_system_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.reparameterised_torsional_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)


class SystemGuestAmberSystem:

    """
    A class used to generate a force field XML file for the system
    from the given amber forcefield topology files and
    regenerate the reparameterised forcefield XML file but without
    the host QM parameters.

    This class contain methods to generate a XML force field through
    parmed if the amber forcefield topology files are given.
    Re-parameterized XML force field files are then generated from
    these XML focefield files. Different energy components such as
    bond, angle, torsional and non-bonded energies are computed for the
    non-reparametrized and the reparameterized force fields. Difference
    between the non-reparameterized and reparameterized force field energies
    can then be analyzed.
    ...

     Attributes
    ----------

    host_pdb: str, optional
        PDB file for the host.

    system_pdb: str, optional
        PDB file for the system (host, guest and solvent).

    prmtop_system: str, optional
        Topology file for the system (host, guest and solvent).

    system_xml: str, optional
        Serialised XML forcefield file generated by parmed.

    charge_parameter_file_guest: str, optional
        Receptor PDB file with atom numbers beginning from 1.

    guest_qm_pdb: str, optional
        Ligand PDB file with atom numbers beginning from 1.

    bond_parameter_file_guest: str, optional
        Text file containing the bond parameters for the ligand.

    angle_parameter_file_guest: str, optional
        Text file containing the angle parameters of the ligand.

    guest_qm_params_file: str, optional
        Text file containing QM obtained parameters for the ligand.

    reparameterised_intermediate_system_xml_file: str, optional
        XML force field file with bond and angle parameter lines replaced by
        corresponding values obtained from the QM calculations.

    system_xml_non_bonded_file: str, optional
        Text file to write the NonBondedForce Charge Parameters from
        the non-parameterised system XML file.

    system_xml_non_bonded_reparams_file: str, optional
        Text file containing the non-bonded parameters parsed from the
        XML force field file.

    reparameterised_system_xml_file: str, optional
        Reparameterized force field XML file obtained using
        openforcefield.

    reparameterized_torsional_params_file : str, optional
        Text file containing the forcefield parameters for the
        ligand previously obtained without torsional reparameterization.

    reparameterised_intermediate_torsional_system_xml_file : str, optional
        XML force field file for the system (without the QM charges) obtained
        with torsional reparamaterization.

    reparameterised_torsional_system_xml_file : str, optional
        XML force field file for the system obtained with
        torsional reparamaterization.

    load_topology: str, optional
        Argument to specify how to load the topology. Can either be "openmm"
        or "parmed".

    non_reparameterised_system_xml_file: str, optional
        Non-reparameterized force field XML file.

    prmtop_system_non_params: str, optional
        Non-reparameterized topology file.

    inpcrd_system_non_params: str, optional
        Non-reparameterized INPCRD file.

    prmtop_system_intermediate_params: str, optional
        Reparameterized topology file but without the QM charges.

    inpcrd_system_intermediate_params: str, optional
        Reparameterized INPCRD file but without the QM charges.

    prmtop_system_params: str, optional
        Reparameterized topology file.

    inpcrd_system_params: str, optional
        Reparameterized INPCRD file.

    """

    def __init__(
        self,
        host_pdb="host.pdb",
        system_pdb="",
        prmtop_system="hostguest.parm7",
        system_xml="hostguest.xml",
        charge_parameter_file_guest="guest_qm_surround_charges.txt",
        guest_qm_pdb="guest_init_II.pdb",
        bond_parameter_file_guest="guest_bonds.txt",
        angle_parameter_file_guest="guest_angles.txt",
        guest_qm_params_file="guest_qm_params.txt",
        reparameterised_intermediate_system_xml_file="hostguest_intermediate.xml",
        system_xml_non_bonded_file="hostguest_non_bonded.txt",
        system_xml_non_bonded_reparams_file="hostguest_non_bonded_reparams.txt",
        reparameterised_system_xml_file="hostguest_reparameterised.xml",
        reparameterized_torsional_params_file="reparameterized_torsional_params.txt",
        reparameterised_intermediate_torsional_system_xml_file="reparameterized_torsional_params.txt",
        reparameterised_torsional_system_xml_file="hostguest_torsional_reparameterised.xml",
        load_topology="openmm",
        non_reparameterised_system_xml_file="hostguest.xml",
        prmtop_system_non_params="hostguest.parm7",
        inpcrd_system_non_params="hostguest_non_params.pdb",
        prmtop_system_intermediate_params="hostguest_intermediate.prmtop",
        inpcrd_system_intermediate_params="hostguest_intermediate.inpcrd",
        prmtop_system_params="hostguest_params.prmtop",
        inpcrd_system_params="hostguest_params.inpcrd",
    ):

        self.host_pdb = host_pdb
        self.system_pdb = system_pdb
        self.prmtop_system = prmtop_system
        self.system_xml = system_xml
        self.charge_parameter_file_guest = charge_parameter_file_guest
        self.guest_qm_pdb = guest_qm_pdb
        self.bond_parameter_file_guest = bond_parameter_file_guest
        self.angle_parameter_file_guest = angle_parameter_file_guest
        self.guest_qm_params_file = guest_qm_params_file
        self.reparameterised_intermediate_system_xml_file = (
            reparameterised_intermediate_system_xml_file
        )
        self.system_xml_non_bonded_file = system_xml_non_bonded_file
        self.system_xml_non_bonded_reparams_file = (
            system_xml_non_bonded_reparams_file
        )
        self.reparameterised_system_xml_file = reparameterised_system_xml_file
        self.reparameterized_torsional_params_file = (
            reparameterized_torsional_params_file
        )
        self.reparameterised_intermediate_torsional_system_xml_file = (
            reparameterised_intermediate_torsional_system_xml_file
        )
        self.reparameterised_torsional_system_xml_file = (
            reparameterised_torsional_system_xml_file
        )
        self.load_topology = load_topology
        self.non_reparameterised_system_xml_file = (
            non_reparameterised_system_xml_file
        )
        self.prmtop_system_non_params = prmtop_system_non_params
        self.inpcrd_system_non_params = inpcrd_system_non_params
        self.prmtop_system_intermediate_params = (
            prmtop_system_intermediate_params
        )
        self.inpcrd_system_intermediate_params = (
            inpcrd_system_intermediate_params
        )
        self.prmtop_system_params = prmtop_system_params
        self.inpcrd_system_params = inpcrd_system_params

    def generate_xml_from_prmtop(self):

        """
        Generates a serialsed XML forcefield file through parmed, given
        the PDB file and its corresponding topology file.
        """

        parm = parmed.load_file(self.prmtop_system, self.system_pdb)
        system = parm.createSystem()
        with open(self.system_xml, "w") as f:
            f.write(simtk.openmm.XmlSerializer.serialize(system))

    def write_guest_params_non_zero(self):

        """
        Saves the parameters of the ligand obtained from the QM log files
        in a text file starting from non-zero ( indexing begins from the
        index of the last atom of the receptor ).
        """

        # Charges from QM files
        df_charges = pd.read_csv(
            self.charge_parameter_file_guest, header=None, delimiter=r"\s+"
        )
        df_charges.columns = ["atom", "charges"]
        qm_charges = df_charges["charges"].values.tolist()
        qm_charges = [round(num, 6) for num in qm_charges]
        # print(qm_charges)
        # Bond Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        # atom_name_list = [i - 1 for i in atom_name_list]
        no_host_atoms = get_num_host_atoms(self.host_pdb)
        atom_name_list = [i - 1 + no_host_atoms for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.bond_parameter_file_guest, header=None, delimiter=r"\s+"
        )
        df.columns = ["bond", "k_bond", "bond_length", "bond_1", "bond_2"]
        # print(df.head())
        bond_1_list = df["bond_1"].values.tolist()
        bond_1_list = [x - 1 + min(atom_name_list) for x in bond_1_list]
        bond_2_list = df["bond_2"].values.tolist()
        bond_2_list = [x - 1 + min(atom_name_list) for x in bond_2_list]
        # print(bond_1_list)
        # print(bond_2_list)
        k_bond_list = df["k_bond"].values.tolist()
        k_bond_list = [
            i * KCAL_MOL_PER_KJ_MOL * ANGSTROMS_PER_NM**2 for i in k_bond_list
        ]  # kcal/mol * A^2 to kJ/mol * nm^2
        k_bond_list = [round(num, 10) for num in k_bond_list]
        # print(k_bond_list)
        bond_length_list = df["bond_length"].values.tolist()
        bond_length_list = [i / 10.00 for i in bond_length_list]
        bond_length_list = [round(num, 6) for num in bond_length_list]
        # print(bond_length_list)
        # Angle Parameters from QM files
        ppdb = PandasPdb()
        ppdb.read_pdb(self.guest_qm_pdb)
        atom_name_list = ppdb.df["ATOM"]["atom_number"].values.tolist()
        # atom_name_list = [i - 1 for i in atom_name_list]
        no_host_atoms = get_num_host_atoms(self.host_pdb)
        atom_name_list = [i - 1 + no_host_atoms for i in atom_name_list]
        # print(atom_name_list)
        df = pd.read_csv(
            self.angle_parameter_file_guest, header=None, delimiter=r"\s+"
        )
        df.columns = [
            "angle",
            "k_angle",
            "angle_degrees",
            "angle_1",
            "angle_2",
            "angle_3",
        ]
        # print(df.head())
        angle_1_list = df["angle_1"].values.tolist()
        angle_1_list = [x - 1 + min(atom_name_list) for x in angle_1_list]
        # print(angle_1_list)
        angle_2_list = df["angle_2"].values.tolist()
        angle_2_list = [x - 1 + min(atom_name_list) for x in angle_2_list]
        # print(angle_2_list)
        angle_3_list = df["angle_3"].values.tolist()
        angle_3_list = [x - 1 + min(atom_name_list) for x in angle_3_list]
        # print(angle_3_list)
        k_angle_list = df["k_angle"].values.tolist()
        k_angle_list = [
            i * KCAL_MOL_PER_KJ_MOL for i in k_angle_list
        ]  # kcal/mol * radian^2 to kJ/mol * radian^2
        k_angle_list = [round(num, 6) for num in k_angle_list]
        # print(k_angle_list)
        angle_list = df["angle_degrees"].values.tolist()
        angle_list = [i * RADIANS_PER_DEGREE for i in angle_list]
        angle_list = [round(num, 6) for num in angle_list]
        # print(angle_list)
        xml = open(self.guest_qm_params_file, "w")
        xml.write("Begin writing the Bond Parameters" + "\n")
        # TODO: use string formatting and templates to write these lines
        for i in range(len(k_bond_list)):
            xml.write(
                "                                "
                + "<Bond"
                + " "
                + "d="
                + '"'
                + str(bond_length_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_bond_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(bond_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(bond_2_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Bond Parameters" + "\n")
        xml.write("Begin writing the Angle Parameters" + "\n")
        for i in range(len(k_angle_list)):
            xml.write(
                "                                "
                + "<Angle"
                + " "
                + "a="
                + '"'
                + str(angle_list[i])
                + '"'
                + " "
                + "k="
                + '"'
                + str(k_angle_list[i])
                + '"'
                + " "
                + "p1="
                + '"'
                + str(angle_1_list[i])
                + '"'
                + " "
                + "p2="
                + '"'
                + str(angle_2_list[i])
                + '"'
                + " "
                + "p3="
                + '"'
                + str(angle_3_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Angle Parameters" + "\n")
        xml.write("Begin writing the Charge Parameters" + "\n")
        for i in range(len(qm_charges)):
            xml.write(
                "<Particle"
                + " "
                + "q="
                + '"'
                + str(qm_charges[i])
                + '"'
                + " "
                + "eps="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "sig="
                + '"'
                + str(0.00)
                + '"'
                + " "
                + "atom="
                + '"'
                + str(atom_name_list[i])
                + '"'
                + "/>"
                + "\n"
            )
        xml.write("Finish writing the Charge Parameters" + "\n")
        xml.close()

    def write_intermediate_reparameterised_system_xml(self):

        """
        Writes a reparameterised XML force field file for the
        system but without the QM obtained charges.
        """

        # Bond Parameters
        f_params = open(self.guest_qm_params_file, "r")
        lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [comb_1, comb_2, comb_3, comb_4, comb_5, comb_6]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()

    def write_reparameterised_system_xml(self):

        """
        Writes a reparameterised XML force field file for the system.
        """

        # Bond Parameters
        with open(self.guest_qm_params_file, "r") as f_params:
            lines_params = f_params.readlines()
        # Bond Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Bond Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Bond Parameters" in lines_params[i]:
                to_end = int(i)
        bond_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_bond = []
        # TODO: again, use string formatting.
        for i in bond_params:
            bond_line_to_replace = i
            # print(bond_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_bond = [comb_1, comb_2]
            # print(comb_list_bond)
            list_search_bond = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
            ]
            # print(list_search_bond)
            for j in range(len(list_search_bond)):
                if list_search_bond[j] != []:
                    to_add = (list_search_bond[j], i)
                    # print(to_add)
                    index_search_replace_bond.append(to_add)
        # Angle Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Angle Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Angle Parameters" in lines_params[i]:
                to_end = int(i)
        angle_params = lines_params[to_begin + 1 : to_end]
        index_search_replace_angle = []
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
        index_search_replace_angle = []
        # TODO: use string formatting (generalize to function?)
        for i in angle_params:
            angle_line_to_replace = i
            # print(angle_line_to_replace)
            atom_number_list = [
                re.findall("\d*\.?\d+", i)[3],
                re.findall("\d*\.?\d+", i)[5],
                re.findall("\d*\.?\d+", i)[7],
            ]
            # print(atom_number_list)
            comb_1 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_2 = (
                "p1="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_3 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[2]
                + '"'
                + "/>"
            )
            comb_4 = (
                "p1="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_5 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[0]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[1]
                + '"'
                + "/>"
            )
            comb_6 = (
                "p1="
                + '"'
                + atom_number_list[2]
                + '"'
                + " "
                + "p2="
                + '"'
                + atom_number_list[1]
                + '"'
                + " "
                + "p3="
                + '"'
                + atom_number_list[0]
                + '"'
                + "/>"
            )
            comb_list_angle = [comb_1, comb_2, comb_3, comb_4, comb_5, comb_6]
            # print(comb_list_angle)
            list_search_angle = [
                search_in_file(file=self.system_xml, word=comb_1),
                search_in_file(file=self.system_xml, word=comb_2),
                search_in_file(file=self.system_xml, word=comb_3),
                search_in_file(file=self.system_xml, word=comb_4),
                search_in_file(file=self.system_xml, word=comb_5),
                search_in_file(file=self.system_xml, word=comb_6),
            ]
            # print(list_search_angle)
            for j in range(len(list_search_angle)):
                if list_search_angle[j] != []:
                    to_add = (list_search_angle[j], i)
                    # print(to_add)
                    index_search_replace_angle.append(to_add)
        f_org = open(self.system_xml)
        lines = f_org.readlines()
        for i in range(len(index_search_replace_bond)):
            line_number = index_search_replace_bond[i][0][0][0] - 1
            line_to_replace = index_search_replace_bond[i][0][0][1]
            line_to_replace_with = index_search_replace_bond[i][1]
            lines[line_number] = line_to_replace_with
        for i in range(len(index_search_replace_angle)):
            line_number = index_search_replace_angle[i][0][0][0] - 1
            line_to_replace = index_search_replace_angle[i][0][0][1]
            line_to_replace_with = index_search_replace_angle[i][1]
            lines[line_number] = line_to_replace_with
        f_cop = open(self.reparameterised_intermediate_system_xml_file, "w")
        for i in lines:
            f_cop.write(i)
        f_cop.close()
        f_params = open(self.guest_qm_params_file)
        lines_params = f_params.readlines()
        # Charge Parameters
        for i in range(len(lines_params)):
            if "Begin writing the Charge Parameters" in lines_params[i]:
                to_begin = int(i)
            if "Finish writing the Charge Parameters" in lines_params[i]:
                to_end = int(i)
        charge_params = lines_params[to_begin + 1 : to_end]
        non_bonded_index = []
        for k in charge_params:
            non_bonded_index.append(int(re.findall("[-+]?\d*\.\d+|\d+", k)[3]))
        charge_for_index = []
        for k in charge_params:
            charge_for_index.append(
                float(re.findall("[-+]?\d*\.\d+|\d+", k)[0])
            )
        xml_off = open(self.system_xml)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)
        nonbond_params = xml_off_lines[to_begin + 4 : to_end - 1]
        # print(len(nonbond_params))
        f_non_bonded = open(self.system_xml_non_bonded_file, "w")
        for x in nonbond_params:
            f_non_bonded.write(x)
        f_non_bonded = open(self.system_xml_non_bonded_file)
        lines_non_bonded = f_non_bonded.readlines()
        # print(len(lines_non_bonded))
        lines_non_bonded_to_write = []
        for i in range(len(non_bonded_index)):
            line_ = lines_non_bonded[non_bonded_index[i]]
            # print(line_)
            eps = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[0])
            sig = float(re.findall("[-+]?\d*\.\d+|\d+", line_)[2])
            line_to_replace = (
                "                                "
                + "<Particle "
                + "eps="
                + '"'
                + str(eps)
                + '"'
                + " "
                + "q="
                + '"'
                + str(charge_for_index[i])
                + '"'
                + " "
                + "sig="
                + '"'
                + str(sig)
                + '"'
                + "/>"
            )
            lines_non_bonded_to_write.append(line_to_replace)
        data_ = list(zip(non_bonded_index, lines_non_bonded_to_write))
        df_non_bonded_params = pd.DataFrame(
            data_, columns=["line_index", "line"]
        )
        # print(df_non_bonded_params.head())
        f_non_bonded_ = open(self.system_xml_non_bonded_file)
        lines_non_bonded_ = f_non_bonded_.readlines()
        for i in range(len(lines_non_bonded_)):
            if i in non_bonded_index:
                lines_non_bonded_[i] = (
                    df_non_bonded_params.loc[
                        df_non_bonded_params.line_index == i, "line"
                    ].values[0]
                ) + "\n"
        # print(len(lines_non_bonded_))
        f_write_non_bonded_reparams = open(
            self.system_xml_non_bonded_reparams_file, "w"
        )
        for p in range(len(lines_non_bonded_)):
            f_write_non_bonded_reparams.write(lines_non_bonded_[p])
        f_write_non_bonded_reparams.close()
        f_ = open(self.system_xml_non_bonded_reparams_file)
        lines_ = f_.readlines()
        print(len(lines_) == len(lines_non_bonded))
        xml_off = open(self.reparameterised_intermediate_system_xml_file)
        xml_off_lines = xml_off.readlines()
        for i in range(len(xml_off_lines)):
            if "<GlobalParameters/>" in xml_off_lines[i]:
                to_begin = int(i)
            if "<Exceptions>" in xml_off_lines[i]:
                to_end = int(i)
        lines_before_params = xml_off_lines[: to_begin + 4]
        f__ = open(self.system_xml_non_bonded_reparams_file)
        lines_params_non_bonded = f__.readlines()
        lines_after_params = xml_off_lines[to_end - 1 :]
        f_reparams_xml = open(self.reparameterised_system_xml_file, "w")
        for x in lines_before_params:
            f_reparams_xml.write(x)
        for x in lines_params_non_bonded:
            f_reparams_xml.write(x)
        for x in lines_after_params:
            f_reparams_xml.write(x)
        f_reparams_xml.close()

    def write_torsional_reparams_intermediate(self):
        """
        Generates a XML force field file for the system ( without the
        QM charges ) with reparameterized torsional parameters of the ligand.
        """

        no_host_atoms = get_num_host_atoms(self.host_pdb)
        xml_tor = open(self.reparameterized_torsional_params_file, "r")
        xml_tor_lines = xml_tor.readlines()
        xml_tor_lines_renum = []
        for i in xml_tor_lines:
            i = i.replace(
                "p1=" + '"' + str(int(re.findall("\d*\.?\d+", i)[2])) + '"',
                "p1="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[2]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p2=" + '"' + str(int(re.findall("\d*\.?\d+", i)[4])) + '"',
                "p2="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[4]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p3=" + '"' + str(int(re.findall("\d*\.?\d+", i)[6])) + '"',
                "p3="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[6]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p4=" + '"' + str(int(re.findall("\d*\.?\d+", i)[8])) + '"',
                "p4="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[8]) + no_host_atoms))
                + '"',
            )
            xml_tor_lines_renum.append(i)

        non_zero_k_tor = []
        for i in xml_tor_lines_renum:
            to_find = "k=" + '"' + "0.0" + '"'
            if to_find not in i:
                non_zero_k_tor.append(i)
        # print(non_zero_k_tor)
        p1 = []
        for i in range(len(non_zero_k_tor)):
            p1.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[2]))
        # print(p1)
        p2 = []
        for i in range(len(non_zero_k_tor)):
            p2.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[4]))
        # print(p2)
        p3 = []
        for i in range(len(non_zero_k_tor)):
            p3.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[6]))
        # print(p3)
        p4 = []
        for i in range(len(non_zero_k_tor)):
            p4.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[8]))
        # print(p4)
        periodicity = []
        for i in range(len(non_zero_k_tor)):
            periodicity.append(
                int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[9])
            )
        # print(periodicity)
        xml_tor_reparams = open(
            self.reparameterised_intermediate_system_xml_file, "r"
        )
        xml_tor_reparams_lines = xml_tor_reparams.readlines()
        for j in range(len(xml_tor_reparams_lines)):
            for i in range(len(non_zero_k_tor)):
                to_find_tor = (
                    "p1="
                    + '"'
                    + str(p1[i])
                    + '"'
                    + " "
                    + "p2="
                    + '"'
                    + str(p2[i])
                    + '"'
                    + " "
                    + "p3="
                    + '"'
                    + str(p3[i])
                    + '"'
                    + " "
                    + "p4="
                    + '"'
                    + str(p4[i])
                    + '"'
                    + " "
                    + "periodicity="
                    + '"'
                    + str(periodicity[i])
                    + '"'
                )
                if to_find_tor in xml_tor_reparams_lines[j]:
                    print(xml_tor_reparams_lines[j])
                    xml_tor_reparams_lines[j] = non_zero_k_tor[i]
        with open(
            self.reparameterised_intermediate_torsional_system_xml_file, "w"
        ) as f:
            for i in xml_tor_reparams_lines:
                f.write(i)

    def write_torsional_reparams(self):
        """
        Generates a XML force field file for the system with reparameterized
        torsional parameters of the ligand.
        """

        no_host_atoms = get_num_host_atoms(self.host_pdb)
        with open(self.reparameterized_torsional_params_file, "r") as xml_tor:
            xml_tor_lines = xml_tor.readlines()
        xml_tor_lines_renum = []
        # TODO: string formatting and clean up this code to be more concise
        for i in xml_tor_lines:
            i = i.replace(
                "p1=" + '"' + str(int(re.findall("\d*\.?\d+", i)[2])) + '"',
                "p1="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[2]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p2=" + '"' + str(int(re.findall("\d*\.?\d+", i)[4])) + '"',
                "p2="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[4]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p3=" + '"' + str(int(re.findall("\d*\.?\d+", i)[6])) + '"',
                "p3="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[6]) + no_host_atoms))
                + '"',
            )
            i = i.replace(
                "p4=" + '"' + str(int(re.findall("\d*\.?\d+", i)[8])) + '"',
                "p4="
                + '"'
                + str(int(int(re.findall("\d*\.?\d+", i)[8]) + no_host_atoms))
                + '"',
            )
            xml_tor_lines_renum.append(i)

        non_zero_k_tor = []
        for i in xml_tor_lines_renum:
            to_find = "k=" + '"' + "0.0" + '"'
            if to_find not in i:
                non_zero_k_tor.append(i)
        # print(non_zero_k_tor)
        p1 = []
        for i in range(len(non_zero_k_tor)):
            p1.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[2]))
        # print(p1)
        p2 = []
        for i in range(len(non_zero_k_tor)):
            p2.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[4]))
        # print(p2)
        p3 = []
        for i in range(len(non_zero_k_tor)):
            p3.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[6]))
        # print(p3)
        p4 = []
        for i in range(len(non_zero_k_tor)):
            p4.append(int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[8]))
        # print(p4)
        periodicity = []
        for i in range(len(non_zero_k_tor)):
            periodicity.append(
                int(re.findall("\d*\.?\d+", non_zero_k_tor[i])[9])
            )
        # print(periodicity)
        xml_tor_reparams = open(self.reparameterised_system_xml_file, "r")
        xml_tor_reparams_lines = xml_tor_reparams.readlines()
        for j in range(len(xml_tor_reparams_lines)):
            for i in range(len(non_zero_k_tor)):
                to_find_tor = (
                    "p1="
                    + '"'
                    + str(p1[i])
                    + '"'
                    + " "
                    + "p2="
                    + '"'
                    + str(p2[i])
                    + '"'
                    + " "
                    + "p3="
                    + '"'
                    + str(p3[i])
                    + '"'
                    + " "
                    + "p4="
                    + '"'
                    + str(p4[i])
                    + '"'
                    + " "
                    + "periodicity="
                    + '"'
                    + str(periodicity[i])
                    + '"'
                )
                if to_find_tor in xml_tor_reparams_lines[j]:
                    print(xml_tor_reparams_lines[j])
                    xml_tor_reparams_lines[j] = non_zero_k_tor[i]
        with open(self.reparameterised_torsional_system_xml_file, "w") as f:
            for i in xml_tor_reparams_lines:
                f.write(i)

    def save_amber_params_non_qm_charges(self):

        """
        Saves amber generated topology files for the system
        without the QM charges.
        """

        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(
                    self.reparameterised_intermediate_torsional_system_xml_file
                ),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(
                    self.reparameterised_intermediate_torsional_system_xml_file
                ),
            )
        openmm_system.save(
            self.prmtop_system_intermediate_params, overwrite=True
        )
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(
            self.inpcrd_system_intermediate_params, overwrite=True
        )
        parm = parmed.load_file(
            self.prmtop_system_intermediate_params,
            self.inpcrd_system_intermediate_params,
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(
                self.reparameterised_intermediate_torsional_system_xml_file
            ),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)

    def save_amber_params(self):

        """
        Saves amber generated topology files for the system.
        """

        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(self.non_reparameterised_system_xml_file),
            )
        openmm_system.save(self.prmtop_system_non_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_non_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_non_params, self.inpcrd_system_non_params
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.non_reparameterised_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_non_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_non_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)
        if self.load_topology == "parmed":
            openmm_system = parmed.openmm.load_topology(
                parmed.load_file(self.system_pdb, structure=True).topology,
                parmed.load_file(
                    self.reparameterised_torsional_system_xml_file
                ),
            )
        if self.load_topology == "openmm":
            openmm_system = parmed.openmm.load_topology(
                simtk.openmm.app.PDBFile(self.system_pdb).topology,
                parmed.load_file(
                    self.reparameterised_torsional_system_xml_file
                ),
            )
        openmm_system.save(self.prmtop_system_params, overwrite=True)
        openmm_system.coordinates = parmed.load_file(
            self.system_pdb, structure=True
        ).coordinates
        openmm_system.save(self.inpcrd_system_params, overwrite=True)
        parm = parmed.load_file(
            self.prmtop_system_params, self.inpcrd_system_params
        )
        xml_energy_decomposition = parmed.openmm.energy_decomposition_system(
            openmm_system,
            parmed.load_file(self.reparameterised_torsional_system_xml_file),
        )
        xml_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in xml_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        xml_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_xml = pd.DataFrame(
            list(
                zip(
                    xml_energy_decomposition_list,
                    xml_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_xml_params"],
        )
        df_energy_xml = df_energy_xml.set_index("Energy_term")
        prmtop_energy_decomposition = parmed.openmm.energy_decomposition_system(
            parm, parm.createSystem()
        )
        prmtop_energy_decomposition_value = [
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicBondForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("HarmonicAngleForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("PeriodicTorsionForce"),
            list_to_dict(
                [
                    item
                    for sublist in [
                        list(elem) for elem in prmtop_energy_decomposition
                    ]
                    for item in sublist
                ]
            ).get("NonbondedForce"),
        ]
        prmtop_energy_decomposition_list = [
            "HarmonicBondForce",
            "HarmonicAngleForce",
            "PeriodicTorsionForce",
            "NonbondedForce",
        ]
        df_energy_prmtop = pd.DataFrame(
            list(
                zip(
                    prmtop_energy_decomposition_list,
                    prmtop_energy_decomposition_value,
                )
            ),
            columns=["Energy_term", "Energy_prmtop_params"],
        )
        df_energy_prmtop = df_energy_prmtop.set_index("Energy_term")
        df_compare = pd.concat([df_energy_xml, df_energy_prmtop], axis=1)
        print(df_compare)
