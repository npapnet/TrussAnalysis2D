#%%
import pathlib
import numpy as np
import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt

from npp_2d_truss_analysis.truss_input import Info, FileData,Mesh,Displacements,Forces, write_input_data
from npp_2d_truss_analysis.truss_analysis_2d import Dofs, Analysis
from npp_2d_truss_analysis.truss_solution import Solution, write_results


def get_colors(current_value, positive_value, negative_value):
    color_compression = np.array([0.7843, 0, 0.1569])
    color_zero = np.array([0.9020, 0.9020, 0.9020])
    color_tension = np.array([0.1569, 0, 0.7843])

    if current_value < 0:
        ratio = current_value / negative_value
        c1 = color_compression
        c2 = color_zero
    else:
        ratio = current_value / positive_value
        c1 = color_tension
        c2 = color_zero

    element_color = np.zeros(3)
    element_color[1] = c2[1] + ratio * (c1[1] - c2[1])
    element_color[0] = c2[0] + ratio * (c1[0] - c2[0])
    element_color[2] = c2[2] + ratio * (c1[2] - c2[2])

    return element_color

def get_roller_lines(app_point, dir_vector, plot_scale):
    """returns the 

    Args:
        app_point (list two elemetns): list element
        dir_vector (int): 1-normal, 2-parallel
        plot_scale (float): plot scale

    Returns:
        list: [x1,y1, x2,y2] end coordinates of roller
    """    
    roller_l_paper = 16  # mm
    roller_h_paper = 2.5  # mm

    roller_l = roller_l_paper / 10 / plot_scale  # converting to meters
    roller_h = roller_h_paper / 10 / plot_scale  # converting to meters

    d_dir = dir_vector
    n_dir = np.array([[0, -1], [1, 0]]) @ d_dir

    point_o = app_point
    point_a1 = point_o + (n_dir * roller_h / 2) - (d_dir * roller_l / 2)
    point_b1 = point_o + (n_dir * roller_h / 2) + (d_dir * roller_l / 2)
    point_a2 = point_o - (n_dir * roller_h / 2) - (d_dir * roller_l / 2)
    point_b2 = point_o - (n_dir * roller_h / 2) + (d_dir * roller_l / 2)

    draw_seg = np.array([point_a1, point_b1, point_a2, point_b2])
    return draw_seg


def get_force_arrow(app_point, dir_vector, vector_length, plot_scale):
    arrow_l_paper = 3  # mm
    arrow_w_paper = 2  # mm
    vector_l_paper = vector_length  # mm

    arrow_l = arrow_l_paper / 10 / plot_scale  # converting to meters
    arrow_w = arrow_w_paper / 10 / plot_scale  # converting to meters
    vector_l = vector_l_paper / 10 / plot_scale  # converting to meters

    d_dir = dir_vector
    n_dir = np.array([[0, -1], [1, 0]]) @ d_dir

    point_o = app_point
    point_c = point_o + d_dir * vector_l
    point_a = point_c - (d_dir * arrow_l) + (n_dir * arrow_w / 2)
    point_b = point_c - (d_dir * arrow_l) - (n_dir * arrow_w / 2)

    draw_seg = np.array([point_o, point_c, point_a, point_c, point_b, point_c])
    return draw_seg

