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

#This contains a number of things for investigating a TTS corpus. E.g. a count for the number of triphoneme types in the corpus.

#Load the SiReImports.pth file
import site
site.addsitedir(".")

import argparse, dictionary, utterance, sire_io, sire_math, os, math, phoneme_features

from error_messages import SiReError
from check_dictionary import get_oov_words
from sire_io import open_writefile_safe
from sire_io import load_txt_dir

def get_utts(txt, args):
  print "Making utts..."
  utts = []
  for t in txt:
    utts.append(utterance.Utterance(t, args))
  print "Done"
  return utts

def get_text_utts(indir, compilexpath):
  txt = load_txt_dir(indir)
  
  dct = dictionary.Dictionary(compilexpath)
  
  oov = get_oov_words(txt, dct)
  
  if len(oov) != 0:
    print "Please remove all OOV word containing sents or add the words to dictonary before proceeding."
    for w in oov:
      print w
    raise SiReError("OOV words present, cannot continue.")
  
  args.dictionary = dct
  args.intype = "txt"
  utts = get_utts(txt, args)
  return utts

def get_sire_utts(labdir, context_type, hhed_fix, durlab=False):
  labs = sire_io.open_labdir_line_by_line(labdir, dur_lab=durlab)
  quinphone = []
  phone = []
  triphone = []
  args.intype = "sire_lab"
  args.context_type = context_type
  args.HHEd_fix = hhed_fix
  #args.dictionary = dictionary.Dictionary(dictionarypath)
  args.phoneme_features = phoneme_features.CombilexPhonemes()
  #As we do not require the input text to analyse from a sire_lab we need to disable the festival features
  args.festival_features = False
  utts = get_utts(labs, args)
  return utts

#Analysis a list of phones with some standard measurements
def list_analysis(pls, name, f0, words=False):
  outstr = "\nStarting {0} analysis...\n".format(name)
  outstr += "Number of {0}\n".format(name)
  num_phones = len(pls)
  outstr += str(num_phones)+"\n"
  outstr += "Total duration of {0} (s)\n".format(name)
  durs = [x.get_duration()/10000 for x in pls]
  pdur = sum(durs)
  outstr += str(pdur/1000)+"\n"
  outstr += "Total duration of {0} (min)\n".format(name)
  outstr += str(pdur/1000/60)+"\n"
  outstr += "Mean {0} duration in corpus (ms)\n".format(name)
  pmean = sire_math.mean(durs, pdur)
  outstr += str(pmean)+"\n"
  outstr += "Median {0} duration in corpus (ms)\n".format(name)
  pmedian = sire_math.median(durs)
  outstr += str(pmedian)+"\n"
  outstr += "{0} duration variance in corpus (ms)\n".format(name)
  pvar = sire_math.variance(durs, m=pmean)
  outstr += str(pvar)+"\n"
  outstr += "{0} duration std dev in corpus (ms)\n".format(name)
  outstr += str(sire_math.std_dev(durs, m=pmean, var=pvar))+"\n"
  if f0 == True:
    p_f0 = []
    for p in pls:
      if words == True:
        for phon in p.phonemes:
          p_f0 += phon.f0
      else:
        p_f0 += p.f0
    p_f0 = sorted([x for x in p_f0 if 360 > x > 60])
    outstr += "Mean {0} f0\n".format(name)
    f0m = sire_math.mean_no_zero(p_f0)
    outstr += str(f0m)+"\n"
    outstr += "Min {0} f0\n".format(name)
    outstr += str(p_f0[0])+"\n"
    outstr += "Max {0} f0\n".format(name)
    outstr += str(p_f0[-1])+"\n"
    outstr += "Median {0} f0\n".format(name)
    outstr += str(sire_math.median_no_zero(p_f0))+"\n"
    outstr += "{0} f0 variance\n".format(name)
    f0var = sire_math.variance(p_f0, m=f0m)
    outstr += str(f0var)+"\n"
    outstr += "{0} f0 std dev\n".format(name)
    outstr += str(sire_math.std_dev(durs, m=f0m, var=f0var))+"\n"
  
  return outstr

