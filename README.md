# Wave Detector

uses the device magnetometer sampled at a low framerate and some fancy maths to emulate a wire detector
the framerate it samples at is lower than twice the rate of a typical powerline frequency, so it relies of either subharmonics, or spectral leakage in the signal.

## usage
set the powerline frequency to the relevant value for your region (it doesn't seem to make much difference for coils)
observe: coils (such as the ones in speakers) make the reading go up, and hopefully induced magnetic fields from mains-carrying wires also cause a slight increase.
