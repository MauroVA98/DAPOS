# -*- coding: utf-8 -*-
"""
Created on Thu May 16 14:14:28 2019

@author: msjor
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 15 09:44:48 2019

@author: msjor
"""
############################################# Imports #################################################
import numpy as np

import matplotlib.pyplot as plt

############################################# Functions ###############################################


def panel_area(t_o, t_e, pr_day, pr_eclipse):
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

def comms(h, freq, G_trans, D_reciever, Ts, R, E_N, rain):
    """Link budget in order to calculate the power required for the transmitter

    INPUT
    h = altitude [km]
    freq = frequency used for communication [Hz]
    G_trans = gain of the transmitting antenna of the spacecraft [dB]
    D_reciever = diameter of the recieving antenna [m]
    Ts = system noise temperature [K]
    R = data rate during communications [bps]
    E_N = signal to noise ratio [dB]
    Rain = rain attentuation losses [dB] from table page 534 smad using optimal elevation angle and iterative estimation of the power

    OUTPUT
    power required for transmitter [W]"""

    #Characterisics of the system
    dish_eff = 0.6  #efficiency of the dish of the recieving station
    Ts = Ts+290*(1-10**(rain/10))
    #Losses and gains
    line = 0.89     #line losses [dB]
    space = 147.55-20*np.log10(h*10**3)-20*np.log10(freq)   #space losses [dB]
    G_rec = -159.59+20*np.log10(D_reciever)+20*np.log10(freq)+10*np.log10(dish_eff) #gain of the recieving antenna [dB]
    G_trans = G_trans
    #[103] A New Approach for Enhanced Communication to LEO Satellites
    E_opt= 45.-0.00446*h #[deg]     optimal elevation angle for communications

    P= 10.**((E_N-line-G_trans-space-rain-G_rec-228.6+10.*np.log10(Ts)+10.*np.log10(R))/10.) #[W]

    return P

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
        e           = eccentricity [-]
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
        delta_T_tot = (theta/n)[np.where(T<D)] # s, time when T < D
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
        i     = np.arccos(-2/3 * P_orb/P_ES * 1/(J_2 * (R_e / p)**2)) # rad
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

def cam_res(alt, res, alt_orbit):
    """Find the camera resolutions at a certain altitude

    INPUT
    alt= altitude for which the camera resolution is known [m]
    res= known camera resolution [m/pixel]
    alt_orbit = altitude of operating orbit [m]

    OUTPUT
    vleores = resoltuion at operating altitude [m/pixel]"""
    theta = np.arctan(res/2/alt)
    vleores = 2*alt_orbit*np.tan(theta)

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
    massf_req= massf_req/45.37/(10**6)

    #compute intake and frontal area based on the required massflow
    intakeA = massf_req/dens/velocity/intake_eff
    if intakeA<min_intake:
        intakeA = min_intake
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

