#%%
import pathlib
import numpy as np
import tkinter as tk
from tkinter import filedialog

from npp_2d_truss_analysis.truss_input import Info, FileData,Mesh,Displacements,Forces, write_input_data
from npp_2d_truss_analysis.truss_analysis_2d import Dofs, Analysis
from npp_2d_truss_analysis.truss_solution import Solution, write_results
from npp_2d_truss_analysis.truss_plotter import TrussPlotter

#%%
class TrussAnalysisProject:
    _mesh:Mesh = None
    _displacements:Displacements = None
    _forces:Forces = None
    _dofs:Dofs = None
    _analysis:Analysis = None
    _solution:Solution = None
    _tp:TrussPlotter =  TrussPlotter()

    def __init__(self,info:Info, mesh:Mesh, displacements:Displacements, forces:Forces):
        self._info = info
        self._mesh = mesh
        self._displacements = displacements
        self._forces = forces
    
    def update_matrices(self):
        self._dofs = Dofs()
        self._dofs.process_dofs(mesh=self._mesh, displacements=self._displacements)
        self._analysis = Analysis()
        self._analysis.get_global_stiffness_matrix(mesh=self._mesh)
        self._analysis.get_global_force_vector(forces=self._forces, dofs=self._dofs)
        self._analysis.get_new_displacement_vector(displacements=self._displacements, dofs=self._dofs)
        self._analysis.get_new_transformation_matrix(displacements=self._displacements, dofs=self._dofs)  
    
    def solve(self, to_disk:bool = True):
        # force the update of the matrix analysis
        self.update_matrices()
        #================== Solution ==================
        self._solution = Solution()
        self._solution.solve_displacement(self._analysis, self._dofs)
        self._solution.solve_reaction(displacements=self._displacements)
        self._solution.solve_stress(mesh=self._mesh)
        # Usage example
        # Assume info, mesh, displacements, and solution are instances of their respective classes with attributes set
        if to_disk:
            write_results(self._info, mesh=self._mesh, displacements=self._displacements, solution=self._solution)

    def write_input_data(self):
        write_input_data(info=self._info, mesh=self._mesh, displacements=self._displacements, forces=self._forces)


    def plot_truss(self, save:bool=True, show:bool=True):
        self._tp.get_plot_parameters(mesh=self._mesh, solution=None)

        # Usage example
        # Assume info, plot, mesh, forces, and displacements are instances of their respective classes with attributes set
        self._tp.plot_truss(self._info, self._mesh, self._forces, self._displacements, save=save, show=show)

    def plot_deformation(self, save:bool=True, show:bool=True):
        # Requires solution to be calculated
        self._tp.get_plot_parameters(mesh=self._mesh, solution=self._solution)

        # Usage example
        # Assume info, plot, mesh, forces, and displacements are instances of their respective classes with attributes set
        self._tp.plot_deformation(info=self._info, 
                mesh=self._mesh, forces=self._forces, 
                displacements=self._displacements,
                solution=self._solution,
                save=save, show=show)

    def plot_stresses(self, save:bool=True, show:bool=True):
        # Requires solution to be calculated
        self._tp.get_plot_parameters(mesh=self._mesh, solution=self._solution)

        # Usage example
        # Assume info, plot, mesh, forces, and displacements are instances of their respective classes with attributes set
        self._tp.plot_stress(info=self._info, 
                mesh=self._mesh, forces=self._forces, 
                displacements=self._displacements,
                solution=self._solution,
                save=save, show=show)


    def report_reactions(self, fmt:str = '.3g'):
        """prints the reaction forces on each support using a specified format"""
        print('Reaction forces:')
        print('|- Pinned Nodes:')
        for i in range(self._displacements.number_pin):
            f_x = self._solution.global_reactions[0,i]
            f_y = self._solution.global_reactions[1,i]
            print(f"|   |- Node {self._displacements.pin_nodes[i]} = ({format(f_x, fmt)}, {format(f_y, fmt)})    | mag: {format(np.sqrt(f_x**2+f_y**2), fmt)}")
        print('|- Roller Nodes:')
        for i in range(self._displacements.number_roller):
            j = i + self._displacements.number_pin
            f_x = self._solution.global_reactions[0,j]
            f_y = self._solution.global_reactions[1,j]
            print(f"|   |- Node {self._displacements.roller_nodes[i]} = ({format(f_x, fmt)}, {format(f_y, fmt)})    | mag: {format(np.sqrt(f_x**2+f_y**2), fmt)}")


    def report_rod_forces(self, fmt:str = '.3g'):
        """prints the  forces on each member using a specified format"""
        print('Rods forces:')
        for i in range(self._mesh.number_elements):
            f = self._solution.element_force[i]
            print(f"|   |- Rod {i+1} = {format(f, fmt)}")

    @classmethod
    def from_json_file(cls, json_file_name:str, info:Info):
        # read the JSON_FILE_NAME file content into json_problem_data string
        if isinstance(json_file_name, pathlib.Path):
            json_file_name = str(json_file_name.absolute())
        with open(json_file_name, 'r') as json_file:
            json_problem_data = json_file.read()

        return cls.from_json(json_text=json_problem_data, info=info)

    @classmethod
    def from_json(cls,  json_text:str, info:Info=None):
        
        mesh = Mesh.from_json(json_data=json_text)

        displacements = Displacements.from_json(json_str=json_text)
        # displacements.process_displacements(file_data= fileData.displacements)

        forces = Forces.from_json_str(json_text)
        return cls(info=info, mesh=mesh, displacements=displacements, forces=forces)

if __name__ == "__main__":
    
    pp_project_dir = pathlib.Path('exam2024-01')
    pp_project_dir = pathlib.Path('../examples/example_101')
    FNAME_PREFIX = 'test'
    

    info = Info(project_directory=str(pp_project_dir.absolute()), file_name=FNAME_PREFIX)

    fileData = FileData.from_directory(info.project_directory)
    mesh = Mesh()
    mesh.process_mesh(file_data= fileData.mesh)

    displacements = Displacements()
    displacements.process_displacements(file_data= fileData.displacements)
    forces = Forces()
    forces.process_forces(file_data= fileData.forces)
    #%%
    truss_problem = TrussAnalysisProject(info=info, mesh=mesh, displacements=displacements, forces=forces)
    truss_problem.write_input_data()
    truss_problem.solve()
    truss_problem.plot_truss(save=True, show=True)
# %%

# %%
