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

#Methods for converting labels from one format to another. The ones here are simply the ones that has been needed so far.
#Load the SiReImports.pth file
import site
site.addsitedir("../")

import argparse, sire_io, os
from error_messages import SiReError

def merge_hvite_state_align_and_full_context_lab(state_align_labs, full_context_labs):
  """
  Create a state-alignment based full-context label for use in e.g. Neural Network systems that rely on HMM state-alignments.
  Input:
    state_align_labs - Labels from an HVite alignment output at the state-level.
    full_context_labs - Labels from any full-context method on the phoneme level (any SiRe output contexts or standard HTS full-context labels)
  """
  if len(state_align_labs) != len(full_context_labs):
    raise SiReError("Number of align labs ({0}) not equal to the number of full context labs ({1})!".format(len(state_align_labs), len(full_context_labs)))
  
  #Prep out list
  merged = []
  
  #Sort them by name
  state_align_labs = sorted(state_align_labs, key=lambda name: name[0])
  full_context_labs = sorted(full_context_labs, key=lambda name: name[0])
  for i, lab in enumerate(state_align_labs):
    f_lab = full_context_labs[i]
    #Check we have the correct labels to merge
    if f_lab[0] != lab[0]:
      raise SiReError("The labels are not from the same files! State lab = {0}, context lab = {1}".format(lab[0], f_lab[0]))
    #Do the merging
    f_lab.pop(0)
    p = -1
    f_line = None
    c_merge = [lab.pop(0)]
    for l in lab:
      if len(l) == 7:
        p += 1
        f_line = f_lab[p][-1]
        c_merge.append([l[0], l[1], f_line+"["+l[2][-1]+"]", f_line])
      elif len(l) == 4:
        c_merge.append([l[0], l[1], f_line+"["+l[2][-1]+"]"])
      else:
        raise SiReError("Error in align lab line: {0}".format(l))
    merged.append(c_merge)
  return merged

def merge_hvite_state_with_sp_align_mlf(state_labs, phone_labs):
  """
  Create a state-alignment based mlf for use in e.g. Neural Network systems that rely on HMM state-alignments.
  Input:
    state_mlf - MLF from an HVite alignment output at the state-level not containing short pause (SP) and syllable stress/boundary markers.
    phone_mlf - MLF suitable as input for a HVite alignment at the phoneme level containing short pause (SP) and syllable stress/boundary markers. This is equivalent to the sp.mlf produced by make_lattices_and_mlfs.py.
  Output:
    merged_mlf - MLF in HVite state-level alignment format as if SP and syllable stress/boundary information had initially existed (given 0 duration).
  """
  if len(state_labs) != len(phone_labs):
    raise SiReError("Number of state align labs ({0}) not equal to the number of phone align labs ({1})!".format(len(state_labs), len(phone_labs)))
  
  #Sort them by name
  state_labs = sorted(state_labs, key=lambda name: name[0])
  phone_labs = sorted(phone_labs, key=lambda name: name[0])
  
  #Prep out list
  merged = []
  
  for i, s_lab in enumerate(state_labs):
    p_lab = phone_labs[i]
    #Check we have the correct labels to merge
    if s_lab[0] != p_lab[0]:
      raise SiReError("The labels are not from the same files! State lab = {0}, context lab = {1}".format(s_lab[0], p_lab[0]))
    #Do the merging
    s_lab.pop(0)
    s_lab_count = 0
    c_merge = [p_lab.pop(0)]
    for line in p_lab:
      c_p = []
      s_phone = s_lab[s_lab_count][0][-1]
      if line[-1] != s_phone:
        if line[-1] in ["#1", ".", "#2", "sp"]:
          c_p.append(["0", "0", "s2", "FAKE", line[-1], "FAKE", line[-1]])
          c_p.append(["0", "0", "s3"])
          c_p.append(["0", "0", "s4"])
          c_p.append(["0", "0", "s5"])
          c_p.append(["0", "0", "s6"])
          c_merge.append(c_p)
        else:
          print s_phone
          print line[-1]
          raise SiReError("Mismatch in phone content! Please check MLFs for lab {0}!".format(c_merge[0]))
      else:
        c_merge.append(s_lab[s_lab_count])
        s_lab_count += 1
    merged.append(c_merge)
  return merged

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Utility file convertion related methods.')
  parser.add_argument('-merge_hvite_state_with_full_context', nargs=3, help="Merge an HVite state level alignment MLF with full-context labels in a directory and output state-level full-context labels to another.", metavar=('mlf_path', 'lab_dir', 'out_dir'))
  parser.add_argument('-merge_hvite_state_with_sp_align_mlf', nargs=3, help="Merge an HVite state level alignment MLF which does not contain SP and syllable stress information with a phone level alignment ready mlf which does and output a state-level with SP and syllable stress.", metavar=('state_mlf_path', 'phone_mlf_path', 'out_mlf_path'))
  parser.add_argument('-collapse_closure', action="store_true", help="Collapses stops split into closure and release into one when merging state_align_labs with full_context_labs.")
  parser.add_argument('-f', action="store_true", help="Force overwrite of files in output dir.")
  args = parser.parse_args()
  
  if args.merge_hvite_state_with_sp_align_mlf != None:
    state_mlf = sire_io.open_file_line_by_line(args.merge_hvite_state_with_sp_align_mlf[0])
    phone_mlf = sire_io.open_file_line_by_line(args.merge_hvite_state_with_sp_align_mlf[1])
    state_utts = sire_io.parse_mlf(state_mlf, "state_align_mlf")
    phone_utts = sire_io.parse_mlf(phone_mlf, "hts_mlf")
    merged_utts = merge_hvite_state_with_sp_align_mlf(state_utts, phone_utts)
    if args.f == True:
      wf = sire_io.open_writefile_safe(args.merge_hvite_state_with_sp_align_mlf[2], overwrite=True)
    else:
      wf = sire_io.open_writefile_safe(args.merge_hvite_state_with_sp_align_mlf[2])
    wf.write("#!MLF!#\n")
    for utt in merged_utts:
      wf.write("\"*/"+utt.pop(0)+".rec\"\n")
      for phone in utt:
        for state in phone:
          wf.write(" ".join(state)+"\n")
      wf.write(".\n")
    wf.close()
  
  if args.merge_hvite_state_with_full_context != None:
    full_context_labs = sire_io.open_labdir_line_by_line(args.merge_hvite_state_with_full_context[1])
    mlf = sire_io.open_file_line_by_line(args.merge_hvite_state_with_full_context[0])
    state_labs = sire_io.parse_mlf(mlf, "align_mlf")
    if args.collapse_closure == True:
      for x, lab in enumerate(state_labs):
        for i, l in enumerate(lab):
          if '_cl' in l[-1]:
            if state_labs[x][i+3][-1]+'_cl' == l[-1]:
              state_labs[x][i+3] = lab[i+3][:4]
            else:
              raise SiReError("Something wrong with {0}".format(l))
    merged = merge_hvite_state_align_and_full_context_lab(state_labs, full_context_labs)
    outdirpath = args.merge_hvite_state_with_full_context[2]
    for lab in merged:
      filename = lab.pop(0)+".lab"
      print "Creating - "+os.path.join(outdirpath, filename)
      if args.f == True:
        wf = sire_io.open_writefile_safe(os.path.join(outdirpath, filename), overwrite=True)
      else:
        wf = sire_io.open_writefile_safe(os.path.join(outdirpath, filename))
      for l in lab:
        wf.write(" ".join(l)+"\n")
      wf.close()