def elevationangle(longitude_ground, latitude_ground, longitude_sub, latitude_sub, elevation_min, incl, concept):

    """Compute the contact time with the ground station, istantaneous position parameters

    INPUT
    longitude_ground = [deg] longitude of ground station
    latitude_ground = [deg] latitude of ground station
    longitude_sub = [deg] longitude of subsatellite point (groundtrack) GET DATA FROM ORBIT MODEL
    latitude_sub = [deg] latitude of subsatellite point (groundtrack) GET DATA FROM ORBIT MODEL
    elevation_min = [deg] minimum elevation angle at which the ground station is visible

    OUTPUT

    elevation = [deg] istantaneous elevation angle to the horizon of the ground station
    contact_time = [sec] contact time with the ground station

    """

    #INSTANTANEOUS POSITION OF S/C
    #FROM SMAD PAG 109-111

    R_E= 6378 #[km]
    rho_rad= np.arcsin(R_E/(R_E+h)) #[rad] angular radius of Earth
    rho=np.rad2deg(rho_rad) #[deg]
    lambda_0=90-rho #[deg] angular radius measured at the centre of the earth of the region as seen from s/c
    lambda_0_rad= np.deg2rad(lambda_0) #[rad]
    D_max= R_E*np.tan(lambda_0_rad)#[km] distance to the horizon
    Delta_L= np.abs(longitude_sub-longitude_ground)
    latitude_sub_rad=np.deg2rad(latitude_sub)
    latitude_ground_rad=np.deg2rad(latitude_ground)
    Delta_L_rad=np.deg2rad(Delta_L)
    lambda_Earth_rad= np.arccos(   np.sin(latitude_sub_rad)*np.sin(latitude_ground_rad)+np.cos(latitude_sub_rad)*np.cos(latitude_ground_rad)*np.cos(Delta_L_rad)   ) #[rad] earth centered angle, measured from subsatellite point to target
    lambda_Earth=np.rad2deg(lambda_Earth_rad) #[deg]
    eta_rad= np.arctan(  np.sin(rho_rad)*np.sin(lambda_Earth_rad)/(1-np.sin(rho_rad)*np.cos(lambda_Earth_rad))   ) #[rad] angle from nadir
    eta= np.rad2deg(eta_rad)  #[deg] angle from nadir
    elevation= 90- eta -lambda_Earth   #[deg] elevation angle
    D=R_E*np.sin(lambda_Earth_rad)/np.sin(eta_rad) #[km]

    elevation_min_rad=np.deg2rad(elevation_min)

    #FROM NOW ON: ASSUMPTION OF CIRCULAR ORBIT

    etaMAX_rad= np.arcsin(  np.sin(rho_rad)*np.cos(elevation_min_rad)   ) #[rad] angle from nadir
    etaMAX= np.rad2deg(etaMAX_rad)  #[deg] angle from nadir
    lambdaMAX= 90-etaMAX-elevation_min
    elevation_max= 180-elevation_min

    if incl !=None:
        lat_pole= 90-incl #[deg]
        lat_pole_rad=np.deg2rad(lat_pole)
        long_pole= 100 #L_node-90
        Dlong= np.abs(long_pole-longitude_ground)
        Dlong_rad= np.deg2rad(Dlong)
        lambdaMIN= np.arcsin(    np.sin(lat_pole_rad)*np.sin(latitude_ground_rad)+np.cos(lat_pole_rad)*np.cos(latitude_ground_rad)*np.cos(Dlong_rad)     )

    if incl == None:
        lambdaMIN=7 #[deg]   #assumption (can be calculated using the inclination and ascending node of the S/C from SMAD p 116)
    lambdaMIN_rad=np.deg2rad(lambdaMIN)
    lambdaMAX_rad=np.deg2rad(lambdaMAX)
    contact_time =(t_o/180)*np.rad2deg(np.arccos(np.cos(lambdaMAX_rad)/np.cos(lambdaMIN_rad))) #[s] Contact time with the ground station

    return elevation, contact_time



############################### Select concepts to be solved for #######################################
#Concept 1: payload performance with constant density
#Concept 2: Low orbit with gravity measurement
#Concept 3: Highly elliptic orbit concept
#<<<<<<< HEAD
concepts = [True, True, False]
#=======
concepts = [True, False , False]
#>>>>>>> 7a044f535c14734b278b04029b06fe32af65c052
names = ["Paylöd", "Grävt", "supposedly cool"]

######################################## General inputs #################################################
#drag coefficients of different shapes, based on the projected area
accomodation = 0.95     #[-]    Accomodation factor
incidence = 0           #[rad]
CD_cyl = 2.6            #[-]            CD of cylinder of l/D =1, alpha= 0.95, T = 600K
CD_plate = 2.35         #[-]            CD of flat plate, diffuse reflections
panel_t = 0.05          #[m]
min_intake = 0.         #[m^2] minimum intake area
w = 0.001               #[m] thickness of skin intake
mat_dens = 2800         #[kg/m^3] density of the material 

