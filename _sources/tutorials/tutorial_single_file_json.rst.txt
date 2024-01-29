Tutorial for single file json   input
=====================================

This tutorial demonstrates the way of using json file to input the problem definition for Truss Analysis project.

We will use a JSON configuration to define the truss structure and then perform an analysis to determine the reactions and rod forces.

Import Necessary Libraries/Setup
--------------------------------

To start, we need to import necessary modules and define the project directory and file name prefix.

.. code-block:: python

    import pathlib
    import numpy as np
    import tkinter as tk
    from tkinter import filedialog

    from npp_2d_truss_analysis.truss_input import Info, FileData, Mesh, Displacements, Forces, write_input_data
    from npp_2d_truss_analysis.truss_analysis_2d import Dofs, Analysis
    from npp_2d_truss_analysis.truss_solution import Solution, write_results
    from npp_2d_truss_analysis.truss_plotter import TrussPlotter
    from npp_2d_truss_analysis.truss_project import TrussAnalysisProject

    pp_project_dir = pathlib.Path('./')
    FNAME_PREFIX = 'test'

    info = Info(project_directory=str(pp_project_dir.absolute()), file_name=FNAME_PREFIX)


Defining the Truss Structure
----------------------------
The truss structure is defined using a JSON string. This includes the definition of nodes, elements, materials, displacements, and forces.


.. code-block:: python

    JSON_TEXT="""{
        "mesh":{
            "nodes": [
            {"id": 1, "coordinates": [0, 0]},
            {"id": 2, "coordinates": [0, 2]},
            {"id": 3, "coordinates": [0, 4]},
            {"id": 4, "coordinates": [4, 4]},
            {"id": 5, "coordinates": [4, 2]}
            ],
            "elements": [
            {"id": 1, "connectivity": [4, 3], "materialId": 1},
            {"id": 2, "connectivity": [3, 2], "materialId": 1},
            {"id": 3, "connectivity": [2, 4], "materialId": 1},
            {"id": 4, "connectivity": [4, 5], "materialId": 1},
            {"id": 5, "connectivity": [5, 2], "materialId": 1},
            {"id": 6, "connectivity": [2, 1], "materialId": 1},
            {"id": 7, "connectivity": [1, 5], "materialId": 1}
            ],
            "materials": [
            {"id": 1, "youngModulus": 200000000000.0, "area": 1.0}
            ]
        },
        "displacements":{
            "pin": [
            {"id": 1, "node":4, "angle": 0,"dx": 0, "dy":0}
            ],
            "rollers": [
            {"id": 1, "node": 1, "direction": 1, "angle": -63.4349, "dx":0}
            ]
        },
        "forces": [
        {"id": 1, "node":5, "direction": -180,"x": 40000, "y":0},
        {"id": 2, "node":3, "direction":  200,"x": 20000, "y":0}
        ]
    }"""

Creating the Truss Problem
--------------------------

We instantiate the truss problem from the JSON text.

.. code-block:: python

    truss_problem = TrussAnalysisProject.from_json(json_text=JSON_TEXT, 


Updating Forces (optional)
--------------------------

Before solving the problem, we update the forces as needed.

.. code-block:: python

    truss_problem._forces.update_force_by_id(force_id=1, angle=180+20)


Listing Forces (Optional)
-------------------------

Optionally, list the forces to verify the updates.

.. code-block:: python

    truss_problem._forces.list_forces()

Solving the Problem
-------------------

Now, we write the input data and solve the truss problem.

.. code-block:: python

    truss_problem.write_input_data()
    # truss_problem.update_matrices() # optional because solve automatically does that
    truss_problem.solve()


Reporting the Solution
----------------------

Finally, we print the solution, including the reactions and rod forces.

.. code-block:: python

    print("-------------solution ----------------")
    truss_problem.report_reactions(fmt='>12.1f')
    truss_problem.report_rod_forces(fmt='>12.1f')


Plotting the truss
------------------

It is also possible to plot the truss using the following code:


.. code-block:: python

    truss_problem.plot_truss(save=True, show=True)

using the flags save and show to save the plot to a file and/or show the plot on the screen.



Plotting truss deformation and stresses
---------------------------------------

After solving the problem, we can plot the deformed state and the stresses.


.. code-block:: python

    truss_problem.plot_deformation(save=True, show=True)
    truss_problem.plot_stresses(save=True, show=True)

using the flags save and show to save the plot to a file and/or show the plot on the screen.

The color of the rods in the stress plot indicates the stress level and whether it is in tension or compression. The color of the rods in the deformation plot indicates the displacement level and whether it is in tension or compression.
More specifically, the color of the rods in the stress plot will be :

- blue: if the rod is in tension

- red: if the rod is in compression


Complete Code of the Tutorial
-----------------------------


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

    pp_project_dir = pathlib.Path('./')
    FNAME_PREFIX = 'test'

    info = Info(project_directory=str(pp_project_dir.absolute()), file_name=FNAME_PREFIX)

    JSON_TEXT="""{
        "mesh":{
            "nodes": [
            {"id": 1, "coordinates": [0, 0]},
            {"id": 2, "coordinates": [0, 2]},
            {"id": 3, "coordinates": [0, 4]},
            {"id": 4, "coordinates": [4, 4]},
            {"id": 5, "coordinates": [4, 2]}
            ],
            "elements": [
            {"id": 1, "connectivity": [4, 3], "materialId": 1},
            {"id": 2, "connectivity": [3, 2], "materialId": 1},
            {"id": 3, "connectivity": [2, 4], "materialId": 1},
            {"id": 4, "connectivity": [4, 5], "materialId": 1},
            {"id": 5, "connectivity": [5, 2], "materialId": 1},
            {"id": 6, "connectivity": [2, 1], "materialId": 1},
            {"id": 7, "connectivity": [1, 5], "materialId": 1}
            ],
            "materials": [
            {"id": 1, "youngModulus": 200000000000.0, "area": 1.0}
            ]
        },
        "displacements":{
            "pin": [
            {"id": 1, "node":4, "angle": 0,"dx": 0, "dy":0}
            ],
            "rollers": [
            {"id": 1, "node": 1, "direction": 1, "angle": -63.4349, "dx":0}
            ]
        },
        "forces": [
        {"id": 1, "node":5, "direction": -180,"x": 40000, "y":0},
        {"id": 2, "node":3, "direction":  200,"x": 20000, "y":0}
        ]
    }"""
    

    truss_problem = TrussAnalysisProject.from_json(json_text=JSON_TEXT, info=info)

    truss_problem._forces.update_force_by_id(force_id=1, angle=180+20)
    truss_problem._forces.list_forces()
    truss_problem.write_input_data()
    truss_problem.plot_truss(save=True, show=True)

    # solution
    truss_problem.solve()
    print("-------------solution ----------------")
    truss_problem.report_reactions(fmt='>12.1f')
    truss_problem.report_rod_forces(fmt='>12.1f')
    # plotting results
    truss_problem.plot_deformation(save=True, show=True)
    truss_problem.plot_stresses(save=True, show=True)