class TrussPlotter:
    def __init__(self):
        self.plot_x_limits = None
        self.plot_y_limits = None
        self.paper_size = None
        self.paper_position = None
        self.plot_scale = None
        self.scale_factor = None

    def get_plot_parameters(self, mesh:Mesh, solution:Solution=None):
        node_coordinates = np.array(mesh.node_coordinates)
        # node_displacements = np.array(solution.global_displacements) if Solution is not None else np.zeros_like(node_coordinates)
        node_displacements_max = solution.get_max_displacement() if solution is not None else 0

        # Node coordinates
        nc_x = node_coordinates[:, 0]
        nc_y = node_coordinates[:, 1]

        # Truss limits
        tx_min = np.min(nc_x)
        tx_max = np.max(nc_x)
        ty_min = np.min(nc_y)
        ty_max = np.max(nc_y)

        # Truss size
        tx_size = tx_max - tx_min
        ty_size = ty_max - ty_min

        # Margins
        margins = 0.09 * max(tx_size, ty_size)

        # Plot limits
        px_min = tx_min - margins
        px_max = tx_max + margins
        py_min = ty_min - margins
        py_max = ty_max + margins
        plot_x_limits = [px_min, px_max]
        plot_y_limits = [py_min, py_max]

        # Axis size
        ax_size = px_max - px_min
        ay_size = py_max - py_min
        
        # Figure size
        fXSize = ax_size / 0.84
        fYSize = ay_size / 0.88

        # Figure size and paper orientation
        if fXSize  > fYSize:
            paper_size = [29.7, 21.0]  # A4 landscape
            if fXSize / fYSize > 297 / 210:
                plot_scale = 29.7 / fXSize
            else:
                plot_scale = 21.0 / fYSize
        else:
            paper_size = [21.0, 29.7]  # A4 portrait
            if fXSize / fYSize > 210 / 297:
                plot_scale = 21.0 / fXSize
            else:
                plot_scale = 29.7 / fYSize
        paper_position = [0, 0] + paper_size

        # Deformed scale factor
        max_displ = np.max(np.abs(node_displacements_max))
        scale_factor = margins * 0.5 / max_displ if max_displ != 0 else 0

        self.plot_x_limits = plot_x_limits
        self.plot_y_limits = plot_y_limits
        self.paper_size = paper_size
        self.paper_position = paper_position
        self.plot_scale = plot_scale
        self.scale_factor = scale_factor


    def plot_truss(self, info, mesh:Mesh, forces:Forces, 
                   displacements:Displacements, 
                   save:bool=True, show:bool=True):
        project_dir = info.project_directory
        file_name = info.file_name
        number_nodes = mesh.number_nodes
        number_elements = mesh.number_elements
        node_coordinates = np.array(mesh.node_coordinates)
        element_connectivity = mesh.element_connectivity
        force_nodes = forces.force_nodes

        new_file_name = f"{file_name}_TRUSS.pdf"
        file_path = f"{project_dir}/{new_file_name}"

        # Node number text real displacement
        d_x_real = 0.14 / self.plot_scale  # meters
        d_y_real = 0.5 / self.plot_scale  # meters

        # Create figure and axes
        fig, ax = plt.subplots(
            figsize=(self.paper_size[0]/2.54, self.paper_size[1]/2.54))  # Size in inches
        ax.set_xlim(self.plot_x_limits)
        ax.set_ylim(self.plot_y_limits)
        ax.set_title(f"{file_name}: Truss")
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        ax.set_aspect('equal', adjustable='box')

        # plot rollers 
        self._plot_rollers(node_coordinates, displacements, ax)

        # Plot elements
        for i in range(number_elements):
            node1, node2 = element_connectivity[i]
            x_coords = [node_coordinates[node1-1][0], node_coordinates[node2-1][0]]
            y_coords = [node_coordinates[node1-1][1], node_coordinates[node2-1][1]]
            ax.plot(x_coords, y_coords, linestyle='-', linewidth=2.5, color='grey')

        # plot forces
        self._plot_force_vectors(node_coordinates, forces, ax)

        # % Nodes
        self._plot_all_nodes(mesh= mesh, displacements=displacements, ax=ax)

        # Force nodes
        force_nodes_adjusted = [fn - 1 for fn in force_nodes]
        force_x_coord = node_coordinates[force_nodes_adjusted, 0]
        force_y_coord = node_coordinates[force_nodes_adjusted, 1]
        ax.plot(force_x_coord, force_y_coord, linestyle='none', linewidth=0.1,
                marker='o', markersize=1.3, markeredgecolor='black',
                markerfacecolor='black')

        # Plot node numbers
        for i in range(number_nodes):
            x, y = node_coordinates[i]
            ax.text(x + d_x_real, y + d_y_real, mesh.node_names[i], fontsize=6,
                    ha='center', va='center', backgroundcolor='white')

        # Plot element numbers
        self._plot_element_numbers(mesh, ax)

        # Save plot as PDF
        if save:
            plt.savefig(file_path)
        if show:
            plt.show()
        plt.close()

    def _plot_element_numbers(self, mesh:Mesh,  ax):
        element_connectivity = mesh.element_connectivity
        number_elements = mesh.number_elements
        node_coordinates = np.array(mesh.node_coordinates)
        
        for i in range(number_elements):
            node1, node2 = element_connectivity[i]
            mid_point = (node_coordinates[node1-1] + node_coordinates[node2-1]) / 2
            ax.text(mid_point[0], mid_point[1], str(i+1), fontsize=6, 
                    ha='center', va='center', backgroundcolor='white')

    def _plot_all_nodes(self, mesh:Mesh, displacements:Displacements, ax):
        node_coordinates = np.array(mesh.node_coordinates)
        pin_nodes = displacements.pin_nodes
        roller_nodes = displacements.roller_nodes

        node_x_coord = node_coordinates[:, 0]
        node_y_coord = node_coordinates[:, 1]
        ax.plot(node_x_coord, node_y_coord, linestyle='none', linewidth=1,
            marker='o', markersize=14, markeredgecolor='black', 
            markerfacecolor='white')

        # % Pin nodes
        pin_nodes_adjusted = [pn - 1 for pn in pin_nodes]

        # Pin Nodes
        pin_x_coord = node_coordinates[pin_nodes_adjusted, 0]
        pin_y_coord = node_coordinates[pin_nodes_adjusted, 1]
        ax.plot(pin_x_coord, pin_y_coord, linestyle='none', linewidth=1.5,
                marker='o', markersize=5, markeredgecolor='black',
                markerfacecolor='black')

        # Roller nodes
        roller_nodes_adjusted = [rn - 1 for rn in roller_nodes]
        # Roller Nodes
        roller_x_coord = node_coordinates[roller_nodes_adjusted, 0]
        roller_y_coord = node_coordinates[roller_nodes_adjusted, 1]
        ax.plot(roller_x_coord, roller_y_coord, linestyle='none', linewidth=1.5,
                marker='o', markersize=5, markeredgecolor='black',
                markerfacecolor='white')

    def _plot_force_vectors(self, node_coordinates,
            forces:Forces, ax):
        number_forces = forces.number_forces
        force_nodes = forces.force_nodes
        force_components = np.array(forces.force_components)
        force_angles = forces.force_angles
        for num_for in range(number_forces):
            f_node = force_nodes[num_for] - 1  # Adjust for zero-based indexing in Python
            f_comp_xi_yi = force_components[num_for, :]
            f_angle = force_angles[num_for]
            c = np.cos(np.radians(f_angle))
            s = np.sin(np.radians(f_angle))
            t = np.array([[c, s], [-s, c]])
            f_comp_xy = t.T @ f_comp_xi_yi
            f_dir_vec = f_comp_xy / np.linalg.norm(f_comp_xy)

            draw_seg = get_force_arrow(node_coordinates[f_node,:], f_dir_vec, 14, self.plot_scale)
            for seg in range(3):
                ax.plot(draw_seg[2*seg:2*seg+2, 0], draw_seg[2*seg:2*seg+2, 1],
                        linestyle='-', linewidth=1.3, marker='none', color='black')

    def _plot_rollers(self, node_coordinates, displacements:Displacements, ax):
        number_roller = displacements.number_roller
        roller_nodes = displacements.roller_nodes
        roller_directions = displacements.roller_directions
        roller_angles = displacements.roller_angles
        
        for num_rol in range(number_roller):
            r_node = roller_nodes[num_rol] - 1  # Adjust for zero-based indexing in Python
            r_direction = roller_directions[num_rol]
            r_angle = roller_angles[num_rol]
            c = np.cos(np.radians(r_angle))
            s = np.sin(np.radians(r_angle))

            r_dir_vec = np.array([c, s]) if r_direction == 1 else np.array([-s, c])

            draw_seg = get_roller_lines(node_coordinates[r_node,:], r_dir_vec, self.plot_scale)
            for seg in range(2):
                ax.plot(draw_seg[2*seg:2*seg+2, 0], draw_seg[2*seg:2*seg+2, 1],
                        linestyle='-', linewidth=1, marker='none', color='black')


    def plot_deformation(self, info:Info, mesh:Mesh, forces:Forces, 
            displacements:Displacements, solution:Solution, 
            save:bool=True, show:bool=True):
        # TODO some lists need to be converted to arrays. 
        project_dir = info.project_directory
        file_name = info.file_name
        # paper_position = self.paper_position
        number_nodes = mesh.number_nodes
        number_elements = mesh.number_elements
        node_coordinates = np.transpose(np.array(mesh.node_coordinates))
        element_connectivity = np.array(mesh.element_connectivity)
        number_pin = displacements.number_pin
        pin_nodes = np.array(displacements.pin_nodes)
        number_roller = displacements.number_roller
        roller_nodes = np.array(displacements.roller_nodes)
        node_real_displacements = solution.global_displacements

        new_file_name = f"{file_name}_DEFORMATION.pdf"
        file_path = f"{project_dir}/{new_file_name}"

        node_displacements = node_real_displacements * self.scale_factor

        # Figure and axes setup
        fig, ax = plt.subplots()
        fig.set_size_inches(self.paper_size[0] / 2.54, self.paper_size[1] / 2.54)  # Convert cm to inches
        ax.set_xlim(self.plot_x_limits)
        ax.set_ylim(self.plot_y_limits)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(f"{file_name}: Deformation (x{self.scale_factor:.2E})")
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')

        # Undeformed elements
        for num_ele in range(number_elements):
            node1, node2 = element_connectivity[num_ele,:]
            x1_coord, y1_coord = node_coordinates[:,node1 - 1]
            x2_coord, y2_coord = node_coordinates[:, node2 - 1]
            ax.plot([x1_coord, x2_coord], [y1_coord, y2_coord], linestyle='--', linewidth=1, color=[0.6, 0.6, 0.6])

        # Undeformed nodes
        node_x_coord = node_coordinates[0, :]
        node_y_coord = node_coordinates[1, :]
        ax.plot(node_x_coord, node_y_coord, linestyle='none', linewidth=1, marker='o', markersize=3, markeredgecolor=[0.0, 0.0, 0.0], markerfacecolor=[1.0, 1.0, 1.0])

        # Undeformed pin nodes
        pin_x_coord = node_coordinates[0, pin_nodes - 1]  # Adjust for zero-based indexing
        pin_y_coord = node_coordinates[1, pin_nodes - 1]
        ax.plot(pin_x_coord, pin_y_coord, linestyle='none', linewidth=1.5, marker='o', markersize=3, markeredgecolor=[0.0, 0.0, 0.0], markerfacecolor=[0.0, 0.0, 0.0])
        
        # Undeformed roller nodes
        roller_x_coord = node_coordinates[0, roller_nodes - 1]  # Adjust for zero-based indexing
        roller_y_coord = node_coordinates[1, roller_nodes - 1]
        ax.plot(roller_x_coord, roller_y_coord, linestyle='none', linewidth=1.5, marker='o', markersize=3, markeredgecolor=[0.0, 0.0, 0.0], markerfacecolor=[1.0, 1.0, 1.0])

        # Deformed elements
        for num_ele in range(number_elements):
            node1, node2 = element_connectivity[num_ele,:]
            x1_coord, y1_coord = node_coordinates[:, node1 - 1]  # Adjust for zero-based indexing
            x2_coord, y2_coord = node_coordinates[:, node2 - 1]
            x1_def = node_displacements[2 * (node1 - 1)]
            y1_def = node_displacements[2 * (node1 - 1) + 1]
            x2_def = node_displacements[2 * (node2 - 1)]
            y2_def = node_displacements[2 * (node2 - 1) + 1]
            ax.plot([x1_coord + x1_def, x2_coord + x2_def], [y1_coord + y1_def, y2_coord + y2_def], linestyle='-', linewidth=2.5, color=[0.4, 0.4, 0.4])

        # Deformed nodes
        for num_nod in range(number_nodes):
            node_x_coord = node_coordinates[0, num_nod]
            node_y_coord = node_coordinates[1, num_nod]
            node_x_def = node_displacements[2 * num_nod]
            node_y_def = node_displacements[2 * num_nod + 1]
            ax.plot(node_x_coord + node_x_def, node_y_coord + node_y_def, 
                    linestyle='none', linewidth=1, 
                    marker='o', markersize=4, 
                    markeredgecolor=[0.0, 0.0, 0.0], 
                    markerfacecolor=[1.0, 1.0, 1.0])

        # Deformed pin nodes
        for num_pin in range(number_pin):
            node = pin_nodes[num_pin] - 1  # Adjusting for zero-based indexing
            pin_x_coord = node_coordinates[0, node]
            pin_y_coord = node_coordinates[1, node]
            pin_x_def = node_displacements[2 * node]
            pin_y_def = node_displacements[2 * node + 1]
            ax.plot(pin_x_coord + pin_x_def, pin_y_coord + pin_y_def, 
                    linestyle='none', linewidth=1.5, 
                    marker='o', markersize=5, 
                    markeredgecolor=[0.0, 0.0, 0.0], markerfacecolor=[0.0, 0.0, 0.0])


        # Deformed roller nodes
        for num_rol in range(number_roller):
            node = roller_nodes[num_rol] - 1  # Adjusting for zero-based indexing
            roller_x_coord = node_coordinates[0, node]
            roller_y_coord = node_coordinates[1, node]
            roller_x_def = node_displacements[2 * node]
            roller_y_def = node_displacements[2 * node + 1]
            ax.plot(roller_x_coord + roller_x_def, roller_y_coord + roller_y_def, 
                    linestyle='none', linewidth=1.5, 
                    marker='o', markersize=5, 
                    markeredgecolor=[0.0, 0.0, 0.0], 
                    markerfacecolor=[1.0, 1.0, 1.0])

                
        if save:
            # Save figure as PDF
            plt.savefig(file_path, format='pdf')
        # NotImplementedError()


    def plot_stress(self, info:Info, mesh:Mesh, forces:Forces,
            displacements:Displacements, solution:Solution,
            save:bool=True, show:bool=True):
        # TODO some lists need to be converted to arrays.
        project_dir = info.project_directory
        file_name = info.file_name
        paper_size = self.paper_size
        paper_position = self.paper_position
        # scale_factor = self.scale_factor
        number_nodes = mesh.number_nodes
        number_elements = mesh.number_elements
        node_coordinates = np.transpose(np.array(mesh.node_coordinates))
        element_connectivity = np.array(mesh.element_connectivity)
        number_pin = displacements.number_pin
        pin_nodes = np.array(displacements.pin_nodes)
        number_roller = displacements.number_roller
        roller_nodes = np.array(displacements.roller_nodes)
        roller_directions = displacements.roller_directions
        roller_angles = displacements.roller_angles
        element_stress = solution.element_stress
        global_reactions = solution.global_reactions
        
        new_file_name = f"{file_name}_Stress.pdf"
        file_path = f"{project_dir}/{new_file_name}"

        # File path creation
        new_file_name = f"{file_name}_STRESS.pdf"
        file_path = f"{project_dir}/{new_file_name}"

        # Figure and axes setup
        fig, ax = plt.subplots()
        fig.set_size_inches(self.paper_size[0] / 2.54, 
                            self.paper_size[1] / 2.54)  # Convert cm to inches
        fig.patch.set_facecolor([1, 1, 1])
        ax.set_xlim(self.plot_x_limits)
        ax.set_ylim(self.plot_y_limits)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(f"{file_name}: Stress")
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')

        self._plot_rollers(node_coordinates.T, 
            displacements=displacements,
            ax=ax)

        # Elements
        pos_stress = element_stress[element_stress >= 0]
        neg_stress = element_stress[element_stress <= 0]
        max_pos_stress = max(pos_stress)
        max_neg_stress = min(neg_stress)
        for num_ele in range(number_elements):
            node1, node2 = element_connectivity[num_ele, :]
            x1_coord, y1_coord = node_coordinates[:, node1 - 1]  # Adjust for zero-based indexing
            x2_coord, y2_coord = node_coordinates[:, node2 - 1]
            element_color = get_colors(element_stress[num_ele], max_pos_stress, max_neg_stress)
            ax.plot([x1_coord, x2_coord], [y1_coord, y2_coord], 
                    linestyle='-', linewidth=3, color=element_color)

        # Forces vectors
        self._plot_force_vectors(node_coordinates.T, forces, ax)

        # Reaction vectors
        s_node = 0  # Adjusted for zero-based indexing
        # Pin reactions
        for num_pin in range(number_pin):
            p_node = pin_nodes[num_pin] - 1
            p_reaction = global_reactions[:, s_node]
            # x component
            x_react = p_reaction[0]
            f_dir_vec = np.array([x_react, 0]) / abs(x_react)
            draw_seg = get_force_arrow(node_coordinates[:, p_node], f_dir_vec, 8, self.plot_scale)
            for seg in range(3):
                ax.plot(draw_seg[2*seg:2*seg+2, 0], draw_seg[2*seg:2*seg+2, 1],
                    # draw_seg[2 * seg - 1, :], draw_seg[2 * seg, :], 
                        linestyle='-', linewidth=1, color=[0.5, 0.5, 0.5])
                
            # y component
            y_react = p_reaction[1]
            f_dir_vec = np.array([0, y_react]) / abs(y_react)
            draw_seg = get_force_arrow(node_coordinates[:, p_node], f_dir_vec, 8, self.plot_scale)
            for seg in range(3):
                ax.plot(draw_seg[2*seg:2*seg+2, 0], draw_seg[2*seg:2*seg+2, 1],
                    # draw_seg[2 * seg - 1, :], draw_seg[2 * seg, :], 
                    linestyle='-', linewidth=1, color=[0.5, 0.5, 0.5])
            s_node += 1

        # Roller reactions
        for num_rol in range(number_roller):
            r_node = roller_nodes[num_rol] - 1
            r_reaction = global_reactions[:, s_node]
            f_dir_vec = r_reaction / np.linalg.norm(r_reaction)
            draw_seg = get_force_arrow(node_coordinates[:, r_node], f_dir_vec, 8, self.plot_scale)
            for seg in range(3):
                ax.plot(draw_seg[2*seg:2*seg+2, 0], draw_seg[2*seg:2*seg+2, 1],
                    # draw_seg[2 * seg - 1, :], draw_seg[2 * seg, :], 
                    linestyle='-', linewidth=1, color=[0.5, 0.5, 0.5])
            s_node += 1

        # plot nodes, Pin Nodes, and Roller Nodes
        self._plot_all_nodes(mesh=mesh, displacements=displacements, ax=ax)

        # plot element numbers
        self._plot_element_numbers(mesh, ax)
        # Save and/or show plot
        if save:
            plt.savefig(file_path)
        if show:
            plt.show()


        # NotImplementedError()