def do_analysis(utts, plots=False, f0=False):
  p_feats = phoneme_features.CombilexPhonemes()
  outstr = ""
  #Phone numbers
  quinphone = []
  phone = []
  triphone = []
  n_words = 0
  sil_phones = []
  consonants = []
  vowels = []
  #For disfluencies
  uh_words = []
  uh_l_sylls = []
  uh_r_sylls = []
  um_words = []
  um_l_sylls = []
  um_r_sylls = []
  for utt in utts:
    n_words += utt.num_words_no_pau()
    #Phone level information
    for p in utt.phonemes:
      llp = p.get_left_left_phoneme().id
      lp = p.get_left_phoneme().id
      cp = p.id
      rp = p.get_right_phoneme().id
      rrp = p.get_righ_right_phoneme().id
      quinphone.append((llp, lp, cp, rp, rrp))
      triphone.append((lp, cp, rp))
      phone.append(p)
      if p_feats.is_vowel(p.id):
        vowels.append(p)
      elif p_feats.is_consonant(p.id):
        consonants.append(p)
      else:
        sil_phones.append(p)
    #Word level information
    for word in utt.words:
#      if word.id == "V":
      if word.id == "UH":
#      if word.id == "@":
        uh_words.append(word)
        l_syll = word.phonemes[0].parent_syllable.get_left_syllable()
        if l_syll != "xx" and l_syll.vowel_id != "novowel":
          for p in l_syll.phonemes:
            if p.id == l_syll.vowel_id:
              uh_l_sylls.append(p)
              break
        r_syll = word.phonemes[0].parent_syllable.get_right_syllable()
        if r_syll != "xx" and r_syll.vowel_id != "novowel":
          for p in r_syll.phonemes:
            if p.id == r_syll.vowel_id:
              uh_r_sylls.append(p)
              break
#      if word.id == "Vm":
      if word.id == "UHm":
#      if word.id == "@m":
        um_words.append(word)
        l_syll = word.phonemes[0].parent_syllable.get_left_syllable()
        if l_syll != "xx" and l_syll.vowel_id != "novowel":
          for p in l_syll.phonemes:
            if p.id == l_syll.vowel_id:
              um_l_sylls.append(p)
              break
        r_syll = word.phonemes[0].parent_syllable.get_right_syllable()
        if r_syll != "xx" and r_syll.vowel_id != "novowel":
          for p in r_syll.phonemes:
            if p.id == r_syll.vowel_id:
              um_r_sylls.append(p)
              break
  
  outstr = "\nCorpora details\n\n"
  
  outstr += "Number of words:\n"
  outstr += str(n_words)+"\n\n"
  
  quinphone = set(quinphone)
  triphone = set(triphone)
  outstr += "Number of phones\n"
  num_phones = len(phone)
  outstr += str(num_phones)+"\n"
  outstr += "number of unique quinphones\n"
  outstr += str(len(quinphone))+"\n"
  outstr += "Number of unique triphones\n"
  outstr += str(len(triphone))+"\n"
  outstr += "Silence Quinphone Types\n"
  outstr += str(len([x for x in quinphone if x[2] in ["pau", "sil"]]))+"\n"
  outstr += "Silence Triphones Types\n"
  outstr += str(len([x for x in triphone if x[1] in ["pau", "sil"]]))+"\n"

  outstr += list_analysis(phone, "phones", True)
  outstr += list_analysis(sil_phones, "silence", False)
  outstr += list_analysis(vowels, "vowels", True)
  outstr += list_analysis(consonants, "consonants", True)
