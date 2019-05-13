# -*- coding: utf-8 -*-
"""
Created on Mon May 13 10:12:59 2019

@author: msjor
"""
import numpy as np
import matplotlib.pyplot as plt
############################    Functions   ############################
#instead of import from power in src folder, as import doesn't work 
def panel_area(t_o, t_e, pr_day, pr_eclipse):
    #INPUTS
    wm = 200 #[W/m^2] not really needed as we are mainly concerned with solar radiation and panel efficiencies
    wkg = 80 #[W/kg]
    #t_o = 14095 #orbital period in [s]
    #t_e = 5920 #eclipse time [s]
    t_d = t_o - t_e #day time [s]
    sr = 1400 #solar radiation [W/m^2]
    theta = 0 #solar panel incidence angle [rad]
    T = 10 #mission lifetime [years]
    d = 0.99 #yearly degradation
    eff = 0.28 #solar panel efficiency
    eff_c = 0.99 #battery charging efficiency
    eff_dc = 0.99 #battery discharging efficiency
    #pr_day = 500 #power required during the day EOL [W]
    pr_eclipse = pr_eclipse/eff_c/eff_dc #power required during eclipse EOL [W]
    
    #EQUATIONS
    pbol = ((pr_day*t_d+pr_eclipse*t_e)/(t_d)/(d**T))/np.cos(theta) #bol power accounting for degradation, eclipse time, incidence angle
    
    psol = pbol/eff #power that needs to be generated by solar panels accounting for their efficiency
    
    A = psol/sr #area
    m = psol/wkg #mass
    
    #print('power =', psol, 'A=', A, 'm =', m)
    
    return A, m

#area to drag and power relations 
def A_to_Drag(A):
    return density*(velocity**2)*(1.+np.pi/6.)*np.sqrt(A/np.pi)*A

def Drag_to_A(D):
    return np.cbrt((D/(density*velocity**2*(1+np.pi/6)))**2*np.pi)

def panel_drag(A_p):
    return 0.3*A_p*0.5*density*velocity**2

def area_panel_drag(D_p):
    return D_p*2/0.3/density/velocity**2

def massf_to_A(mf):
    return mf/intake_eff/density/velocity

def comms(h, freq, G_trans, D_reciever, Ts, R):
    dish_eff = 0.55
    rain = 4+3/13*(freq*10**-9-27)
    space = 147.55-20*np.log10(h*10**3)-20*np.log10(freq)
    G_rec = -159.59+20*np.log10(D_reciever)+20*np.log10(freq)+10*np.log10(dish_eff)
    line = 0.89
    G_trans = G_trans
    E_N = 7
    
    return 10**((E_N-line-G_trans-space-rain-G_rec-228.6+10*np.log10(Ts)+10*np.log10(R))/10)

def thrust_power(T):
    return (T+0.00069068)/0.0000156

################################    main     #############################
#define orbit parameters 
t_o = 3600*1.5  #orbital period
t_e = 36.9*60   #eclipse period
h = 225   #orbital altitude #[km]
density = 1*10**-10  #[kg/m^3]
velocity = 7787 #[m/s]

#propulsion parameters
Isp = 3546 #[s]
intake_eff = 0.4    #[-]
area_correction = 1.1
T_over_D = 1.2
massf_req = 8/45.37 #[mg/s]
massf_req = massf_req/(10**6) #[kg/s]

#communication parameters 
freq = 36 #communication frequency [GHz]
freq = freq*10**9 #communications frequency [Hz]
G_trans = 15 #gain satellite antenna [dBi]
D_reciever = 1.5 #diameter reciever on ground [m]
Ts = 600 #system noise temperature [K]
datarate_imaging = 2632*10**6 #[bps]
compression_rat = 3/5   #[-]
data_orbit = datarate_imaging*(t_o-t_e)*compression_rat     #data produced during orbit [bits]
contact_time = 0.015*t_o       #[s]
R = data_orbit/contact_time    #data rate [bps]


#find power required for communication system 
P_comm = comms(h, freq, G_trans, D_reciever, Ts, R)

#power needed for other subsystems (from power budget)
P_camera = 10.

#compute intake and frontal area based on the massflow requirement
intakeA = massf_to_A(massf_req)
frontalA = intakeA*area_correction
#compute drag (without solar panels)
drag_sat = A_to_Drag(frontalA)

#compute intial thrust and power needed for purely the satellite 
thrust = drag_sat*T_over_D
power_init = thrust_power(thrust)

#size solar panels for intial requirements
power_day_i = power_init+P_comm+P_camera
power_eclipse_i = power_init+P_comm
panelA_i, panelM_i = panel_area(t_o, t_e, power_day_i, power_eclipse_i)

#added drag due to the solar panels
drag_panel = panel_drag(panelA_i)

#iterate to find total power requirement

while np.abs((drag_sat+drag_panel)*T_over_D-thrust)>0.0000001:
    #set thrust to counteract new drag force
    thrust = T_over_D*(drag_sat+drag_panel)
    #compute power needed for new thrust force
    power_thrust = thrust_power(thrust)
    power_day = power_thrust+P_comm+P_camera
    power_eclipse = power_thrust+P_comm
    #size solar panels at new power
    panelA, panelM = panel_area(t_o, t_e, power_day, power_eclipse)
    #compute new drag
    drag_panel = panel_drag(panelA)

print ("massflow required for engine operations [kg/s]:", massf_req)  
print ("Intake area [m^2] = ", intakeA)
print ("Panel area [m^2] and mass [kg] = ", panelA,"|||",  panelM)
print ("Power required to operate engine = ", power_thrust)
print ("Thrust, drag [N] and T/D", thrust, "|||", drag_panel+drag_sat, "||||", thrust/(drag_panel+drag_sat))