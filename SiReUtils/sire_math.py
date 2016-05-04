##########################################################################
#Copyright 2016 Rasmus Dall                                              #
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

#Some simple mathematical functions. A surrogate for importing non-standard libraries like numpy.

#Load the SiReImports.pth file
import site
site.addsitedir(".")

import math
from error_messages import SiReError

#Returns the floating point mean of a list of values, if total or n is not given they are calculated from the list.
#If total and mean are both given the input list is ignored (but why are you calling this function then?)
#Total and n are options simply to reduce computation if you've already calculated them earlier.
def mean(ls, total=None, n=None):
  if total == None:
    total = math.fsum(ls)
  else:
    #Float to be sure it is a float
    total = float(total)
  if n == None:
    n = len(ls)
  else:
    #To ensure n is an int (or can be intified) and fail if impossible
    n = int(n)
  if n == 0:
    return 0
  return total/n

#Returns the mean ignoring 0
def mean_no_zero(ls):
  new_ls = [x for x in ls if int(x) > 0]
  return mean(new_ls)

#Gets the central element of a list of values after ordering them.
#I.e. the median.
def median(ls):
  ls = sorted(ls)
  return ls[len(ls)/2]

#Gets the central element of a list of values after ordering themand ignoring zeroes.
def median_no_zero(ls):
  new_ls = [x for x in ls if int(x) > 0]
  return median(new_ls)

#Finds the variance of a list of values.
#Any mean can be prespecified.
def variance(ls, m=None, n=None):
  if n == None:
    n = len(ls)
  else:
    #Check n is an int (or can be intified) and fail if impossible
    n = int(n)
  if m == None:
    m = mean(ls, None, n)
  else:
    #Check that this is a value
    m = float(m)
  sumsq = 0
  for val in ls:
    sumsq += math.pow(val-m, 2)
  return float(sumsq)/(n-1)

#Finds the standard deviation of a list of values.
#Any of mean and variance can be prespecified.
def std_dev(ls, m=None, var=None):
  if m == None:
    m = mean(ls)
  else:
    #Check this is a value
    m = float(m)
  if var == None:
    var = variance(ls, m)
  else:
    #Check this is a value
    var = float(var)
  return math.sqrt(var)

#Returns the frame number from an HTK nano second number
def get_frame(num, frameshift=5):
  return int(num)/10000/frameshift
