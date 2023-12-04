#!/usr/bin/python3

import scipy.io.wavfile
from PIL import Image
from math import pi, sin
import numpy as np

# Robot B&W 12 160×120: 7.0ms sync (1200 Hz), then 93.0ms image (1500 Hz - black, 2300 Hz - white)
# 93 ms / 160 px = 0.58125 ms/px == ~1720 Hz sample rate, but we need up to 2300 Hz bandwidth
# 5161 Hz samplerate: 3 samples per pixel, freqs up to >2500 Hz (Nyquist limit)

px = Image.open("bw12.jpg").load() # load image
sr = 5161                         # sample rate, obviously
osc = 0     # angle of IQ oscillator, using angle only since ampl is const == 1
out = np.array([])   # empty array for storing the output
wave = []            # array for wav samples

for l in range(120): # for every line in image
    out = np.append(out, [1200] * round(sr*0.007)) # generate sync pulse - 1200 Hz for 7 ms
    
    for R, G, B in [px[x, l] for x in range(160)]:    # for every pixel
        inst_freq = 1500 + (((R+G+B)/3 * 800/255))    # convert average value of R,G,B into frequency
        out = np.append(out, [inst_freq]*3)           # and store it in output list (*3, because we use 3 samples per pixel)
    
for freq in out:
    osc = (osc + 2*freq*pi/sr) % (2*pi) # rotate the IQ oscillator
    wave.append(sin(osc)) # and store just "I" value in wav

scipy.io.wavfile.write("bw12.wav", sr, np.float32(wave)) # store wav
