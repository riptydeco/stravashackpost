from scipy.constants import g, R, atm
import numpy as np
from itertools import product
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import os

# air density in kg/m^3
def air_density(altitude=1500, T=293):
    L = 0.0065
    T0 = 298
    M = 0.02896
    Rs = 287.058
    p_exp = M*g/(R*L)
    p = atm*(1-(L*altitude/T0))**p_exp
    return p/(Rs*T)

# resisting force from air
def F_air(mph, CdA, rho=air_density()):
    speed = mph/2.237
    return 0.5 * CdA * rho * speed**2

#rolling resistance
def F_roll(grad, m, Crr):
    return Crr * np.cos(np.arctan(grad)) * m * g    

#gravity
def F_grav(grad, m):
    return np.sin(np.arctan(grad)) * m * g

def P_needed(mph, grad, m, CdA, Crr, rho, L_dt=0.051):
    speed = mph/2.237 # convert to m/s
    F_resist = F_air(mph, CdA, rho) + F_roll(grad, m, Crr) + F_grav(grad, m)
    return F_resist * speed / (1.0-L_dt)

# mph_vals = np.arange(4,12.1,0.1)
# grad_vals = np.arange(0.0, 0.25, 0.03)
# df = pd.DataFrame.from_records(data=[p for p in product(mph_vals, grad_vals)], columns=["speed", "gradient"])
# # calculate for me and my bike
# df['W/kg'] = [Wperkg(63.5, 8.0, a.speed, a.gradient) for a in df.itertuples()]
# sns.lineplot(x='speed', y='W/kg', data=df, hue='gradient', palette=sns.cubehelix_palette(len(grad_vals), start=0, rot=.5))

# plus some plot formatting stuff
# 
#def calc_speed(watts_per_kg, grad, body_mass, bike_mass, CdA=0.45, Crr=0.00483, rho=air_density(500), L_dt=0.051):
#changed to lower rolling resistance




#def calc_speed(watts_per_kg, grad, body_mass, bike_mass, CdA=0.45, Crr=0.004, rho=air_density(1500), L_dt=0.051):
#def calc_speed(watts_per_kg, grad, body_mass, bike_mass, rho=air_density(500), CdA=0.45, Crr=0.004, L_dt=0.051):
def calc_speed(watts_per_kg, grad, body_mass, bike_mass, rho, CdA=0.45, Crr=0.004, L_dt=0.051):
    total_mass = body_mass + bike_mass
    a3 = 0.5*CdA*rho
    a1 = F_roll(grad, total_mass, Crr) + F_grav(grad, total_mass)
    a0 = -1.0 * watts_per_kg*body_mass * (1.0-L_dt)
    rts = np.roots([a3, 0, a1, a0])
    # one should be real, return that one
    return [r.real*2.237 for r in rts if r.imag==0][0] #2.237 changes m/s to mph

    #P_vals = np.arange(1.0,22.1,3.0)
    #grad_vals = np.arange(0.0,0.252,0.002)
    #df = pd.DataFrame.from_records(data=[p for p in product(P_vals, grad_vals)], columns=["W/kg", "gradient"])
    #df['mph'] = [calc_speed(a[1], a.gradient, 63.5, 8.0) for a in df.itertuples()]
    #print(df['mph'])

def main():
    altitude_m = 1500
    bodyWeightLb = 197
    bikeWeightLb = 15
    body_mass = bodyWeightLb / 2.2
    bike_mass = bikeWeightLb / 2.2
    powerW = 172
    watts_per_kg = powerW / body_mass
    print(f'{os.path.basename(__file__)} has no main code, only functions.')


    #print(calc_speed(watts_per_kg, 0, body_mass, bike_mass, air_density(altitude_m)))
    # calc_speed(watts_per_kg, 0, body_mass, bike_mass, air_density(altitude_m))
    # sns.lineplot(x='gradient', y='mph', data=df, hue='W/kg', palette=sns.cubehelix_palette(len(P_vals), start=0.2, rot=1.0))

    # plus some more beautification    

if __name__ == '__main__':
    main()