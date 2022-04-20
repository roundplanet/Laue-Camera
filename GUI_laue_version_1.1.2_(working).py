# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 20:57:29 2021

@author: Julian Kaiser

Test for saving on github
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import ndimage
import scipy.ndimage.filters as filters
import scipy.optimize as opt
import queue
"""
import platform 
if(platform.platform()[:5] == "Linux"):
    import imutils
"""
import Basicfunctions_GUI as bsf
import AsyncSnap_functions_GUI as asf
import AsyncRaster_functions_GUI as arf
import AsyncBackgroundRemove_functions_GUI as abf
import AsyncCenterDetection as acd
import Frame_blueprints_GUI as fbp
import socket

#from scipy import ndimage
import time
#from matplotlib import pyplot as plt
#import datetime as dt
#from threading import Thread

#from HintergrundAbziehen_GUI import removeBackgroundFit2


request_kontur_queue = queue.Queue()
request_cur_det_max_queue = queue.Queue()
stop_exposure_queue = queue.Queue()
stop_exposure_count_queue = queue.Queue()
center_detection_queue = queue.Queue()


""" vielleicht weniger abstürze...mal schauen
import matplotlib
matplotlib.use('agg')
"""

class Window_App():
    
    #ButtonState = True
    
    def __init__(self):
        
        self.version = "1.1.2"
        
        self.root = tk.Tk(className='Laue-Camera Application')
        self.root.title("Laue-Camera Application")
        self.root.resizable(0,0)
        
        image = Image.open('./laue_app_icon_transparent_rund_neu_klein.png')
        #image = Image.open('./laue_app_icon_transparent.png')
        python_image = ImageTk.PhotoImage(image)        
        self.root.iconphoto(True, python_image)
        
        # define canvas dimension
        self.canvas_width = 975
        self.canvas_height = 643
        self.canvas_diagonal = 1168
        
        # init the first displayed image
        self.displayed_img_raw = 127 * np.ones((self.canvas_height,self.canvas_width))
        self.displayed_img_raw[0][0] = 0
        self.displayed_img_raw[1][0] = 255
        self.displayed_img_raw_backup = 127 * np.ones((self.canvas_height,self.canvas_width))
        
        # define importend lists
        self.button_list = []
        self.buttons_to_activate = []
        self.entry_list = []
        self.entries_to_activate = []
        self.radiobutton_list = []
        self.radiobuttons_to_activate = []
        
        ##############################################################################
        #### Menu Bar     ############################################################
        ##############################################################################  
        
        # define upper menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        
        # define variables for settings
        self.save_directory = os.getcwd()
        self.initialfile_name = ""
        self.SetWindow = None
        self.default_settings_list = []
        self.settings_gamma_var = tk.StringVar(self.root)
        self.settings_step_size_var = tk.StringVar(self.root)
        self.settings_neighborhood_var = tk.StringVar(self.root)
        self.settings_threshold_var = tk.StringVar(self.root)
        self.settings_scroll_faktor_var = tk.StringVar(self.root)
        self.settings_scroll_faktor = 1
        self.settings_scroll_step_size_int_var = tk.StringVar(self.root)
        self.settings_scroll_step_size_float_var = tk.StringVar(self.root)
        self.settings_scroll_widgets_list = []
        self.settings_scroll_widgets_int_list = []
        self.settings_scroll_widgets_float_list = []
        self.settings_file_prefix = ""
        self.settings_comment_var = tk.StringVar(self.root)
        self.settings_bgRemove_normal = tk.IntVar(self.root)
        self.settings_subtract_darkcurrent_with_poly = tk.IntVar(self.root)
        self.settings_polyfit_auto_delta = tk.StringVar(self.root)
        self.settings_polyfit_auto_delta_value = 40
        self.settings_polyfit_auto_increment = tk.StringVar(self.root)
        self.settings_polyfit_auto_increment_value = 40
        self.settings_comment = ""
        self.settings_symmetry_center_x_var = tk.StringVar(self.root)
        self.settings_symmetry_center_y_var = tk.StringVar(self.root)
        self.symmetry_center_x = 487.5
        self.symmetry_center_y = 321.5
        self.settings_sample_var = tk.StringVar(self.root)
        self.settings_voltage_var = tk.StringVar(self.root)
        self.settings_current_var = tk.StringVar(self.root)
        self.settings_distance_var = tk.StringVar(self.root)
        self.settings_bgRemove_during_raster = tk.IntVar(self.root)
        self.settings_raster_on_kontur = tk.IntVar(self.root)
        self.settings_raster_kontur_dehold_widgets = None
        self.settings_raster_on_kontur_threshold_percent = tk.StringVar(self.root)
        self.settings_calculate_max_exposure_during_raster = tk.IntVar(self.root)
        self.settings_center_detection_during_raster = tk.IntVar(self.root)
        self.settings_center_detection_search_width_widgets = None
        self.settings_center_detection_search_width = tk.StringVar(self.root)
        self.settings_center_detection_search_height_widgets = None
        self.settings_center_detection_search_height = tk.StringVar(self.root)
        self.settings_center_detection_search_offset_x_widgets = None
        self.settings_center_detection_search_offset_x = tk.StringVar(self.root)
        self.settings_center_detection_search_offset_y_widgets = None
        self.settings_center_detection_search_offset_y = tk.StringVar(self.root)
        self.settings_center_detection_linewidth_widgets = None
        self.settings_center_detection_linewidth = tk.StringVar(self.root)
        self.settings_center_detection_starting_angle_widgets = None
        self.settings_center_detection_starting_angle = tk.StringVar(self.root)
        self.settings_center_detection_num_lines_widgets = None
        self.settings_center_detection_num_lines = tk.StringVar(self.root)
        self.settings_center_detection_save_info_images_raster_widgets = None
        self.settings_center_detection_save_info_images_raster = tk.IntVar(self.root)
        self.settings_advanced_raster_analysis_display_offset = tk.StringVar(self.root)
        self.settings_advanced_raster_analysis_min_distance = tk.StringVar(self.root)
        self.settings_advanced_raster_analysis_max_distance = tk.StringVar(self.root)
        self.settings_advanced_raster_analysis_max_sigma = tk.StringVar(self.root)
        self.settings_advanced_raster_analysis_size_gaus_check = tk.StringVar(self.root)
        
        self.settings_12_bit_exposure = tk.IntVar(self.root)
        self.setting_is_displayed = False
        
        self.settings_12_bit_exposure_subsubframe = None
        self.settings_raster_calculate_max_exposure_during_raster_subsubframe = None
        self.settings_bg_remove_polyfit_auto_delta_subsubframe = None
        self.settings_bg_remove_polyfit_auto_increment_subsubframe = None
        
        #define variables for advanced raster analysis
        self.advanced_raster_analysis_is_displayed = False
        self.advanced_raster_analysis_add_rect_button = None
        self.advanced_raster_analysis_sub_rect_button = None
        self.advanced_raster_analysis_button_frame = None
        self.advanced_raster_analysis_cut_coords = None
        
        self.advanced_raster_analysis_rectangles_ids = []
        self.advanced_raster_analysis_rectangels_starting_coords = []
        self.advanced_raster_analysis_cut_coords_list = []
        self.advanced_raster_analysis_threshold_list = []
        self.advanced_raster_analysis_neighborhood_list = []
        
        self.advanced_raster_analysis_result_map = None
        
        #define variables for auto kontur dialog
        self.auto_kontur_detection_is_displayed = False
        self.AutoKonturDetectionWindow = None
        self.auto_kontur_detection_origin_var = tk.StringVar(self.root)
        self.auto_kontur_detection_origin_var.set("0,0")
        self.auto_kontur_detection_scale_var = tk.StringVar(self.root)
        self.auto_kontur_detection_scale_var.set("0.25")
        self.auto_kontur_detection_minimum_dots = tk.StringVar(self.root)
        self.auto_kontur_detection_minimum_dots.set("1")
        self.auto_kontur_detection_maximum_dots = tk.StringVar(self.root)
        self.auto_kontur_detection_maximum_dots.set("150")
        self.auto_kontur_detection_maximal_mean = tk.StringVar(self.root)
        self.auto_kontur_detection_maximal_mean.set("185.0")
        self.auto_kontur_detection_raster_after = tk.IntVar(self.root)
        self.auto_kontur_detection_raster_after.set(0)
        self.auto_kontur_detection_is_continuous = tk.IntVar(self.root)
        self.auto_kontur_detection_is_continuous.set(0)
        self.auto_kontur_detection_exposure_time_raster_after_subframe = None
        self.auto_kontur_detection_radio = []
        self.auto_kontur_detection_exposure_time_raster_after = tk.StringVar(self.root)
        self.auto_kontur_detection_exposure_time_raster_after.set("30")
        
        #define variables for fine-tuning bg dialog
        self.fine_tuning_bg_is_displayed = False
        self.FineTuningBgWindow = None
        self.displayed_img_raw_backup_for_file_tuning = None
        self.fine_tuning_canvas = None
        self.fine_tuning_init_img = None
        self.fine_tuning_img_on_canvas = None
        
        self.fine_tuning_max_scale_var = tk.IntVar(self.root)
        self.fine_tuning_max_scale_var.set(1000)
        self.fine_tuning_max_entry_var = tk.StringVar(self.root)
        self.fine_tuning_max_entry_var.set(str(self.fine_tuning_max_scale_var.get()))
        
        self.fine_tuning_apply_button = None

        #define variables for multiple raster dialog
        self.multiple_raster_dialog_is_displayed = False
        self.MultipleRasterWindow = None
        self.multiple_raster_big_frame = None
        self.multiple_raster_button_subframe = None
        self.multiple_raster_new_raster_button = None
        self.multiple_raster_delete_raster_button = None
        self.multiple_raster_apply_button = None
        self.multiple_raster_cancel_button = None
        self.multiple_raster_list = []
        
        # define save-shortcut
        self.root.bind('<Control-o>', self.open_file_shortcut)
        self.root.bind('<Control-r>', self.open_raster_shortcut)
        self.root.bind('<Control-Shift-R>', self.open_original_raster_shortcut)
        self.root.bind('<Control-s>', self.autosave)
        self.root.bind('<Control-Shift-S>', self.autosave_original)
        self.root.bind('<Control-Alt-s>', self.save_shortcut)
        self.root.bind('<Control-Alt-Shift-S>', self.save_original_shortcut)
        
        # define menu entries
        self.open_raster_is_original = False
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Open raster", command=self.open_raster)
        self.file_menu.add_command(label="Open original raster", command=self.open_original_raster)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save Original", command=self.save_original_file)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.tools_menu = tk.Menu(self.menu, tearoff=False)
        self.tools_menu.add_command(label="Remove Background from raster", command = self.remove_bg_from_raster)
        self.tools_menu.add_command(label="Convert .tif raster to .bmp", command = self.convert_tif_to_bmp)
        self.tools_menu.add_command(label="Analyse center of raster", command = self.analyse_center_of_raster)
        self.tools_advanced_raster_analysis_submenu = tk.Menu(self.menu, tearoff=False)
        self.tools_advanced_raster_analysis_submenu.add_command(label="Search configuration", command = self.config_advanced_raster_analysis)
        self.tools_advanced_raster_analysis_submenu.add_command(label="Start analysis of raster", command = self.begin_advanced_raster_analysis)
        self.tools_advanced_raster_analysis_submenu.add_command(label="Save results", command = self.save_results_advanced_raster_analysis)
        self.tools_advanced_raster_analysis_submenu.add_command(label="Cancel advanced raster analysis", command = self.cancel_advanced_raster_analysis)
        self.tools_menu.add_cascade(label="Advanced analysis of raster", menu=self.tools_advanced_raster_analysis_submenu)
        self.tools_menu.add_command(label="calculate max. exposure time", command = self.calculate_max_exposure)
        self.tools_menu.add_separator()
        self.tools_change_kontur_submenu = tk.Menu(self.menu, tearoff=False)
        self.tools_change_kontur_submenu.add_command(label="change kontur manually", command = self.change_kontur_manually)
        self.tools_change_kontur_submenu.add_command(label="apply manual changed kontur", command = self.apply_manual_changed_kontur)
        self.tools_change_kontur_submenu.add_command(label="cancel change kontur manually", command=self.cancel_change_kontur_manually)
        self.tools_menu.add_cascade(label="change kontur", menu=self.tools_change_kontur_submenu)
        self.tools_menu.add_command(label="new evaluation of kontur", command = self.tools_new_evaluation_of_kontur)
        self.tools_menu.add_command(label="auto kontur finding", command = self.auto_kontur_finding)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="multiple raster", command = self.multiple_raster)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="save top-bottom flipped pattern", command = self.save_tbfliped_pattern)
        self.tools_menu.add_command(label="save left-right flipped pattern", command = self.save_lrfliped_pattern)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="check NTXLaue", command=self.check_laue_camera)
        self.tools_menu.add_command(label="close NTXLaue", command=self.close_laue_camera)
        self.tools_menu.add_command(label="restart NTXLaue", command=self.restart_laue_camera)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="check PSLViewer", command=self.check_PSLViewer)
        self.tools_menu.add_command(label="restart PSLViewer", command=self.restart_PSLViewer)
        self.menu.add_cascade(label="Tools", menu=self.tools_menu)
        self.menu.add_command(label="Settings", command=self.settings_command)
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label="German", command=self.help_command_german)
        self.help_menu.add_command(label="English", command=self.help_command_english)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        
        self.change_kontur_manually_is_happening = False
        self.raster_in_progress = False
        
        ##############################################################################
        #### Canvas Frame ############################################################
        ##############################################################################        
                
        # init canvas frame
        self.canvas_frame = tk.Frame(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas_frame.grid(row=0, column=0)
        
        # init testpicture
        self.var_array = None
        self.var_img = None
        self.max_img_return = np.max(self.displayed_img_raw)
        self.min_img_return = np.min(self.displayed_img_raw)
        
        # display testpicture
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height)
        self.test_img = ImageTk.PhotoImage(image=Image.fromarray(self.displayed_img_raw), master=self.canvas_frame)
        self.img_on_canvas = self.canvas.create_image((self.canvas_width / 2, self.canvas_height / 2), image=self.test_img)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        ##############################################################################
        #### Config Frame ############################################################
        ##############################################################################

        # init config frame
        self.config_frame = tk.Frame(self.root, width=370)
        self.config_frame.grid(row=0, column=1, rowspan=2, sticky='n')
        
        # init slider variables
        self.current_value_max = tk.DoubleVar()
        self.current_value_min = tk.DoubleVar()
        self.current_gamma = tk.DoubleVar()
        self.current_neighborhood = tk.DoubleVar()
        self.current_threshold = tk.DoubleVar()

        
        # init entry variables
        self.max_input = tk.StringVar(self.root)
        self.min_input = tk.StringVar(self.root)
        self.gamma_input = tk.StringVar(self.root)
        self.neighborhood_input = tk.StringVar(self.root)
        self.threshold_input = tk.StringVar(self.root)        

        self.root.bind('<Return>', self.return_func)
        self.root.bind('<KP_Enter>', self.return_func)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_root_window)
        
        ##################################################################################
        #### Snap Subframe ###############################################################
        ##################################################################################
        
        #init snap subframe of config frame
        self.snap_subframe = tk.LabelFrame(self.config_frame, bd=2, text='take a picture', pady=5, width=370)
        
        self.max_exposure = 600
        self.max_exposure_PSL_Viewer = 16383
        self.has_moved = True
        
        # snap button
        self.snap_button = tk.Button(self.snap_subframe, text="snap", height=3, width=15, command=self.snap)
        self.snap_button.grid(row=0, column=0)
        self.button_list.append(self.snap_button)
        
        # cancel button
        self.cancel_snap_button = tk.Button(self.snap_subframe, text="cancel", height=3, width=15, command=self.cancel_snap, state=tk.DISABLED)
        self.cancel_snap_button.grid(row=0, column=1)
        self.button_list.append(self.cancel_snap_button)
        
        # exposure widgets
        self.exposure_var = tk.IntVar(self.root)
        self.exposure_var.set(120)
        self.exposure = self.exposure_var.get()
        
        self.exposure_widgets = fbp.LabelEntry_grid(self.snap_subframe, 1,0, text_label='Exposure (s)', entry_var=self.exposure_var, label_sticky='', entry_sticky='')
        self.exposure_widgets.entry.config(width=10)
        self.entry_list.append(self.exposure_widgets.entry)
        
        # display snap subframe        
        self.snap_subframe.pack(pady=5, fill='x')
        
        ##################################################################################
        #### Move Subframe ###############################################################
        ##################################################################################
        
        #init move subframe of config frame
        self.move_subframe = tk.LabelFrame(self.config_frame, bd=2, text='move/rotate sample', pady=5, width=370)
        
        # move button
        self.move_button = tk.Button(self.move_subframe, text="move", height=3, width=15, command=self.move)
        self.move_button.grid(row=0, column=0, columnspan=2)
        self.button_list.append(self.move_button)
        
        #home button
        self.home_button = tk.Button(self.move_subframe, text="home", height=3, width=15, command=self.home)
        self.home_button.grid(row=0, column=2, columnspan=2)
        self.button_list.append(self.home_button)
        
        # var for movements
        self.move_x_var = tk.DoubleVar()
        self.move_y_var = tk.DoubleVar()
        self.rotate_x_var = tk.DoubleVar()
        self.rotate_y_var = tk.DoubleVar()
        
        self.move_x_widgets = fbp.LabelEntry_grid(self.move_subframe, 1,0, ' Move X', entry_var=self.move_x_var, replace_komma=True)
        self.entry_list.append(self.move_x_widgets.entry)
        
        self.rotate_x_widgets = fbp.LabelEntry_grid(self.move_subframe, 1,2, ' Rotate X', entry_var=self.rotate_x_var, replace_komma=True)
        self.entry_list.append(self.rotate_x_widgets.entry)
        
        self.move_y_widgets = fbp.LabelEntry_grid(self.move_subframe, 2,0, ' Move Y', entry_var=self.move_y_var, replace_komma=True)
        self.entry_list.append(self.move_y_widgets.entry)
        
        self.rotate_y_widgets = fbp.LabelEntry_grid(self.move_subframe, 2,2, ' Rotate Y', entry_var=self.rotate_y_var, replace_komma=True)
        self.entry_list.append(self.rotate_y_widgets.entry)
        
        # display move subframe
        self.move_subframe.pack(pady=5, fill='x')
        
        
        ##################################################################################
        #### Symmetry Subframe ###########################################################
        ##################################################################################
        
        # define importend variables 
        self.id_circel= None
        self.line_id_list = []
        self.move_circel_step_size = 0.5
        self.step_size_var = tk.DoubleVar()
        self.step_size_var.set(0.5)
        self.step_size_text = tk.StringVar(self.root)
        self.symmetry = tk.IntVar()    
        self.step_size_max = 10.0
        
        # init symmetry subframe
        self.symmetry_subframe = tk.LabelFrame(self.config_frame, bd=2, text='optimize symmetry', pady=5, width=370)
        
        # symmetry help button
        self.show_symmetry_help = tk.Button(self.symmetry_subframe, text="show symmetry help", height=3, width=18, command=self.show_symmetry_help_click)
        self.show_symmetry_help.grid(row=0, column=0, columnspan=2)
        self.symmetry_help_is_displayed = False
        self.button_list.append(self.show_symmetry_help)
        
        # centralise button
        self.centralise_button = tk.Button(self.symmetry_subframe, text="centralise", height=3, width=12, command=self.centralise_picture, state=tk.DISABLED)
        self.centralise_button.grid(row=0, column=2)
        self.button_list.append(self.centralise_button)
        
        self.symmetry_step_size_widgets = fbp.LabelScaleEntry_grid(self.symmetry_subframe, row_=1, text_label='step size:',
                                                                   scale_from=0.5, scale_to=self.step_size_max, scale_command=self.slider_step_size_changed,
                                                                   scale_var=self.step_size_var, entry_var=self.step_size_text, replace_komma=True, 
                                                                   entry_scale_scrollable=True)
        
        self.symmetry_step_size_widgets.scroll_diff = 0.5
        self.symmetry_step_size_widgets.scroll_faktor = self.settings_scroll_faktor
        self.settings_scroll_widgets_list.append(self.symmetry_step_size_widgets)
        
        self.symmetry_step_size_widgets.scale.config(state=tk.DISABLED)
        self.symmetry_step_size_widgets.entry.insert(0,str(self.move_circel_step_size))
        self.symmetry_step_size_widgets.entry.config(state=tk.DISABLED)
        self.entry_list.append(self.symmetry_step_size_widgets.entry)

        # define symmetry label
        self.rotational_sym_label = ttk.Label(self.symmetry_subframe, text='rot. sym.')
        self.rotational_sym_label.grid(row=2, column=0, sticky='ne')          
        
        # define several radiobuttons
        self.symmetry_radio_frame = tk.Frame(self.symmetry_subframe)
        self.symmetry_radio_frame.grid(row=2, column=1, sticky='nw', columnspan=2)
        self.symmetry_radio_0 = tk.Radiobutton(self.symmetry_radio_frame, text='wo', variable=self.symmetry, value=0, command=self.change_symmetry)
        self.symmetry_radio_2 = tk.Radiobutton(self.symmetry_radio_frame, text='2', variable=self.symmetry, value=2, command=self.change_symmetry)
        self.symmetry_radio_3 = tk.Radiobutton(self.symmetry_radio_frame, text='3', variable=self.symmetry, value=3, command=self.change_symmetry)
        self.symmetry_radio_4 = tk.Radiobutton(self.symmetry_radio_frame, text='4', variable=self.symmetry, value=4, command=self.change_symmetry)
        self.symmetry_radio_6 = tk.Radiobutton(self.symmetry_radio_frame, text='6', variable=self.symmetry, value=6, command=self.change_symmetry)
        self.symmetry_radio_0.pack(side='left')
        self.symmetry_radio_2.pack(side='left')
        self.symmetry_radio_3.pack(side='left')
        self.symmetry_radio_4.pack(side='left')
        self.symmetry_radio_6.pack(side='left')
        self.radiobutton_list.append(self.symmetry_radio_0)
        self.radiobutton_list.append(self.symmetry_radio_2)
        self.radiobutton_list.append(self.symmetry_radio_3)
        self.radiobutton_list.append(self.symmetry_radio_4)
        self.radiobutton_list.append(self.symmetry_radio_6)
        self.disable_radiobuttons()
        
        # display symmetry subframe
        self.symmetry_subframe.pack(pady=5, fill='x')
    
        
        ##################################################################################
        #### Contrast Subframe ###########################################################
        ##################################################################################
        
        # init contrast subframe
        self.contrast_subframe = tk.LabelFrame(self.config_frame, bd=2, text='optimize picture', pady=5, width=370)
        
        # define constant here to avoid errors
        self.bg_removed = False   #to descide if the normal or the background-removed picture have to be displayed
        
        #### max widgets ###########s##################################################
        
        self.contrast_max_widgets = fbp.LabelScaleEntry_grid(self.contrast_subframe, 0, "Maximum:", 
                                                             scale_from=self.min_img_return, scale_to=self.max_img_return,
                                                             scale_command=self.slider_max_changed, scale_var=self.current_value_max,
                                                             entry_var=self.max_input, entry_scale_scrollable=True)
        self.contrast_max_widgets.scroll_diff = 1
        self.contrast_max_widgets.scroll_faktor = self.settings_scroll_faktor
        self.settings_scroll_widgets_list.append(self.contrast_max_widgets)
        self.settings_scroll_widgets_int_list.append(self.contrast_max_widgets)
        self.entry_list.append(self.contrast_max_widgets.entry)
        
        #### min widgets #############################################################
        
        self.contrast_min_widgets = fbp.LabelScaleEntry_grid(self.contrast_subframe, 1, 'Minimum:',
                                                             scale_from=self.min_img_return, scale_to=self.max_img_return, 
                                                             scale_command=self.slider_min_changed, scale_var=self.current_value_min,
                                                             entry_var=self.min_input, entry_scale_scrollable=True)
        
        self.contrast_min_widgets.scroll_diff = 1
        self.contrast_min_widgets.scroll_faktor = self.settings_scroll_faktor
        self.settings_scroll_widgets_list.append(self.contrast_min_widgets)
        self.settings_scroll_widgets_int_list.append(self.contrast_min_widgets)
        self.entry_list.append(self.contrast_min_widgets.entry)

        
        #### gamma widgets #############################################################
        
        self.gamma_max = 2.0
        self.contrast_gamma_widgets = fbp.LabelScaleEntry_grid(self.contrast_subframe, 2, 'Gamma:',
                                                               scale_from=0, scale_to=self.gamma_max, scale_command=self.slider_gamma_changed,
                                                               scale_var=self.current_gamma, entry_var=self.gamma_input, replace_komma=True,
                                                               entry_scale_scrollable=True)
        
        self.contrast_gamma_widgets.scroll_diff = 0.01
        self.contrast_gamma_widgets.scroll_faktor = self.settings_scroll_faktor
        self.settings_scroll_widgets_list.append(self.contrast_gamma_widgets)
        self.settings_scroll_widgets_float_list.append(self.contrast_gamma_widgets)
        self.entry_list.append(self.contrast_gamma_widgets.entry)
        
        #### neighborhood widgets ######################################################
        
        self.neighborhood_max = 15
        self.contrast_neighborhood_widgets = fbp.LabelScaleEntry_grid(self.contrast_subframe, 3, 'Neighbors:',
                                                                      scale_from=1, scale_to=self.neighborhood_max, scale_command=self.slider_neighborhood_changed,
                                                                      scale_var=self.current_neighborhood, entry_var=self.neighborhood_input, entry_scale_scrollable=True)
        
        self.contrast_neighborhood_widgets.scroll_diff = 1
        self.contrast_neighborhood_widgets.scroll_faktor = self.settings_scroll_faktor
        self.settings_scroll_widgets_list.append(self.contrast_neighborhood_widgets)
        self.settings_scroll_widgets_int_list.append(self.contrast_neighborhood_widgets)
        self.entry_list.append(self.contrast_neighborhood_widgets.entry)
        
        #### threshold widgets #########################################################
        
        self.threshold_max = 200
        self.contrast_threshold_widgets = fbp.LabelScaleEntry_grid(self.contrast_subframe, 4, 'Threshold:',
                                                                      scale_from=1, scale_to=self.threshold_max, scale_command=self.slider_threshold_changed,
                                                                      scale_var=self.current_threshold, entry_var=self.threshold_input, entry_scale_scrollable=True)
        
        self.contrast_threshold_widgets.scroll_diff = 1
        self.contrast_threshold_widgets.scroll_faktor = self.settings_scroll_faktor
        self.settings_scroll_widgets_list.append(self.contrast_threshold_widgets)
        self.settings_scroll_widgets_int_list.append(self.contrast_threshold_widgets)
        self.entry_list.append(self.contrast_threshold_widgets.entry)

        
        #### init sliders ###########################################################
        self.contrast_max_widgets.scale.set(self.max_img_return)
        self.contrast_min_widgets.scale.set(self.min_img_return)
        self.current_value_max.set(self.max_img_return)
        self.current_value_min.set(self.min_img_return)
        self.contrast_gamma_widgets.scale.set(1.0)
        self.contrast_neighborhood_widgets.scale.set(10)
        self.contrast_threshold_widgets.scale.set(100)
        
        self.contrast_neighborhood_widgets.scale.config(state=tk.DISABLED)
        self.contrast_neighborhood_widgets.entry.config(state=tk.DISABLED)
        self.contrast_threshold_widgets.scale.config(state=tk.DISABLED)
        self.contrast_threshold_widgets.entry.config(state=tk.DISABLED)
        
        
        
        #### Background Button #######################################################
        
        self.contrast_button_frame = tk.Frame(self.contrast_subframe)
        # bg button        
        self.bg_button = tk.Button(self.contrast_button_frame, command=self.bg_button_action, 
                                   text="remove background", height=3, width=33)
        #self.bg_button.grid(row=5, column=0, columnspan=3)
        self.bg_button.pack(side=tk.LEFT, fill='x')
        self.button_list.append(self.bg_button)
        
        self.bg_fine_tuning_button = tk.Button(self.contrast_button_frame, command=self.bg_fine_tuning_action,
                                               text="bg fine-tuning", height=3, width=15)
        self.button_list.append(self.bg_fine_tuning_button)
        
        self.contrast_button_frame.grid(row=5, column=0, columnspan=3)
        
        # disable sliders, entries and bg_button 
        self.disable_sliders_entries()
        self.bg_button.config(state=tk.DISABLED)
        
        self.contrast_subframe.pack(pady=5, fill='x')
        
        ##################################################################################
        #### Raster Subframe #############################################################
        ##################################################################################
        
        # init raster subframe
        self.raster_subframe = tk.LabelFrame(self.config_frame, bd=2, text='raster sample', pady=5, width=370)
        
        # raster button
        self.raster_button = tk.Button(self.raster_subframe, text="start raster", height=3, width=15, command=self.start_raster)
        self.raster_button.grid(row=0, column=0, columnspan=2)
        self.button_list.append(self.raster_button)
        
        # cancel raster button
        self.cancel_raster_button = tk.Button(self.raster_subframe, text="cancel", height=3, width=15, command=self.cancel_raster, state=tk.DISABLED)
        self.cancel_raster_button.grid(row=0, column=2, columnspan=2, sticky='w')
        self.button_list.append(self.cancel_raster_button)
        
        # init radiobuttons continuous and additive
        self.is_continuous = tk.IntVar()
        self.raster_radio_0 = tk.Radiobutton(self.raster_subframe, text='continuous', variable=self.is_continuous, value=1, pady=3)
        self.raster_radio_1 = tk.Radiobutton(self.raster_subframe, text='additive', variable=self.is_continuous, value=0, pady=3)
        self.raster_radio_0.grid(row=1, column=2, columnspan=2, sticky='w')
        self.raster_radio_1.grid(row=1, column=0, columnspan=2, sticky='w')
        self.radiobutton_list.append(self.raster_radio_0)
        self.radiobutton_list.append(self.raster_radio_1)
        
        # h_w widgets
        self.raster_h_w_var = tk.StringVar(self.root)
        self.raster_h_w_var.set("3,3")
        self.raster_h_w_widgets = fbp.LabelEntry_grid(self.raster_subframe, 2,0, text_label='(height,width)', entry_var=self.raster_h_w_var)
        self.raster_h_w_widgets.entry.config(width=5)
        self.entry_list.append(self.raster_h_w_widgets.entry)
        
        # scale widgets
        self.raster_scale_var = tk.DoubleVar(self.root)
        self.raster_scale_var.set(0.5)
        self.raster_scale_widgets = fbp.LabelEntry_grid(self.raster_subframe, 2,2, text_label=' scale', entry_var=self.raster_scale_var, replace_komma=True)
        self.raster_scale_widgets.entry.config(width=5)
        self.entry_list.append(self.raster_scale_widgets.entry)

        # coord widgets
        self.raster_coord_var = tk.StringVar(self.root)
        self.raster_coord_var.set("0,0")
        self.raster_coord_widgets = fbp.LabelEntry_grid(self.raster_subframe, 3,0, text_label='coord. (x0,y0)', entry_var=self.raster_coord_var)
        self.raster_coord_widgets.entry.config(width=5)
        self.entry_list.append(self.raster_coord_widgets.entry)
        
        #raster widgets
        self.raster_exposure_time_var = tk.IntVar(self.root)
        self.raster_exposure_time_var.set(14)
        self.raster_exposure_time_widgets = fbp.LabelEntry_grid(self.raster_subframe, 3,2, text_label=' exp. time', entry_var=self.raster_exposure_time_var)
        self.raster_exposure_time_widgets.entry.config(width=5)
        self.entry_list.append(self.raster_exposure_time_widgets.entry)
        
        # help to decide which text have to be displayed on the buttons
        self.raster_analyse_is_happening = False
        
        # analyse button raster
        self.raster_analyse_button = tk.Button(self.raster_subframe, text="analyse raster", height=3, width=15, command=self.raster_analyse)
        self.raster_analyse_button.grid(row=4, column=0, columnspan=2)
        self.button_list.append(self.raster_analyse_button)

        # move to frame button raster
        self.raster_analyse_move_to_button = tk.Button(self.raster_subframe, text="Move to Frame", height=3, width=15, command=self.raster_analyse_move_to_frame, state=tk.DISABLED)
        self.raster_analyse_move_to_button.grid(row=4, column=2, columnspan=2, sticky='w')
        self.button_list.append(self.raster_analyse_move_to_button)
        
        self.is_continuous.set(0)
        
        #display raster subframe
        self.raster_subframe.pack(pady=5, fill='x')
        
        
        ##############################################################################
        #### Console Frame ###########################################################
        ##############################################################################
        
        self.lower_frame = tk.Frame(self.root)
        self.lower_frame.grid(row=1,column=0, sticky='w')
        self.console = tk.Text(self.lower_frame, height=19, width=121, wrap=tk.WORD)
        self.console.pack(side='left')
        self.console.config(state=tk.DISABLED)
        self.print_on_console("Welcome to the Laue-GUI-Software Version " + self.version + "!")
        
        ##############################################################################
        #### Right Subframe #######################################################
        ##############################################################################
        
        self.right_subframe = tk.Frame(self.root)
        self.right_subframe.grid(row=0,column=2, rowspan=2)
        #figsize_var = (350/96, 280/96)
        figsize_var = (390/96, 312/96)
        
        ##############################################################################
        #### Plot Current Maximum Frame ##############################################
        ##############################################################################
        
        self.fig_cur_det_max_array = Figure(figsize=figsize_var, dpi=100)
        self.axes_cur_det_max_array = self.fig_cur_det_max_array.add_subplot(111)
        self.axes_cur_det_max_array.yaxis.set_tick_params(size=0, labelsize=0,labelbottom=False, labeltop=False, labelleft=False, labelright=False)
        self.axes_cur_det_max_array.xaxis.set_tick_params(size=0, labelsize=0,labelbottom=False, labeltop=False, labelleft=False, labelright=False)
        self.plot_cur_det_max_array = FigureCanvasTkAgg(self.fig_cur_det_max_array, master=self.right_subframe)
        self.plot_cur_det_max_array.get_tk_widget().pack(side='top')

        
        
        ##############################################################################
        #### Plot Array Frame ########################################################
        ##############################################################################
        
        self.fig_array = Figure(figsize=figsize_var, dpi=100)
        self.axes_array = self.fig_array.add_subplot(111)
        self.plot_array = FigureCanvasTkAgg(self.fig_array, master=self.right_subframe)
        self.plot_array.get_tk_widget().pack(side='top')
        
        self.plot_array.get_tk_widget().bind("<Button-3>", self.popmenu_for_raster_map)
        self.kontur_display_var = tk.IntVar(self.root)
        
        self.queue_stop = False
        self.plot_array_on_CanvasTkAgg_kontur(np.ones((3,3)))
        self.filelist = []
        self.current_kontur_array = None
        self.current_kontur_array_backup = None
        self.current_kontur_shape = None
        self.current_kontur_offset= (0,0)
        self.current_kontur_scale = 1
        self.current_kontur_position = (0,0)
        
        self.raster_with_center_detection_data = False
        self.center_detection_coord_data = None
        self.center_detection_rotated_angle_data = None
        self.center_detection_detailed_diff_map = None
        self.center_detection_detailed_diff_map_right_size = None
        self.center_detection_combo_map = None
        self.advanced_raster_analysis_result_map_to_display = None
        
        
        self.menu_raster_maps = tk.Menu(self.root, tearoff = 0)
        self.menu_raster_maps.add_radiobutton(label ="kontur map", variable=self.kontur_display_var, value=0, command=self.update_kontur_map_style)
        self.menu_raster_maps.add_separator()
        
        
        ##############################################################################
        #### Plot BG_Fit Frame #######################################################
        ##############################################################################
        
        #self.plot_frame = tk.Frame(self.root, width = 150)
        #self.plot_frame.grid(row=0,column=2)
        #self.fig = Figure(figsize=(310/96, 248/96), dpi=100)
        self.fig_bg = Figure(figsize=figsize_var, dpi=100)
        self.axes_bg = self.fig_bg.add_subplot(111)
        self.plot_bg = FigureCanvasTkAgg(self.fig_bg, master=self.right_subframe)
        self.plot_bg.get_tk_widget().pack(side='top')
        
        if(self.check_connection()):
            # init all move entries with the current value from the goniometer
            self.init_move_entries()
        
        self.settings_command()
        self.default_settings(call_from_main=True)
        #self.apply_changed_settings()
        
        
        
        self.root.mainloop()
        
        
    def on_closing_root_window(self):
        self.root.destroy()
        
        
    def disable_all_buttons(self):
        self.buttons_to_activate.clear()
        for i in self.button_list:
            if(str(i['state']) == 'normal'):
                i.config(state=tk.DISABLED)
                self.buttons_to_activate.append(i)
                
    def enable_disabled_buttons(self):
        for i in self.buttons_to_activate:
            i.config(state=tk.NORMAL)
        self.buttons_to_activate.clear()
        
    def disable_all_entries(self):
        self.entries_to_activate.clear()
        for i in self.entry_list:
            if(str(i['state']) == 'normal'):
                i.config(state=tk.DISABLED)
                self.entries_to_activate.append(i)
                
    def enable_disabled_entries(self):
        for i in self.entries_to_activate:
            i.config(state=tk.NORMAL)
        self.entries_to_activate.clear()
        
    def disable_all_radiobuttons(self):
        self.radiobuttons_to_activate.clear()
        for i in self.radiobutton_list:
            if(str(i['state']) == 'normal'):
                i.config(state=tk.DISABLED)
                self.radiobuttons_to_activate.append(i)
    
    def enable_disabled_radiobuttons(self):
        for i in self.radiobuttons_to_activate:
            i.config(state=tk.NORMAL)
        self.radiobuttons_to_activate.clear()
    
    def open_file(self):
        if self.advanced_raster_analysis_is_displayed:
            self.print_on_console("Advanced raster analysis is still in progress.")
            return
        filename = filedialog.askopenfilename(initialdir=self.save_directory, title="Select BMP File")
        print(filename)
        #, filetypes=[("BMP Files","*.bmp")]
        if not filename:
            return # user cancelled; stop this method
        if self.bg_removed:
            self.bg_button_action()
        self.displayed_img_raw = cv2.imread(filename, -1)
        #noch prüfen ob richige Größe
        self.var_img = None
        
        #self.var_img = None
        self.max_img_return = np.max(self.displayed_img_raw)
        self.min_img_return = np.min(self.displayed_img_raw)
        
        # enable sliders, entries and bg_button
        self.enable_sliders_entries()
        self.bg_button.config(state=tk.NORMAL)
                
        # init sliders
        self.contrast_max_widgets.scale.config(from_=self.min_img_return, to=self.max_img_return)
        self.contrast_min_widgets.scale.config(from_=self.min_img_return, to=self.max_img_return)
        
        self.contrast_max_widgets.scale.set(self.max_img_return)
        self.contrast_min_widgets.scale.set(self.min_img_return)
      
    def open_raster(self):
        if self.advanced_raster_analysis_is_displayed:
            self.print_on_console("Advanced raster analysis is still in progress.")
            return
        if self.raster_in_progress:
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        open_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select Raster")
        if not open_directory:
            return
        result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
        filenames = []
        for i in sorted(result):
            filenames.append(str(open_directory) + "/" + str(i))
        """
        filenames = filedialog.askopenfilenames(initialdir=self.save_directory, title="Select BMP Files")
        if not filenames:
            return # user cancelled; stop this method
        """
        if self.bg_removed:
            self.bg_button_action()
        datei = open(filenames[len(filenames)-1],'r')
        text_ = datei.read()
        datei.close()
        if text_.find("\n$$$") != -1:
            text = text_[:text_.find("\n$$$")].split('#',2)
        else:
            text = text_.split('#',2)
        logfile = text[0].split(':')
        text_arr = text[1]        
        try:
            self.current_kontur_shape = (int(logfile[1]),int(logfile[3]))
            self.raster_h_w_var.set(str(self.current_kontur_shape[0]) + "," + str(self.current_kontur_shape[1]))
            self.current_kontur_offset= tuple(map(float, logfile[9].replace('(','').replace(')','').split(', ')))
            self.raster_coord_var.set(str(self.current_kontur_offset[0]) + "," + str(self.current_kontur_offset[1]))
            self.current_kontur_scale = float(logfile[5])
            self.raster_scale_var.set(self.current_kontur_scale)
            self.raster_exposure_time_var.set(int(float(logfile[7])))
        except:
            self.print_on_console("Error: Raster logfile is written in a wrong format.")
            return
        
        arr = np.ones(self.current_kontur_shape[0]*self.current_kontur_shape[1], dtype=int)
        i = 0
        for val in text_arr:
            if val.isnumeric():
                arr[i] = val
                i = i + 1
                
        begin_centerData = "\n$$$beginCenterData$$$"
        end_centerData = "$$$endCenterData$$$\n"
        
        if (text_.find(begin_centerData) != -1) and (text_.find(end_centerData) != -1):
            self.raster_with_center_detection_data = True
            data = text_[text_.find(begin_centerData)+len(begin_centerData):text_.find(end_centerData)]  
            
            data_center_coord = data[1].split("]\n [")
            data_rotated_degree = data[0].replace("[","").replace("]","").replace(",","").split(" ")
                        
            data_center_coord[0] = data_center_coord[0].replace("\n", "").replace("[[", "").replace("]]", "")
            data_center_coord[1] = data_center_coord[1].replace("\n", "").replace("[[", "").replace("]]", "")
            self.center_detection_coord_data = np.zeros((2,self.current_kontur_shape[0],self.current_kontur_shape[1]))
            #TODO: checken ob nicht bei .5 probleme auftauchen
            data_x = data_center_coord[0].replace(".", "").replace("  ", " ").split(" ")
            data_arr_x = np.reshape(np.array(data_x), self.current_kontur_shape)
            data_y = data_center_coord[1].replace(".", "").replace("  ", " ").split(" ")
            data_arr_y = np.reshape(np.array(data_y), self.current_kontur_shape)
            
            self.center_detection_coord_data[0,:,:] = data_arr_x
            self.center_detection_coord_data[1,:,:] = data_arr_y
            
            self.center_detection_rotated_angle_data = np.reshape(np.array(data_rotated_degree, dtype=int), self.current_kontur_shape)
            
            self.center_detection_detailed_diff_map = np.zeros(((self.center_detection_coord_data.shape[1]-2)*3+4,(self.center_detection_coord_data.shape[2]-2)*3+4))
    
            def abstand(p1,p2):
                return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            
            for y in range(self.center_detection_coord_data.shape[1]):
                for x in range(self.center_detection_coord_data.shape[2]):
                    all_dist = []
                    for dy in [1,-1,0]:
                        for dx in [1,-1,0]:
                            x_pos = x*3 + dx
                            y_pos = y*3 + dy
                            if dy == 0 and dx == 0:
                                self.center_detection_detailed_diff_map[y_pos,x_pos] = np.mean(all_dist)
                            elif not(x_pos < 0 or x_pos >= self.center_detection_detailed_diff_map.shape[1]):
                                if not(y_pos < 0 or y_pos >= self.center_detection_detailed_diff_map.shape[0]):
                                    dist = abstand(self.center_detection_coord_data[:,y,x], self.center_detection_coord_data[:,y+dy,x+dx])
                                    self.center_detection_detailed_diff_map[y_pos,x_pos] = dist
                                    all_dist.append(dist)
                                    
            self.center_detection_detailed_diff_map_right_size = cv2.resize(self.center_detection_detailed_diff_map, dsize=(self.current_kontur_shape[1], self.current_kontur_shape[0]), interpolation=cv2.INTER_CUBIC)
            
            self.center_detection_combo_map  = self.center_detection_rotated_angle_data+self.center_detection_detailed_diff_map_right_size
            
        else:
            self.raster_with_center_detection_data = False
            
        begin_advancedData = "\n$$$beginAdvancedData$$$"
        end_advancedData = "$$$endAdvancedData$$$\n"
        
        if (text_.find(begin_advancedData) != -1) and (text_.find(end_advancedData) != -1):
            cache_arr = np.ones(self.current_kontur_shape[0]*self.current_kontur_shape[1], dtype=int)
            cache_text = text_[text_.find(begin_advancedData)+len(begin_advancedData):text_.find(end_advancedData)]
            i = 0
            for val in cache_text:
                if val.isnumeric():
                    cache_arr[i] = val
                    i = i + 1
            self.advanced_raster_analysis_result_map_to_display = np.copy(cache_arr.reshape(self.current_kontur_shape))
        else:
            self.advanced_raster_analysis_result_map_to_display = None
                
        self.kontur_display_var.set(0)
        kontur = arr.reshape(self.current_kontur_shape)
        self.bg_button.config(state=tk.NORMAL)
        self.current_kontur_array = np.copy(kontur)
        self.current_kontur_array_backup = np.copy(self.current_kontur_array)
        self.plot_array_on_CanvasTkAgg_kontur(kontur)
        self.filelist = list(filenames[0:(len(filenames)-1)])
        self.open_raster_is_original = False
        
    def open_original_raster(self):
        if self.raster_in_progress:
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        if self.advanced_raster_analysis_is_displayed:
            self.print_on_console("Advanced raster analysis is still in progress.")
            return
        open_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select Original Raster")
        if not open_directory:
            return
        result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
        filenames = []
        for i in sorted(result):
            filenames.append(str(open_directory) + "/" + str(i))
        """
        filenames = filedialog.askopenfilenames(initialdir=self.save_directory, title="Select TIF Files")
        if not filenames:
            return # user cancelled; stop this method
        """
        if self.bg_removed:
            self.bg_button_action()
        datei = open(filenames[len(filenames)-1],'r')
        text_ = datei.read()
        datei.close()
        if text_.find("\n$$$") != -1:
            text = text_[:text_.find("\n$$$")].split('#',2)
        else:
            text = text_.split('#',2)
        logfile = text[0].split(':')
        text_arr = text[1]
        try:
            self.current_kontur_shape = (int(logfile[1]),int(logfile[3]))
            self.raster_h_w_var.set(str(self.current_kontur_shape[0]) + "," + str(self.current_kontur_shape[1]))
            self.current_kontur_offset= tuple(map(float, logfile[9].replace('(','').replace(')','').split(', ')))
            self.raster_coord_var.set(str(self.current_kontur_offset[0]) + "," + str(self.current_kontur_offset[1]))
            self.current_kontur_scale = float(logfile[5])
            self.raster_scale_var.set(self.current_kontur_scale)
            self.raster_exposure_time_var.set(int(float(logfile[7])))
        except:
            self.print_on_console("Error: Raster logfile is written in a wrong format.")
            return

        arr = np.ones(self.current_kontur_shape[0]*self.current_kontur_shape[1], dtype=int)
        i = 0
        for val in text_arr:
            if val.isnumeric():
                arr[i] = val
                i = i + 1
                
        begin_centerData = "\n$$$beginCenterData$$$"
        end_centerData = "$$$endCenterData$$$\n"
        
        if (text_.find(begin_centerData) != -1) and (text_.find(end_centerData) != -1):
            self.raster_with_center_detection_data = True
            data = text_[text_.find(begin_centerData)+len(begin_centerData)+2:text_.find(end_centerData)].split('\n#')
            
            data_center_coord = data[1].split("]\n [")
            data_rotated_degree = data[0].replace("[","").replace("]","").replace(",","").split(" ")
                        
            data_center_coord[0] = data_center_coord[0].replace("\n", "").replace("[[", "").replace("]]", "")
            data_center_coord[1] = data_center_coord[1].replace("\n", "").replace("[[", "").replace("]]", "")
            self.center_detection_coord_data = np.zeros((2,self.current_kontur_shape[0],self.current_kontur_shape[1]))
            data_x = data_center_coord[0].replace(".", "").replace("  ", " ").split(" ")
            data_arr_x = np.reshape(np.array(data_x), self.current_kontur_shape)
            data_y = data_center_coord[1].replace(".", "").replace("  ", " ").split(" ")
            data_arr_y = np.reshape(np.array(data_y), self.current_kontur_shape)
            
            self.center_detection_coord_data[0,:,:] = data_arr_x
            self.center_detection_coord_data[1,:,:] = data_arr_y
            
            self.center_detection_rotated_angle_data = np.reshape(np.array(data_rotated_degree, dtype=int), self.current_kontur_shape)
            
            self.center_detection_detailed_diff_map = np.zeros(((self.center_detection_coord_data.shape[1]-2)*3+4,(self.center_detection_coord_data.shape[2]-2)*3+4))
    
            def abstand(p1,p2):
                return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            
            for y in range(self.center_detection_coord_data.shape[1]):
                for x in range(self.center_detection_coord_data.shape[2]):
                    all_dist = []
                    for dy in [1,-1,0]:
                        for dx in [1,-1,0]:
                            x_pos = x*3 + dx
                            y_pos = y*3 + dy
                            if dy == 0 and dx == 0:
                                self.center_detection_detailed_diff_map[y_pos,x_pos] = np.mean(all_dist)
                            elif not(x_pos < 0 or x_pos >= self.center_detection_detailed_diff_map.shape[1]):
                                if not(y_pos < 0 or y_pos >= self.center_detection_detailed_diff_map.shape[0]):
                                    dist = abstand(self.center_detection_coord_data[:,y,x], self.center_detection_coord_data[:,y+dy,x+dx])
                                    self.center_detection_detailed_diff_map[y_pos,x_pos] = dist
                                    all_dist.append(dist)
                                    
            self.center_detection_detailed_diff_map_right_size = cv2.resize(self.center_detection_detailed_diff_map, dsize=(self.current_kontur_shape[1], self.current_kontur_shape[0]), interpolation=cv2.INTER_CUBIC)
            
            self.center_detection_combo_map  = self.center_detection_rotated_angle_data+self.center_detection_detailed_diff_map_right_size
            
        else:
            self.raster_with_center_detection_data = False
            
        begin_advancedData = "\n$$$beginAdvancedData$$$"
        end_advancedData = "$$$endAdvancedData$$$\n"
        
        if (text_.find(begin_advancedData) != -1) and (text_.find(end_advancedData) != -1):
            cache_arr = np.ones(self.current_kontur_shape[0]*self.current_kontur_shape[1], dtype=int)
            cache_text = text_[text_.find(begin_advancedData)+len(begin_advancedData):text_.find(end_advancedData)]
            i = 0
            for val in cache_text:
                if val.isnumeric():
                    cache_arr[i] = val
                    i = i + 1
            self.advanced_raster_analysis_result_map_to_display = np.copy(cache_arr.reshape(self.current_kontur_shape))
        else:
            self.advanced_raster_analysis_result_map_to_display = None
            
        self.kontur_display_var.set(0)
        kontur = arr.reshape(self.current_kontur_shape)
        self.bg_button.config(state=tk.NORMAL)
        self.current_kontur_array = np.copy(kontur)
        self.current_kontur_array_backup = np.copy(self.current_kontur_array)
        self.plot_array_on_CanvasTkAgg_kontur(kontur)
        self.filelist = list(filenames[0:(len(filenames)-1)])
        self.open_raster_is_original = True
        
    def save_file(self):
        filename = filedialog.asksaveasfilename(initialfile = self.initialfile_name + ".bmp", defaultextension='.bmp', initialdir=self.save_directory, title="Save as BMP File (default) or other filetype (add .xxx)", filetypes=[("BMP Files","*.bmp")])
        if not filename:
            return # user cancelled; stop this method
        cv2.imwrite(filename, self.var_array)
        
    def save_original_file(self):
        filename = filedialog.asksaveasfilename(initialfile = self.initialfile_name + ".tif", defaultextension='.tif', initialdir=self.save_directory, title="Save as TIF File", filetypes=[("TIF Files","*.tif")])
        if not filename:
            return # user cancelled; stop this method
        #cv2.imwrite(filename, self.displayed_img_raw)
        save_image = self.displayed_img_raw.astype('uint16')
        cv2.imwrite(filename, save_image)
        
    def return_func(self, event):  
        try: 
            neighborhood_user = int(self.contrast_neighborhood_widgets.entry.get())
            self.contrast_neighborhood_widgets.scale.set(neighborhood_user)
        except ValueError:
            self.contrast_neighborhood_widgets.entry.delete(0, tk.END)
            self.contrast_neighborhood_widgets.entry.insert(0,str(self.contrast_neighborhood_widgets.scale.get()))
            self.print_on_console("Couldn't convert 'neighborhood' to float!")
            
        
        try:
            max_input_user = int(self.max_input.get())
            self.contrast_max_widgets.scale.set(max_input_user)
        except ValueError:
            self.contrast_max_widgets.entry.delete(0,tk.END)
            self.contrast_max_widgets.entry.insert(0,str(int(self.current_value_max.get())))
            self.print_on_console("Couldn't convert 'maximum' to int!")
            
        try:
            min_input_user = int(self.min_input.get())
            self.contrast_min_widgets.scale.set(min_input_user)
        except ValueError:
            self.contrast_min_widgets.entry.delete(0,tk.END)
            self.contrast_min_widgets.entry.insert(0,str(int(self.current_value_min.get())))
            self.print_on_console("Couldn't convert 'minimum' to int!")
        
        try:
            gamma_input_user = float(self.gamma_input.get())
            self.contrast_gamma_widgets.scale.set(gamma_input_user)
        except ValueError:
            self.contrast_gamma_widgets.entry.delete(0,tk.END)
            self.contrast_gamma_widgets.entry.insert(0,str(self.current_gamma.get()))
            self.print_on_console("Couldn't convert 'gamma' to float!")
            
        try:
            step_size_user = round(float(self.step_size_text.get()),2)
            if(step_size_user > self.step_size_max):
                self.symmetry_step_size_widgets.scale.set(step_size_user)
            elif(step_size_user < 0.5):
                self.symmetry_step_size_widgets.scale.set(0.5)
            else:
                self.symmetry_step_size_widgets.scale.set(step_size_user)
        except ValueError:
            self.symmetry_step_size_widgets.entry.delete(0,tk.END)
            self.symmetry_step_size_widgets.entry.insert(0,str(self.symmetry_step_size_widgets.scale.get()))
            self.print_on_console("Couldn't convert 'symmetry step size' to float!")
        
        try: 
            threshold_user = int(self.contrast_threshold_widgets.entry.get())
            self.contrast_threshold_widgets.scale.set(threshold_user)
        except ValueError:
            self.contrast_threshold_widgets.entry.delete(0, tk.END)
            self.contrast_threshold_widgets.entry.insert(0,str(self.contrast_threshold_widgets.scale.get()))
            self.print_on_console("Couldn't convert 'threshold' to float!")
            
            
    def settings_command(self):
        if self.setting_is_displayed:
            self.SetWindow.lift()
            return
        self.setting_is_displayed = True
        self.SetWindow = tk.Toplevel(self.root)
        self.SetWindow.protocol("WM_DELETE_WINDOW", self.on_closing_settings_window)
        self.SetWindow.title("Settings")
        
        top_frame = tk.Frame(self.SetWindow)
        left_subframe = tk.Frame(top_frame, width=370)
        right_subframe = tk.Frame(top_frame, width=370)
        
        
        ##############################################################################
        #### Max Values Subframe #####################################################
        ##############################################################################
        
        settings_max_values_subframe = tk.LabelFrame(left_subframe, bd=2, text='max values', pady=5, width=370)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_max_values_subframe, 'gamma', self.settings_gamma_var, replace_komma=True)
        self.settings_gamma_var.set(self.gamma_max)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_max_values_subframe, 'symmetry step size', self.settings_step_size_var, replace_komma=True)
        self.settings_step_size_var.set(self.step_size_max)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_max_values_subframe, 'neighborhood', self.settings_neighborhood_var, replace_komma=True)
        self.settings_neighborhood_var.set(self.neighborhood_max)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_max_values_subframe, 'threshold', self.settings_threshold_var, replace_komma=True)
        self.settings_threshold_var.set(self.threshold_max)
        
        ##############################################################################
        
        self.settings_12_bit_exposure_subsubframe = fbp.FrameLabelCheckbutton_pack(settings_max_values_subframe, text_label="record 12-Bit images only (Raster and Snap)", checkbutton_var=self.settings_12_bit_exposure)
        
        ##############################################################################
        
        settings_max_values_subframe.pack(pady=5, fill='x')
        
        ##############################################################################
        #### Scroll Subframe #########################################################
        ##############################################################################
        
        settings_scroll_subframe = tk.LabelFrame(left_subframe, bd=2, text='scroll settings', pady=5, width=370)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_scroll_subframe, 'scroll faktor', self.settings_scroll_faktor_var, replace_komma=True)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_scroll_subframe, 'scroll step size for int', self.settings_scroll_step_size_int_var)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_scroll_subframe, 'scroll step size for float', self.settings_scroll_step_size_float_var, replace_komma=True)
        
        ##############################################################################
        
        settings_scroll_subframe.pack(pady=5, fill='x')
        
        ##############################################################################
        #### Symmetry Center Subframe ################################################
        ##############################################################################
                
        settings_symmetry_center_subframe = tk.LabelFrame(left_subframe, bd=2, text='symmetry center', pady=5, width=370)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_symmetry_center_subframe, 'center position x (px)', self.settings_symmetry_center_x_var, replace_komma=True)
        self.settings_symmetry_center_x_var.set(self.symmetry_center_x)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_symmetry_center_subframe, 'center position y (px)', self.settings_symmetry_center_y_var, replace_komma=True)
        self.settings_symmetry_center_y_var.set(self.symmetry_center_y)
        
        ##############################################################################
        
        settings_symmetry_center_subframe.pack(pady=5, fill='x')
        
        ##############################################################################
        #### Save File Settings Subframe #############################################
        ##############################################################################
        
        settings_save_file_subframe = tk.LabelFrame(left_subframe, bd=2, text='save settings', pady=5, width=370)
        
        settings_save_file_button = tk.Button(settings_save_file_subframe, text="change save directory", height=2, width=48, command=self.change_save_file_directory)
        settings_save_file_button.pack(fill='x')
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_save_file_subframe, 'sample name/number', self.settings_sample_var)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_save_file_subframe, 'voltage (kV)', self.settings_voltage_var)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_save_file_subframe, 'current (mA)', self.settings_current_var)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_save_file_subframe, 'distance (mm)', self.settings_distance_var, replace_komma=True)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_save_file_subframe, 'comment', self.settings_comment_var)
        
        ##############################################################################
        
        settings_save_file_subframe.pack(pady=5, fill='x') 
        
        ##############################################################################
        #### BG-Remove Settings Subframe #############################################
        ##############################################################################
        
        settings_bg_remove_settings_subframe = tk.LabelFrame(left_subframe, bd=2, text='background remove settings', pady=5, width=370)
        
        fbp.FrameLabelCheckbutton_pack(settings_bg_remove_settings_subframe, text_label='normal (entire screen)', checkbutton_var=self.settings_bgRemove_normal)
        
        fbp.FrameLabelCheckbutton_pack(settings_bg_remove_settings_subframe, text_label='partial (each detector separately)', checkbutton_var=self.settings_bgRemove_normal).checkbutton.config(onvalue=0, offvalue=1)
        
        fbp.FrameLabelCheckbutton_pack(settings_bg_remove_settings_subframe, text_label='remove dark-current background with polynomial fit', checkbutton_var=self.settings_subtract_darkcurrent_with_poly).checkbutton.config(command=self.polyfit_check_entry_checkbox)
        
        self.settings_bg_remove_polyfit_auto_delta_subsubframe = fbp.FrameLabelEntry_pack(settings_bg_remove_settings_subframe, 'auto delta for polynomial fit', self.settings_polyfit_auto_delta)
        
        self.settings_bg_remove_polyfit_auto_increment_subsubframe = fbp.FrameLabelEntry_pack(settings_bg_remove_settings_subframe, 'auto increment for polynomial fit', self.settings_polyfit_auto_increment)
        
        if self.settings_subtract_darkcurrent_with_poly.get():
            self.settings_bg_remove_polyfit_auto_delta_subsubframe.entry.config(state=tk.NORMAL)
            self.settings_bg_remove_polyfit_auto_increment_subsubframe.entry.config(state=tk.NORMAL)
        else:
            self.settings_bg_remove_polyfit_auto_delta_subsubframe.entry.config(state=tk.DISABLED)
            self.settings_bg_remove_polyfit_auto_increment_subsubframe.entry.config(state=tk.DISABLED)
        
        settings_bg_remove_settings_subframe.pack(pady=5, fill='x')#, side='top') 
        
        ##############################################################################
        #### Raster Settings Subframe ################################################
        ##############################################################################

        settings_raster_settings_subframe = tk.LabelFrame(right_subframe, bd=2, text='raster settings', pady=5, width=370)
        
        ##############################################################################
        
        fbp.FrameLabelCheckbutton_pack(settings_raster_settings_subframe, text_label='auto background remove during raster', checkbutton_var=self.settings_bgRemove_during_raster)
        
        ##############################################################################
        
        self.settings_raster_calculate_max_exposure_during_raster_subsubframe = fbp.FrameLabelCheckbutton_pack(settings_raster_settings_subframe, text_label='calculate max. exposure time during raster', checkbutton_var = self.settings_calculate_max_exposure_during_raster)
        
        ##############################################################################
        
        fbp.FrameLabelCheckbutton_pack(settings_raster_settings_subframe, text_label='enable raster on kontur', checkbutton_var=self.settings_raster_on_kontur).checkbutton.config(command=self.threshold_check_entry_checkbox)
        
        ##############################################################################
        
        self.settings_raster_kontur_threshold_widgets = fbp.FrameLabelEntry_pack(settings_raster_settings_subframe, text_label='threshold (time for kontur to time for raster in %)', entry_var=self.settings_raster_on_kontur_threshold_percent, replace_komma=True)
        if self.settings_raster_on_kontur.get():
            self.settings_raster_kontur_threshold_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_raster_kontur_threshold_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################
        
        settings_raster_settings_subframe.pack(pady=5, fill='x', side='top')
        
        ##############################################################################
        #### Center Detection Subframe ###############################################
        ##############################################################################
        
        settings_center_detection_settings_subframe = tk.LabelFrame(right_subframe, bd=2, text='center detection settings', pady=5, width=370)
        
        ##############################################################################
        
        fbp.FrameLabelCheckbutton_pack(settings_center_detection_settings_subframe, text_label='enable center detection during raster', checkbutton_var=self.settings_center_detection_during_raster).checkbutton.config(command=self.center_detection_check_entry_checkbox)
        
        ##############################################################################
        
        self.settings_center_detection_search_width_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='search width', entry_var=self.settings_center_detection_search_width, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_search_width_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_search_width_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################  
        
        self.settings_center_detection_search_height_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='search height', entry_var=self.settings_center_detection_search_height, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_search_height_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_search_height_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################  
               
        self.settings_center_detection_search_offset_x_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='search x-offset', entry_var=self.settings_center_detection_search_offset_x, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_search_offset_x_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_search_offset_x_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################
        
        self.settings_center_detection_search_offset_y_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='search y-offset', entry_var=self.settings_center_detection_search_offset_y, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_search_offset_y_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_search_offset_y_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################
        
        self.settings_center_detection_linewidth_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='search linewidth', entry_var=self.settings_center_detection_linewidth, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_linewidth_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_linewidth_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################  
        
        self.settings_center_detection_starting_angle_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='starting angle', entry_var=self.settings_center_detection_starting_angle, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_starting_angle_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_starting_angle_widgets.entry.config(state=tk.DISABLED)
        
        ##############################################################################  
        
        self.settings_center_detection_num_lines_widgets = fbp.FrameLabelEntry_pack(settings_center_detection_settings_subframe, text_label='number of lines', entry_var=self.settings_center_detection_num_lines, replace_komma=True)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_num_lines_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_num_lines_widgets.entry.config(state=tk.DISABLED)
        
        ############################################################################## 
        
        self.settings_center_detection_save_info_images_raster_widgets = fbp.FrameLabelCheckbutton_pack(settings_center_detection_settings_subframe, text_label='save info image during center detection', checkbutton_var=self.settings_center_detection_save_info_images_raster)
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_save_info_images_raster_widgets.checkbutton.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_save_info_images_raster_widgets.checkbutton.config(state=tk.DISABLED)
        
        
        ##############################################################################
        
        settings_center_detection_settings_subframe.pack(pady=5, fill='x', side='top')
        
        ##############################################################################
        #### Advanced raster analysis Subframe #######################################
        ##############################################################################
        
        settings_advanced_raster_analysis_settings_subframe = tk.LabelFrame(right_subframe, bd=2, text='advanced raster analysis settings', pady=5, width=370)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_advanced_raster_analysis_settings_subframe, 'display offset', self.settings_advanced_raster_analysis_display_offset)

        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_advanced_raster_analysis_settings_subframe, 'minimum distance', self.settings_advanced_raster_analysis_min_distance)

        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_advanced_raster_analysis_settings_subframe, 'maximum distance', self.settings_advanced_raster_analysis_max_distance)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_advanced_raster_analysis_settings_subframe, 'maximum sigma', self.settings_advanced_raster_analysis_max_sigma)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(settings_advanced_raster_analysis_settings_subframe, 'size of gaus-check', self.settings_advanced_raster_analysis_size_gaus_check)
        
        ##############################################################################
        
        settings_advanced_raster_analysis_settings_subframe.pack(pady=5, fill='x', side='top')
        
        left_subframe.pack(side='left', padx=5, fill=None, expand=False)
        right_subframe.pack(side='top', padx=5, fill=None, expand=False)
        top_frame.pack()
        
        settings_button_subframe = tk.Frame(self.SetWindow)
        
        settings_apply_button = tk.Button(settings_button_subframe, text='apply', height=1, command=self.apply_changed_settings)
        settings_apply_button.pack(side = tk.LEFT)
        
        settings_default_button = tk.Button(settings_button_subframe, text='default', height=1, command=self.default_settings)
        settings_default_button.pack(side = tk.RIGHT)        
        
        settings_button_subframe.pack(pady=5) 
        
    
    
    def on_closing_settings_window(self):
        self.SetWindow.destroy()
        self.setting_is_displayed = False
        
    def change_save_file_directory(self):
        self.save_directory = filedialog.askdirectory(initialdir=self.save_directory)
        
    def polyfit_check_entry_checkbox(self):
        if self.settings_subtract_darkcurrent_with_poly.get():
            self.settings_bg_remove_polyfit_auto_delta_subsubframe.entry.config(state=tk.NORMAL)
            self.settings_bg_remove_polyfit_auto_increment_subsubframe.entry.config(state=tk.NORMAL)
        else:
            self.settings_bg_remove_polyfit_auto_delta_subsubframe.entry.config(state=tk.DISABLED)
            self.settings_bg_remove_polyfit_auto_increment_subsubframe.entry.config(state=tk.DISABLED)
        
    def threshold_check_entry_checkbox(self):
        if self.settings_raster_on_kontur.get():
            self.settings_raster_kontur_threshold_widgets.entry.config(state=tk.NORMAL)
        else:
            self.settings_raster_kontur_threshold_widgets.entry.config(state=tk.DISABLED)
            
    def center_detection_check_entry_checkbox(self):
        if self.settings_center_detection_during_raster.get():
            self.settings_center_detection_search_width_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_search_height_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_linewidth_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_starting_angle_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_num_lines_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_search_offset_x_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_search_offset_y_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_save_info_images_raster_widgets.checkbutton.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_search_width_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_search_height_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_linewidth_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_starting_angle_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_num_lines_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_search_offset_x_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_search_offset_y_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_save_info_images_raster_widgets.checkbutton.config(state=tk.DISABLED)
        
    def apply_changed_settings(self, call_from_default=False):
        errors = 0
        try:
            gamma_max_user = round(float(self.settings_gamma_var.get()),2)
            if(gamma_max_user < 0):
                self.print_on_console("'gamma max' must be greater than 0! Is set to default.")
                self.settings_gamma_var.set(self.default_settings_list[0])
                gamma_max_user = round(float(self.settings_gamma_var.get()),2)
            self.gamma_max = gamma_max_user
            self.contrast_gamma_widgets.scale.config(to=self.gamma_max)
        except:
            self.print_on_console("Couldn't convert 'gamma max' to float! Is set to float.")
            self.settings_gamma_var.set(self.default_settings_list[0])
            errors = errors + 1
        
        try:
            if(str(self.symmetry_step_size_widgets.scale['state']) == 'disabled'):
                self.symmetry_step_size_widgets.scale.config(state=tk.NORMAL)
                symmetry_step_size_user = round(float(self.settings_step_size_var.get()),2)
                self.symmetry_step_size_widgets.scale.config(to=symmetry_step_size_user)
                self.symmetry_step_size_widgets.scale.config(state=tk.DISABLED)
            else:
                symmetry_step_size_user = round(float(self.settings_step_size_var.get()),2)
                self.symmetry_step_size_widgets.scale.config(to=symmetry_step_size_user)
        except:
            self.print_on_console("Couldn't convert 'symmetry step size max' to float! Is set to default.")
            self.settings_step_size_var.set(self.default_settings_list[1])
            errors = errors + 1
        
            
        try:
            neighborhood_max_user = int(self.settings_neighborhood_var.get())
            if (neighborhood_max_user < 1):
                self.print_on_console("'neighborhood max' must be greater than 0! Is set to default.")
                self.settings_neighborhood_var.set(self.default_settings_list[2])
                errors = errors + 1
            else:
                self.neighborhood_max = neighborhood_max_user
                self.contrast_neighborhood_widgets.scale.config(to=self.neighborhood_max)
                case = 0
                if not(self.contrast_neighborhood_widgets.entry['state'] == 'normal'):
                    self.contrast_neighborhood_widgets.entry.config(state = tk.NORMAL)
                    case = 1
                self.contrast_neighborhood_widgets.entry.delete(0,tk.END)
                if self.current_neighborhood.get() > neighborhood_max_user:
                    self.contrast_neighborhood_widgets.entry.insert(0, str(neighborhood_max_user))
                else:
                    self.contrast_neighborhood_widgets.entry.insert(0, str(int(self.current_neighborhood.get())))
                if case:
                    self.contrast_neighborhood_widgets.entry.config(state = tk.DISABLED)
        except:
            self.print_on_console("'neighborhood max' can't be converted to int! Is set to default.")
            self.settings_neighborhood_var.set(self.default_settings_list[2])
            errors = errors + 1
            
        try:
            threshold_max_user = int(self.settings_threshold_var.get())
            if threshold_max_user < 1:
                self.print_on_console("'threshold max' must be greater than 0! Is set to default.")
                self.settings_threshold_var.set(self.default_settings_list[3])
                errors = errors + 1
            else:
                self.threshold_max = threshold_max_user
                self.contrast_threshold_widgets.scale.config(to=self.threshold_max)
                case = 0
                if not(self.contrast_threshold_widgets.entry['state'] == 'normal'):
                    self.contrast_threshold_widgets.entry.config(state = tk.NORMAL)
                    case = 1
                self.contrast_threshold_widgets.entry.delete(0,tk.END)
                if self.current_threshold.get() > threshold_max_user:
                    self.contrast_threshold_widgets.entry.insert(0, str(threshold_max_user))
                else:
                    self.contrast_threshold_widgets.entry.insert(0, str(int(self.current_threshold.get())))
                if case:
                    self.contrast_threshold_widgets.entry.config(state = tk.DISABLED)
        except:
            self.print_on_console("'threshold max' can't be converted to int! Is set to default.")
            self.settings_threshold_var.set(self.default_settings_list[3])
            errors = errors + 1
            
        try:
            scroll_faktor_user = float(self.settings_scroll_faktor_var.get())
            if scroll_faktor_user < 0:
                self.print_on_console("Value of 'scroll faktor' is less than 0! Is set to 0.")
            else:
                self.settings_scroll_faktor = scroll_faktor_user
        except:
            self.print_on_console("Couldn't convert 'scroll faktor' to float! Is set to default.")
            self.settings_scroll_faktor_var.set(self.default_settings_list[5])
            errors = errors + 1
            
        try:
            scroll_step_size_int_user = int(self.settings_scroll_step_size_int_var.get())
            if scroll_step_size_int_user < 0:
                self.print_on_console("Value of 'scroll step size for int' is less than 0! Is set to 0.")
        except:
            self.print_on_console("Couldn't convert 'scroll step size for int' to int! Is set to default.")
            self.settings_scroll_step_size_int_var.set(self.default_settings_list[6])
            errors = errors + 1
            
        try:
            scroll_step_size_float_user = float(self.settings_scroll_step_size_float_var.get())
            if scroll_step_size_float_user < 0:
                self.print_on_console("Value of 'scroll step size for float' is less than 0! Is set to 0.")
        except:
            self.print_on_console("Couldn't convert 'scroll step size for float' to float! Is set to default.")
            self.settings_scroll_step_size_float_var.set(self.default_settings_list[7])
            errors = errors + 1
        
        try:
            symmetry_center_x_user = round(float(self.settings_symmetry_center_x_var.get()),1)
            if(symmetry_center_x_user < 0):
                self.print_on_console("Value of 'symmetry center x' is negative, is set to 0.0")
                self.symmetry_center_x = 0.0
                errors = errors + 1
            elif(symmetry_center_x_user > self.canvas_width):
                self.print_on_console("Value of 'symmetry center x' is greater than canvas width, is set to " + str(self.canvas_width) + ".")
                self.symmetry_center_x = self.canvas_width
                errors = errors + 1
            else: 
                self.symmetry_center_x = symmetry_center_x_user
        except:
            self.print_on_console("Couldn't convert 'symmetry center x' to float! Is set to default")
            self.settings_symmetry_center_x_var.set(self.default_settings_list[8])
            self.symmetry_center_x = round(float(self.settings_symmetry_center_x_var.get()),1)
            errors = errors + 1
            
        try:
            symmetry_center_y_user = round(float(self.settings_symmetry_center_y_var.get()),1)
            if(symmetry_center_y_user < 0):
                self.print_on_console("Value of 'symmetry center y' is negative, is set to 0.0")
                self.symmetry_center_y = 0.0
                errors = errors + 1
            elif(symmetry_center_y_user > self.canvas_height):
                self.print_on_console("Value of 'symmetry center y' is greater than canvas height, is set to " + str(self.canvas_height) + ".")
                self.symmetry_center_y = self.canvas_height
                errors = errors + 1
            else: 
                self.symmetry_center_y = symmetry_center_y_user
        except:
            self.print_on_console("Couldn't convert 'symmetry center y' to float! Is set to default")
            self.settings_symmetry_center_y_var.set(self.default_settings_list[9])
            self.symmetry_center_y = round(float(self.settings_symmetry_center_y_var.get()),1)
            errors = errors + 1
        
        self.show_symmetry_help_click()
        self.show_symmetry_help_click()
        
        try:
            voltage = round(int(self.settings_voltage_var.get()))
        except:
            self.print_on_console("Couldn't convert 'voltage' to int! Is set to default.")
            voltage = self.default_settings_list[11]
            self.settings_voltage_var.set(self.default_settings_list[11])
            errors = errors + 1
            
        try:
            current = round(int(self.settings_current_var.get()))
        except:
            self.print_on_console("Couldn't convert 'current' to int! Is set to default.")
            current = self.default_settings_list[12]
            self.settings_current_var.set(self.default_settings_list[12])
            errors = errors + 1
            
        try:
            distance = round(float(self.settings_distance_var.get()),1)
        except:
            self.print_on_console("Couldn't convert 'distance' to float! Is set to default")
            distance = self.default_settings_list[13]
            self.settings_distance_var.set(self.default_settings_list[13])
            errors = errors + 1
            
        try:
            auto_delta_polyfit = int(self.settings_polyfit_auto_delta.get())
            if (auto_delta_polyfit < 0):
                self.print_on_console("Value of 'auto delta for polyfit' is negativ!. Is set to default.")
                self.settings_polyfit_auto_delta.set(self.default_settings_list[17])
                self.settings_polyfit_auto_delta_value = 0
                errors = errors + 1
            else:
                self.settings_polyfit_auto_delta_value = auto_delta_polyfit
        except:
            self.print_on_console("Couldn't convert 'auto delta for polyfit' to int. Is set to default.")
            self.settings_polyfit_auto_delta.set(self.default_settings_list[17])
            errors = errors + 1
            
        try:
            auto_increment_polyfit = int(self.settings_polyfit_auto_increment.get())
            if (auto_increment_polyfit < 0):
                self.print_on_console("Value of 'auto increment for polyfit' is negativ!. Is set to default.")
                self.settings_polyfit_auto_increment.set(self.default_settings_list[18])
                self.settings_polyfit_auto_increment_value = 0
                errors = errors + 1
            else:
                self.settings_polyfit_auto_increment_value = auto_increment_polyfit
        except:
            self.print_on_console("Couldn't convert 'auto delta for polyfit' to int.")
            self.settings_polyfit_auto_increment.set(self.default_settings_list[18])
            errors = errors + 1
                
            
        try:
            threshold_percent = float(self.settings_raster_on_kontur_threshold_percent.get())
            if threshold_percent > 100.0:
                self.print_on_console("Value of 'threshold' is greater than 100%. Is set to '100.0'")
                self.settings_raster_on_kontur_threshold_percent.set("100.0")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'threshold' to float. Is set to default.")
            self.settings_raster_on_kontur_threshold_percent.set(self.default_settings_list[22])
            errors = errors + 1
        
        try:
            center_detect_width = int(self.settings_center_detection_search_width.get())
            if (center_detect_width < 0):
                self.print_on_console("No negative values for search width in center detection are allowed!")
                errors = errors + 1
            if (center_detect_width > 643):
                self.print_on_console("Values greater than image width for search width in center detection are not allowed!")
                errors = errors + 1
            if (center_detect_width%2 == 0):
                self.print_on_console("Values for search width in center detection ar not allowed to be even! Search width is increased by 1.")
                self.settings_center_detection_search_width.set(str(center_detect_width + 1))
            
        except:
            self.print_on_console("Couldn't convert 'search width' to int. Is set to default.")
            self.settings_center_detection_search_width.set(self.default_settings_list[24])
            errors = errors + 1

        
        try:
            center_detect_height = int(self.settings_center_detection_search_height.get())
            if (center_detect_height < 0):
                self.print_on_console("No negative values for search height in center detection are allowed!")
                errors = errors + 1
            if (center_detect_height > 975):
                self.print_on_console("Values greater than image height for search height in center detection are not allowed!")
                errors = errors + 1
            if (center_detect_height%2 == 0):
                self.print_on_console("Values for search height in center detection ar not allowed to be even! Search height is increased by 1.")
                self.settings_center_detection_search_height.set(center_detect_height + 1)
        except:
            self.print_on_console("Couldn't convert 'search height' to int. Is set to default.")
            self.settings_center_detection_search_height.set(self.default_settings_list[25])
            errors = errors + 1
            
        try:
            center_detect_offset_x = int(self.settings_center_detection_search_offset_x.get())
            if (center_detect_width//2)-np.abs(center_detect_offset_x) < 0:
                self.print_on_console("Defined x-offset is too large for the defined width! Please increase the search width.")
                errors = errors + 1
            if np.abs(center_detect_offset_x) > 487:
                self.print_on_console("Defined x-offset can't be greater than half of the image width!")
        except:
            self.print_on_console("Couldn't convert 'search x-offset' to int. Is set to default.")
            self.settings_center_detection_search_offset_x.set(self.default_settings_list[26])
            errors = errors + 1
            
        try:
            center_detect_offset_y = int(self.settings_center_detection_search_offset_y.get())
            if (center_detect_height//2)-np.abs(center_detect_offset_y) < 0:
                self.print_on_console("Defined x-offset is too large for the defined height! Please increase the search height.")
                errors = errors + 1
            if np.abs(center_detect_offset_y) > 321:
                self.print_on_console("Defined y-offset can't be greater than half of the image height!")
        except:
            self.print_on_console("Couldn't convert 'search y-offset' to int. Is set to default.")
            self.settings_center_detection_search_offset_y.set(self.default_settings_list[27])
            errors = errors + 1
        
        try:
            center_detect_linewidth = int(self.settings_center_detection_linewidth.get())
            if (center_detect_linewidth < 0):
                self.print_on_console("No negative values for linewidth in center detection are allowed!")
                errors = errors + 1
            if (center_detect_linewidth > 100):
                self.print_on_console("Values greater than 100 for linewidth in center detection maybe produce false results!")
        except:
            self.print_on_console("Couldn't convert 'linewidth' to int. Is set to default.")
            self.settings_center_detection_linewidth.set(self.default_settings_list[28])
            errors = errors + 1
                
        
        try:
            starting_angle = int(self.settings_center_detection_starting_angle.get())
            if starting_angle > 359:
                self.settings_center_detection_starting_angle.set(str(starting_angle%360))
                self.print_on_console("Starting angle is greater than 360°. Is normalised to the range between 0° and 360°.")
            if starting_angle < 0:
                self.settings_center_detection_starting_angle.set(str(starting_angle%360))
                self.print_on_console("Starting angle is lower than 0°. Is normalised to the range between 0° and 360°.")
        except:
            self.print_on_console("Couldn't convert 'starting angle' to int. Is set to default.")
            self.settings_center_detection_starting_angle.set(self.default_settings_list[29])
            errors = errors + 1
            
        self.settings_center_detection_num_lines_widgets
        
        try:
            num_lines = int(self.settings_center_detection_num_lines.get())
            if num_lines > 10:
                self.print_on_console("Number of lines greater than 10 are not supported!")
                errors = errors + 1
            elif num_lines < 0:
                self.print_on_console("Number of lines has to be positive!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'number of lines' to int. Is set to default.")
            self.settings_center_detection_num_lines.set(self.default_settings_list[30])
            errors = errors + 1
            
        try:
            display_offset_user = int(self.settings_advanced_raster_analysis_display_offset.get())
            if display_offset_user < 1:
                self.print_on_console("Display offset has to be greater than 0!")
                errors = errors + 1
            elif display_offset_user > 300:
                self.print_on_console("Display offset is too large!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'display offset' to int. Is set to default.")
            self.settings_advanced_raster_analysis_display_offset.set(self.default_settings_list[32])
            errors = errors + 1
            
        try:
            min_distance_user = int(self.settings_advanced_raster_analysis_min_distance.get())
            if min_distance_user < 2:
                self.print_on_console("Minimum distance has to be greater than 1!")
                errors = errors + 1
            elif min_distance_user > int(self.settings_advanced_raster_analysis_max_distance.get()):
                self.print_on_console("Minimum distance has to be smaller than maximum distance!")
                errors = errors + 1
        except ValueError:
            self.print_on_console("Couldn't convert 'minimum distance' to int. Is set to default.")
            self.settings_advanced_raster_analysis_min_distance.set(self.default_settings_list[33])
            errors = errors + 1
            
        try:
            max_distance_user = int(self.settings_advanced_raster_analysis_max_distance.get())
            if min_distance_user < 2:
                self.print_on_console("Maximum distance has to be greater than 1!")
                errors = errors + 1
            elif max_distance_user < int(self.settings_advanced_raster_analysis_min_distance.get()):
                self.print_on_console("Maximum distance has to be greater than minimum distance!")
                errors = errors + 1
        except ValueError:
            self.print_on_console("Couldn't convert 'maximum distance' to int. Is set to default.")
            self.settings_advanced_raster_analysis_max_distance.set(self.default_settings_list[34])
            errors = errors + 1
            
        try:
            max_sigma_user = int(self.settings_advanced_raster_analysis_max_sigma.get())
            if max_sigma_user < 2:
                self.print_on_console("Maximum sigma has to be greater than 1!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'maximum sigma' to int. Is set to default.")
            self.settings_advanced_raster_analysis_max_sigma.set(self.default_settings_list[35])
            errors = errors + 1
            
        try:
            size_gaus_check_user = int(self.settings_advanced_raster_analysis_size_gaus_check.get())
            if size_gaus_check_user < 2:
                self.print_on_console("Size of gaus-check has to be greater than 1!")
                errors = errors + 1
            elif size_gaus_check_user%2 == 0:
                self.print_on_console("Size of gaus-check is not allowed to be even!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'size gaus-check' to int. Is set to default.")
            self.settings_advanced_raster_analysis_size_gaus_check.set(self.default_settings_list[36])
            errors = errors + 1
            
        
        if self.settings_12_bit_exposure.get() and self.settings_calculate_max_exposure_during_raster.get():
                self.settings_12_bit_exposure_subsubframe.checkbutton.flash()
                self.settings_raster_calculate_max_exposure_during_raster_subsubframe.checkbutton.flash()
                self.print_on_console("'12-bit exposure' and 'max. exposure calculation' can't be selected at the same time!")
                return False
        
        if errors > 0:
            return False
        else:
            self.settings_file_prefix = self.settings_sample_var.get() + "_" + str(voltage) + "kV" + str(current) + "mA_" + str(int(distance//1)) + "p" + str(int(round((distance%1)*10,1))) + "mm" 
            self.settings_comment = self.settings_comment_var.get()
            
            self.change_initialfile_name()            
            
            for i in self.settings_scroll_widgets_list:
                i.scroll_faktor = self.settings_scroll_faktor
            for i in self.settings_scroll_widgets_int_list:
                i.scroll_diff = scroll_step_size_int_user
            for i in self.settings_scroll_widgets_float_list:
                i.scroll_diff = scroll_step_size_float_user 
            if call_from_default:
                return True
            self.SetWindow.destroy()
            self.setting_is_displayed = False
            if self.advanced_raster_analysis_is_displayed:
                self.advanced_raster_analysis_bind_events()
            return True
        
    def set_default_settings(self):
        self.settings_gamma_var.set(self.default_settings_list[0])
        self.settings_step_size_var.set(self.default_settings_list[1])
        self.settings_neighborhood_var.set(self.default_settings_list[2])
        self.settings_threshold_var.set(self.default_settings_list[3])
        self.settings_12_bit_exposure.set(int(self.default_settings_list[4]))
        self.settings_scroll_faktor_var.set(self.default_settings_list[5])
        self.settings_scroll_step_size_int_var.set(self.default_settings_list[6])
        self.settings_scroll_step_size_float_var.set(self.default_settings_list[7])
        self.settings_symmetry_center_x_var.set(self.default_settings_list[8])
        self.settings_symmetry_center_y_var.set(self.default_settings_list[9])
        self.save_directory = os.getcwd()
        self.settings_sample_var.set(self.default_settings_list[10])
        self.settings_voltage_var.set(self.default_settings_list[11])
        self.settings_current_var.set(self.default_settings_list[12])
        self.settings_distance_var.set(self.default_settings_list[13])
        self.settings_comment_var.set(self.default_settings_list[14])
        self.settings_bgRemove_normal.set(int(self.default_settings_list[15]))
        self.settings_subtract_darkcurrent_with_poly.set(int(self.default_settings_list[16]))
        self.settings_polyfit_auto_delta.set(self.default_settings_list[17])
        self.settings_polyfit_auto_increment.set(self.default_settings_list[18])
        self.settings_bgRemove_during_raster.set(int(self.default_settings_list[19]))
        self.settings_calculate_max_exposure_during_raster.set(int(self.default_settings_list[20]))
        self.settings_raster_on_kontur.set(int(self.default_settings_list[21]))
        self.settings_raster_on_kontur_threshold_percent.set(self.default_settings_list[22])
        self.settings_center_detection_during_raster.set(int(self.default_settings_list[23]))
        self.settings_center_detection_search_width.set(self.default_settings_list[24])
        self.settings_center_detection_search_height.set(self.default_settings_list[25])
        self.settings_center_detection_search_offset_x.set(self.default_settings_list[26])
        self.settings_center_detection_search_offset_y.set(self.default_settings_list[27])
        self.settings_center_detection_linewidth.set(self.default_settings_list[28])
        self.settings_center_detection_starting_angle.set(self.default_settings_list[29])
        self.settings_center_detection_num_lines.set(self.default_settings_list[30])
        self.settings_center_detection_save_info_images_raster.set(int(self.default_settings_list[31]))
        self.settings_advanced_raster_analysis_display_offset.set(self.default_settings_list[32])
        self.settings_advanced_raster_analysis_min_distance.set(self.default_settings_list[33])
        self.settings_advanced_raster_analysis_max_distance.set(self.default_settings_list[34])
        self.settings_advanced_raster_analysis_max_sigma.set(self.default_settings_list[35])
        self.settings_advanced_raster_analysis_size_gaus_check.set(self.default_settings_list[36])
            
        if not(int(self.default_settings_list[19])):
            self.settings_raster_kontur_threshold_widgets.entry.config(state=tk.DISABLED)
        else:
            self.settings_raster_kontur_threshold_widgets.entry.config(state=tk.NORMAL)
            
        if int(self.default_settings_list[21]):
            self.settings_center_detection_search_width_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_search_height_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_search_offset_x_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_search_offset_y_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_linewidth_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_starting_angle_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_num_lines_widgets.entry.config(state=tk.NORMAL)
            self.settings_center_detection_save_info_images_raster_widgets.checkbutton.config(state=tk.NORMAL)
        else:
            self.settings_center_detection_search_width_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_search_height_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_search_offset_x_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_search_offset_y_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_linewidth_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_starting_angle_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_num_lines_widgets.entry.config(state=tk.DISABLED)
            self.settings_center_detection_save_info_images_raster_widgets.checkbutton.config(state=tk.DISABLED)
            
        if self.settings_subtract_darkcurrent_with_poly.get():
            self.settings_bg_remove_polyfit_auto_delta_subsubframe.entry.config(state=tk.NORMAL)
            self.settings_bg_remove_polyfit_auto_increment_subsubframe.entry.config(state=tk.NORMAL)
        else:
            self.settings_bg_remove_polyfit_auto_delta_subsubframe.entry.config(state=tk.DISABLED)
            self.settings_bg_remove_polyfit_auto_increment_subsubframe.entry.config(state=tk.DISABLED)
        
    def default_settings(self, call_from_main=False):
        datei = open("./default_settings",'r')
        text = datei.read().split('\n',37)
        datei.close()
        text = text[:-1]
        for i in range(len(text)):
            pos = text[i].find(":")
            text[i] = text[i][pos+1:]
        self.default_settings_list = text
        checkbutton_var = [4, 15, 16, 19, 20, 21, 23, 31]
        for j in checkbutton_var:
            try:
                k = int(text[j])
                if not(k == 1) and not(k ==0):
                    self.print_on_console("Default settings file contains non-formated argument in line " + str(j) + ". Default settings are set to the original settings.")
                    self.default_settings_list = ['2.0', '10.0', '15', '200', '0', '1.0', '1', '0.01', '487.5', '321.5', 'Sample_1', '20', '30', '40.0', 'comment', '0', '1', '40', '40', '0', '1', '0', '5.0', '0', '41', '41', '0', '0', '10', '0', '6', '0', '5', '2', '20', '15', '11']
            except:
                self.print_on_console("Default settings file contains non-formated argument in line " + str(j) + ". Default settings are set to the original settings.")
                self.default_settings_list = ['2.0', '10.0', '15', '200', '0', '1.0', '1', '0.01', '487.5', '321.5', 'Sample_1', '20', '30', '40.0', 'comment', '0', '1', '40', '40', '0', '1', '0', '5.0', '0', '41', '41', '0', '0', '10', '0', '6', '0', '5', '2', '20', '15', '11']
        self.set_default_settings()
        if not(self.apply_changed_settings(call_from_default=True)):
            self.default_settings_list = ['2.0', '10.0', '15', '200', '0', '1.0', '1', '0.01', '487.5', '321.5', 'Sample_1', '20', '30', '40.0', 'comment', '0', '1', '40', '40', '0', '1', '0', '5.0', '0', '41', '41', '0', '0', '10', '0', '6', '0', '5', '2', '20', '15', '11']
            self.set_default_settings()
            self.apply_changed_settings(call_from_default=True)
            self.print_on_console("Default settings file contains non-formated arguments! Default settings are set to the original settings.")
        if call_from_main:
            self.SetWindow.destroy()
            self.setting_is_displayed = False
            return
        if self.advanced_raster_analysis_is_displayed:
            self.advanced_raster_analysis_bind_events()
        
    
    def change_initialfile_name(self):
        self.initialfile_name = self.settings_file_prefix + "_" + str(self.exposure) + "s" + "_" + self.settings_comment
        
        if (self.initialfile_name.find('/') != -1):
            self.print_on_console("Warning! File prefix contains the char '/', exceptions during save process are common.")
            
    def help_command_german(self):
        help_thread_german = asf.AsyncHelpGermanDisplay()
        help_thread_german.start()
        
    def help_command_english(self):
        help_thread_english = asf.AsyncHelpEnglishDisplay()
        help_thread_english.start()
        
    def open_file_shortcut(self, event):
        self.open_file()
        
    def open_raster_shortcut(self, event):
        self.open_raster()
        
    def open_original_raster_shortcut(self, event):
        self.open_original_raster()
        
    def autosave(self, event):
        if(os.path.isfile(str(self.save_directory) + "/" + str(self.initialfile_name) + "_000.bmp")):
            self.autosave_extend_filename(1)
        else:
            cv2.imwrite(str(self.save_directory) + "/" + str(self.initialfile_name) + "_000.bmp", self.var_array)
            self.print_on_console("Autosave file '" + str(self.initialfile_name) + "_000.bmp'")
        
    def autosave_extend_filename(self, i):
        if(os.path.isfile(str(self.save_directory) + "/" + str(self.initialfile_name) + "_%0.3u"% (i) + ".bmp")):
            self.autosave_extend_filename(i + 1)
        else:
            cv2.imwrite(str(self.save_directory) + "/" + str(self.initialfile_name) + "_%0.3u"% (i)+ ".bmp", self.var_array)
            self.print_on_console("Autosave file '" + str(self.initialfile_name) + "_%0.3u"% (i) + ".bmp'")
            
    def autosave_original(self, event):
        if(os.path.isfile(str(self.save_directory) + "/" + str(self.initialfile_name) + "_original_000.tif")):
            self.autosave_original_extend_filename(1)
        else:
            cv2.imwrite(str(self.save_directory) + "/" + str(self.initialfile_name) + "_original_000.tif", self.displayed_img_raw)
            self.print_on_console("Autosave original file '" + str(self.initialfile_name) + "_original_000.tif'")
            
    def autosave_original_extend_filename(self, i):
        if(os.path.isfile(str(self.save_directory) + "/" + str(self.initialfile_name) + "_original_%0.3u"% (i) + ".tif")):
            self.autosave_original_extend_filename(i + 1)
        else:
            cv2.imwrite(str(self.save_directory) + "/" + str(self.initialfile_name) + "_original_%0.3u"% (i)+ ".tif", self.displayed_img_raw)
            self.print_on_console("Autosave original file '" + str(self.initialfile_name) + "_original_%0.3u"% (i) + ".tif'")
    
    def save_shortcut(self, event):
        self.save_file()      
        
    def save_original_shortcut(self, event):
        self.save_original_file()
        
    def remove_bg_from_raster(self):
        open_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select a raster to remove background")
        if not open_directory:
            return
        result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
        filenames = []
        filedirs = []
        for i in sorted(result):
            filedirs.append(str(open_directory) + "/" + str(i))
            filenames.append(str(i))
            
        save_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select a new save directory for raster without background") 
        if not save_directory:
            return
        save_directory = save_directory + "/Raster_Bg_Removed/"
        try:
            os.makedirs(save_directory)
        except FileExistsError:
            save_directory = self.extend_save_directory(save_directory, 2)
        print(save_directory)
        
        #filedirs = list(filedirs[0:(len(filedirs)-1)])
        """
        for i in range(len(filedirs)-1):
            file = cv2.imread(filedirs[i], -1)
            return_image,_,_,_ = removeBackgroundFit2(file)
            cv2.imwrite(save_directory + filenames[i], return_image)
        last = len(filedirs) - 1
        cv2.imwrite(save_directory[last] + filenames[last], filedirs[last])
        """
        bgRemoveRasterThread = abf.AsyncBgRemoveForRaster(filedirs, save_directory, filenames, self)
        bgRemoveRasterThread.start()
    
    def convert_tif_to_bmp(self):
        max_value = int(self.current_value_max.get())
        min_value = int(self.current_value_min.get())
        mean_to_scale = tk.simpledialog.askinteger(".tif- to .bmp-raster" , "Choose a mean-value to which the contrast is optimized", parent=self.root, minvalue=min_value, maxvalue=max_value, initialvalue=70)
        if mean_to_scale == None:
            return

        open_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select a .tif-raster to convert to a .bmp-raster")
        if not open_directory:
            return
        result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
        filenames = []
        filedirs = []
        for i in sorted(result):
            filedirs.append(str(open_directory) + "/" + str(i))
            filenames.append(str(i))
            
        save_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select a new save directory for the .bmp-raster") 
        if not save_directory:
            return
        save_directory = save_directory + "/bitmaps/"
        try:
            os.makedirs(save_directory)
        except FileExistsError:
            save_directory = self.extend_save_directory(save_directory, 2)
        print(save_directory)
        
        bgConvertTifRasterToBmpRasterThread = abf.AsyncConvertionTifToBmp(filedirs, save_directory, filenames, mean_to_scale, self)
        bgConvertTifRasterToBmpRasterThread.start()
        
        
    def analyse_center_of_raster(self):
        if self.raster_in_progress:
            self.print_on_console("Another operation is still in progress, please wait until it's finished.")
            return
        open_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select a raster to analyse")
        if not open_directory:
            return
        result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
        filenames = []
        filedirs = []
        for i in sorted(result):
            filedirs.append(str(open_directory) + "/" + str(i))
            filenames.append(str(i))
            
        logfile = filenames[-1]
        filenames = filenames[:-1]
        save_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select a new save directory for the results") 
        if not save_directory:
            return
        save_directory = save_directory + "/Center_Detection_Results/"
        try:
            os.makedirs(save_directory)
        except FileExistsError:
            save_directory = self.extend_save_directory(save_directory, 2)

        
        save_directory_whole_results = save_directory + "whole_results/"
        os.makedirs(save_directory_whole_results)
        if (self.settings_center_detection_save_info_images_raster.get()):
            saveDirectoryCenterDetectionInfoImages = save_directory + "info_images/"
            os.makedirs(saveDirectoryCenterDetectionInfoImages)
        
            datei = open(open_directory+'/'+logfile,'r')
            text = datei.read()
            datei.close()
            with open(save_directory+ "info_images/" + logfile, 'w') as f:
                f.write(text)
        
        width = int(self.settings_center_detection_search_width.get())
        height = int(self.settings_center_detection_search_height.get())
        offset_x = int(self.settings_center_detection_search_offset_x.get())
        offset_y = int(self.settings_center_detection_search_offset_x.get())
        linewidth = int(self.settings_center_detection_linewidth.get())
        starting_angle = int(self.settings_center_detection_starting_angle.get())
        num_lines = int(self.settings_center_detection_num_lines.get())
        save_info_images = int(self.settings_center_detection_save_info_images_raster.get())
        center_coord_P5 = np.zeros((2, len(filenames)))
        rotated_degree = []
        center_detect_thread = acd.AsyncCenterDetection(width, height, offset_x, offset_y, linewidth, starting_angle, num_lines, center_coord_P5, rotated_degree, save_info_images, center_detection_queue, self)
        center_detect_thread.start()
        
        for i in filenames:
            center_detection_queue.put((open_directory + "/" + i,save_directory))
        center_detection_queue.put(("Stop",save_directory_whole_results, open_directory+'/'+logfile, save_directory+ "info_images/" + logfile))
        
        self.print_on_console("Analysis of the selected raster started. The program tends to be slower during the process. Please don't close the application!")
        
    def extend_save_directory(self,save_directory,i):
        if i == 2:
            save_directory = save_directory[:-1] + "_%0.3u"% (i) + "/"
        else:
            save_directory = save_directory[:-5] + "_%0.3u"% (i) + "/"
        try:
            os.makedirs(save_directory)
            return save_directory
        except FileExistsError:
            save_directory = self.extend_save_directory(save_directory, i + 1)  
            return save_directory
    
    def config_advanced_raster_analysis(self):
        if self.current_kontur_array is None:
            self.print_on_console("No Kontur messured")
            return
        if self.advanced_raster_analysis_is_displayed:
            self.print_on_console("Advanced raster analysis is still in progress.")
            return
        if self.raster_in_progress:
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        self.advanced_raster_analysis_is_displayed = True
        self.bg_button.pack_forget()
        self.advanced_raster_analysis_button_frame = tk.Frame(self.contrast_button_frame)
        
        self.advanced_raster_analysis_add_rect_button = tk.Button(self.advanced_raster_analysis_button_frame, command=self.add_rect,
                                               text="add rect", height=3, width=15)
        self.advanced_raster_analysis_add_rect_button.grid(row=0, column=0)
        self.advanced_raster_analysis_sub_rect_button = tk.Button(self.advanced_raster_analysis_button_frame, command=self.sub_rect,
                                               text="sub rect", height=3, width=15)
        self.advanced_raster_analysis_sub_rect_button.grid(row=0, column=1)
        
        self.advanced_raster_analysis_button_frame.pack(fill='x')
        
        self.advanced_raster_analysis_bind_events()
        self.current_kontur_position = (0,0)        
        
        self.contrast_neighborhood_widgets.scale.config(state=tk.NORMAL)
        self.contrast_neighborhood_widgets.entry.config(state=tk.NORMAL)
        self.contrast_threshold_widgets.scale.config(state=tk.NORMAL)
        self.contrast_threshold_widgets.entry.config(state=tk.NORMAL)
        
        self.disable_all_buttons()
        
        if self.current_kontur_array is None:
            self.print_on_console("No Kontur messured")
            self.cancel_advanced_raster_analysis()
        else:
            self.display_analysed_kontur_in_advanced_raster_analysis()
    
    def advanced_raster_analysis_bind_events(self):
        self.canvas.bind('<Button-1>', self.rectangle)
        self.canvas.bind('<B1-Motion>', self.rectangle)
        self.canvas.bind('<ButtonRelease-1>', self.save_new_cut_borders)
        self.canvas.bind('<Double-Button-3>', self.config_rectangle)
        self.canvas.bind('<Button-3>', self.change_current_rectangle)
        
        self.root.bind('<KeyPress-Up>', self.change_kontur_vertical)
        self.root.bind('<KeyPress-Down>', self.change_kontur_vertical)
        self.root.bind('<KeyPress-Left>', self.change_kontur_horizontal)
        self.root.bind('<KeyPress-Right>', self.change_kontur_horizontal)
    
    def add_rect(self):
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            self.canvas.itemconfigure(self.advanced_raster_analysis_rectangles_ids[-1], outline='orange')
        if len(self.advanced_raster_analysis_rectangles_ids) == 2:
            self.print_on_console("Warning! Code is only developed for two rectangels at the moment! ")
        self.advanced_raster_analysis_rectangles_ids.append(self.canvas.create_rectangle(100, 100, 110, 110, outline='blue'))
        self.advanced_raster_analysis_rectangels_starting_coords.append((100,100))
        self.advanced_raster_analysis_cut_coords = (100,110,100,110)
        self.advanced_raster_analysis_cut_coords_list.append((100,110,100,110))
        
        self.advanced_raster_analysis_threshold_list.append(int(self.current_threshold.get()))
        self.advanced_raster_analysis_neighborhood_list.append(int(self.current_neighborhood.get()))
       
    def sub_rect(self):
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            self.canvas.delete(self.advanced_raster_analysis_rectangles_ids[-1])
            
            self.advanced_raster_analysis_threshold_list = self.advanced_raster_analysis_threshold_list[:-1]
            self.advanced_raster_analysis_neighborhood_list = self.advanced_raster_analysis_neighborhood_list[:-1]
            self.current_threshold.set(int(self.advanced_raster_analysis_threshold_list[-1]))
            self.slider_threshold_changed(None)
            self.current_neighborhood.set(int(self.advanced_raster_analysis_neighborhood_list[-1]))
            self.slider_neighborhood_changed(None)
        
            self.advanced_raster_analysis_rectangles_ids = self.advanced_raster_analysis_rectangles_ids[:-1]
            self.canvas.itemconfigure(self.advanced_raster_analysis_rectangles_ids[-1], outline='blue')
            self.advanced_raster_analysis_rectangels_starting_coords = self.advanced_raster_analysis_rectangels_starting_coords[:-1]
            self.advanced_raster_analysis_cut_coords_list = self.advanced_raster_analysis_cut_coords_list[:-1]
            
        else:
            self.print_on_console("No rectangels remains to delete!")
        
    def begin_advanced_raster_analysis(self):
        if len(self.advanced_raster_analysis_rectangles_ids) == 0:
            self.print_on_console("Please configure the analysis parameter before!")
            return
        if len(self.advanced_raster_analysis_threshold_list) == len(self.advanced_raster_analysis_rectangles_ids):
            self.advanced_raster_analysis_threshold_list[-1] = int(self.current_threshold.get())
            self.advanced_raster_analysis_neighborhood_list[-1] = int(self.current_neighborhood.get())
        else:
            self.advanced_raster_analysis_threshold_list.append(int(self.current_threshold.get()))
            self.advanced_raster_analysis_neighborhood_list.append(int(self.current_neighborhood.get()))
        cases_result_ = []
        dots_result = np.zeros(self.current_kontur_shape)
        for i, coord in enumerate(self.advanced_raster_analysis_cut_coords_list):
            (h0,h1,w0,w1) = coord
            threshold = self.advanced_raster_analysis_threshold_list[i]
            neighborhood = self.advanced_raster_analysis_neighborhood_list[i]
            dots = np.zeros(self.current_kontur_shape)
            cases = np.zeros(self.current_kontur_shape)
            for index, j in enumerate(self.filelist):
                position = (index//dots_result.shape[1],index%dots_result.shape[1])
                img = cv2.imread(j, -1)
                data = img[h0:h1+1,w0:w1+1]
                dots_cache = self.DetectByMaximaAndCheckWithGaussian(data, threshold=threshold, neighborhood=neighborhood)
                dots[position], cases[position] = self.CheckAndClassifyDots(dots_cache)
            dots_result = dots_result + dots
            cases[cases > 2] = 2
            cases_result_.append(cases)
        
        #TODO: für mehr als zwei Bereiche
        heat_map = np.zeros(self.current_kontur_shape)
        if len(cases_result_) == 2:
            for h in range(cases_result_[0].shape[0]):
                for w in range(cases_result_[0].shape[1]):
                    cache = cases_result_[0][h,w] + cases_result_[1][h,w]
                    if cache == 3:
                        heat_map[h,w] = 4
                    elif cache == 2 and cases_result_[0][h,w] == 1 and cases_result_[1][h,w] == 1:
                        heat_map[h,w] = 3
                    else:
                        heat_map[h,w] = int(cache)
        else:
            heat_map = cases_result_[0]
            
        """
        heat_map = np.zeros(self.current_kontur_shape)
        heat_map[cases_result_[0] == 1] = 1
        heat_map[cases_result_[1] == 1] = 1
        heat_map[cases_result_[0] == 2] = 2
        heat_map[cases_result_[1] == 2] = 2
        cache_cases_result_ = np.copy(cases_result_[1])
        cache_cases_result_[cache_cases_result_ != 1] = -1
        heat_map[cases_result_[0] == cache_cases_result_] = 3
        cache_cases_result_ = np.copy(cases_result_[1])
        cache_cases_result_[cache_cases_result_ != 2] = -1
        cache_cases_result_[cache_cases_result_ > 0] = 1
        heat_map[cases_result_[0] == cache_cases_result_] = 4
        cache_cases_result_ = np.copy(cases_result_[0])
        cache_cases_result_[cache_cases_result_ != 2] = -1
        cache_cases_result_[cache_cases_result_ > 0] = 1
        heat_map[cache_cases_result_ == cases_result_[1]] = 4
        """
        self.current_kontur_array = heat_map
        self.display_analysed_kontur_in_advanced_raster_analysis()
           
        self.advanced_raster_analysis_result_map = np.copy(heat_map)

    
    def save_results_advanced_raster_analysis(self):
        if self.advanced_raster_analysis_result_map is None:
            self.print_on_console("No results to save!")
            return
        begin_advancedData = "\n$$$beginAdvancedData$$$"
        end_advancedData = "$$$endAdvancedData$$$\n"
        filename = filedialog.askopenfilename(initialdir=self.save_directory, title="Select logfile to overwrite")
        if not filename:
            self.print_on_console("No kontur has been saved!")
            return # user cancelled; stop this method
        if not(filename[(len(filename) - 11):] == "logfile.txt"):
            self.print_on_console("No 'logfile.txt' was selected.")
            return
        
        datei = open(filename,'r')
        text_ = datei.read()
        datei.close()
        
        if (text_.find(begin_advancedData) != -1) and (text_.find(end_advancedData) != -1):
            cache = text_[text_.find(end_advancedData)+len(end_advancedData):]
            text = text_[:text_.find(begin_advancedData)]
            text = text + begin_advancedData + str(self.advanced_raster_analysis_result_map) + end_advancedData
            text = text + cache
        else:
            text = text_ + begin_advancedData + str(self.advanced_raster_analysis_result_map) + end_advancedData
        
        with open(filename, 'w') as f:
            f.write(text)
            
        self.print_on_console("Result was saved in selected 'logfile.txt'.")
        
                
        
    def cancel_advanced_raster_analysis(self):
        if not(self.advanced_raster_analysis_is_displayed):
            self.print_on_console("Advanced raster analysis isn't in progress.")
            return
        self.kontur_display_var.set(0)
        self.update_kontur_map_style()
        self.advanced_raster_analysis_result_map = None
        for i in self.advanced_raster_analysis_rectangles_ids:
            self.canvas.delete(i)
        self.current_kontur_array = self.current_kontur_array_backup
        self.kontur_display_var.set(0)
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        self.canvas.unbind('<Button-3>')
        self.root.unbind('<KeyPress-Up>')
        self.root.unbind('<KeyPress-Down>')
        self.root.unbind('<KeyPress-Left>')
        self.root.unbind('<KeyPress-Right>')
        self.contrast_neighborhood_widgets.scale.config(state=tk.DISABLED)
        self.contrast_neighborhood_widgets.entry.config(state=tk.DISABLED)
        self.contrast_threshold_widgets.scale.config(state=tk.DISABLED)
        self.contrast_threshold_widgets.entry.config(state=tk.DISABLED)
        self.advanced_raster_analysis_button_frame.pack_forget()
        self.bg_button.pack()
        #self.contrast_subframe.pack()
        self.enable_disabled_buttons()
        self.advanced_raster_analysis_reset_variables()
        
    def advanced_raster_analysis_reset_variables(self):
        self.advanced_raster_analysis_is_displayed = False
        self.advanced_raster_analysis_add_rect_button = None
        self.advanced_raster_analysis_sub_rect_button = None
        self.advanced_raster_analysis_button_frame = None
        self.advanced_raster_analysis_cut_coords = None
        
        self.advanced_raster_analysis_rectangles_ids = []
        self.advanced_raster_analysis_rectangels_starting_coords = []
        self.advanced_raster_analysis_cut_coords_list = []
        self.advanced_raster_analysis_threshold_list = []
        self.advanced_raster_analysis_neighborhood_list = []
        
    def rectangle(self, event):
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            if event.state == 272 or event.state == 264:
                self.canvas.coords(self.advanced_raster_analysis_rectangles_ids[-1], (self.advanced_raster_analysis_rectangels_starting_coords[-1][0], self.advanced_raster_analysis_rectangels_starting_coords[-1][1], event.x, event.y))
            else:
                self.advanced_raster_analysis_rectangels_starting_coords[-1] = (event.x,event.y)
                #self.rect_start_coords = (event.x,event.y)
                self.canvas.coords(self.advanced_raster_analysis_rectangles_ids[-1], (self.advanced_raster_analysis_rectangels_starting_coords[-1][0], self.advanced_raster_analysis_rectangels_starting_coords[-1][1], self.advanced_raster_analysis_rectangels_starting_coords[-1][0]+10, self.advanced_raster_analysis_rectangels_starting_coords[-1][1]+10))

    def save_new_cut_borders(self, event):
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            w_0,h_0,w_1,h_1 = (self.advanced_raster_analysis_rectangels_starting_coords[-1][0], self.advanced_raster_analysis_rectangels_starting_coords[-1][1], event.x, event.y)
            if w_0 == w_1:
                w_1 = w_0 + 10
            if h_0 == h_1:
                h_1 = h_0 + 10
                        
            w0 = np.min([w_0, w_1])
            w1 = np.max([w_0, w_1])
            h0 = np.min([h_0, h_1])
            h1 = np.max([h_0, h_1])
            self.advanced_raster_analysis_cut_coords = (h0,h1,w0,w1)
            if len(self.advanced_raster_analysis_cut_coords_list) == len(self.advanced_raster_analysis_rectangles_ids):
                self.advanced_raster_analysis_cut_coords_list[-1] = self.advanced_raster_analysis_cut_coords
            else:
                self.advanced_raster_analysis_cut_coords_list.append(self.advanced_raster_analysis_cut_coords)
            self.update_maxima_from_cut_data()
            
    def config_rectangle(self, event):
        for index, i in enumerate(self.advanced_raster_analysis_cut_coords_list):
            if event.x in range(i[2],i[3]+1) and event.y in range(i[0],i[1]+1):
                print(index)
                print("drin")
                answer = tk.simpledialog.askstring("configure rectangle coord" , "Modify coordinates (y0, y1, x0, x1): ", parent=self.root, initialvalue=str(i))
                if answer is None:
                    return #user cancelled
                try:
                    answer = tuple(np.array(answer.replace("(", "").replace(")","").split(","), dtype=int))
                    if len(answer) != 4:
                        self.print_on_console("Wrong format for input! Please try again.")
                        return
                except ValueError:
                    self.print_on_console("Input can't be converted to int! Please try again.")
                    return
                self.advanced_raster_analysis_cut_coords_list[index] = answer
                self.advanced_raster_analysis_rectangels_starting_coords[index] = (answer[2], answer[0])
                self.canvas.coords(self.advanced_raster_analysis_rectangles_ids[index], (answer[2], answer[0], answer[3], answer[1]))
                self.update_maxima_from_cut_data()
                break
            else:
                print("nein")
                    
    def change_current_rectangle(self, event):
        if len(self.advanced_raster_analysis_rectangles_ids) > 1:
            print(self.advanced_raster_analysis_cut_coords_list)
            def put_element_at_index_to_end(list_, index):
                cache = []
                cache = cache + list_[:index]
                cache = cache + list_[index+1:]
                cache.append(list_[index])
                return cache.copy()
            
            for index, i in enumerate(self.advanced_raster_analysis_cut_coords_list):
                if event.x in range(i[2],i[3]+1) and event.y in range(i[0],i[1]+1):
                    print(index)
                    self.canvas.itemconfigure(self.advanced_raster_analysis_rectangles_ids[-1], outline='orange')
                    self.advanced_raster_analysis_rectangles_ids = put_element_at_index_to_end(self.advanced_raster_analysis_rectangles_ids, index)
                    self.advanced_raster_analysis_rectangels_starting_coords = put_element_at_index_to_end(self.advanced_raster_analysis_rectangels_starting_coords, index)
                    self.advanced_raster_analysis_cut_coords_list = put_element_at_index_to_end(self.advanced_raster_analysis_cut_coords_list, index)
                    self.advanced_raster_analysis_threshold_list = put_element_at_index_to_end(self.advanced_raster_analysis_threshold_list, index)
                    self.advanced_raster_analysis_neighborhood_list = put_element_at_index_to_end(self.advanced_raster_analysis_neighborhood_list, index)
                    self.advanced_raster_analysis_cut_coords = self.advanced_raster_analysis_cut_coords_list[-1]
                    self.canvas.itemconfigure(self.advanced_raster_analysis_rectangles_ids[-1], outline='blue')
                    self.current_threshold.set(int(self.advanced_raster_analysis_threshold_list[-1]))
                    self.slider_threshold_changed(None)
                    self.current_neighborhood.set(int(self.advanced_raster_analysis_neighborhood_list[-1]))
                    self.slider_neighborhood_changed(None)
                    self.update_maxima_from_cut_data()
                    
        
    def update_maxima_from_cut_data(self):
        (h0,h1,w0,w1) = self.advanced_raster_analysis_cut_coords_list[-1]
        offset = int(self.settings_advanced_raster_analysis_display_offset.get())
        if w0 in range(offset,975-offset) and h0 in range(offset,643-offset) :
            data = self.var_array[h0-offset:h1+offset+1,w0-offset:w1+offset+1]
            coord_data = self.displayed_img_raw[h0-offset:h1+offset+1,w0-offset:w1+offset+1]
            #norm_data = np.array(data, dtype=int)
            norm_data = np.float32(data)
            coords = self.calculate_maxima(coord_data)
            coords_ = self.DetectByMaximaAndCheckWithGaussian(coord_data)
    
            cimage = cv2.cvtColor(norm_data,cv2.COLOR_GRAY2BGR)
            cimage = np.array(cimage, dtype=int)
            cimage[offset-1,offset-1:-offset+1] = [0,0,255]
            cimage[-offset,offset-1:-offset+1] = [0,0,255]
            cimage[offset-1:-offset+1,offset-1] = [0,0,255]
            cimage[offset-1:-offset+1,-offset] = [0,0,255]
        else:
            data = self.var_array[h0:h1,w0:w1]
            norm_data = np.float32(data)
            coord_data = self.displayed_img_raw[h0:h1,w0:w1]
            coords = self.calculate_maxima(data)
    
            cimage = cv2.cvtColor(norm_data,cv2.COLOR_GRAY2BGR)
            cimage = np.array(cimage, dtype=int)
            
        for i in range(len(coords[0])):
            h,w = (int(coords[1][i]),int(coords[0][i]))
            cimage[h,w] = [255,0,0]
        for i in range(len(coords_[0])):
            h,w = (int(coords_[1][i]),int(coords_[0][i]))
            cimage[h,w] = [0,255,0]
        
        self.plot_array_on_CanvasTkAgg_cur_det_max(cimage)
        
        
        
    def calculate_maxima(self, data, threshold=None, neighborhood=None):
        if threshold is None:
            threshold = int(self.current_threshold.get())
        if neighborhood is None:
            neighborhood = int(self.current_neighborhood.get())
        data_max = filters.maximum_filter(data, neighborhood)
        maxima = (data == data_max)
        data_min = filters.minimum_filter(data, neighborhood)
        diff = ((data_max - data_min) > threshold)
        maxima[diff == 0] = 0
        
        labeled, num_objects = ndimage.label(maxima)
        slices = ndimage.find_objects(labeled)
        x, y = [], []
        for dy,dx in slices:
            x_center = (dx.start + dx.stop - 1)/2
            x.append(x_center)
            y_center = (dy.start + dy.stop - 1)/2    
            y.append(y_center)
        return (x,y)
                   
    def display_analysed_kontur_in_advanced_raster_analysis(self):
        to_display = np.copy(self.current_kontur_array)
        to_display[self.current_kontur_position[0]][self.current_kontur_position[1]] = np.max(self.current_kontur_array)+1
        self.plot_array_on_CanvasTkAgg_kontur(to_display, from_advanced_raster_analysis="True")
        path = self.filelist[self.current_kontur_position[0]*self.current_kontur_shape[1]+self.current_kontur_position[1]]
        if self.open_raster_is_original:
            original_arr = cv2.imread(path, -1)
            self.change_displayed_img_raw(original_arr)
        else:
            raw_array = cv2.imread(path, cv2.IMREAD_GRAYSCALE )
            self.change_displayed_img_raw(raw_array[:643,:975])
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            self.update_maxima_from_cut_data()
    
    def DetectByMaximaAndCheckWithGaussian(self, data, threshold=None, neighborhood=None):
        x = np.linspace(0,data.shape[1]-1,data.shape[1])
        y = np.linspace(0,data.shape[0]-1,data.shape[0])
        data_X, data_Y = np.meshgrid(x, y)
        
        if threshold is None:
            threshold = int(self.current_threshold.get())
        if neighborhood is None:
            neighborhood = int(self.current_neighborhood.get())
        
        maxima = self.calculate_maxima(data, threshold, neighborhood)
        
        initial_guess_2 = []
        for i in range(len(maxima[0])):
            initial_guess_2.append(1)
            #initial_guess_2.append(maxima[0][i])
            #initial_guess_2.append(maxima[1][i])
            initial_guess_2.append(1)
            initial_guess_2.append(1)
        
        final_dots_0 = []
        final_dots_1 = []
        rms = 0
        max_sigma = int(self.settings_advanced_raster_analysis_max_sigma.get())
        size = int(self.settings_advanced_raster_analysis_size_gaus_check.get())//2
        
        
        def get_dataXY(x_start, x_stop, y_start, y_stop):
            x = np.linspace(x_start,x_stop,x_stop+1)
            y = np.linspace(y_start,y_stop,y_stop+1)
            data_X, data_Y = np.meshgrid(x, y)
            return data_X, data_Y
        
        def Gaus2D_noRavel(dat, amplitude, sigma_x, sigma_y):
            x,y,x0,y0 = dat
            gaus = amplitude * np.exp(-((x-x0)**2/(2*sigma_x**2) + (y-y0)**2/(2*sigma_y**2)))
            return gaus
        
        def _gaussian(M, *args):
            x,_,_,_ = M
            arr = np.zeros(x.shape)
            for i in range(len(args)//3):
               arr += Gaus2D_noRavel(M, *args[i*3:(i+1)*3])
            return arr
        for i in range(len(maxima[0])):
            try: 
                h,w = (int(maxima[1][i]),int(maxima[0][i]))
                h_0 = np.max([0,h-size])
                h_1 = np.min([data.shape[0]-1,h+size])
                w_0 = np.max([0,w-size])
                w_1 = np.min([data.shape[1]-1,w+size])
                data_X_,data_Y_ = get_dataXY(0,w_1-w_0,0,h_1-h_0)
                cache_data = data[h_0:h_1+1,w_0:w_1+1]
                x0 = w-w_0
                data_x0 = np.ones(data_X_.ravel().shape)*x0
                y0 = h-h_0
                data_y0 = np.ones(data_Y_.ravel().shape)*y0
                popt, pcov = opt.curve_fit(_gaussian, (data_X_.ravel(),data_Y_.ravel(),data_x0,data_y0), cache_data.ravel(), p0=initial_guess_2[i*3:(i+1)*3])
                data_x0 = np.ones(data_X_.shape)*x0
                data_y0 = np.ones(data_Y_.shape)*y0
                fit = _gaussian((data_X_, data_Y_,data_x0,data_y0), *popt)
                rms = rms + np.sqrt(np.mean((cache_data - fit)**2))
                
                if abs(popt[1]) < max_sigma or abs(popt[2]) < max_sigma:
                    final_dots_0.append(maxima[0][i])
                    final_dots_1.append(maxima[1][i])
                
            except RuntimeError:
                x0 = 5
                data_x0 = np.ones(data_X_.ravel().shape)*x0
                y0 = 5
                data_y0 = np.ones(data_Y_.ravel().shape)*y0
                popt = initial_guess_2[i*3:(i+1)*3]
                fit = _gaussian((data_X, data_Y,data_x0,data_y0), *popt)
                rms = rms + np.sqrt(np.mean((data - fit)**2))
        final_dots = (final_dots_0,final_dots_1)
        
        return final_dots
        
    def CheckAndClassifyDots(self, data):
        min_dist = int(self.settings_advanced_raster_analysis_min_distance.get())
        max_dist = int(self.settings_advanced_raster_analysis_max_distance.get())
        x = data[0]
        y = data[1]
        p = []
        result_distances = np.zeros((len(x), len(y)))
        for i in range(len(x)):
            p.append((x[i],y[i]))
            
        def distance(p1,p2):
            return np.sqrt((p1[0]-p2[0])**2+(p1[0]-p2[0])**2)
        
        for index1, p1 in enumerate(p):
            for index2, p2 in enumerate(p):
                if not(index1 == index2):
                    result_distances[index1,index2] = distance(p1,p2)
                    
        data_big_gap = np.copy(result_distances)
        
        result_distances[result_distances == 0] = min_dist + 1 
        result_distances[result_distances < min_dist] = -1
        result_distances[result_distances >= min_dist] = 0
        dot_num = len(x) - np.nansum(result_distances*(-1))//2
        
        data_big_gap[data_big_gap < max_dist] = 0
        data_big_gap[data_big_gap >= max_dist] = -1
        long_dist = np.nansum(data_big_gap*(-1))//2
        
        case = 0
        if dot_num == 1:
            #Fall 1: keine Verzwilligung
            case = 1
        elif dot_num > 1 and long_dist == 0:
            #Fall 2: kleine Verzwilligung
            case = 2
        elif dot_num == 2 and long_dist > 0:
            #Fall 3: große Verzwilligung
            case = 3
        elif dot_num > 2 and long_dist > 0:
            #Fall 4: kleine und große Verzwilligung 
            case = 4
            
        return dot_num, case
        
            
    def slider_neighborhood_changed(self, event):
        self.contrast_neighborhood_widgets.entry.delete(0,tk.END)
        self.contrast_neighborhood_widgets.entry.insert(0,str(int(self.current_neighborhood.get())))
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            self.update_maxima_from_cut_data()
            self.advanced_raster_analysis_neighborhood_list[-1] = int(self.current_neighborhood.get())
    
    def slider_threshold_changed(self, event):
        self.contrast_threshold_widgets.entry.delete(0,tk.END)
        self.contrast_threshold_widgets.entry.insert(0,str(int(self.current_threshold.get())))
        if len(self.advanced_raster_analysis_rectangles_ids) > 0:
            self.advanced_raster_analysis_threshold_list[-1] = int(self.current_threshold.get())
            self.update_maxima_from_cut_data()
    
    def calculate_max_exposure(self):
        if self.raster_in_progress:
            self.print_on_console("Another operation is still in progress, please wait until it's finished.")
            return
        self.raster_in_progress = True
        self.snap_button.config(state=tk.DISABLED)
        self.raster_button.config(state=tk.DISABLED)
        if not(stop_exposure_queue.empty()):
            stop_exposure_queue.get()
        calculate_max_exposure_thread = asf.AsyncSnapCalculateMaxExposure(stop_exposure_queue)   
        calculate_max_exposure_thread.start()
        self.monitor_calculate_max_exposure_thread(calculate_max_exposure_thread)
        
    def monitor_calculate_max_exposure_thread(self, thread):
        if thread.is_alive():
            self.snap_button.after(250, lambda: self.monitor_calculate_max_exposure_thread(thread))
        else:
            img = np.copy(thread.return_image)
            self.max_exposure = int(114000/(np.max(img) - 100))
            self.snap_button.config(state=tk.NORMAL)
            self.raster_button.config(state=tk.NORMAL)
            self.print_on_console(str(self.max_exposure))
            self.has_moved = False
            self.raster_in_progress = False
        
    def change_kontur_manually(self):
        if self.kontur_display_var.get() != 0:
            self.kontur_display_var.set(0)
            self.update_kontur_map_style()
        if self.raster_in_progress:
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        self.raster_in_progress = True
        if not(self.raster_analyse_is_happening):
            self.raster_analyse()
        self.disable_all_buttons()
        self.disable_all_entries()
        self.disable_all_radiobuttons()
        for i in range(0,4):
            self.root.bind(str(i), self.modify_kontur)
            self.root.bind("<KP_" + str(i) + ">", self.modify_kontur)
        self.change_kontur_manually_is_happening = True
        
    def modify_kontur(self, event):
        print(event)
        if (event.keysym == "KP_1") or(event.keysym == "KP_2") or (event.keysym == "KP_3"):
            number = int(event.keycode) - 86
        if (event.keysym == "1") or (event.keysym == "2") or (event.keysym == "3"):
            number = int(event.keycode) - 9
        if (event.keysym == "0") or (event.keysym == "KP_0"):
            number = 0
        self.current_kontur_array[self.current_kontur_position[0]][self.current_kontur_position[1]] = number
        self.display_analysed_kontur()
    
    def apply_manual_changed_kontur(self):
        if self.raster_in_progress and not(self.change_kontur_manually_is_happening):
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        if not(self.change_kontur_manually_is_happening):
            self.print_on_console("Kontur wasn't manually changed yet!")
            return
        for i in range(0,4):
            self.root.unbind(str(i))
            self.root.unbind("<KP_" + str(i) + ">")
        filename = filedialog.askopenfilename(initialdir=self.save_directory, title="Select logfile to overwrite")
        if not filename:
            self.print_on_console("No changed kontur has been saved!")
            return # user cancelled; stop this method
        if not(filename[(len(filename) - 11):] == "logfile.txt"):
            self.print_on_console("No 'logfile.txt' was selected.")
            return
        #TODO: fallunterscheidung falls centerdata oder advanced data vorhanden
        datei = open(filename,'r')
        text_ = datei.read()
        datei.close()
        
        begin_centerData = "\n$$$beginCenterData$$$"
        begin_advancedData = "\n$$$beginAdvancedData$$$"
        if (text_.find(begin_centerData) == -1) and (text_.find(begin_advancedData) == -1):
            text = text_.split('#',2)
            with open(filename, 'w') as f:
                f.write(text[0] + "#" + str(self.current_kontur_array))
        else:
            index = text_.find("\n$$$")
            text = text_[:index]
            text = text_.split('#',2)
            with open(filename, 'w') as f:
                f.write(text[0] + "#" + str(self.current_kontur_array) + text_[index:])
        self.enable_disabled_buttons()
        self.enable_disabled_entries()
        self.enable_disabled_radiobuttons()
        
        for i in range(0,4):
            self.root.unbind(str(i))
            self.root.unbind("<KP_" + str(i) + ">")
        self.change_kontur_manually_is_happening = False
        self.raster_in_progress = False
        self.raster_analyse()
        self.print_on_console("New kontur saved successfully!")
        
    def cancel_change_kontur_manually(self):
        if not(self.change_kontur_manually_is_happening):
            return
        self.enable_disabled_buttons()
        self.enable_disabled_entries()
        self.enable_disabled_radiobuttons()
        for i in range(0,4):
            self.root.unbind(str(i))
            self.root.unbind("<KP_" + str(i) + ">")
        self.current_kontur_array = np.copy(self.current_kontur_array_backup)
        self.display_analysed_kontur()
        self.raster_analyse()
        self.change_kontur_manually_is_happening = False
        self.raster_in_progress = False
        
    def tools_new_evaluation_of_kontur(self):
        open_directory = filedialog.askdirectory(initialdir=self.save_directory, title="Select Raster")
        if not open_directory:
            return
        result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
        filenames = []
        for i in sorted(result):
            filenames.append(str(open_directory) + "/" + str(i))
            
        datei = open(filenames[len(filenames)-1],'r')
        text = datei.read().split('#',2)
        datei.close()
        logfile = text[0].split(':')
        text_arr = text[1]      
        center_data = None
        if len(text) == 3:
            center_data = text[0]
        try:
            kontur_shape = (int(logfile[1]),int(logfile[3]))
        except:
            self.print_on_console("Error: Raster logfile is written in a wrong format.")
            return 
        
        arr = np.ones(kontur_shape[0]*kontur_shape[1], dtype=int)
        i = 0
        for val in text_arr:
            if val.isnumeric():
                arr[i] = val
                i = i + 1
        kontur = arr.reshape(kontur_shape)
        
        new_evaluation = abf.AsyncBgRemoveForNewEvaluation(filenames, text[0], kontur, self, center_data=center_data)
        new_evaluation.start()
        
        
        
        
    def auto_kontur_finding(self):
        if self.raster_in_progress:
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        self.raster_in_progress = True
        if self.auto_kontur_detection_is_displayed:
            self.AutoKonturDetectionWindow.lift()
            return
        self.auto_kontur_detection_is_displayed = True
        self.AutoKonturDetectionWindow = tk.Toplevel(self.root)
        self.AutoKonturDetectionWindow.protocol("WM_DELETE_WINDOW", self.on_closing_auto_kontur_finding)
        self.AutoKonturDetectionWindow.title("Auto kontur detection")
        
        auto_kontur_detection_subframe = tk.Frame(self.AutoKonturDetectionWindow)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(auto_kontur_detection_subframe, text_label='origin (x0,y0)', entry_var=self.auto_kontur_detection_origin_var)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(auto_kontur_detection_subframe, text_label='scale', entry_var=self.auto_kontur_detection_scale_var, replace_komma=True)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(auto_kontur_detection_subframe, text_label='mimimum dots', entry_var=self.auto_kontur_detection_minimum_dots)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(auto_kontur_detection_subframe, text_label='maximum dots', entry_var=self.auto_kontur_detection_maximum_dots)
        
        ##############################################################################
        
        fbp.FrameLabelEntry_pack(auto_kontur_detection_subframe, text_label='maximum mean', entry_var=self.auto_kontur_detection_maximal_mean, replace_komma=True)
        
        ##############################################################################
        
        fbp.FrameLabelCheckbutton_pack(auto_kontur_detection_subframe, text_label='acquire raster after kontur detection', checkbutton_var=self.auto_kontur_detection_raster_after).checkbutton.config(command=self.raster_after_kontur_check_entry_checkbox)
        self.auto_kontur_detection_raster_after.set(0)
        
        ##############################################################################
        
        auto_kontur_detection_is_continuous_subsubframe = tk.Frame(auto_kontur_detection_subframe)
        
        radio_0 = tk.Radiobutton(auto_kontur_detection_is_continuous_subsubframe, text='additive', variable=self.auto_kontur_detection_is_continuous, value=0, pady=3)
        radio_1 = tk.Radiobutton(auto_kontur_detection_is_continuous_subsubframe, text='continouse', variable=self.auto_kontur_detection_is_continuous, value=1, pady=3)
        radio_0.pack(side=tk.LEFT)
        radio_1.pack(side=tk.RIGHT)
        self.auto_kontur_detection_is_continuous.set(0)
        self.auto_kontur_detection_radio.clear()
        self.auto_kontur_detection_radio.append(radio_0)
        self.auto_kontur_detection_radio.append(radio_1)
        for i in self.auto_kontur_detection_radio:
            i.config(state=tk.DISABLED)
        
        auto_kontur_detection_is_continuous_subsubframe.pack(side=tk.TOP)
        
        self.auto_kontur_detection_exposure_time_raster_after_subframe = fbp.FrameLabelEntry_pack(auto_kontur_detection_subframe, text_label='exposure time of following raster  ', entry_var=self.auto_kontur_detection_exposure_time_raster_after)
        self.auto_kontur_detection_exposure_time_raster_after_subframe.entry.config(state=tk.DISABLED)
        self.auto_kontur_detection_exposure_time_raster_after.set("30")
        
        ##############################################################################
        
        auto_kontur_detection_subframe.pack(pady=5, fill='x')
        
        
        auto_kontur_detection_button_subframe = tk.Frame(self.AutoKonturDetectionWindow)
        
        auto_kontur_detection_apply_button = tk.Button(auto_kontur_detection_button_subframe, text='apply', height=1, command=self.apply_auto_kontur_detection)
        auto_kontur_detection_apply_button.pack(side = tk.LEFT)
        
        auto_kontur_detection_default_button = tk.Button(auto_kontur_detection_button_subframe, text='default', height=1, command=self.default_auto_kontur_detection)
        auto_kontur_detection_default_button.pack(side = tk.RIGHT)
        
        auto_kontur_detection_button_subframe.pack(pady=5)
        
    def raster_after_kontur_check_entry_checkbox(self):
        if (str(self.auto_kontur_detection_exposure_time_raster_after_subframe.entry['state']) == 'disabled'):
            self.auto_kontur_detection_exposure_time_raster_after_subframe.entry.config(state=tk.NORMAL)
            for i in self.auto_kontur_detection_radio:
                i.config(state=tk.NORMAL)
        else:
            self.auto_kontur_detection_exposure_time_raster_after_subframe.entry.config(state=tk.DISABLED)
            for i in self.auto_kontur_detection_radio:
                i.config(state=tk.DISABLED)
                
    def default_auto_kontur_detection(self):
        self.auto_kontur_detection_origin_var.set("0,0")
        self.auto_kontur_detection_scale_var.set("0.25")
        self.auto_kontur_detection_minimum_dots.set("1")
        self.auto_kontur_detection_maximum_dots.set("150")
        self.auto_kontur_detection_maximal_mean.set("185.0")
        self.auto_kontur_detection_raster_after.set(0)
        self.auto_kontur_detection_exposure_time_raster_after.set("30")
        self.auto_kontur_detection_exposure_time_raster_after_subframe.entry.config(state=tk.DISABLED)
        
    def apply_auto_kontur_detection(self):
        errors = 0
        try: 
            x0,y0 = tuple(map(float, self.auto_kontur_detection_origin_var.get().split(',')))
            if abs(x0) > 15 or abs(y0) > 15:
                self.print_on_console("Maximum range of the goniometer for x,y is +-15mm!")
                self.auto_kontur_detection_origin_var.set("0,0")
        except:
            self.print_on_console("Couldn't convert 'origin (x0, y0)' to float or is written in an illegal format. Must be u,v (u and v are float). Is set to default '0,0'.")
            self.auto_kontur_detection_origin_var.set("0,0")
            errors = errors + 1
        try:
            scale = round(float(self.auto_kontur_detection_scale_var.get()),3)
            if scale < 0:
                self.print_on_console("Value of 'scale' is negative!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'scale' to float!")
            self.auto_kontur_detection_scale_var.set("0.25")
            errors = errors + 1
        
        try:
            minimum_dots = int(self.auto_kontur_detection_minimum_dots.get())
            if(minimum_dots < 0):
                self.print_on_console("Value of 'minimum dots' is negative!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'minimum dots' to int!")
            self.auto_kontur_detection_minimum_dots.set("1")
            errors = errors + 1
            
        try:
            maximum_dots = int(self.auto_kontur_detection_maximum_dots.get())
            if(maximum_dots < 0):
                self.print_on_console("Value of 'maximum dots' is negative!")
                errors = errors + 1
            elif(maximum_dots < minimum_dots):
                self.print_on_console("Value of 'maximum dots' is greater than value of 'maximum dots'")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'maximum dots' to int!")
            self.auto_kontur_detection_minimum_dots.set("1")
            errors = errors + 1            
            
        try:
            maximum_mean = round(float(self.auto_kontur_detection_maximal_mean.get()),2)
            if(maximum_mean < 0):
                self.print_on_console("Value of 'maximum mean' is negative!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'maximum mean' to float!")
            self.auto_kontur_detection_maximal_mean.set("185.0")
            errors = errors + 1
        
        if self.auto_kontur_detection_raster_after.get():
            try:
                exposure_time = int(self.auto_kontur_detection_exposure_time_raster_after.get())
                if exposure_time < 0:
                    self.print_on_console("Value of 'exposure time' is negative. Is set to 1.")
                    self.auto_kontur_detection_exposure_time_raster_after.set("1")
                    errors = errors + 1
            except:
                self.print_on_console("Couldn't convert 'exposure time' to int!")
            
        if errors > 0:
            return
        
        self.disable_all_buttons()
        self.disable_all_entries()
        self.disable_all_radiobuttons()
        
        self.AutoKonturDetectionWindow.destroy()
        self.auto_kontur_detection_is_displayed = False
        
        find_kontur_thread = arf.AsyncKonturDetection((x0,y0), scale, minimum_dots, maximum_dots, maximum_mean, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, self)
        find_kontur_thread.start()
        self.queue_stop = False
        self.timertick_plot_array()
        self.timertick_plot_cur_det_max()
        self.monitor_find_kontur_thread(find_kontur_thread)
    
    def monitor_find_kontur_thread(self, thread):
        if thread.is_alive():
            self.snap_button.after(1000, lambda: self.monitor_find_kontur_thread(thread))
        else:
            self.queue_stop = True
            self.current_kontur_shape = (int(thread.solution[2]),int(thread.solution[3]))
            self.raster_h_w_var.set(str(self.current_kontur_shape[0]) + "," + str(self.current_kontur_shape[1]))
            self.current_kontur_offset = (thread.solution[0], thread.solution[1])
            self.raster_coord_var.set(str(self.current_kontur_offset[0]) + "," + str(self.current_kontur_offset[1]))
            self.current_kontur_scale = float(thread.stepsize)
            self.raster_scale_var.set(self.current_kontur_scale)
            self.enable_disabled_buttons()
            self.enable_disabled_entries()
            self.enable_disabled_radiobuttons()
            self.raster_in_progress = False
            if self.auto_kontur_detection_raster_after.get():
                self.raster_exposure_time_var.set(int(self.auto_kontur_detection_exposure_time_raster_after.get()))
                self.is_continuous.set(self.auto_kontur_detection_is_continuous.get())
                self.start_raster()
            
            
    def on_closing_auto_kontur_finding(self):
        self.AutoKonturDetectionWindow.destroy()
        self.auto_kontur_detection_is_displayed = False
        self.raster_in_progress = False    
        
        
    def multiple_raster(self):
        if self.raster_in_progress:
            self.print_on_console("A raster is still in progress, please wait until it's finished.")
            return
        if self.multiple_raster_dialog_is_displayed:
            self.MultipleRasterWindow.lift()
            return
        self.multiple_raster_dialog_is_displayed = True
        self.MultipleRasterWindow = tk.Toplevel(self.root)
        self.MultipleRasterWindow.protocol("WM_DELETE_WINDOW", self.multiple_raster_cancel)
        self.MultipleRasterWindow.title("Multiple raster")

        for i in self.multiple_raster_list:
            #i.LabelFrame.pack(pady=5, fill='x')  
            i.LabelFrame.pack(pady=5)
        
        self.multiple_raster_button_subframe = tk.Frame(self.MultipleRasterWindow)
        
        self.multiple_raster_new_raster_button = tk.Button(self.multiple_raster_button_subframe, text='new raster', height=1, command=self.multiple_raster_add_new_raster)
        self.multiple_raster_new_raster_button.pack(side = tk.LEFT)
        
        self.multiple_raster_delete_raster_button = tk.Button(self.multiple_raster_button_subframe, text='delete raster', height=1, command=self.multiple_raster_delete_raster)
        
        self.multiple_raster_apply_button = tk.Button(self.multiple_raster_button_subframe, text='apply', height=1, command=self.multiple_raster_apply)

        self.multiple_raster_cancel_button = tk.Button(self.multiple_raster_button_subframe, text='cancel', height=1, command=self.multiple_raster_cancel)
        self.multiple_raster_cancel_button.pack(side = tk.LEFT)
        
        self.multiple_raster_button_subframe.pack(pady=5)

        """
        multiple_raster_subframe = fbp.RasterFrame(self.MultipleRasterWindow, self.multiple_raster_h_w_var, self.multiple_raster_scale_var, 
                                                   self.multiple_raster_coord_var, self.multiple_raster_exposure_var)
        """
        
    def save_tbfliped_pattern(self):
        filename = filedialog.asksaveasfilename(initialfile = self.initialfile_name + "_tb_flipped.bmp", defaultextension='.bmp', initialdir=self.save_directory, title="Save as BMP File (default) or other filetype (add .xxx)", filetypes=[("BMP Files","*.bmp")])
        if not filename:
            return # user cancelled; stop this method
        cv2.imwrite(filename, np.flipud(self.var_array))
        
    def save_lrfliped_pattern(self):
        filename = filedialog.asksaveasfilename(initialfile = self.initialfile_name + "_lr_flipped.bmp", defaultextension='.bmp', initialdir=self.save_directory, title="Save as BMP File (default) or other filetype (add .xxx)", filetypes=[("BMP Files","*.bmp")])
        if not filename:
            return # user cancelled; stop this method
        cv2.imwrite(filename, np.fliplr(self.var_array))
    
        
    def check_laue_camera(self):
        answ = bsf.laueClient("192.168.1.10", 50000, "GetCam\n")
        if str(answ) == "b'NTXLaue'":
            self.print_on_console("'NTXLaue' is open.")
        else:
            self.print_on_console("'NTXLaue' is closed.")
    
    def close_laue_camera(self):
        answ = bsf.laueClient("192.168.1.10", 50000, "GetCam\n")
        if str(answ) == "b'NTXLaue'":
            answ = bsf.laueClient("192.168.1.10", 50000, "Close\n")
            if str(answ) == "b'True'":
                self.print_on_console("'NTXLaue' closed successfully!")
            else:
                self.print_on_console("An error occured while closing 'NTXLaue'! Please check on the other computer.")
        else:
            self.print_on_console("'NTXLaue' is already closed.")
    
    def restart_laue_camera(self):
        answ = bsf.laueClient("192.168.1.10", 50000, "GetCam\n")
        if not(str(answ) == "b'NTXLaue'"):
            answ = bsf.laueClient("192.168.1.10", 50000, "Open;NTXLaue\n")
            if str(answ) == "b'True'":
                self.print_on_console("'NTXLaue' started successfully!")
        else:
            answ = bsf.laueClient("192.168.1.10", 50000, "Close\n")
            print(str(answ))
            if str(answ) == "b'True'":
                self.print_on_console("'NTXLaue' closed successfully!")
            else:
                self.print_on_console("An error occured while closing 'NTXLaue'! Please check on the other computer.")
                return
            answ = bsf.laueClient("192.168.1.10", 50000, "Open;NTXLaue\n")
            print(str(answ))
            if str(answ) == "b'True'":
                self.print_on_console("'NTXLaue' restarted successfully!")
            else:
                self.print_on_console("An error occured while open 'NTXLaue'! Please check on the other computer.")
                return
        if str(answ) == "b'camera failed to start'":
            self.print_on_console("Camera failed to start. Both cameras have to be on.")
            
    def check_PSLViewer (self):
        if (self.check_connection()):
            self.print_on_console("PSLViewer and 'Server control' are online!")
            
    def restart_PSLViewer(self):

        if not(self.check_connection()):
            self.print_on_console("PSLViewer and 'Server control' have to be online.")
            return
        bsf.laueClient_to_restart("192.168.1.10", 50000, "ShellCMD;start restart_PSLViewer.bat\n")
        time.sleep(3)
        if not(self.check_connection()):
            self.print_on_console("Something went wrong during the restart. Please check the program manually.")
            return
        else:
            self.print_on_console("PSLViewer restarted successfully!")
    
    def multiple_raster_add_new_raster(self):
        number = len(self.multiple_raster_list) + 1
        self.multiple_raster_list.append(fbp.RasterFrame(self.MultipleRasterWindow, number))
        for i in self.multiple_raster_list:
            #i.LabelFrame.pack(pady=5, fill='x')  
            i.LabelFrame.pack(pady=5)
            
        self.multiple_raster_button_forget_pack()
        self.multiple_raster_new_raster_button.pack(side = tk.LEFT)
        self.multiple_raster_delete_raster_button.pack(side = tk.LEFT)
        self.multiple_raster_apply_button.pack(side = tk.LEFT)
        self.multiple_raster_cancel_button.pack(side = tk.LEFT)

    
    def multiple_raster_delete_raster(self):
        self.multiple_raster_list[-1].LabelFrame.destroy()
        self.multiple_raster_list = self.multiple_raster_list[:-1]
        for i in self.multiple_raster_list:
            #i.LabelFrame.pack(pady=5, fill='x')  
            i.LabelFrame.pack(pady=5)
    
        self.multiple_raster_button_forget_pack()
        
        if len(self.multiple_raster_list) == 0:
            self.multiple_raster_new_raster_button.pack(side = tk.LEFT)
            self.multiple_raster_cancel_button.pack(side = tk.RIGHT)
        else:
            self.multiple_raster_new_raster_button.pack(side = tk.LEFT)
            self.multiple_raster_delete_raster_button.pack(side = tk.LEFT)
            self.multiple_raster_apply_button.pack(side = tk.LEFT)
            self.multiple_raster_cancel_button.pack(side = tk.LEFT)

    def multiple_raster_button_forget_pack(self):
        self.multiple_raster_button_subframe.pack_forget()
        self.multiple_raster_new_raster_button.pack_forget()
        self.multiple_raster_delete_raster_button.pack_forget()
        self.multiple_raster_apply_button.pack_forget()
        self.multiple_raster_cancel_button.pack_forget()    
        self.multiple_raster_button_subframe.pack(pady=5)
    
    def multiple_raster_apply(self):
        if not(self.check_multiple_raster_entries()):
            return
        
        for i in self.multiple_raster_list:
            i.radio_0.config(state=tk.DISABLED)
            i.radio_1.config(state=tk.DISABLED)
        self.multiple_raster_new_raster_button.config(state=tk.DISABLED)
        self.multiple_raster_delete_raster_button.config(state=tk.DISABLED)
        self.multiple_raster_cancel_button.config(state=tk.DISABLED)
        self.multiple_raster_apply_button.config(state=tk.DISABLED)
        self.MultipleRasterWindow.protocol("WM_DELETE_WINDOW", self.on_closing_multiple_raster)
        
        self.queue_stop = True
        self.monitor_multiple_raster(0)
        
            
    def check_multiple_raster_entries(self):
        errors = 0
        for i in self.multiple_raster_list:
            try:
                h,w = tuple(map(int, i.h_w_var.get().split(',')))
                i.h_w_widgets.entry.config(state=tk.DISABLED)
            except:
                errors = errors + 1
                self.print_on_console("Couldn't convert '(height, width)' to int or is written in an illegal format. Must be i,j (i and j are integers)")
            
            try: 
                x0,y0 = tuple(map(float, i.coord_var.get().split(',')))
                i.coord_widgets.entry.config(state=tk.DISABLED)
            except:
                errors = errors + 1
                self.print_on_console("Couldn't convert '(x0, y0)' to float or is written in an illegal format. Must be u,v (u and v are float)")
                
            try:
                i.scale_var.get()
                i.scale_widgets.entry.config(state=tk.DISABLED)
            except:
                errors = errors + 1
                self.print_on_console("Couldn' convert 'scale' to float.")
                
            try: 
                i.exposure_var.get()
                i.exposure_widgets.entry.config(state=tk.DISABLED)
            except:
                errors = errors + 1
                self.print_on_console("Couldn't convert 'exp. time' to int.")
                
        if errors > 0:
            return False
        else:
            return True
            
                        
    def monitor_multiple_raster(self, n):
        if self.queue_stop:
            if n == len(self.multiple_raster_list):
                self.multiple_raster_cancel()
                return
            if n > 0:
                self.multiple_raster_list[n - 1].LabelFrame.config(text='raster ' + str(n) + ' done!')
            self.multiple_raster_list[n].LabelFrame.config(text='raster ' + str(n+1) + ' ... is recording')
            self.is_continuous.set(self.multiple_raster_list[n].radio_var.get())
            self.raster_h_w_var.set(self.multiple_raster_list[n].h_w_var.get())
            self.raster_coord_var.set(self.multiple_raster_list[n].coord_var.get())
            self.raster_scale_var.set(self.multiple_raster_list[n].scale_var.get())
            self.raster_exposure_time_var.set(self.multiple_raster_list[n].exposure_var.get())
            self.start_raster()
            self.monitor_multiple_raster(n+1)
        else:
            self.multiple_raster_new_raster_button.after(1000, lambda: self.monitor_multiple_raster(n))   
    
    def on_closing_multiple_raster(self):
        return
          
    def multiple_raster_cancel(self):
        self.MultipleRasterWindow.destroy()
        self.multiple_raster_dialog_is_displayed = False
        self.raster_in_progress = False
        self.multiple_raster_list = []
    
    def snap(self):
        if(not(self.check_connection())):
            return
        if not(stop_exposure_queue.empty()):
            stop_exposure_queue.get()
        if self.raster_in_progress:
            self.print_on_console("Another operation is still in progress, please wait until it's finished.")
            return
        self.cancel_snap_button.config(state=tk.NORMAL)
        self.snap_button.config(state=tk.DISABLED)
        self.exposure_widgets.entry.config(state=tk.DISABLED)
        self.raster_button.config(state=tk.DISABLED)
        self.raster_radio_0.config(state=tk.DISABLED)
        self.raster_radio_1.config(state=tk.DISABLED)
        self.raster_analyse_button.config(state=tk.DISABLED)
        self.disable_raster_entries()
        self.disable_move_frame()
        try:
            cur_exposure = self.exposure_var.get()
            self.exposure = cur_exposure
            if not(stop_exposure_count_queue.empty()):
                stop_exposure_count_queue.get()
            snap_thread = asf.AsyncSnap(cur_exposure, self, stop_exposure_queue)
            snap_thread.start()
            self.monitor_snap_thread(snap_thread)
        except:
            self.exposure_widgets.entry.delete(0,tk.END)
            self.exposure_widgets.entry.insert(0,str(120))
            self.print_on_console("Can't convert exposure-time to int. Set to default 120s")
            self.cancel_snap()
        
    def monitor_snap_thread(self, thread):
        if thread.is_alive():
            self.snap_button.after(250, lambda: self.monitor_snap_thread(thread))
        else:
            if self.bg_removed:
                self.bg_button_action()
            self.change_displayed_img_raw(thread.var_array)
            self.change_initialfile_name()
            
            self.cancel_snap()
            self.bg_button.config(state=tk.NORMAL)
            self.exposure_widgets.entry.config(state=tk.NORMAL)
            
    def snap_count(self, exposure_max, exposure, only30 = False):
        if exposure > 0:
            if not(stop_exposure_count_queue.empty()):
                stop_exposure_count_queue.get()
                self.exposure_widgets.entry.config(state=tk.NORMAL)
                self.exposure_var.set(exposure_max)
                return
            else:
                self.exposure_widgets.entry.config(state=tk.NORMAL)
                self.exposure_var.set(exposure-1)
                self.exposure_widgets.entry.config(state=tk.DISABLED)
                self.exposure_widgets.label.after(1016, lambda: self.snap_count(exposure_max, exposure - 1))
        else:
            if not(stop_exposure_count_queue.empty()):
                stop_exposure_count_queue.get()
            self.exposure_widgets.entry.config(state=tk.NORMAL)
            self.exposure_var.set(exposure_max)
            if only30:
                self.exposure_widgets.entry.config(state=tk.DISABLED)
        
    def cancel_snap(self):
        stop_exposure_queue.put("Stop")
        stop_exposure_count_queue.put("Stop")
        self.cancel_snap_button.config(state=tk.DISABLED)
        self.snap_button.config(state=tk.NORMAL)
        self.exposure_widgets.entry.config(state=tk.NORMAL)
        self.raster_button.config(state=tk.NORMAL)
        self.raster_radio_0.config(state=tk.NORMAL)
        self.raster_radio_1.config(state=tk.NORMAL)
        self.raster_analyse_button.config(state=tk.NORMAL)
        self.enable_raster_entries()
        self.enable_move_frame()
        
        
    def move(self):
        if self.raster_in_progress:
            self.print_on_console("Another operation is still in progress, please wait until it's finished.")
            return
        errors = 0
        try: 
            mx = self.move_x_var.get()
            if abs(mx) > 15:
                self.print_on_console("Maximum range of the goniometer for x is +-15mm!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'Move X' to float or is written in an illegal format. Is set to default '0.0'.")
            self.move_x_var.set(0.0)
            errors = errors + 1
        try: 
            rx = self.rotate_x_var.get()
        except:
            self.print_on_console("Couldn't convert 'Rotate X' to float or is written in an illegal format. Is set to default '0.0'.")
            self.rotate_x_var.set(0.0)
            errors = errors + 1
        if np.abs(rx) > 19:
            self.print_on_console("Error: rotation angle greater than 19° are not possible. Is set to default '0.0'.")
            self.rotate_x_var.set(0.0)
            errors = errors + 1
        try: 
            my = self.move_y_var.get()
            if abs(my) > 15:
                self.print_on_console("Maximum range of the goniometer for y is +-15mm!")
                errors = errors + 1
        except:
            self.print_on_console("Couldn't convert 'Move Y' to float or is written in an illegal format. Is set to default '0.0'.")
            self.move_y_var.set(0.0)
            errors = errors + 1
        try: 
            ry = self.rotate_y_var.get()
        except:
            self.print_on_console("Couldn't convert 'Rotate Y' to float or is written in an illegal format. Is set to default '0.0'.")
            self.rotate_y_var.set(0.0)
            errors = errors + 1
        if np.abs(ry) > 19:
            self.print_on_console("Error: rotation angle greater than 19° are not possible. Is set to default '0.0'.")
            self.rotate_y_var.set(0.0)
            errors = errors + 1
        
        if errors > 0:
            return
        
        bsf.motorClient('M','X', mx)
        bsf.motorClient('M','Y', my)
        bsf.motorClient('R','X', rx)
        bsf.motorClient('R','Y', ry)
        self.has_moved = True

        
        
    def home(self):
        bsf.home()
        self.move_x_var.set(0.0)
        self.move_y_var.set(0.0)
        self.rotate_x_var.set(0.0)
        self.rotate_y_var.set(0.0)
        self.has_moved = True
        
    def disable_move_frame(self):
        self.move_button.config(state=tk.DISABLED)
        self.home_button.config(state=tk.DISABLED)
        self.move_x_widgets.entry.config(state=tk.DISABLED)
        self.rotate_x_widgets.entry.config(state=tk.DISABLED)
        self.move_y_widgets.entry.config(state=tk.DISABLED)
        self.rotate_y_widgets.entry.config(state=tk.DISABLED)        
    
    def enable_move_frame(self):
        self.move_button.config(state=tk.NORMAL)
        self.home_button.config(state=tk.NORMAL)
        self.move_x_widgets.entry.config(state=tk.NORMAL)
        self.rotate_x_widgets.entry.config(state=tk.NORMAL)
        self.move_y_widgets.entry.config(state=tk.NORMAL)
        self.rotate_y_widgets.entry.config(state=tk.NORMAL)

    def init_move_entries(self):
        mx,my,rx,ry = bsf.motorClient('Q','X',0, ret=True)
        self.move_x_var.set(round(float(mx),3))
        self.move_y_var.set(round(float(my),3))
        self.rotate_x_var.set(round(float(rx),3))
        self.rotate_y_var.set(round(float(ry),3))

    def canvas_klick(self, event):
        (x, y) = (event.x, event.y)
        self.canvas.coords(self.id_circel, (x-5, y-5, x+5, y+5))
        for i in self.line_id_list:
            (x1,y1,x2,y2) = tuple(self.canvas.coords(i))
            self.canvas.coords(i, (x, y, x + (x2-x1), y + (y2-y1)))
    
    def canvas_circel_move_up(self, event):
        (x0, y0, x1, y1) = tuple(self.canvas.coords(self.id_circel))
        if y0 > self.move_circel_step_size:
            self.canvas.coords(self.id_circel, (x0, y0-self.move_circel_step_size, x1, y1-self.move_circel_step_size))
            for i in self.line_id_list:
                (x2, y2, x3, y3) = tuple(self.canvas.coords(i))
                self.canvas.coords(i, (x2, y2-self.move_circel_step_size, x3, y3-self.move_circel_step_size))
        
    def canvas_circel_move_down(self, event):
        (x0, y0, x1, y1) = tuple(self.canvas.coords(self.id_circel))
        if y1 < self.canvas_height - self.move_circel_step_size:
            self.canvas.coords(self.id_circel, (x0, y0+self.move_circel_step_size, x1, y1+self.move_circel_step_size))
            for i in self.line_id_list:
                (x2, y2, x3, y3) = tuple(self.canvas.coords(i))
                self.canvas.coords(i, (x2, y2+self.move_circel_step_size, x3, y3+self.move_circel_step_size))

  
    def canvas_circel_move_right(self, event):
        (x0, y0, x1, y1) = tuple(self.canvas.coords(self.id_circel))
        if x1 < self.canvas_width - self.move_circel_step_size:
            self.canvas.coords(self.id_circel, (x0+self.move_circel_step_size, y0, x1+self.move_circel_step_size, y1))
            for i in self.line_id_list:
                (x2, y2, x3, y3) = tuple(self.canvas.coords(i))
                self.canvas.coords(i, (x2+self.move_circel_step_size, y2, x3+self.move_circel_step_size, y3))
        
    def canvas_circel_move_left(self, event):
        (x0, y0, x1, y1) = tuple(self.canvas.coords(self.id_circel))
        if x0 > self.move_circel_step_size:
            self.canvas.coords(self.id_circel, (x0-self.move_circel_step_size, y0, x1-self.move_circel_step_size, y1))
            for i in self.line_id_list:
                (x2, y2, x3, y3) = tuple(self.canvas.coords(i))
                self.canvas.coords(i, (x2-self.move_circel_step_size, y2, x3-self.move_circel_step_size, y3))

        
    def show_symmetry_help_click(self):
        if not(self.symmetry_help_is_displayed):
            # generate circel
            delta = 5
            xm = self.symmetry_center_x
            ym = self.symmetry_center_y
            self.id_circel = self.canvas.create_oval(xm-delta, ym-delta, xm+delta, ym+delta, fill='red')
            # enable centralise
            self.centralise_button.config(state=tk.NORMAL)
            # enable symmetry_step_size_widgets.scale
            self.symmetry_step_size_widgets.scale.config(state=tk.NORMAL)
            
            self.symmetry_step_size_widgets.entry.config(state=tk.NORMAL)
            
            # enable radiobuttuns
            self.enable_radiobuttons()
            self.symmetry_radio_0.select()
            # bind all functions
            self.canvas.bind('<Button-1>', self.canvas_klick)
            self.root.bind('<KeyPress-Up>', self.canvas_circel_move_up)
            self.root.bind('<KeyPress-Down>', self.canvas_circel_move_down)
            self.root.bind('<KeyPress-Right>', self.canvas_circel_move_right)
            self.root.bind('<KeyPress-Left>', self.canvas_circel_move_left)
            self.canvas.bind('<MouseWheel>', self.rotate_mousewheel)
            self.canvas.bind('<Button-4>', self.rotate_mousewheel)
            self.canvas.bind('<Button-5>', self.rotate_mousewheel)
            
            # set symmetry_help_is_displayed to True
            self.symmetry_help_is_displayed = True
            # refresh the displayed text on the Button
            self.show_symmetry_help.config(text="hide symmetry help")
            #ensure that analyse raster and check symmetry can not be executed at the same time
            self.raster_analyse_button.config(state=tk.DISABLED)
            
        else:
            # delete circel and lines
            self.canvas.delete(self.id_circel)
            self.delete_lines()
            # disabel centralise
            self.centralise_button.config(state=tk.DISABLED)
            # disable symmetry_step_size_widgets.scale
            self.symmetry_step_size_widgets.scale.config(state=tk.DISABLED)
            
            self.symmetry_step_size_widgets.entry.config(state=tk.DISABLED)
            # disable radiobuttons
            self.disable_radiobuttons()
            # unbind all functions
            self.canvas.unbind('<Button-1>')
            self.root.unbind('<KeyPress-Up>')
            self.root.unbind('<KeyPress-Down>')
            self.root.unbind('<KeyPress-Right>')
            self.root.unbind('<KeyPress-Left>')
            self.canvas.unbind('<MouseWheel>')
            self.canvas.unbind('<Button-4>')
            self.canvas.unbind('<Button-5>')
            # set symmetry_help_is_displayed to False
            self.symmetry_help_is_displayed = False
            # refresh the displayed text on the Button
            self.show_symmetry_help.config(text="show symmetry help")
            #enable analyse raster
            self.raster_analyse_button.config(state=tk.NORMAL)

    def disable_radiobuttons(self):
        self.symmetry_radio_0.config(state=tk.DISABLED)
        self.symmetry_radio_2.config(state=tk.DISABLED)
        self.symmetry_radio_3.config(state=tk.DISABLED)
        self.symmetry_radio_4.config(state=tk.DISABLED)
        self.symmetry_radio_6.config(state=tk.DISABLED)
    
    def enable_radiobuttons(self):
        self.symmetry_radio_0.config(state=tk.NORMAL)
        self.symmetry_radio_2.config(state=tk.NORMAL)
        self.symmetry_radio_3.config(state=tk.NORMAL)
        self.symmetry_radio_4.config(state=tk.NORMAL)
        self.symmetry_radio_6.config(state=tk.NORMAL)
    
    def slider_step_size_changed(self, event):
        self.move_circel_step_size = round(self.step_size_var.get()*2)/2
        #self.symmetry_step_size_widgets.entry.config(state=tk.NORMAL)
        self.symmetry_step_size_widgets.entry.delete(0,tk.END)
        self.symmetry_step_size_widgets.entry.insert(0,str(self.move_circel_step_size))
        #self.symmetry_step_size_widgets.entry.config(state=tk.DISABLED)
        
    def change_step_size_by_mousewheel(self, event):
        if(self.step_size_is_changeable):
            if event.delta > 0 or event.num == 4:
                self.symmetry_step_size_widgets.scale.set(self.symmetry_step_size_widgets.scale.get() + 0.5)
            if event.delta < 0  or event.num == 5:
                self.symmetry_step_size_widgets.scale.set(self.symmetry_step_size_widgets.scale.get() - 0.5)
                
    def change_step_size_by_mousewheel_in(self, event):
        self.step_size_is_changeable = True
        
    def change_step_size_by_mousewheel_out(self, event):
        self.step_size_is_changeable = False
        
    def rotate_around_point(self, x1, y1, x2, y2, phi):
        x3 = x2 - x1
        y3 = y2 - y1
        r = np.sqrt(x3**2 + y3**2)
        x4 = np.cos(phi * np.pi/180 + np.arctan2(y3,x3)) * r
        y4 = np.sin(phi * np.pi/180 + np.arctan2(y3,x3)) * r
        #return (int(x4 + x1), int(y4 + y1))
        return ((x4 + x1), (y4 + y1))
        
    def rotate_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            for i in self.line_id_list:
                (x1, y1, x2, y2) = tuple(self.canvas.coords(i))
                x3,y3 = self.rotate_around_point(x1, y1, x2, y2, self.step_size_var.get())
                self.canvas.coords(i, (x1,y1,x3,y3))
        if event.delta < 0  or event.num == 5:
            for i in self.line_id_list:
                (x1, y1, x2, y2) = tuple(self.canvas.coords(i))
                x3,y3 = self.rotate_around_point(x1, y1, x2, y2, -self.step_size_var.get())
                self.canvas.coords(i, (x1,y1,x3,y3))
        
            
    def change_symmetry(self):
        self.delete_lines()
        for i in range(self.symmetry.get()):
            (x0, y0, x1, y1) = tuple(self.canvas.coords(self.id_circel))
            xm = (x1+x0)/2
            ym = (y1+y0)/2
            if i==0:
                self.line_id_list.append(self.canvas.create_line(xm,ym,xm,-1000, fill='red'))
            else:
                x1,y1 = self.rotate_around_point(xm,ym,xm,-1000,(360/self.symmetry.get()) * i)
                self.line_id_list.append(self.canvas.create_line(xm,ym,x1,y1, fill='red'))
        #self.id_line_1 = self.canvas.create_line(490, 325, 490, -1000, fill='red')
    
    def delete_lines(self):
        for i in self.line_id_list:
            self.canvas.delete(i)
        self.line_id_list.clear()
        
    def centralise_picture(self):
        if self.raster_in_progress:
            self.print_on_console("Another operation is still in progress, please wait until it's finished.")
            return
        xm = self.symmetry_center_x
        ym = self.symmetry_center_y
        (x1,y1,x2,y2) = tuple(self.canvas.coords(self.id_circel))
        self.print_on_console("\u0394x = " + str(np.abs(xm-(x1+x2)/2)) + "\t \u0394y = " + str(np.abs(ym-(y1+y2)/2)))
        if((xm-(x1+x2)/2) == 0 and (ym-(y1+y2)/2) == 0):
            return
        mm_pro_pixel = 155/975
        distance = float(self.settings_distance_var.get())
        x = (x1+x2)/2 - xm
        y = (y1+y2)/2 - ym
        
        """
        argument_phi = -distance/(x*mm_pro_pixel)
        phi_rad = 0
        if argument_phi < 0:
            phi_rad = np.arctan(argument_phi) + np.pi
        else:
            phi_rad = np.arctan(argument_phi)
        argument_theta = -distance/(y*mm_pro_pixel*np.sin(phi_rad))
        if argument_theta < 0:
            theta_rad = np.arctan(argument_theta) + np.pi
        else:
            theta_rad = np.arctan(argument_theta)
        """
        phi_rad = np.pi/2
        if abs(x)>0:
            argument_phi = -distance/(x*mm_pro_pixel)
            if argument_phi < 0:
                phi_rad = np.arctan(argument_phi) + np.pi
            else:
                phi_rad = np.arctan(argument_phi)
        theta_rad = np.pi/2
        if abs(y)>0:
            argument_theta = -distance/(y*mm_pro_pixel*np.sin(phi_rad))
            if argument_theta < 0:
                theta_rad = np.arctan(argument_theta) + np.pi
            else:
                theta_rad = np.arctan(argument_theta)
        phi = (90-np.rad2deg(phi_rad))/2
        theta = (np.rad2deg(theta_rad)-90)/2
        mx,my,rx,ry = bsf.motorClient('Q','X',0, ret=True)
        rx = float(rx)
        ry = float(ry)
        if(np.abs(rx-phi) > 19):
            self.print_on_console("absolute rotational angle x is greater than 19°, is limited to adjustable range.")
            if((rx-phi) > 19):
                bsf.motorClient('R', 'X', 19)
                self.rotate_x_var.set(19.0)
            if((rx-phi) < -19):
                bsf.motorClient('R', 'X', -19)
                self.rotate_x_var.set(-19.0)
        else:
            bsf.motorClient('R', 'X', rx-phi)
            self.rotate_x_var.set(round(rx-phi,3))
        if(np.abs(ry-theta) > 19):
            self.print_on_console("absolute rotational angle y is greater than 19°, is limited to adjustable range.")
            if((ry-theta) > 19):
                bsf.motorClient('R', 'X', 19)
                self.rotate_y_var.set(19.0)
            if((ry-theta) < -19):
                bsf.motorClient('R', 'X', -19)
                self.rotate_y_var.set(-19.0)
        else:
            bsf.motorClient('R', 'Y', ry-theta)
            self.rotate_y_var.set(round(ry-theta,3))
        self.has_moved = True

    def slider_max_changed(self, event):
        self.contrast_max_widgets.entry.delete(0,tk.END)
        self.contrast_max_widgets.entry.insert(0,str(int(self.current_value_max.get())))
        self.update_image_contrast(False)
        if self.advanced_raster_analysis_is_displayed:
            self.slider_neighborhood_changed(None)
        
    def slider_min_changed(self, event):
        self.contrast_min_widgets.entry.delete(0,tk.END)
        self.contrast_min_widgets.entry.insert(0,str(int(self.current_value_min.get())))
        self.update_image_contrast(True)
        if self.advanced_raster_analysis_is_displayed:
            self.slider_neighborhood_changed(None)
        
    def slider_gamma_changed(self, event):
        self.contrast_gamma_widgets.entry.delete(0,tk.END)
        self.contrast_gamma_widgets.entry.insert(0,str(round(float(self.current_gamma.get()),2)))
        self.update_image_contrast()
        if self.advanced_raster_analysis_is_displayed:
            self.slider_neighborhood_changed(None)
        
    def disable_sliders_entries(self):
        self.contrast_max_widgets.entry.config(state=tk.DISABLED)
        self.contrast_min_widgets.entry.config(state=tk.DISABLED)
        self.contrast_gamma_widgets.entry.config(state=tk.DISABLED)
        self.contrast_max_widgets.scale.config(state=tk.DISABLED)
        self.contrast_min_widgets.scale.config(state=tk.DISABLED)
        self.contrast_gamma_widgets.scale.config(state=tk.DISABLED)

    
    def enable_sliders_entries(self):
        self.contrast_max_widgets.entry.config(state=tk.NORMAL)
        self.contrast_min_widgets.entry.config(state=tk.NORMAL)
        self.contrast_gamma_widgets.entry.config(state=tk.NORMAL)
        self.contrast_max_widgets.scale.config(state=tk.NORMAL)
        self.contrast_min_widgets.scale.config(state=tk.NORMAL) 
        self.contrast_gamma_widgets.scale.config(state=tk.NORMAL)
        

    def rescale_img(image, definedMin, definedMax):
        image = (255.0/(float(definedMax) - float(definedMin))) * np.subtract(image, definedMin)
        image[image < 0.0] = 0.0
        image[image > 255.0] = 255.0
        return image
    
    def update_image_contrast(self, from_min = True):
        max_value = int(self.current_value_max.get())
        min_value = int(self.current_value_min.get()) - 0.1
        gamma = float(self.current_gamma.get())
        faktor = 255.0**(1-gamma)
        if from_min and min_value > max_value:
            self.contrast_max_widgets.scale.set(min_value)
        if not(from_min) and max_value < min_value:
            self.contrast_min_widgets.scale.set(max_value)
        """
        diff_arr = np.copy(self.displayed_img_raw)
        
        if self.settings_subtract_darkcurrent_with_poly.get():
            bg_array = np.copy(self.displayed_img_raw)
            bg_array[bg_array > 255] = np.nan
            bg_array = (bg_array).astype('uint8')
            mblur = cv2.medianBlur(bg_array,3)
            x = np.arange(0,975)
            for j in range(mblur.shape[0]):
                y_all = self.CalculateBgWithPoly(x, mblur[j][:], 10)
                diff_arr[j][:] = diff_arr[j][:] - y_all
            self.var_array = (255.0/(float(max_value) - float(min_value))) * np.subtract(diff_arr, min_value)
        else:
            self.var_array = (255.0/(float(max_value) - float(min_value))) * np.subtract(self.displayed_img_raw, min_value) """
        
        self.var_array = (255.0/(float(max_value) - float(min_value))) * np.subtract(self.displayed_img_raw, min_value) 
        self.var_array[self.var_array < 0.0] = 0.0
        self.var_array[self.var_array > 255.0] = 255.0
        self.var_array = self.var_array**gamma * faktor

        """    
        if self.settings_subtract_darkcurrent_with_poly.get():
            bg_array = (self.var_array).astype('uint8')
            mblur = cv2.medianBlur(bg_array,3)
            x = np.arange(0,975)
            for j in range(mblur.shape[0]):
                y_all = self.CalculateBgWithPoly(x, mblur[j][:], 10)
                self.var_array[j][:] = self.var_array[j][:] - y_all           
        """    
        self.var_img = ImageTk.PhotoImage(image=Image.fromarray(self.var_array), master=self.canvas_frame)
        self.canvas.itemconfig(self.img_on_canvas, image = self.var_img)
            
    def bg_button_action(self):
        if not(self.bg_removed):
            self.bg_button.config(text="in progress...", state=tk.DISABLED)
            self.disable_sliders_entries()
            #self.axes.clear()
            
            max_value = int(self.current_value_max.get())
            min_value = int(self.current_value_min.get()) - 0.1
            gamma = float(self.current_gamma.get())
            faktor = 255.0**(1-gamma)
            
            arr = np.copy(self.displayed_img_raw)
            arr[arr < min_value] = min_value
            arr[arr > max_value] = max_value
            arr = arr**gamma * faktor
            
            bg_remove_thread = abf.AsyncBgRemove(arr, self.console, self)
            bg_remove_thread.start()
            
            self.monitor_bg_remove_thread(bg_remove_thread)
        else:
            self.change_displayed_img_raw(np.copy(self.displayed_img_raw_backup))
            self.bg_button.config(text="Remove Background", state=tk.NORMAL)
            self.bg_removed = False
            
            self.bg_button.pack_forget()
            self.bg_button.pack(side=tk.LEFT, fill='x')
            self.bg_button.config(width=33)
            self.bg_fine_tuning_button.pack_forget()
            self.bg_fine_tuning_button.config(state=tk.DISABLED)
            if not(str(type(self.FineTuningBgWindow)) == "<class 'NoneType'>"):
                self.on_closing_fine_tuning_window()

    def monitor_bg_remove_thread(self, thread):
        if thread.is_alive():
            self.bg_button.after(1000, lambda: self.monitor_bg_remove_thread(thread))
        else:
            if thread.no_exception: 
                self.displayed_img_raw_backup = np.copy(self.displayed_img_raw)
                diff_arr = np.copy(thread.image)
                self.displayed_img_raw_backup_for_file_tuning = np.copy(thread.image)
                
                if self.settings_subtract_darkcurrent_with_poly.get():
                    bg_array = self.DeleteGreaterValuesFromArray(thread.image, 0, auto=True)                    
                    bg_array = (bg_array).astype('uint16')
                    mblur = cv2.medianBlur(bg_array,3)
                    x = np.arange(0,975)
                    for j in range(mblur.shape[0]):
                        y_all = self.CalculateBgWithPoly(x, mblur[j][:], 10)
                        diff_arr[j][:] = diff_arr[j][:] - y_all
                    diff_arr[diff_arr < 0] = 0
                    self.change_displayed_img_raw(np.copy(diff_arr))
                    self.var_array = diff_arr
                    self.var_img = ImageTk.PhotoImage(image=Image.fromarray(diff_arr), master=self.canvas_frame)
                else:
                    self.change_displayed_img_raw(np.copy(thread.image))
                    self.var_array = thread.image
                    self.var_img = ImageTk.PhotoImage(image=Image.fromarray(thread.image), master=self.canvas_frame)
                
                
                self.canvas.itemconfig(self.img_on_canvas, image = self.var_img)
                self.print_on_console("Succusfull removal of the Background! Minimum: " + str(int(self.current_value_min.get()))
                                      + " \tMaximum: " + str(int(self.current_value_max.get())))
                self.bg_button.config(text="show original picture", state=tk.NORMAL)
                self.bg_removed = True
                self.enable_sliders_entries()
                
                self.bg_button.pack_forget()
                self.bg_button.pack(side=tk.LEFT, fill='x')
                self.bg_button.config(width=15)
                self.bg_fine_tuning_button.pack(side=tk.LEFT, fill='x')
                if not(self.settings_subtract_darkcurrent_with_poly.get()):
                    self.bg_fine_tuning_button.config(state=tk.DISABLED)
                else:
                    self.bg_fine_tuning_button.config(state=tk.NORMAL)
                
                self.axes_bg.clear()
                #self.plot.draw()
                #self.axes.autoscale()
                x = np.arange(975)
                label_ = self.settings_sample_var.get()
                self.axes_bg.scatter(x, thread.mod, label=label_, s=1, alpha=1)
        
                self.axes_bg.plot(x, thread.y_fit, label=label_ + ' fit (' + str(round(thread.r_squared,4)) + ')', linewidth="1", color = 'black')
                self.axes_bg.set(xlabel='Horizontale Position [Pixel]', ylabel='Wert [W.E.]')
                self.axes_bg.grid()
                self.axes_bg.set_xlim([0,975])
                self.fig_bg.tight_layout()

                self.plot_bg.draw()
                
                self.slider_max_changed("")
                
            else:
                self.print_on_console(str(thread.error) + " It is recommend to increase the adjusted range betweed Maximum and Minimum.")
                self.bg_button.config(text="Remove Background", state=tk.NORMAL)
                self.enable_sliders_entries()
                
    def DeleteGreaterValuesFromArray(self, array, num, auto=False):
        arr = np.copy(array)
        if auto:
            
            delta = self.settings_polyfit_auto_delta_value
            mean = np.zeros((1286,))
            for i in range(mean.shape[0]//2):
                mean[i] = np.mean(arr[i][delta:488-delta])
                mean[643+i] = np.mean(arr[i][488+delta:975-delta])
                
            increment = self.settings_polyfit_auto_increment_value        
            self.fine_tuning_max_scale_var.set(int(np.max(mean)+increment))
            
            arr[arr > int(np.max(mean)+increment)] = np.nan
        else:
            arr[arr > int(num)] = np.nan
        return np.copy(arr)
            
    def CalculateBgWithPoly(self, xData, yData, n):
        split = xData.shape[0]//2 + 1
    
        polynomial_coeff_left = np.polyfit(xData[:split], yData[:split], n)
        y_fit_left = np.poly1d(polynomial_coeff_left)
        
        polynomial_coeff_right = np.polyfit(xData[split:], yData[split:], n)
        y_fit_right = np.poly1d(polynomial_coeff_right)
        
        x1 = np.arange(np.min(xData), xData[split] + 1)
        x2 = np.arange(xData[split+1], np.max(xData) + 1)
        
        y_all = np.concatenate((y_fit_left(x1),y_fit_right(x2)))
        
        return y_all
    
    def bg_fine_tuning_action(self):
        if self.fine_tuning_bg_is_displayed:
            self.FineTuningBgWindow.lift()
            return
        self.fine_tuning_bg_is_displayed = True
        self.FineTuningBgWindow = tk.Toplevel(self.root)
        self.FineTuningBgWindow.protocol("WM_DELETE_WINDOW", self.on_closing_fine_tuning_window)
        self.FineTuningBgWindow.title("fine-tuning of poly-background subtraction")
        
        self.fine_tuning_canvas_frame = tk.Frame(self.FineTuningBgWindow, width=self.canvas_width, height=self.canvas_height, bg="white")
        
        self.fine_tuning_canvas = tk.Canvas(self.fine_tuning_canvas_frame, width=self.canvas_width, height=self.canvas_height)
        init_array = self.DeleteGreaterValuesFromArray(self.displayed_img_raw_backup_for_file_tuning, 0, auto=True)
        self.fine_tuning_init_img = ImageTk.PhotoImage(image=Image.fromarray(init_array), master=self.fine_tuning_canvas_frame)
        self.fine_tuning_img_on_canvas = self.fine_tuning_canvas.create_image((self.canvas_width / 2, self.canvas_height / 2), image=self.fine_tuning_init_img)
        self.fine_tuning_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.fine_tuning_canvas_frame.grid(row=0, column=0)

        widget_frame = tk.Frame(self.FineTuningBgWindow)
        
        widget_subframe = tk.Frame(widget_frame)
        
        self.fine_tuning_max_widgets = fbp.LabelScaleEntry_grid(widget_subframe, row_=0, text_label='Maximum pixel value ',
                                                                scale_from=0, scale_to=np.max(self.displayed_img_raw_backup_for_file_tuning), scale_command=self.update_fine_tuning_canvas,
                                                                scale_var=self.fine_tuning_max_scale_var, entry_var=self.fine_tuning_max_entry_var, entry_scale_scrollable=True)
        self.fine_tuning_max_widgets.scale.config(length=400)
        self.fine_tuning_max_widgets.entry.bind('<Return>', self.fine_tuning_max_widgets_return)
        self.fine_tuning_max_widgets.entry.bind('<KP_Enter>', self.fine_tuning_max_widgets_return)
        
        widget_subframe.pack(side='left', padx=15, pady=15)
        
        self.fine_tuning_apply_button = tk.Button(widget_frame, text='apply', width=8, height=1, command=self.apply_fine_tuning)
        self.fine_tuning_apply_button.pack(side='left')
        
        self.fine_tuning_default_button = tk.Button(widget_frame, text='default', width=8, height=1, command=self.default_fine_tuning)
        self.fine_tuning_default_button.pack(side='left')
        
        widget_frame.grid(row=1, column=0)
        
        self.update_fine_tuning_canvas(None)
        
    def update_fine_tuning_canvas(self, event):
        self.fine_tuning_max_entry_var.set(str(self.fine_tuning_max_scale_var.get()))
        max_ = int(self.fine_tuning_max_scale_var.get())
        image_arr = self.DeleteGreaterValuesFromArray(self.displayed_img_raw_backup_for_file_tuning, max_)
        self.fine_tuning_image_img = ImageTk.PhotoImage(image=Image.fromarray(image_arr), master=self.fine_tuning_canvas_frame)
        self.fine_tuning_canvas.itemconfig(self.fine_tuning_img_on_canvas, image = self.fine_tuning_image_img)
        
        """
        #image_arr = self.DeleteGreaterValuesFromArray(self.displayed_img_raw_backup_for_file_tuning, max_)
        #TODO:schauen ob vllt noch zum laufen gebracht werden kann
        arr = np.copy(self.displayed_img_raw_backup_for_file_tuning)
        arr[arr < int(max_)] = 0
        display_arr = np.copy(self.displayed_img_raw)        
        arr[arr >= int(max_)] = 1
        
        s = ndimage.generate_binary_structure(2,2)
        labeled_array, num_features = ndimage.label(arr, structure=s)
        num_list = ndimage.find_objects(labeled_array)
        
        max_list = []
        print(len(num_list))
        for i in range(len(num_list)):
            cache = np.copy(self.displayed_img_raw[num_list[i]])
            cache = cache.astype(float)
            cache[cache < 1] = np.nan
            max_list.append(np.nanmax(cache))
        print(np.mean(np.array(max_list)))
        mean = np.mean(np.array(max_list))
        
        plt.hist(np.array(max_list), bins='auto')
        plt.show()
        
        def gaussian_2d_remove_simple(x,y,o_x,o_y,s_x,s_y,alpha):
            return alpha * np.exp(-(x-o_x)**2/(s_x)**2) * np.exp(-(y-o_y)**2/(s_y)**2)
        
        def subtract_2d_simple_gaussian_from_array(array, mean):
            array = np.copy(array)
            max_ = np.max(array)
            alpha = max_ - mean
            index = np.where(array==max_)
            o_x = index[1][0]
            o_y = index[0][0]
            s_x = np.max([[1, np.min([[o_x,array.shape[1]-o_x-1]])]])
            s_y = np.max([[1, np.min([[o_y,array.shape[0]-o_y-1]])]])
            
            
            for y in range(array.shape[0]):
                for x in range(array.shape[1]):
                    gaus = gaussian_2d_remove_simple(x,y,o_x,o_y,s_x,s_y,alpha)
                    array[y,x] = array[y,x] - int(gaus)
                    
            return array
            
        for i in range(len(num_list)):
            cache = np.copy(self.displayed_img_raw[num_list[i]])
            cache = cache.astype(float)
            cache[cache < 1] = np.nan
            cur_max = np.nanmax(cache)
            if cur_max - mean > 0:
                new_arr = subtract_2d_simple_gaussian_from_array(display_arr[num_list[i]], mean)
                print(np.max(new_arr))
                display_arr[num_list[i]] = new_arr
                
        display_arr[display_arr < 0] = 0
        self.change_displayed_img_raw(display_arr)
        
        self.fine_tuning_image_img = ImageTk.PhotoImage(image=Image.fromarray(display_arr.astype('uint8')), master=self.fine_tuning_canvas_frame)
        self.fine_tuning_canvas.itemconfig(self.fine_tuning_img_on_canvas, image = self.fine_tuning_image_img)
        """
        
    def fine_tuning_max_widgets_return(self, event):
        try:
            max_ = int(self.fine_tuning_max_entry_var.get())
            self.fine_tuning_max_scale_var.set(max_)
            self.update_fine_tuning_canvas(None)
        except:
            self.print_on_console("Couldn't convert 'maximum pixel value' to int! Is set to default.")
            self.default_fine_tuning()
        
    def apply_fine_tuning(self):
        max_ = int(self.fine_tuning_max_entry_var.get())
        bg_array = self.DeleteGreaterValuesFromArray(self.displayed_img_raw_backup_for_file_tuning, max_)
        bg_array = (bg_array).astype('uint16')
        mblur = cv2.medianBlur(bg_array,3)
        x = np.arange(0,975)
        diff_arr = np.copy(self.displayed_img_raw_backup_for_file_tuning)
        for j in range(mblur.shape[0]):
            y_all = self.CalculateBgWithPoly(x, mblur[j][:], 10)
            diff_arr[j][:] = diff_arr[j][:] - y_all
        diff_arr[diff_arr < 0] = 0
        self.change_displayed_img_raw(np.copy(diff_arr))
        self.var_array = diff_arr
        self.var_img = ImageTk.PhotoImage(image=Image.fromarray(diff_arr), master=self.canvas_frame)
        self.update_image_contrast()
        self.on_closing_fine_tuning_window()
        
    def default_fine_tuning(self):
        self.DeleteGreaterValuesFromArray(self.displayed_img_raw_backup_for_file_tuning, 0, auto=True)
        self.update_fine_tuning_canvas(None)        
        
        """
        self.plot_fine_tuning = FigureCanvasTkAgg(self.fig_fine_tuning, master=self.FineTuningBgWindow)
        self.plot_fine_tuning.get_tk_widget().pack(side='left')
        
        maximum = np.max(self.displayed_img_raw)
        bin_arr = np.arange(maximum+1)
        maximum_arange = np.arange(maximum)
        self.histo,_ = np.histogram(self.displayed_img_raw, bins=bin_arr)
        
        #self.axes_fine_tuning.hist(self.displayed_img_raw, histtype='step')
        self.axes_fine_tuning.bar(maximum_arange, self.histo)#, linewidths=0.5)
        self.axes_fine_tuning.set_xlabel('Pixelvalue')
        self.axes_fine_tuning.set_ylabel('# Pixel')
        self.axes_fine_tuning.set_xlim([self.min_x_fine_tuning_scale_var.get(),self.max_x_fine_tuning_scale_var.get()])
        self.axes_fine_tuning.set_ylim([0,np.max(self.histo[self.min_x_fine_tuning_scale_var.get():self.max_x_fine_tuning_scale_var.get()+1])])
        
        self.max_vline = self.axes_fine_tuning.axvline(self.max_vline_scale_var.get(), color='k')
        
        scale_widgets_frame = tk.Frame(self.FineTuningBgWindow)
        
        fbp.LabelScaleEntry_grid(scale_widgets_frame, row_=0, text_label='Minimum Pixelvalue:',
                                                     scale_from=0, scale_to=np.max(self.displayed_img_raw), scale_command=self.slider_fine_tuning_min_changed,
                                                     scale_var=self.min_x_fine_tuning_scale_var, entry_var=self.min_x_fine_tuning_entry_var, entry_scale_scrollable=True)
        
        scale_widgets_frame.pack(side='left')
        
    def slider_fine_tuning_min_changed(self, event):
        self.min_x_fine_tuning_entry_var.set(str(int(self.min_x_fine_tuning_scale_var.get())))
        self.axes_fine_tuning.set_xlim([self.min_x_fine_tuning_scale_var.get(),self.max_x_fine_tuning_scale_var.get()])
        self.axes_fine_tuning.set_ylim([0,np.max(self.histo[self.min_x_fine_tuning_scale_var.get():self.max_x_fine_tuning_scale_var.get()+1])])
        self.plot_fine_tuning.draw()
        
    def fine_tuning_on_click(self, event):
        if event.button == 1:
            x = event.xdata
            if not(x==None):
                self.max_vline.set_xdata(int(x))
                print(x)
        
    """     
    def on_closing_fine_tuning_window(self):
        self.FineTuningBgWindow.destroy()
        self.fine_tuning_bg_is_displayed = False
        """
        self.axes_fine_tuning.clear()
        self.plot_fine_tuning.get_tk_widget().pack_forget()
        """
            
    def change_displayed_img_raw(self, change_array):
        # enable sliders, entries and bg_button
        self.enable_sliders_entries()
        
        self.displayed_img_raw = np.copy(change_array)
        #noch prüfen ob richige Größe
        self.var_img = None
        
        #self.var_img = None
        self.max_img_return = np.max(self.displayed_img_raw)
        self.min_img_return = np.min(self.displayed_img_raw)        
                
        # init sliders
        self.contrast_max_widgets.scale.config(from_=self.min_img_return, to=self.max_img_return)
        self.contrast_min_widgets.scale.config(from_=self.min_img_return, to=self.max_img_return)
        
        if self.contrast_max_widgets.scale.get() > self.max_img_return:
            self.contrast_max_widgets.scale.set(self.max_img_return)
        else:
            self.contrast_max_widgets.scale.set(self.contrast_max_widgets.scale.get())
        if self.contrast_min_widgets.scale.get() < self.min_img_return:
            self.contrast_min_widgets.scale.set(self.min_img_return)
        else:
            self.contrast_min_widgets.scale.set(self.contrast_min_widgets.scale.get())
        
    def start_raster(self):
        if(not(self.check_connection())):
            return
        self.raster_in_progress = True
        self.cancel_raster_button.config(state=tk.NORMAL)
        self.raster_button.config(state=tk.DISABLED)
        self.disable_raster_entries()
        self.raster_radio_0.config(state=tk.DISABLED)
        self.raster_radio_1.config(state=tk.DISABLED)
        self.snap_button.config(state=tk.DISABLED)
        self.exposure_widgets.entry.config(state=tk.DISABLED)
        self.bg_button.config(state=tk.DISABLED)
        self.raster_analyse_button.config(state=tk.DISABLED)
        self.disable_move_frame()
        self.queue_stop = False
        if not(stop_exposure_queue.empty()):
            stop_exposure_queue.get()
        self.timertick_plot_array()
        self.timertick_plot_cur_det_max()
        try:
            h,w = tuple(map(int, self.raster_h_w_var.get().split(',')))
        except:
            self.print_on_console("Couldn't convert '(height, width)' to int or is written in an illegal format. Must be i,j (i and j are integers). Is set to default '3,3'.")
            self.cancel_raster()
            self.raster_h_w_var.set("3,3")
            return
        try: 
            x0,y0 = tuple(map(float, self.raster_coord_var.get().split(',')))
        except:
            self.print_on_console("Couldn't convert '(x0, y0)' to float or is written in an illegal format. Must be u,v (u and v are float). Is set to default '0,0'.")
            self.raster_coord_var.set("0,0")
            self.cancel_raster()
            return
        try:
            scale = self.raster_scale_var.get()
        except:
            self.print_on_console("Couldn' convert 'scale' to float. Is set to default '0.5'")
            self.raster_scale_var.set(0.5)
            self.cancel_raster()
            return
        try: 
            exposure_time = self.raster_exposure_time_var.get()
        except:
            self.print_on_console("Couldn't convert 'exp. time' to int. Is set to default '14'")
            self.raster_exposure_time_var.set(14)
            self.cancel_raster()
            return
            
        percent = 30/exposure_time
        percent_threshold = float(self.settings_raster_on_kontur_threshold_percent.get())
        
        if self.is_continuous.get():
            if percent < percent_threshold and self.settings_raster_on_kontur.get():
                raster_thread = arf.AsyncKonturRaster(h,w,scale,exposure_time,-y0,x0,self, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, center_detection_queue, is_continuous=True)
            else:
                raster_thread = arf.AsyncRaster(h,w,scale,exposure_time,-y0,x0,self, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, center_detection_queue, is_continuous=True)
            raster_thread.start()
            self.monitor_raster_thread(raster_thread)
        elif not(self.is_continuous.get()):
            if percent < percent_threshold and self.settings_raster_on_kontur.get():
                raster_thread = arf.AsyncKonturRaster(h,w,scale,exposure_time,-y0,x0,self, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, center_detection_queue)
            else:
                raster_thread = arf.AsyncRaster(h,w,scale,exposure_time,-y0,x0,self, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, center_detection_queue)
            raster_thread.start()
            self.monitor_raster_thread(raster_thread)
        if int(self.settings_center_detection_during_raster.get()):
            width = int(self.settings_center_detection_search_width.get())
            height = int(self.settings_center_detection_search_height.get())
            offset_x = int(self.settings_center_detection_search_offset_x.get())
            offset_y = int(self.settings_center_detection_search_offset_x.get())
            linewidth = int(self.settings_center_detection_linewidth.get())
            starting_angle = int(self.settings_center_detection_starting_angle.get())
            num_lines = int(self.settings_center_detection_num_lines.get())
            save_info_images = int(self.settings_center_detection_save_info_images_raster.get())
            center_coord_P5 = np.zeros((2, h*w))
            rotated_degree = []
            #self.timertick_center_detection(width, height, offset_x, offset_y, linewidth, starting_angle, num_lines, center_coord_P5, rotated_degree, save_info_images)
            center_detect_thread = acd.AsyncCenterDetection(width, height, offset_x, offset_y, linewidth, starting_angle, num_lines, center_coord_P5, rotated_degree, save_info_images, center_detection_queue, self)
            center_detect_thread.start()
            
            
    def monitor_raster_thread(self,thread):
        if thread.is_alive():
            self.raster_button.after(250, lambda: self.monitor_raster_thread(thread))
        else:
            self.open_raster_is_original = False
            self.filelist.clear()
            self.filelist = thread.filelist
            self.cancel_raster()
            self.queue_stop = True
            self.raster_in_progress = False
            

    def cancel_raster(self):
        stop_exposure_queue.put("Stop")
        center_detection_queue.put("Stop")
        self.queue_stop = True
        self.raster_in_progress = False
        self.cancel_raster_button.config(state=tk.DISABLED)
        self.raster_button.config(state=tk.NORMAL)
        self.raster_radio_0.config(state=tk.NORMAL)
        self.raster_radio_1.config(state=tk.NORMAL)
        self.snap_button.config(state=tk.NORMAL)
        self.exposure_widgets.entry.config(state=tk.NORMAL)
        self.bg_button.config(state=tk.NORMAL)
        self.raster_analyse_button.config(state=tk.NORMAL)
        self.enable_raster_entries()
        self.enable_move_frame()

            
    def disable_raster_entries(self):
        self.raster_h_w_widgets.entry.config(state=tk.DISABLED)
        self.raster_exposure_time_widgets.entry.config(state=tk.DISABLED)
        self.raster_scale_widgets.entry.config(state=tk.DISABLED)
        self.raster_coord_widgets.entry.config(state=tk.DISABLED)
    
    def enable_raster_entries(self):
        self.raster_h_w_widgets.entry.config(state=tk.NORMAL)
        self.raster_exposure_time_widgets.entry.config(state=tk.NORMAL)
        self.raster_scale_widgets.entry.config(state=tk.NORMAL)
        self.raster_coord_widgets.entry.config(state=tk.NORMAL)
        
    def popmenu_for_raster_map(self, event):
        if self.change_kontur_manually_is_happening:
            return
        if self.advanced_raster_analysis_is_displayed:
            return
        self.menu_raster_maps.delete(2,self.menu_raster_maps.index(tk.END))
        if (self.raster_with_center_detection_data) and not(self.advanced_raster_analysis_result_map_to_display is None):
            self.popmenu_for_raster_map_add_center_det_maps()
            self.menu_raster_maps.add_separator()
            self.menu_raster_maps.add_radiobutton(label ="advanced analysis map", variable=self.kontur_display_var, value=4, command=self.update_kontur_map_style)
        elif (self.raster_with_center_detection_data):
            self.popmenu_for_raster_map_add_center_det_maps()
        elif not(self.advanced_raster_analysis_result_map_to_display is None):
            self.menu_raster_maps.add_radiobutton(label ="advanced analysis map", variable=self.kontur_display_var, value=4, command=self.update_kontur_map_style)
        try:
            if not(self.raster_with_center_detection_data) and (self.advanced_raster_analysis_result_map_to_display is None):
                return
            self.menu_raster_maps.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_raster_maps.grab_release()
    
    def popmenu_for_raster_map_add_center_det_maps(self):
        self.menu_raster_maps.add_radiobutton(label ="rotated angle map", variable=self.kontur_display_var, value=1, command=self.update_kontur_map_style)
        self.menu_raster_maps.add_radiobutton(label ="distance map", variable=self.kontur_display_var, value=2, command=self.update_kontur_map_style)
        self.menu_raster_maps.add_radiobutton(label ="combo map", variable=self.kontur_display_var, value=3, command=self.update_kontur_map_style)
        
            
    def update_kontur_map_style(self):
        var = self.kontur_display_var.get()
        if var == 0:
            self.current_kontur_array = np.copy(self.current_kontur_array_backup)
        elif var == 1:
            self.current_kontur_array = np.copy(self.center_detection_rotated_angle_data)
        elif var == 2:
            self.current_kontur_array = np.copy(self.center_detection_detailed_diff_map_right_size)
        elif var == 3:
            self.current_kontur_array = np.copy(self.center_detection_combo_map)
        elif var == 4:
            self.current_kontur_array = np.copy(self.advanced_raster_analysis_result_map_to_display)
        
        if self.raster_analyse_is_happening:
            self.display_analysed_kontur()
        else:
            self.plot_array_on_CanvasTkAgg_kontur(self.current_kontur_array)
        
    def plot_array_on_CanvasTkAgg_kontur(self, array, from_advanced_raster_analysis=None):
        self.axes_array.clear()
        #self.plot.draw()
        var = self.kontur_display_var.get()
        if var == 0 and from_advanced_raster_analysis is None:
            self.axes_array.matshow(array, cmap='jet', vmin=0, vmax=4)
        else:
            self.axes_array.matshow(array, cmap='jet', vmax=np.max(self.current_kontur_array) + 1)
        self.fig_array.tight_layout()
        self.plot_array.draw()
    
    def plot_array_on_CanvasTkAgg_cur_det_max(self, array):
        self.axes_cur_det_max_array.clear()
        #self.plot.draw()
        self.axes_cur_det_max_array.matshow(array, cmap='jet', vmin=0, vmax=3)
        self.fig_cur_det_max_array.tight_layout()
        self.plot_cur_det_max_array.draw()
    
    
    def change_max_by_mousewheel(self, event):
        if(self.max_is_changeable):
            if event.delta > 0 or event.num == 4:
                self.contrast_max_widgets.scale.set(self.contrast_max_widgets.scale.get() + 1)
            if event.delta < 0  or event.num == 5:
                self.contrast_max_widgets.scale.set(self.contrast_max_widgets.scale.get() - 1)
                
    def change_max_by_mousewheel_in(self, event):
        self.max_is_changeable = True
        
    def change_max_by_mousewheel_out(self, event):
        self.max_is_changeable = False
        
        
    def change_min_by_mousewheel(self, event):
        if(self.min_is_changeable):
            if event.delta > 0 or event.num == 4:
                self.contrast_min_widgets.scale.set(self.contrast_min_widgets.scale.get() + 1)
            if event.delta < 0  or event.num == 5:
                self.contrast_min_widgets.scale.set(self.contrast_min_widgets.scale.get() - 1)
                
    def change_min_by_mousewheel_in(self, event):
        self.min_is_changeable = True
        
    def change_min_by_mousewheel_out(self, event):
        self.min_is_changeable = False
        
        
    def change_gamma_by_mousewheel(self, event):
        if(self.gamma_is_changeable):
            if event.delta > 0 or event.num == 4:
                self.contrast_gamma_widgets.scale.set(self.contrast_gamma_widgets.scale.get() + 0.01)
            if event.delta < 0  or event.num == 5:
                self.contrast_gamma_widgets.scale.set(self.contrast_gamma_widgets.scale.get() - 0.01)
                
    def change_gamma_by_mousewheel_in(self, event):
        self.gamma_is_changeable = True
        
    def change_gamma_by_mousewheel_out(self, event):
        self.gamma_is_changeable = False
        
    
    
    def timertick_plot_array(self):
        treffer = np.ones((3,3))
        if not(request_kontur_queue.empty()):
            treffer = request_kontur_queue.get()
            self.plot_array_on_CanvasTkAgg_kontur(treffer)
        if not(self.queue_stop):
            self.raster_button.after(1000, self.timertick_plot_array)
    
    def timertick_plot_cur_det_max(self):
        current_image = np.ones((643,975,3))
        if not(request_cur_det_max_queue.empty()):
            current_image = request_cur_det_max_queue.get()
            self.plot_array_on_CanvasTkAgg_cur_det_max(current_image)
        if not(self.queue_stop):
            self.raster_button.after(1000, self.timertick_plot_cur_det_max)

    
        
    def raster_analyse(self):
        if not(self.raster_analyse_is_happening):
            #self.raster_analyse_button.config(state=tk.DISABLED)
            self.raster_analyse_move_to_button.config(state=tk.NORMAL)
            self.snap_button.config(state=tk.DISABLED)
            self.raster_button.config(state=tk.DISABLED)
            self.move_button.config(state=tk.DISABLED)
            self.home_button.config(state=tk.DISABLED)
            self.show_symmetry_help.config(state=tk.DISABLED)
            self.root.bind('<KeyPress-Up>', self.change_kontur_vertical)
            self.root.bind('<KeyPress-Down>', self.change_kontur_vertical)
            self.root.bind('<KeyPress-Left>', self.change_kontur_horizontal)
            self.root.bind('<KeyPress-Right>', self.change_kontur_horizontal)
            self.current_kontur_position = (0,0)
            if self.current_kontur_array is None:
                self.print_on_console("No Kontur messured")
                self.cancel_raster_analyse()
            else:
                self.display_analysed_kontur()
                self.raster_analyse_button.config(text="Cancel Analysis")
                self.raster_analyse_is_happening = True
        else:
            self.raster_analyse_button.config(text="Analyse Raster")
            self.cancel_raster_analyse()
            self.raster_analyse_is_happening = False
            
    def change_kontur_vertical(self, event):
        if event.keycode == 111 or event.keycode == 38:
            if (self.current_kontur_position[0] - 1 >= 0):
                self.current_kontur_position = (self.current_kontur_position[0] - 1,self.current_kontur_position[1])
                if self.advanced_raster_analysis_is_displayed:
                    self.display_analysed_kontur_in_advanced_raster_analysis()
                else:
                    self.display_analysed_kontur()
        elif event.keycode == 116 or event.keycode == 40:
            if (self.current_kontur_position[0] + 1 < self.current_kontur_shape[0]):
                self.current_kontur_position = (self.current_kontur_position[0] + 1,self.current_kontur_position[1])
                if self.advanced_raster_analysis_is_displayed:
                    self.display_analysed_kontur_in_advanced_raster_analysis()
                else:
                    self.display_analysed_kontur()
                
    def change_kontur_horizontal(self, event):
        if event.keycode == 113 or event.keycode == 37:
            if (self.current_kontur_position[1] - 1 >= 0):
                self.current_kontur_position = (self.current_kontur_position[0],self.current_kontur_position[1] - 1)
                if self.advanced_raster_analysis_is_displayed:
                    self.display_analysed_kontur_in_advanced_raster_analysis()
                else:
                    self.display_analysed_kontur()
        elif event.keycode == 114 or event.keycode == 39:
            if (self.current_kontur_position[1] + 1 < self.current_kontur_shape[1]):
                self.current_kontur_position = (self.current_kontur_position[0],self.current_kontur_position[1] + 1)
                if self.advanced_raster_analysis_is_displayed:
                    self.display_analysed_kontur_in_advanced_raster_analysis()
                else:
                    self.display_analysed_kontur()
            
        
    def cancel_raster_analyse(self):
        self.raster_analyse_move_to_button.config(state=tk.DISABLED)
        self.snap_button.config(state=tk.NORMAL)
        self.raster_button.config(state=tk.NORMAL)
        self.move_button.config(state=tk.NORMAL)
        self.show_symmetry_help.config(state=tk.NORMAL)
        self.root.unbind('<KeyPress-Up>')
        self.root.unbind('<KeyPress-Down>')
        self.root.unbind('<KeyPress-Left>')
        self.root.unbind('<KeyPress-Right>')
        if not(self.current_kontur_array is None):
            self.plot_array_on_CanvasTkAgg_kontur(self.current_kontur_array)
        
    def display_analysed_kontur(self):
        to_display = np.copy(self.current_kontur_array)
        var = self.kontur_display_var.get()
        if var == 0:
            to_display[self.current_kontur_position[0]][self.current_kontur_position[1]] = 4
        else:
            to_display[self.current_kontur_position[0]][self.current_kontur_position[1]] = np.max(self.current_kontur_array) + 1
        
        self.plot_array_on_CanvasTkAgg_kontur(to_display)
        path = self.filelist[self.current_kontur_position[0]*self.current_kontur_shape[1]+self.current_kontur_position[1]]
        if self.open_raster_is_original:
            original_arr = cv2.imread(path, -1)
            #TODO: wieder unteres abschneiden löschen
            self.change_displayed_img_raw(original_arr)
            original_arr = np.uint8(original_arr)
            _, _, dot_image = bsf.maxFinder_large(original_arr, None)
            self.plot_array_on_CanvasTkAgg_cur_det_max(dot_image)
            #self.plot_array_on_CanvasTkAgg_cur_det_max(np.zeros((self.canvas_height,self.canvas_width,3)))
        else:
            max_array = cv2.imread(path)
            self.plot_array_on_CanvasTkAgg_cur_det_max(max_array[643:,975:])
            raw_array = cv2.imread(path, cv2.IMREAD_GRAYSCALE )
            self.change_displayed_img_raw(raw_array[:643,:975])
        
    def raster_analyse_move_to_frame(self):
        x = round(self.current_kontur_offset[0] + self.current_kontur_scale*(self.current_kontur_position[0] - (self.current_kontur_shape[0] - 1)/2),3)
        y = round(self.current_kontur_offset[1] - self.current_kontur_scale*(self.current_kontur_position[1] - (self.current_kontur_shape[1] - 1)/2),3)
        bsf.motorClient('M','X',x)
        bsf.motorClient('M','Y',y)
        self.move_x_var.set(x)
        self.move_y_var.set(y)

        
        
    def print_on_console(self, text=""):
        self.console.config(state=tk.NORMAL)
        self.console.insert('end', text + '\n')
        self.console.see(tk.END)        
        self.console.config(state=tk.DISABLED)
        
    
    def check_connection(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.1.10", 50000))
            sock.close()
            return True
        except:
            self.print_on_console("No connection to PSLViewer!")
            return False
        
        
c = Window_App()


 
