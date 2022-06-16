from __future__ import print_function
import numpy as np
from math import floor, ceil

from objc_util import *
from ctypes import *

from time import perf_counter as get_time
from time import sleep
from math import log


# F_k(n) = F_k(n-1)*e^(2*pi*i*k/N)+x(n)-x(n-N)


Hz = 60
SR = 32


period = 1/SR

FFTSIZE = 3

FFTSIZE = 2**FFTSIZE

bandW = SR/FFTSIZE
bands = FFTSIZE/2+1

band_mid = Hz/bandW
band_low = int(floor(band_mid))
band_high = int(ceil(band_mid))

low_frac = band_mid - band_low
high_frac = band_high - band_mid

print('band(s)', band_low, band_high)

if low_frac + high_frac < 0.999:
    low_frac = 0.5
    high_frac = 0.5

while band_high >= bands:
    band_high -= bands
    band_low -= bands

#print('freq =',str(band*bandW))

chunk = np.zeros((FFTSIZE, 3), dtype=complex)

WIN = np.hanning(FFTSIZE)
WIN = np.repeat(WIN, 3).reshape((FFTSIZE, 3))


CMMotionManager = ObjCClass('CMMotionManager')

class MM:
    def __init__(self):
        self.obj = CMMotionManager.alloc().init()
    
    def __enter__(self):
        return self.obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.obj.release()
        self.obj.dealloc()


with MM() as manager:
    manager.setDeviceMotionUpdateInterval_(period)
    
    
    print(1/manager.deviceMotionUpdateInterval())
    
    print('initialising...')
    manager.startDeviceMotionUpdatesUsingReferenceFrame(4)

    sleep(1)
    while not manager.deviceMotion().magneticField().b.a > 0:
        pass
    print('ready')
    
    i = 0
    t0 = get_time()
    
    av = 0
    
    old = 0
    
    while True:
        #sens = manager.magnetometerData().magneticField()
        sens = manager.deviceMotion().magneticField().a
        chunk[i,0] = sens.a
        chunk[i,1] = sens.b
        chunk[i,2] = sens.c
        if abs(old - sens.a) < 0.0000001:
            print('duplicate')
        old = sens.a
        i += 1
        while get_time() - t0 < i/SR:
            pass
        i %= FFTSIZE
        if i == 0:
            t0 = get_time()
            i = 0
            freq = np.fft.rfft(chunk * WIN, axis=0) / (FFTSIZE)**0.5
            freq_band_low = np.absolute(freq[band_low,:])
            freq_band_high = np.absolute(freq[band_high,:])
            norm_low = np.inner(freq_band_low, freq_band_low)
            norm_high = np.inner(freq_band_high, freq_band_high)
            
            #se = np.inner(freq, freq)
            #ac = np.fft.ifft(se)
            v = norm_low*low_frac + norm_high*high_frac
            #if av == 0:
            #    av = v
            #av = v/4 + 3*av/4
            print(v)
    manager.stopDeviceMotionUpdates()