#  outstr += list_analysis(uh_words, "uhs", True, True)
#  outstr += list_analysis(uh_l_sylls, "uh_left_sylls vowel", True)
#  outstr += list_analysis(uh_r_sylls, "uh_right_sylls vowel", True)
#  outstr += list_analysis(um_words, "ums", True, True)
#  outstr += list_analysis(um_l_sylls, "um_left_sylls vowel", True)
#  outstr += list_analysis(um_r_sylls, "um_right_sylls vowel", True)
  print outstr
  
  #Make some plots if true - note plots rely on matplotlib which is non-standard library.
  #See here http://matplotlib.org/users/installing.html for how to get it.
  if plots == True:
    from matplotlib import pyplot
    #Get it all to ms and remove some outliers
    uhdurs = [float(n)/10000 for n in uhdurs if 700 > float(n)/10000 > 10]
    pyplot.hist(uhdurs, bins=30)
    pyplot.show()
    #Get it all to ms
    umdurs = [float(n)/10000 for n in umdurs if 1000 > float(n)/10000 > 10]
    pyplot.hist(umdurs, bins=30)
    pyplot.show()
    #Phones
    totaldur = [float(n)/10000 for n in totaldur if 600 > float(n)/10000 > 10]
    pyplot.hist(totaldur, bins=30)
    pyplot.show()
    if f0 == True:
      #Get it all to ms
      pyplot.hist(uh_f0, bins=30)
      pyplot.show()
      #Get it all to ms
      pyplot.hist(um_f0, bins=30)
      pyplot.show()
      #Phones
      pyplot.hist(p_f0, bins=30)
      pyplot.show()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Checks a TTS corpora for various statistics.')
  parser.add_argument('-txt_analysis', nargs=2, help='Perform an analysis of a corpora from text files.', metavar=('INDIRPATH', 'COMBILEXPATH'))
  parser.add_argument('-lab_analysis', nargs=3, help='Perform an analysis based on SiRe style full context labels.', metavar=('LABDIRPATH', 'CONTEXTTYPE', 'HHEDFIX'))
  parser.add_argument('-durlab_analysis', nargs=3, help='Perform an analysis based on SiRe style HTS duration labels.', metavar=('LABDIRPATH', 'CONTEXTTYPE', 'HHEDFIX'))
  parser.add_argument('-plots', action='store_true', help='Make some plots as well. Requires matplotlib.')
  parser.add_argument('-lf0', nargs=1, help=('Do analysis of some f0 related things as well. This is converted to F0 with the assumption that the lf0 is in natural log.'), metavar=('LF0DIR'))
  parser.add_argument('-f0', nargs=1, help=('Do analysis of some f0 related things as well. This will take precedence over lf0 analysis.'), metavar=('F0DIR'))
  parser.add_argument('-outfile', type=str, help='The output filepath if stats should be written out.')
  args = parser.parse_args()
  
  utts = None
  
  if args.txt_analysis != None:
    utts = get_text_utts(args.txt_analysis[0], args.txt_analysis[1])
  
  if args.lab_analysis != None:
    utts = get_sire_utts(args.lab_analysis[0], args.lab_analysis[1], bool(args.lab_analysis[2]))
  
  if args.durlab_analysis != None:
    utts = get_sire_utts(args.durlab_analysis[0], args.durlab_analysis[1], bool(args.durlab_analysis[2]), durlab=True)
  
  if args.lf0 != None or args.f0 != None:
    if args.lab_analysis != None or args.durlab_analysis:
      f0 = {}
      if args.f0:
        for f0file in os.listdir(args.f0[0]):
          if ".f0" in f0file:
            f0[f0file[:-3]] = [float(x.strip()) for x in open(os.path.join(args.f0[0], f0file), "r").readlines()]
      elif args.lf0:
        for lf0file in os.listdir(args.lf0[0]):
          if ".lf0" in lf0file:
            f0[lf0file[:-4]] = [math.exp(float(x.strip())) for x in open(os.path.join(args.lf0[0], lf0file), "r").readlines()]
      #Add f0 to the utts
      print "Adding f0 to utts..."
      for utt in utts:
        if utt.id in f0:
          for phone in utt.phonemes:
            #Find the frames
            start = sire_math.get_frame(phone.start)
            end = sire_math.get_frame(phone.end)
            #Add it
            phone.f0 = f0[utt.id][start:end+1]
        else:
          raise SiReError("Don't have f0 for {0}!".format(utt.id))
      print "Done"
    else:
      raise SiReError("Cannot do f0 analysis without labs.")
  
  if utts != None:
    if args.lf0 != None or args.f0 != None:
      do_analysis(utts, args.plots, True)
    else:
      do_analysis(utts, args.plots)

