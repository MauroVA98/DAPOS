# -*- coding: utf-8 -*-
"""
Created on Wed May 15 09:44:48 2019

@author: msjor
"""
############################################# Imports #################################################
import numpy as np

############################################# Functions ###############################################


def panel_area(t_o, t_e, pr_day, pr_eclipse, theta = 0):
    """COmpute the panel area needed for operations

    INPUTS
    t_o = orbital time [sec]
    t_e = eclipse time [sec]
    pr_day = power required during the day [W]
    pr_eclipse = power required during eclipse [W]
    theta = incidence angle [rad]

    OUTPUT
    A = solar panel area [m^2]
    m = solar panel mass [kg]"""

    #Mission parameters
    t_d = t_o - t_e #day time [s]
    T = 10 #mission lifetime [years]
    sr = 1358 #solar radiation [W/m^2]

    #efficiencies
    eff = 0.28 #solar panel efficiency
    eff_c = 0.9 #path efficiency panels to equipments
    eff_dc = 0.85 #path efficiency panels through batteries to equipment

    #solar panel characterisitcs
    wkg = 100 #[W/kg]
    d = 0.9725 #yearly degradation

    #compute required powerzzzz during day and eclipse
    pr_day = pr_day/eff_c #power required during the day EOL [W]
    pr_eclipse = pr_eclipse/eff_dc #power required during eclipse EOL [W]

    #EQUATIONS
    pbol = ((pr_day*t_d+pr_eclipse*t_e)/(t_d)/(d**T))/np.cos(theta) #bol power accounting for degradation, eclipse time, incidence angle

    psol = pbol/eff #power that needs to be generated by solar panels accounting for their efficiency

    #compute area and mass of panels
    A = psol/sr #area
    m = pbol/wkg #mass

    return A, m

def comms_mass(power_transmitter, area_antenna, dens_antenna):
   """Compute the mass of the enitre communications subsystem

   INPUT
   power_transmitter = power required by the transmitter on the spacecraft [W]
   Area of the antenna [m^2]
   dens_antenna = density of the antenna [kg/m^2], typical values 5-8

   OUTPUT
   total_mass = mass of the communications system [kg]
   vol_trans = volume of the transmitter [m^3]"""
   #transmitter characteristics
   specific_power = 2.9 #W/kg
   dens_trans = 0.75*10**-3 #kg/m3
   mass_trans = power_transmitter/specific_power  #kg
   vol_trans = mass_trans/dens_trans  #m3

   #mass of the amplifier
   mass_amp = 0.07*power_transmitter+0.634 #kg

   #Antenna characterisics
   mass_antenna = dens_antenna * area_antenna #kg, antenna on board of spacecraft

   #Combine to find mass total communications system
   total_mass = (mass_antenna + mass_amp + mass_trans)*1.3

   return total_mass, vol_trans

def comms(h, freq, G_trans, D_reciever, Ts, R, E_N):
    """Link budget in order to calculate the power required for the transmitter

    INPUT
    h = altitude [km]
    freq = frequency used for communication [Hz]
    G_trans = gain of the transmitting antenna of the spacecraft [dB]
    D_reciever = diameter of the recieving antenna [m]
    Ts = system noise temperature [K]
    R = data rate during communications [bps]
    E_N = signal to noise ratio [dB]

    OUTPUT
    power required for transmitter [W]"""

    #Characterisics of the system
    dish_eff = 0.5  #efficiency of the dish of the recieving station

    #Losses and gains
    line = 0.89     #line losses [dB]
    rain = 4+3/13*(freq*10**(-9)-27)    #rain attentuation losses [dB], TO BE ADAPTED FOR ALL f
    space = 147.55-20*np.log10(h*10**3)-20*np.log10(freq)   #space losses [dB]
    G_rec = -159.59+20*np.log10(D_reciever)+20*np.log10(freq)+10*np.log10(dish_eff) #gain of the recieving antenna [dB]
    G_trans = G_trans

    return 10**((E_N-line-G_trans-space-rain-G_rec-228.6+10*np.log10(Ts)+10*np.log10(R))/10)

