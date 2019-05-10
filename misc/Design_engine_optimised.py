# -*- coding: utf-8 -*-
"""
Created on Fri May 10 09:47:33 2019

@author: msjor
"""

import numpy as np
import matplotlib.pyplot as plt
from Iterated_drag_surface import Drag_Thrust_Area_iteration
from DAPOS.src.power import panel_area

Isp = 3546 #[s]
density = 1*10**-10  #[kg/m^3]
intake_eff = 0.4    #[-]
velocity = 7800 #[m/s]
thrust_power = 70*10**3   #[W/N]

#find surface area, drag/thrust, massflow and power required for engine
A, F, mdot, power_engine = Drag_Thrust_Area_iteration(Isp, density, intake_eff, velocity, thrust_power)