######################################## Complete designs of the concepts ###############################
if concepts[0]:
    #input of the concept
    #environmental inptus
    h = 205                 #[km] altitude
    density = 3.115*10**-10     #[kg/m^3] density for which the system is designed

    #communication inputs
    frequency = 19.7*10**9    #[Hz] frequency at which communincation is done
    G_trans = 12             #[dB] gain of the transmitter used
    D_rec = 5               #[m] diameter of the reciever antenna
    Ts = 400                #[K] system noise temperature
    E_N = 10                #[dB] signal to noise ratio desired for communications
    rain = -5
    A_antenna = 0.0314         #[m^2] area of the antenna used on the spacecraft
    rho_antenna = 5         #[kg/m^2] density of the antenna used on the spacecraft

    #camera specifications
    cam_alt = 500           #[km] altitude at which the camera selected was tested
    res = 0.6               #[m/pixel] resolution obtained at the tested altitude
    P_pay = 20              #[W] power required to operate payload
    M_pay = 20              #[kg] mass of the payload

    #propulsion parameters
    massf_req = 7           #[SCCM] massflow required for a functional engine
    intake_eff = 0.4        #[-] intake efficicency
    T_D = 1.2               #[-] Thrust to drag ratio

    #geometrical parameters
    aspect_rat = 5          #[-] Aspect ratio of the intake, assumed to be equal for the outer shell
    body_frac = 0.8         #[-] Fraction of body that can be used for solar panels
    area_rat = 1.2          #[-] Ratio between intake area and frontal area


    #power parameters
    P_misc = 200            #[W] power required for other subsystems
    battery_dens = 250      #[Wh/kg] power density of the batteries (only for <100W/kg)
    battery_deg = 0.8       #[-] battery degradation factor over lifetime
    DOD = 0.25              #[-] depth of discharge
    number_batt = 2        #[-] number of battery packs
    theta = np.pi/6     # [rad] incidence angle of solar panels

    #Ground station parameters
    #ESA SVALBARD https://www.esa.int/Our_Activities/Navigation/Galileo/Galileo_IOV_ground_stations_Svalbard
    longitude_ground= 15.399 #[deg] Lt ground station (ESA Svalbard)
    latitude_ground= 78.228 #[deg] delta_t ground station (ESA Svalbard)
    elevation_min=5 #[deg] minimum elevation angle above the horizon to make contact with ground

    # ground track parameters TO BE UPDATED ONCE WE HAVE A MODEL
    longitude_sub= 185 #20 #[deg] Ls subsatellite point (groundtrack to centre of the earth) get INSTANTANEOUS data from orbit model
    latitude_sub= 10#90 #[deg] delta_s subsatellite point (groundtrack to centre of the earth) get INSTANTANEOUS data from orbit model

    #Design specfification computation
    #compute camera resolution performance
    cam_perf = cam_res(cam_alt, res, h)

    #compute orbital parameters from desired orbit
    a, r_a, r_p, r,e, V, t_o, t_e, delta_V_tot, incl  = orbit(h, h, True)
    cycles = 10*365.25*24*3600/t_o          #number of battery charge discharge cycles

    #compute contact time
    elevation, contact_time= elevationangle(longitude_ground, latitude_ground, longitude_sub, latitude_sub, elevation_min, incl, concepts)

    #compute data rate required
    datarate_imaging = 2632.*10.**6. #[bps]
    compression_rat = 3./5.   #[-]
    data_orbit = datarate_imaging*(t_o-t_e)*compression_rat     #data produced during orbit [bits]
    R = data_orbit/contact_time    #[bps] data rate required during communications

    #compute power required for communications
    P_comms = comms(h, frequency, G_trans, D_rec, Ts, R, E_N, rain)

    #compute mass assigned to the communication system
    M_comm, V_comm = comms_mass(P_comms, A_antenna, rho_antenna)

    #find power required during eclipse and day
    P_other_day = P_comms+P_pay+P_misc
    P_other_ecl = P_comms+P_misc

    #Size the solar panels, intake, also compute drag and thrust
    thrust, drag_tot, panelA_tot, panelA_out, panelA_body, panelM, intakeA, frontalA, length, width_panel = sizing(density, massf_req, V[1]*1000., area_rat, P_other_day, P_other_ecl, intake_eff, T_D, aspect_rat, body_frac)

    #battery mass required
    M_batt = (thrust_power(thrust)+P_other_ecl)/battery_deg*t_e/3600/battery_dens/DOD
    print (M_batt*100-P_other_ecl-thrust_power(thrust))
    if M_batt*100<P_other_ecl+thrust_power(thrust):
        print ("BATTERIES CANT PROVIDE REQUIRED POWER< USE LESS BATTERY PACKS")

    else:
        M_batt = M_batt*number_batt

        #result presentation
        print ("-------------------------------Result for", names[0],"---------------------------")
        print (" ")
        print ("                                -Power budget-                        ")
        print ("Power to operate engine = ",  thrust_power(thrust), "[W]")
        print ("Power for communication system = ", P_comms, "[W]")
        print ("Power for payload operations = ", P_pay, "[W]")
        print ("Power for other subsystems = ", P_misc, "[W]")
        print (" ")
        print ("                                -Mass budget-                        ")
        print ("Mass for solar panels =", panelM, "[kg]")
        print ("Mass for batteries =", M_batt, "[kg]")
        print ("Mass for power management system = ", 0.25*(panelM+M_batt)/(1-0.25), "[kg]")
        print ("Mass total power system =", (panelM+M_batt)*1.333333333, "[kg]")
        print ("Mass for communication system =", M_comm, "[kg]")
        print ("Mass for payload =", M_pay, "[kg]")
        print ("Mass for structure = ", np.sqrt(frontalA/np.pi)*2*np.pi*w*mat_dens*length, "[kg]")
        print ("-----------------------------------------------   +")
        print ("Total mass that can be estimated =", M_comm+M_pay+(panelM+M_batt)*1.333333333+np.sqrt(frontalA/np.pi)*2*np.pi*w*mat_dens*length, "[W]")
        print (" ")
        print ("                                -System characteristics-                        ")
        print ("Intake size =", intakeA, "[m^2]")
        print ("Frontal area =", frontalA, "[m^2]")
        print ("Thrust provided by the engine =", thrust, "[N]")
        print ("Drag experienced by the system =", drag_tot, "[N]")
        print ("Length of the satellite = ", length, "[m]")
        print ("Width of solar panels extending from body = ", width_panel, "[m]")
        print ("Achieved payload resolution =", cam_perf, "[m/pixel]")
        print ("Total solar panel area = ", panelA_tot, "[m^2]" )