def thrust_power(T):
    """Compute the power required [W] to provide a certain thrust for RIT ion thruster
        T = thrust [N]"""
    #returns the power required [W] based on a linear relation between thrust and power
    return (T+0.00069068)/0.0000156

def power_thrust(P):
    """Compute the thrust created [N] at a certain power setting for RIT ion thruster
    P = power [W]"""
    #returns the thrust provided [N] based on a linear relation between thrust and power
    return -0.00069068+0.0000156*P

def CD(A):
    """"Compute C_D [-] of a cylinder in a rarified flow
        A = frontal area [m^2]"""
    CD = (1.+np.pi/6.*np.sqrt(A/np.pi))*2
    return CD

def orbit(lower_limit, upper_limit, sun_sync, B=None, rho=None, T=None,
          D=None, N=720):
    """Calculates orbit data.

    For a circular orbit, the lower and upper limit should be the same. The
    output variables are the same no matter the orbit type, but in the case of
    a circular orbit, some output variables will be the same (e.g. semi-major
    axis, apocentre radius and pericentre radius)

    In the case of an elliptical orbit, r and V_orb will be arrays of N
    entries, where N is the number of steps into which the orbit is divided.

    An inclination will only be calculated for a sun-synchronous orbit, as it
    is not unique for a different orbit.

    INPUT:
        lower_limit = lowest orbital altitude [km]
        upper_limit = highest orbital altitude [km]
        sun_sync    = sun-synchronous orbit [True or False]
        B           = ballistic coefficient [kg/m^2] (elliptical orbits only)
        rho         = density [kg/m^3] (elliptical orbits only)
        T           = Thrust [N] (elliptical orbits only)
        D           = Drag [N] (elliptical orbits only)
        N           = number of sections to divide orbit into (optional)

    OUTPUT:
        a           = semi-major axis [km]
        r_a         = appocentre radius [km]
        r_p         = pericentre radius [km]
        r           = orbital radius [km]
        V_orb       = orbital velocity [km/s]
        P_orb       = orbital period [s]
        T_ecl       = eclipse time [s] (first order crude estimate)
        delta_V_tot = required delta V per orbit for station keeping [m/s] (elliptical orbits only)
        i_deg       = inclination [deg] (sun-synchronous orbits only)
    """
    ## constants
    # Earth data
    R_e         = 6378.1           # km, Earth's radius (max)
    g_0         = 0.00981          # km/s^2, Earth's surface gravity
    mu          = 398600.44        # km^3/s^2, Earth's gravitational constant
    G_e         = 6.6725*10**(-11) # Nm^2/kg, universal gravitational constant
    P_ES        = 365.25 * 86400   # s, period of Earth around the sun
    J_2         = 1.082 * 1e-3     # -, J2 effect in gravity field

    ## calculations, for the formulas, see AE2230 equations by heart and
    ## lecture slides.
    theta  = np.linspace(0, 2*np.pi, N)              # rad, orbit angle
    a      = (lower_limit + upper_limit + 2 * R_e)/2 # km, semi-major axis
    r_a    = upper_limit + R_e                       # km, appocentre r
    r_p    = lower_limit + R_e                       # km, pericentre r
    e      = r_a/a - 1                               # -, eccentricity
    p      = a * (1 - e*e)                           # km, semi-latus rectum
    r      = a * (1 - e*e) / (1 + e * np.cos(theta)) # km, orbit radius
    h      = r - R_e                                 # km, orbit height
    V_orb  = np.sqrt( mu * ( (2/r) - (1/a) ) )       # km/s, orbital V
    P_orb  = 2 * np.pi * np.sqrt(a**3 / mu)          # s, orbital period
    n      = 2 * np.pi / P_orb                       # s^-1, mean motion
    time   = theta/n                                 # s, time from 0
    E_tot  = -mu / (2 * a) * 1e6                     # J/kg, specific energy
    T_ecl  = np.arcsin(R_e / a) / np.pi * P_orb              # s, eclipse time (max, 2D, circular

    if lower_limit != upper_limit:
        # required delta V for station keeping per orbit (formula from SMAD)
        Per         = P_orb / (3600 * 24 * 365) # yr, period
        delta_T_tot = (theta/n)[np.where( T < D )] # s, time when T < D
        delta_T = np.hstack( (np.diff(delta_T_tot[np.where(delta_T_tot < P_orb/
                  2)]), np.diff(delta_T_tot[np.where(delta_T_tot > P_orb/2)]) ) )
        loss_part = np.where(np.logical_or(delta_T_tot < P_orb/2, delta_T_tot > P_orb/2))
        delta_V_req = np.pi * (1/B) * rho * (r * V_orb * 1e6) / Per # m/s/yr
        delta_V_mss = delta_V_req / (3600 * 24 * 365)               # m/s/s
        delta_V_tot = sum( delta_V_mss[loss_part][1:-1] * delta_T ) # m/s, tot

    else:
        delta_V_tot = None

    if sun_sync:
        # inclination for a syn-synchronous orbit, see AE2230 lecture 1 p. 57
        i     = np.arccos(-2/3 * P_orb/P_ES * 1/(J_2 * (R_e / r_p)**2)) # rad
        i_deg = np.rad2deg(i) # deg

        # eclipse calculations (3D, maximum eclipse because R_e is max
        # (flattening), atmospheric inteference not taken into account (not
        # relevant for one orbit either, but it is for longer periods),
        # shadow region being a cone not taken into account either)
        # S = shadow function, beta_ is +- 90° (- cw, + ccw) for sun-
        # synchronous orbits and goes down to 0° for equitorial orbits.
        #alpha_ = np.pi/2 - theta # not sure yet
        #beta_  = -np.pi/2 # rad, for sun-synchronous only
        #cosPsi = alpha_ * np.cos(theta) + beta_ * np.cos(theta)
        #Psi    = np.arccos(cosPsi)
        #S      = R_e*R_e*(1 + e*np.cos(theta))**2 + p*p*(cosPsi)**2 - p*p
        #T_in_e = time[np.where(np.logical_and(Psi > np.pi/2, S >= 0))]
        #T_ecl  = max(T_in_e) - min(T_in_e)               # s, eclipse time

    else:
        i_deg = None

    return a, r_a, r_p, r, e, V_orb, P_orb, T_ecl, delta_V_tot, i_deg

