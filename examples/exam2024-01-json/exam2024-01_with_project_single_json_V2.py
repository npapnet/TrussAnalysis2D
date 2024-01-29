#%%[markdown]
# # Scope 
# This is a version of the trust analysis project that uses the class analysis class with the class method from Json file.
# The main difference from the world other version is that individual mesh displacements and forces objects are not created.
# 
# # Notes
# Additionally in this example I am adding the update methods suitable for marking my exam. 
# So please disregard any code snippets that have the `am` variable inside
#%%
import pathlib
import numpy as np
import tkinter as tk
from tkinter import filedialog

from npp_2d_truss_analysis.truss_input import Info, FileData,Mesh,Displacements,Forces, write_input_data
from npp_2d_truss_analysis.truss_analysis_2d import Dofs, Analysis
from npp_2d_truss_analysis.truss_solution import Solution, write_results
from npp_2d_truss_analysis.truss_plotter import TrussPlotter
from npp_2d_truss_analysis.truss_project import TrussAnalysisProject


#%%

pp_project_dir = pathlib.Path('./')
JSON_FILE_NAME = pp_project_dir /'exam2024-01.json'
FNAME_PREFIX = 'test'

info = Info(project_directory=str(pp_project_dir.absolute()), file_name=FNAME_PREFIX)

truss_problem = TrussAnalysisProject.from_json_file(json_file_name=JSON_FILE_NAME, info=info)

#%%
# truss_problem._forces.list_forces()
#%%
am = 20413 
xy =am%100
truss_problem._forces.update_force_by_id(force_id=1, angle=180+20+xy)
#%%
truss_problem._forces.list_forces()
#%%
truss_problem.write_input_data()
truss_problem.solve()
truss_problem.plot_truss(save=False, show=True)
print("-------------solution ----------------")
truss_problem.report_reactions(fmt='>12.1f')
truss_problem.report_rod_forces(fmt='>12.1f')

# %%