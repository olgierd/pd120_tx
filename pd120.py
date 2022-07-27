#!/usr/bin/python3

import scipy.io.wavfile
from PIL import Image
from math import pi, sin
import numpy as np

"""
Only resources used when developing this code:
- https://www.sstv-handbook.com/download/sstv-handbook.pdf
- http://www.barberdsp.com/downloads/Dayton%20Paper.pdf
- https://www.classicsstv.com/pdmodes.php
"""

INPUT_JPG = "a.jpg"
OUTPUT_WAV = "out.wav"

# load image
im = Image.open(INPUT_JPG)
px = im.load()
w, h = im.size

# prepare oscillator
sr = 5263   # sample rate, 5263 because single pixel in PD120 should last for 0.19 ms == 1 sample @ 5263 Hz
q = pi/sr*2  # for conversion frequency -> radians/sample
osc = 0     # position (angle) of IQ oscillator, keeping angle only since ampl == const == 1

# container for the whole image
out = []

# for every other line
for l in range(0, h-1, 2):
    # PD-120 transmits ... two lines as a single line
    line = [px[x, l] for x in range(w)] # get all pixels in line l
    line1 = [px[x, l+1] for x in range(w)] # .. and l+1
    
    # generate sync pulse - 1200 Hz for 20 ms, and black stripe - 1500 Hz for 2.08 mS
    out += [1200] * round(sr*0.02) + [1500] * round(sr*0.00208)
    
    # generate line data, Y for line 0, average of R-Y and B-Y, Y for line 1 
    Y0, RY0, BY0, Y1 = [], [], [], []
    
    for R, G, B in line:  # RGB to YUV / YCbCr
        Y0.append(1500 + (16.0 + (.003906 * ((65.738 * R) + (129.057 * G) + (25.064 * B)))) * 3.1372549)
        RY0.append(1500 + (128.0 + (.003906 * ((112.439 * R) + (-94.154 * G) + (-18.285 * B)))) * 3.1372549)
        BY0.append(1500 + (128.0 + (.003906 * ((-37.945 * R) + (-74.494 * G) + (112.439 * B)))) * 3.1372549)

    for R, G, B in line1:
        Y1.append(1500 + (16.0 + (.003906 * ((65.738 * R) + (129.057 * G) + (25.064 * B)))) * 3.1372549)
    
    out += Y0+RY0+BY0+Y1
    
# container for audio samples
wave = []

# out contains frequencies per sample
for x in out:
    osc = (osc + x*q) % (2*pi) # rotate the IQ oscillator around 
    wave.append(sin(osc)) # and store just "I" value 

# save to wave
scipy.io.wavfile.write(OUTPUT_WAV, sr, np.float32(wave))