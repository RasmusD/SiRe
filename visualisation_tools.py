##########################################################################
#Copyright 2015 Rasmus Dall                                              #
#                                                                        #
#Licensed under the Apache License, Version 2.0 (the "License");         #
#you may not use this file except in compliance with the License.        #
#You may obtain a copy of the License at                                 #
#                                                                        #
#http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                        #
#Unless required by applicable law or agreed to in writing, software     #
#distributed under the License is distributed on an "AS IS" BASIS,       #
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
#See the License for the specific language governing permissions and     #
#limitations under the License.                                          #
##########################################################################

#A few simple pre-written methods for visualising wavs.
#NOTE: Requires matplotlib which is not a standard python module.
#See here http://matplotlib.org/users/installing.html for how to get it.

import wave, argparse, sys, math
from numpy import fromstring
from matplotlib import pyplot
from matplotlib import axes

def get_wav(wav_path):
  wav = wave.open(wav_path, "r")
  if wav.getnchannels() == 2:
    print "Can only handle mono files. {0} had {1} channels.".format(wav_path, wav.getnchannels())
    sys.exit()
  return wav

def plot_wav(wav_path):
  wav = get_wav(wav_path)
  nf = wav.getnframes()
  wav = fromstring(wav.readframes(-1), 'Int16')
  pyplot.figure(1)
  pyplot.title(wav_path)
  pyplot.plot(wav)
  pyplot.xlim(right=nf)
  pyplot.xlabel("Frames")
  pyplot.show()

def plot_spectogram(wav_path, f0=None):
  wav =get_wav(wav_path)
  fs = wav.getframerate()
  nf = wav.getnframes()
  ns = nf/float(fs)
  wav = fromstring(wav.readframes(-1), 'Int16')
  pyplot.figure(1)
  pyplot.title(wav_path)
  pyplot.specgram(wav, Fs=fs)
  pyplot.xlim(right=ns)
  pyplot.ylim(top=8000)
  pyplot.xlabel("Seconds")
  if f0:
    x_points = [(ns/len(f0))*x for x in range(1, len(f0)+1)]
    y_points = [x for x in f0]
    pyplot.plot(x_points, y_points)
  pyplot.show()

def plot_wav_and_spec(wav_path, f0):
  wav = get_wav(wav_path)
  fs = wav.getframerate()
  nf = wav.getnframes()
  ns = nf/float(fs)
  wav = fromstring(wav.readframes(-1), 'Int16')
  
  fig = pyplot.figure()
  pyplot.title(wav_path)
  w = pyplot.subplot(311)
  w.set_xlim(right=nf)
  w.plot(wav)
  pyplot.xlabel("Frames")
  s = pyplot.subplot(312)
  pyplot.specgram(wav, Fs=fs)
  s.set_xlim(right=ns)
  s.set_ylim(top=8000)
  if f0:
    f = pyplot.subplot(313)
    x_points = [(ns/len(f0))*x for x in range(1, len(f0)+1)]
    y_points = [x for x in f0]
    pyplot.plot(x_points, y_points)
    f.set_xlim(right=ns)
  pyplot.xlabel("Seconds")
  pyplot.show()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='A few simple methods for visualisation of wavs etc.')
  parser.add_argument('inwav', type=str, help="The input wavfile.")
  parser.add_argument('-plot_wav', action='store_true', help="Plot a waveform.")
  parser.add_argument('-plot_spec', action='store_true', help="Plot a spectogram.")
  parser.add_argument('-plot_wav_and_spec', action='store_true', help="Plot both a waveform and spectogram.")
  parser.add_argument('-add_f0', type=str, help="If specified the f0 at PATH will be plotted on any spectogram plotted. The f0 is assumed to be in 5ms frames.", metavar=("PATH"))
  parser.add_argument('-add_lf0', type=str, help="If specified the lf0 at PATH will be plotted on any spectogram plotted. The lf0 will be converted to f0 before plotting and is assumed to be in 5ms frames and using the natural log. If both add_f0 and add_lf0 is specified the f0 file takes precedence.", metavar=("PATH"))
  args = parser.parse_args()
  
  if args.add_f0:
    f0 = [float(x.strip()) for x in open(args.add_f0, "r").readlines()]
  elif args.add_lf0:
    f0 = [math.exp(float(x.strip())) for x in open(args.add_lf0, "r").readlines()]
  
  if args.plot_wav:
    plot_wav(args.inwav)
  if args.plot_spec:
    plot_spectogram(args.inwav, f0)
  if args.plot_wav_and_spec:
    plot_wav_and_spec(args.inwav, f0)
