import numpy as np

import metadata as md

# Change tracking information
def changeCenterPositionSensor(tracking, pos_x, pos_y, array_pad=False):

    tracking["X"] = np.multiply(tracking["X"], 0.001) - pos_x
    tracking["Y"] = np.multiply(tracking["Y"], 0.001) - pos_y

    if array_pad:
        
        # Rotation for W4-S204_6e14
        tan_theta = 0.15/1.75

        if md.getNameOfSensor("chan5") == "W4-S215":
        
            tan_theta = 4./300
    
        cos_theta = np.sqrt(1./(1+np.power(tan_theta, 2)))
        sin_theta = np.sqrt(1-np.power(cos_theta, 2))

        # Use the rotation matrix around z
        tracking["X"] = np.multiply(tracking["X"], cos_theta) - np.multiply(tracking["Y"], sin_theta)
        tracking["Y"] = np.multiply(tracking["X"], sin_theta) + np.multiply(tracking["Y"], cos_theta)


    return tracking