if concepts[1]:
    #input of the concept
    #environmental inptus
    selected = 6
    hlist = [140, 150, 160, 170, 180, 190, 200] ##list of considered altitude
    denslist  = [3.1*10**-9, 2*10**-9, 1.1*10**-9, 9.4*10**-10, 6.5*10**-10, 4*10**-10, 2.5*10**-10] #list of maxmimum densities at the presented altitudes
    dens_ratios = [0.7529, 0.678486, 0.60714, 0.54016, 0.4783, 0.422, 0.371698]
    h = hlist[selected-1]                 #[km] altitude selected from [160, 170, 180, 190, 200]
    density = denslist[selected-1]*1.2   #[kg/m^3] density for which the system is designed (20-25 % added for uncertainty in reading of graph)
    dens_rat = dens_ratios[selected-1]
    R_e         = 6378.1           # km, Earth's radius (max)

    #communication inputs
    frequency = 19.7*10**9    #[Hz] frequency at which communincation is done
    G_trans = 12             #[dB] gain of the transmitter used
    D_rec = 5               #[m] diameter of the reciever antenna
    Ts = 400                #[K] system noise temperature
    E_N = 10                #[dB] signal to noise ratio desired for communications
    A_antenna = 0.0314          #[m^2] area of the antenna used on the spacecraft
    rho_antenna = 5         #[kg/m^2] density of the antenna used on the spacecraft
    rain = -5

    #propulsion parameters
    massf_req = 7./dens_rat           #[SCCM] massflow required for a functional engine
    intake_eff = 0.4        #[-] intake efficicency
    T_D = 1.1               #[-] Thrust to drag ratio

    #geometrical parameters
    aspect_rat = 5          #[-] Aspect ratio of the intake, assumed to be equal for the outer shell
    body_frac = 0.9         #[-] Fraction of body that can be used for solar panels
    area_rat = 1.2          #[-] Ratio between intake area and frontal area


    #power parameters
    P_misc = 200            #[W] power required for other subsystems
    battery_dens = 250      #[Wh/kg] power density of the batteries (only for <100W/kg)
    battery_deg = 0.8       #[-] battery degradation factor over lifetime
    DOD = 0.25              #[-] depth of discharge
    number_batt = 2        #[-] number of battery packs
    theta  = 0              #[rad] incidence angle
    
    #Ground station parameters
    #ESA SVALBARD https://www.esa.int/Our_Activities/Navigation/Galileo/Galileo_IOV_ground_stations_Svalbard
    #SvalSat and KSAT's Troll Satellite Station (TrollSat) in Antarctica are the only ground stations that can see a low altitude polar orbiting satellite (e.g., in sun-synchronous orbit) on every revolution as the earth rotates.
    longitude_ground= 15.399 #[deg] Lt ground station (ESA Svalbard)
    latitude_ground= 78.228 #[deg] delta_t ground station (ESA Svalbard)
    elevation_min=5 #[deg] minimum elevation angle above the horizon to make contact with ground

    # ground track parameters TO BE UPDATED ONCE WE HAVE A MODEL
    longitude_sub= 185 #20 #[deg] Ls subsatellite point (groundtrack to centre of the earth) get INSTANTANEOUS data from orbit model
    latitude_sub= 10#90 #[deg] delta_s subsatellite point (groundtrack to centre of the earth) get INSTANTANEOUS data from orbit model

    #Design specfification computation

    #compute orbital parameters from desired orbit
    a, r_a, r_p, r,e, V, t_o, t_e, delta_V_tot, incl  = orbit(h, h, True)
    cycles = 10*365.25*24*3600/t_o          #number of battery charge discharge cycles

    #compute eclipse time based on sun-synchronous dusk-dawn
    H = R_e/(R_e+h)
    d_j = np.arccos(H)
    j = (incl-90)/180*np.pi
    d_1 = (d_j-j)*180/np.pi
    d_2 = (-d_j-j)*180/np.pi
    alpha_1 = np.arccos(np.sin(d_j)/np.sin(23.44/180*np.pi+j))
    alpha_2 = np.arccos(np.sin(d_j)/np.sin(23.44/180*np.pi-j))
    t_e_1 = alpha_1/np.pi*t_o
    t_e_2 = alpha_2/np.pi*t_o
    t_e = max(t_e_1, t_e_2)

    #compute contact time
    elevation, contact_time= elevationangle(longitude_ground, latitude_ground, longitude_sub, latitude_sub, elevation_min, incl, concepts)

    #compute data rate required
    datarate_imaging = 2632.*10.**6. #[bps]
    compression_rat = 3./5.   #[-]
    data_orbit = datarate_imaging*(t_o-t_e)*compression_rat     #data produced during orbit [bits]
    R = data_orbit/contact_time    #[bps] data rate required during communications

    #compute power required for communications
    P_comms = comms(h, frequency, G_trans, D_rec, Ts, R, E_N, rain)

    #compute mass assigned to the communication system
    M_comm, V_comm = comms_mass(P_comms, A_antenna, rho_antenna)

    #find power required during eclipse and day
    P_other_day = P_comms+P_misc
    P_other_ecl = P_comms+P_misc

    #Size the solar panels, intake, also compute drag and thrust
    thrust, drag_tot, panelA_tot, panelA_out, panelA_body, panelM, intakeA, frontalA, length, width_panel = sizing(density, massf_req, V[1]*1000., area_rat, P_other_day, P_other_ecl, intake_eff, T_D, aspect_rat, body_frac)

    #battery mass required
    M_batt = (thrust_power(thrust)+P_other_ecl)/battery_deg*t_e/3600/battery_dens/DOD

    if M_batt*100<P_other_ecl+thrust_power(thrust):

        print ("BATTERIES CANT PROVIDE REQUIRED POWER< USE LESS BATTERY PACKS")

    else:
        M_batt = M_batt*number_batt

    #result presentation
    print ("-------------------------------Result for", names[1],"at", h, "km","---------------------------")
    print (" ")
    print ("                                -Power budget-                        ")
    print ("Power to operate engine = ",  thrust_power(thrust), "[W]")
    print ("Power for communication system = ", P_comms, "[W]")
    print ("Power for other subsystems = ", P_misc, "[W]")
    print ("-----------------------------------------------   +")
    print ("Maximum power required =", thrust_power(thrust)+P_comms+P_misc, "[W]")
    print (" ")
    print ("                                -Mass budget-                        ")
    print ("Mass for solar panels =", panelM, "[kg]")
    print ("Mass for batteries =", M_batt, "[kg]")
    print ("Mass for power management system = ", 0.333333*(panelM+M_batt), "[kg]")
    print ("Mass total power system =", (panelM+M_batt)*1.333333333, "[kg]")
    print ("Mass for communication system =", M_comm, "[kg]")
    print ("Mass for structure = ", np.sqrt(frontalA/np.pi)*2*np.pi*w*mat_dens*length, "[kg]")
    print ("-----------------------------------------------   +")
    print ("Total mass that can be estimated =", M_comm+M_pay+(panelM+M_batt)*1.333333333+np.sqrt(frontalA/np.pi)*2*np.pi*w*mat_dens*length, "[W]")
    print (" ")
    print ("                                -System characteristics-                        ")
    print ("Intake size =", intakeA, "[m^2]")
    print ("Frontal area =", frontalA, "[m^2]")
    print ("Thrust provided by the engine =", thrust, "[N]")
    print ("Drag experienced by the system =", drag_tot, "[N]")
    print ("Length of the satellite = ", length, "[m]")
    print ("Width of solar panels extending from body = ", width_panel, "[m]")
    print ("Total solar panel area = ", panelA_tot, "[m^2]" )

if concepts[2]:
    print ("This is an overhyped concept")

