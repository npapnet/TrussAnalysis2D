Tutorial json  input
====================

This tutorial demonstrates the way of using json to inputing the problem definition for Truss Analysis project.




Import Necessary Libraries
--------------------------

First, import the required modules:

.. code-block:: python

    import pathlib
    import numpy as np
    import tkinter as tk
    from tkinter import filedialog

    from npp_2d_truss_analysis.truss_input import Info, FileData,Mesh,Displacements,Forces, write_input_data
    from npp_2d_truss_analysis.truss_analysis_2d import Dofs, Analysis
    from npp_2d_truss_analysis.truss_solution import Solution, write_results
    from npp_2d_truss_analysis.truss_plotter import TrussPlotter
    from npp_2d_truss_analysis.truss_project import TrussAnalysisProject


**WORK IN PROGRESS**