#%%

if __name__ == '__main__':
    # pp_project_dir = pathlib.Path('example-np')
    pp_project_dir = pathlib.Path('../../examples/exam2024-01')
    info = Info(project_directory=str(pp_project_dir.absolute()), file_name='test')

    fileData = FileData.from_directory(info.project_directory)
    mesh = Mesh()
    mesh.process_mesh(file_data= fileData.mesh)

    displacements = Displacements()
    displacements.process_displacements(file_data= fileData.displacements)

    forces = Forces()
    forces.process_forces(file_data= fileData.forces)
    write_input_data(info=info, mesh=mesh, displacements=displacements, forces=forces)

    dofs = Dofs()
    dofs.process_dofs(mesh=mesh, displacements=displacements)
    analysis = Analysis()
    analysis.get_global_stiffness_matrix(mesh=mesh)
    analysis.get_global_force_vector(forces=forces, dofs=dofs)
    analysis.get_new_displacement_vector(displacements=displacements, dofs=dofs)
    analysis.get_new_transformation_matrix(displacements=displacements, dofs=dofs)  
    #================== Solution ==================
    solution = Solution()
    solution.solve_displacement(analysis, dofs)
    solution.solve_reaction(displacements=displacements)
    solution.solve_stress(mesh=mesh)
    # Usage example
    # Assume info, mesh, displacements, and solution are instances of their respective classes with attributes set
    write_results(info, mesh=mesh, displacements=displacements, solution=solution)

    # %%
    tp = TrussPlotter()
    tp.get_plot_parameters(mesh=mesh, solution=solution)

    tp.plot_truss(info,  mesh, forces, displacements, save=True, show=True)

    # %%
    tp.plot_deformation(info, mesh, forces, displacements, solution, save=False, show=True)
    # %%
    tp.plot_stress(info, mesh, forces, displacements, solution, save=False, show=True)
# %%
