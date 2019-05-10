# -*- coding: utf-8 -*-
"""
Created on Fri May 10 09:31:57 2019

@author: Jeije
"""

import numpy as np
import matplotlib.pyplot as plt



class Propulsion:
    def __init__(self):
        self.isp = 3546            #s
        self.Pspec = 70e3          #W/N
        self.g0 = 9.81#
        self.altlist=np.arange(100000,250000,1000)
        self.denslist= [7.12291353962386e-07,	5.86769021755108e-07,	4.81879870318068e-07,	3.95040209489290e-07,	3.23652177284168e-07,	2.65275598106261e-07,	2.17718176588005e-07,	1.79070892446252e-07,	1.47708997722136e-07,	1.22273226845305e-07,	1.01641139916330e-07,	8.48866195676797e-08,	7.12333449683426e-08,	6.00619506228292e-08,	5.08843607231251e-08,	4.33147837411984e-08,	3.70473163509698e-08,	3.18386163168622e-08,	2.74944683291785e-08,	2.38593439080724e-08,	2.08082675533319e-08,	1.82404622095941e-08,	1.60743698832240e-08,	1.42437370116482e-08,	1.27065091580760e-08,	1.13877396265517e-08,	1.02544682519894e-08,	9.27411770523267e-09,	8.42088842924472e-09,	7.67414445577488e-09,	7.01722876436798e-09,	6.43658273715459e-09,	5.92108392503632e-09,	5.46154257111855e-09,	5.05031496693991e-09,	4.68100374444179e-09,	4.34822352634584e-09,	4.04741618715760e-09,	3.77470411102483e-09,	3.52677279736435e-09,	3.30077631373787e-09,	3.09426066800654e-09,	2.90510133348712e-09,	2.73145202655562e-09,	2.57170248665642e-09,	2.42444350131044e-09,	2.28843779456276e-09,	2.16259568607479e-09,	2.04595465140964e-09,	1.93766208790127e-09,	1.83696072662805e-09,	1.74317623822572e-09,	1.65570666517827e-09,	1.57401338081474e-09,	1.49761332931496e-09,	1.42607234449754e-09,	1.35899938027009e-09,	1.29604151409698e-09,	1.23687960803576e-09,	1.18122453086399e-09,	1.12881386039455e-09,	1.07928369326640e-09,	1.03267830890092e-09,	9.88662139524657e-10,	9.47054164413543e-10,	9.07688727287975e-10,	8.70414006978622e-10,	8.35090661731593e-10,	8.01590625128217e-10,	7.69796034669667e-10,	7.39598276683833e-10,	7.10897133428138e-10,	6.83600020150989e-10,	6.57621301488289e-10,	6.32881677953489e-10,	6.09307634465901e-10,	5.86830943882386e-10,	5.65388219377229e-10,	5.44920510274860e-10,	5.25372936597805e-10,	5.06694358162633e-10,	4.88837074552183e-10,	4.71756552723734e-10,	4.55411179388851e-10,	4.39762035629106e-10,	4.24772691499299e-10,	4.10409018621596e-10,	3.96639018995039e-10,	3.83432668439179e-10,	3.70761773261621e-10,	3.58599838890059e-10,	3.46921949342576e-10,	3.35704656527676e-10,	3.24925878469787e-10,	3.14564805648423e-10,	3.04601814721224e-10,	2.95018388974120e-10,	2.85797044906764e-10,	2.76921264419330e-10,	2.68375432118405e-10,	2.60144743388135e-10,	2.52215287774900e-10,	2.44573791313563e-10,	2.37207710456630e-10,	2.30105153775708e-10,	2.23254842129989e-10,	2.16646071634274e-10,	2.10268679204449e-10,	2.04113010477918e-10,	1.98169889924196e-10,	1.92430592976853e-10,	1.86886820032470e-10,	1.81530672175375e-10,	1.76354628498810e-10,	1.71351524903954e-10,	1.66514534268031e-10,	1.61837147881621e-10,	1.57313158063408e-10,	1.52936641867971e-10,	1.48701945808953e-10,	1.44603671526072e-10,	1.40636662330063e-10,	1.36795990564734e-10,	1.33076945730035e-10,	1.29475023314286e-10,	1.25985914287680e-10,	1.22605495212762e-10,	1.19329818930856e-10,	1.16155105786510e-10,	1.13077735354755e-10,	1.10094238638565e-10,	1.07201290706255e-10,	1.04395703740731e-10,	1.01674420474483e-10,	9.90345079860841e-11,	9.64731518356329e-11,	9.39876505181560e-11,	9.15754102154385e-11,	8.92339398280812e-11,	8.69608462708262e-11,	8.47538300153363e-11,	8.26106831179240e-11,	8.05292760258100e-11,	7.85075678429742e-11,	7.65435931481535e-11,	7.46354610192917e-11,	7.27813517831536e-11,	7.09795139274047e-11,	6.92282611659526e-11,	6.75259696489216e-11,	6.58710753091843e-11]
        
    def thrust4mdot(self, mdot):
        T = mdot*self.isp*self.g0
        return T
    
    def power4thrust(self, thrust):
        P=thrust*self.Pspec
        return P
    
    def minisp(self, V_b ,c_d, n_c):
        isp=0.5*V_b*c_d/n_c/self.g0
        return isp

        
    


"""
put testing/debugging code in the if-statement below
it will only run if you run this python file (response_model.py)
"""
if __name__ == "__main__":
    pr = Propulsion()
    thing=2
    





    if thing==1:
        c_d = np.linspace(2.0,3.2,6)
        V_b= 7.8e3
        n_c = np.linspace(0.1,0.6,20)
        
        minispvec=np.vectorize(pr.minisp)
        
        out=[]
        for x in range(len(c_d)):
            out.append(minispvec(V_b,c_d[x],n_c))
            plt.plot(n_c,out[x])
            
        
        print(out)
            
        plt.ylim(0,4000)
        plt.xlim(0.2,0.6)
        plt.ylabel("ISP (s)")
        plt.xlabel("Collection efficiency (-)")
        plt.show()
    elif thing==2:
        print("hoi")
        plt.plot(pr.altlist,pr.denslist)
        plt.show()
    else:
        print("8==D")
        