def drag(rho, V, CD, S):
    """Comupte the drag for a generic shape
    INPUTS
    rho = density [kg/m^3]
    V = velocity [m/s]
    CD =drag coefficicent [-]
    S = reference area [m^2]

    OUTPUT
    D = drag [N]"""

    D = 0.5*rho*S*V**2*CD
    return D

def cam_res(alt, res):
    theta = np.arctan(res/2/alt)
    vleo = [100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 190000, 200000, 210000, 220000, 230000, 240000, 250000]
    vleores = [2*x*np.tan(theta) for x in vleo]

    return vleores

def sizing(dens, massf_req, velocity, area_rat, P_other_day, P_other_ecl, intake_eff, T_D, aspect_rat, body_frac):
    """Size the intake, power system and propulsion system for a given operating condition

    INPUT
    dens = density the system needs to operate at [kg/m^3]
    massf_req = required massflow for the engine to function [SCCM]
    velocity = orbital velocity the spacecraft is operating at [m/s]
    area_rat = ratio between frontal area and intake area [m^2]
    P_other_day = power needed for all subsystems other than the propulsion systems during day[W]
    P_other_ecl = power needed for all subsystems other than the propulsion systems during eclipse[W]
    intake_eff = intake efficiency [-]
    T_D = required thrust over drag ratio [-]
    aspect_rat = aspect ratio of the spacecraft (L/outer diameter)
    body_frac = fraction of the projected area of the side of the satellite that can be used for solar panels [-]

    OUTPUT
    thrust = thrust provided by the engine [N]
    drag = drag created by the spacecraft [N]
    panelA = total solar panel area needed [m^2]
    panelA_out = panel area placed outside of the body [m^2]
    panelA - panelA_out = panel area placed on the body of the spacecraft [m^2]
    panelM = solar panel mass [kg]
    intakeA = area of the intake to meet required massflow [m^2]
    frontalA = frontal area of the satellite [m^2]
    length = length of the satellite body [m]
    width_panel = length the solar panels extend outside the body [m]"""

    #change massflow to kg/s
    massf_req= 7/45.37/(10**6)

    #compute intake and frontal area based on the required massflow
    intakeA = massf_req/dens/velocity/intake_eff
    frontalA = intakeA*area_rat

    #compute size of the spacecraft and body solar panels based on the intake size
    length = np.sqrt(frontalA/np.pi)*2*aspect_rat
    panel_body_space = length*np.sqrt(frontalA/np.pi)*2*body_frac

    #compute drag and thrust related to the body of the satellite
    drag_sat = drag(dens, velocity, CD_cyl, frontalA)
    thrust = drag_sat*T_D

    #Compute the required solar panel area to provide the thrust for satellite
    P_day = thrust_power(thrust) + P_other_day
    P_ecl = thrust_power(thrust) + P_other_ecl
    panelA, panelM = panel_area(t_o, t_e, P_day, P_ecl)

    #test to see if panels can be placed entirely on the body
    panelA_out =0.
    width_panel = panelA_out/length/2
    if panelA<panel_body_space:
        return thrust, drag_sat, panelA,panelA_out, panelA-panelA_out, panelM, intakeA, frontalA, length, width_panel

    else:
        #find panel area that has to be placed outside of the body
        panelA_out = panelA-panel_body_space
        #find width of said panel area (two rectangular panels along entire body length)
        width_panel = panelA_out/length/2
        #find drag caused by the extending solar panels
        drag_panel = drag(dens, velocity, CD_plate, width_panel*panel_t)

        #iterate until design converges
        while np.abs(((drag_sat+drag_panel)*T_D-thrust))>0.00000001:

            #set thrust to compensate for additional drag
            thrust = (drag_sat+drag_panel)*T_D

            #compute powers and panel areas needed for this thrust
            P_day = thrust_power(thrust) + P_other_day
            P_ecl = thrust_power(thrust) +P_other_ecl
            panelA, panelM = panel_area(t_o, t_e, P_day, P_ecl)

            #place panels on body
            panelA_out = panelA-panel_body_space
            width_panel = panelA_out/length/2

            #find drag created by newly sized panels
            drag_panel = drag(dens, velocity, CD_plate, width_panel*panel_t)


        return thrust, drag_sat+drag_panel, panelA,panelA_out, panelA-panelA_out, panelM, intakeA, frontalA, length, width_panel





############################### Select concepts to be solved for #######################################
#Concept 1: payload performance with constant density
#Concept 2: Low orbit with gravity measurement
#Concept 3: Highly elliptic orbit concept
concepts = [True, True, True]
names = ["Paylöd", "Grav", "supposedly cool"]


######################################## General inputs #################################################
#drag coefficients of different shapes, based on the projected area
accomodation = 0.95     #[-]    Accomodation factor
incidence = 0           #[rad]
CD_cyl = 2.6    #[-]            CD of cylinder of l/D =1, alpha= 0.95, T = 600K
CD_plate = 2+4*accomodation*np.sin(incidence)/3      #[-]            CD of flat plate, diffuse reflections
panel_t = 0.05      #[m]


######################################## Complete designs of the concepts ###############################
if concepts[0]:

    print ("-----------------------------------------------------------------------")

if concepts[1]:
    print ("-----------------------------------------------------------------------")
if concepts[2]:
    print ("-----------------------------------------------------------------------")
