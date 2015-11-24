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

from error_messages import SiReError

#Return a float to two decimal places giving
#the relational position of pos given maximal pos.
#If fw is true the forward position is returned,
#else the backwards.
#The min it returns is 0.01 as 0.0 is reserved for
#segments not at all in utt.
#Note that min of pos is 0, i.e. we count from 0.
#Mpos must thus be the same, i.e. outputs of
#len() should proably be subtracted with 1
def to_relational(pos, mpos, fw, accept_xx=False):
  if accept_xx:
    if pos == "xx" or mpos == "xx":
      return 0.0
  if pos > mpos:
    raise SiReError("Position ({0}) is above max position ({1}). Should not happen!".format(pos, mpos))
  #To avoid dividing with 0
  if mpos == 0:
    #This is technically correct but we could consider using 0.01
    return 1.0
  if fw == True:
    p = 1 - round(float(pos)/float(mpos), 2)
    #0.0 is reserved for pause segments
    if p == 0.0:
      p = 0.01
    return p
  elif fw == False:
    p = round(float(pos)/float(mpos), 2)
    #0.0 is reserved for pause segments
    if p == 0.0:
      p = 0.01
    return p
  else:
    raise SiReError("FW/BW unspecified! Please use bool!")

def check_value(context_skeleton, variable_name, value):
  #Is the value of the correct type?
  attr = getattr(context_skeleton, variable_name)
  if attr == None:
    if variable_name in ["start", "end"]:
      try:
        int(value)
        return True
      except (ValueError, TypeError):
        pass
  elif "float" in attr:
    try:
      float(value)
      return True
    except ValueError:
      if "xx" in attr and value == "xx":
          return True
  elif attr == "bool":
    if isinstance(value, str):
      return True
  elif "int" in attr:
    try:
      int(value)
      return True
    except ValueError:
      if "xx" in attr and value == "xx":
        return True
  else:
    raise SiReError("Unknown attribute type ({0})!".format(attr))
  raise SiReError("Value ({0}) is not valid for variable type ({1}) variable ({2}) in \n {3}".format(value, attr, variable_name, context_skeleton))

#Return the string of the int of the float multiplied by 100.
def strintify(fl):
  #Just to make sure we deal with a float
  if type(fl) is not float:
    raise SiReError("Cannot strintify type {0}! Must be float!".format(type(fl)))
  #First remove any leftovers and make sure we don't just floor
  fl = round(fl, 2)
  #Do the multiplication. We round due to issues with float arithmetic.
  fl = round(fl * 100, 0)
  #Return the int string
  return str(int(fl))
  
#Return the string of the float of the int divided by 100 to two decimal places.
def strfloatify(fl):
  #Just to make sure we deal with a int
  if type(fl) is not int:
    raise SiReError("Cannot strintify type {0}! Must be int!".format(type(fl)))
  #First do the division
  fl = float(fl) / 100
  #Round
  fl = round(fl, 2)
  #Return the float string
  return str(fl)
