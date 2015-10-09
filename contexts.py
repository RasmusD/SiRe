import context_skeletons, phone_features, copy
from context_utils import strintify
from context_utils import strfloatify
from context_utils import to_relational

#This contains the methods for creating a variety of context types from an utterance.

def Relational(phoneme):
  """Creates a relational context string of the given phoneme."""
  c = context_skeletons.Relational()
  add_relational(c, phoneme)
  return c

def RelationalStanford(phoneme):
  """An extension of the relational base set including information from a stanford parsing of the sentence."""
  c = context_skeletons.RelationalStanford()
  add_relational(c, phoneme)
  add_stanford(c, phoneme)
  return c

def add_relational(context_skeleton, phoneme):
  """Adds the relational context set to a context skeleton. If the skeleton does not support the set this will fail."""
  utt = phoneme.parent_utt
  c = context_skeleton
  syll = phoneme.parent_syllable
  word = phoneme.parent_word
  ##### Timings #####
  ##We must use the add method to ensure that the context skeleton already contains this context.
  c.add("start", str(phoneme.start))
  c.add("end", str(phoneme.end))
  ##### Phoneme level features #####
  #print "Adding phoneme level features to {0} in {1}".format(phoneme.id, phoneme.parent_utt.id)
  p_pos_in_utt = phoneme.pos_in_utt()
  p_pos_in_word = phoneme.pos_in_word()
  p_pos_in_syllable = phoneme.pos_in_syllable()
  #Left left phoneme
  if p_pos_in_utt > 1:
    llp = utt.phonemes[p_pos_in_utt - 2].id
  else:
    llp = "xx"
  c.add("llp", llp)
  #Left phoneme
  if p_pos_in_utt > 0:
    lp = utt.phonemes[p_pos_in_utt - 1].id
  else:
    lp = "xx"
  c.add("lp", lp)
  #Current phoneme
  c.add("cp", phoneme.id)
  #Right phoneme
  #Minus one as the pos_in_utt starts at 0
  diff = len(utt.phonemes) - p_pos_in_utt - 1
  if diff > 0:
    rp = utt.phonemes[p_pos_in_utt + 1].id
  else:
    rp = "xx"
  c.add("rp", rp)
  #Right right phoneme
  if diff > 1:
    rrp = utt.phonemes[p_pos_in_utt + 2].id
  else:
    rrp = "xx"
  c.add("rrp", rrp)
  #Add phoneme syll and word pos
  if phoneme.id in phone_features.get_sil_phonemes():
    #Phone forward pos in syll
    c.add("pfwsp", str(0.0))
    #Phone backward pos in syll
    c.add("pbwsp", str(0.0))
    #Phone forward pos in word
    c.add("pfwwp", str(0.0))
    #Phone backward pos in word
    c.add("pbwwp", str(0.0))
  else:
    #Phone forward pos in syll
    s_n_p = syll.num_phonemes()
    c.add("pfwsp", str(to_relational(p_pos_in_syllable, s_n_p - 1, True)))
    #Phone backward pos in syll
    c.add("pbwsp", str(to_relational(p_pos_in_syllable, s_n_p - 1, False)))
    #Phone forward pos in word
    w_n_p = word.num_phonemes()
    c.add("pfwwp", str(to_relational(p_pos_in_word, w_n_p - 1, True)))
    #Phone backward pos in word
    c.add("pbwwp", str(to_relational(p_pos_in_word, w_n_p - 1, False)))
  #Left phoneme stress
  #if lp != "xx":
  #  c.add("lps", str(utt.phonemes[p_pos_in_utt - 1].stress))
  #else:
  #  c.add("lps", "xx")
  #Current phoneme stress
  #c.add("cps", str(phoneme.stress))
  #Right phoneme stress
  #if rp != "xx":
  #  c.add("rps", str(utt.phonemes[p_pos_in_utt + 1].stress))
  #else:
  #  c.add("rps", "xx")
  #Phonemes to next stressed phoneme
  #i = p_pos_in_utt + 1
  #pnsp = "xx"
  #while i < len(utt.phonemes):
  #  if utt.phonemes[i].stress not in ["xx", 0]:
  #    pnsp = str(i - p_pos_in_utt)
  #    break
  #  else:
  #    i += 1
  #c.add("pnsp", pnsp)
  #Phonemes from previous stressed phoneme
  #i = p_pos_in_utt - 1
  #ppsp = "xx"
  #while i > 0:
  #  if utt.phonemes[i].stress not in ["xx", 0]:
  #    ppsp = str(p_pos_in_utt - i)
  #    break
  #  else:
  #    i -= 1
  #c.add("ppsp", ppsp)
  #Phoneme features
  lpf = phone_features.get_phoneme_feats_dict(lp)
  cpf = phone_features.get_phoneme_feats_dict(phoneme.id)
  rpf = phone_features.get_phoneme_feats_dict(rp)
  for feat in phone_features.get_feature_lists():
    #Left phoneme feats
    c.add("lp"+feat, lpf[feat])
    #Current phoneme feats
    c.add("cp"+feat, cpf[feat])
    #Right phoneme feats
    c.add("rp"+feat, rpf[feat])
  
  ##### Syllable level features #####
  #print "Adding syllable level features to {0} in {1}".format(phoneme.id, phoneme.parent_utt.id)
  s_pos_in_utt = syll.pos_in_utt()
  s_pos_in_word = syll.pos_in_word()
  if s_pos_in_utt > 0:
    ls = utt.syllables[s_pos_in_utt - 1]
  else:
    ls = "xx"
  #Minus 1 as pos_in_utt starts at 0
  diff = utt.num_syllables() - s_pos_in_utt - 1
  if diff > 0:
    rs = utt.syllables[s_pos_in_utt + 1]
  else:
    rs = "xx"
  #L Syllable stress
  if ls != "xx":
    c.add("lss", str(ls.stress))
  else:
    c.add("lss", "xx")
  #C Syllable stress
  if syll.stress == "xx":
    print "Warning! Current syllable stress is xx!"
    print "Should only happen when converting hts labs"
    print "Changing to 0 and continuing."
    c.add("css", "0")
  else:
    c.add("css", str(syll.stress))
  #R Syllable stress
  if rs != "xx":
    c.add("rss", str(rs.stress))
  else:
    c.add("rss", "xx")
  #Syllables to next stressed syllable
  i = s_pos_in_utt + 1
  snss = "xx"
  while i < utt.num_syllables():
    if utt.syllables[i].stress not in ["xx", 0]:
      snss = str(i - s_pos_in_utt)
      break
    else:
      i += 1
  c.add("snss", snss)
  #Syllables from previous stressed syllable
  i = s_pos_in_utt - 1
  spss = "xx"
  while i > 0:
    if utt.syllables[i].stress not in ["xx", 0]:
      spss = str(s_pos_in_utt - i)
      break
    else:
      i -= 1
  c.add("spss", spss)
  #L Syllable number of phonemes
  if ls != "xx":
    c.add("lsnp", str(ls.num_phonemes()))
  else:
    c.add("lsnp", "xx")
  #C Syllable number of phonemes
  c.add("csnp", str(syll.num_phonemes()))
  #R Syllable number of phonemes
  if rs != "xx":
    c.add("rsnp", str(rs.num_phonemes()))
  else:
    c.add("rsnp", "xx")
  
  #If this is a silence segment we have no relational pos.
  if phoneme.id in phone_features.get_sil_phonemes():
    #Syllable forward pos in word
    c.add("sfwwp", str(0.0))
    #Syllable backward pos in word
    c.add("sbwwp", str(0.0))
  else:
    #Syllable forward pos in word
    w_n_s = syll.parent_word.num_syllables()
    c.add("sfwwp", str(to_relational(s_pos_in_word, w_n_s - 1, True)))
    #Syllable backward pos in word
    c.add("sbwwp", str(to_relational(s_pos_in_word, w_n_s - 1, False)))
  #Syll vowel id
  c.add("svid", syll.vowel_id)
  #Syll Vowel Feats
  v_dct = phone_features.get_phoneme_feats_dict(syll.vowel_id)
  for feat in phone_features.get_feature_lists():
    c.add("sv"+feat, v_dct[feat])
  
  ##### Word level features #####
  #print "Adding word level features to {0} in {1}".format(phoneme.id, phoneme.parent_utt.id)
  w_pos_in_utt = word.pos_in_utt()
  #Word number of phonemes
  c.add("wnp", str(word.num_phonemes()))
  #Word number of syllables
  c.add("wns", str(word.num_syllables()))
  #Word forward pos in utterance
  u_n_w = word.parent_utt.num_words()
  c.add("wfwup", str(to_relational(w_pos_in_utt, u_n_w - 1, True)))
  #Word forward pos in utterance
  c.add("wbwup", str(to_relational(w_pos_in_utt, u_n_w - 1, False)))
  
  ##### Utterance level features #####
  #Phonemes in utterance
  c.add("unp", str(utt.num_phonemes()))
  #Syllables in utterance
  c.add("uns", str(utt.num_syllables()))
  #Words in utterance
  c.add("unw", str(utt.num_words()))
  
  ##### Experimental! #####
  #Just adding this manually
  #c.add("ut", "spont")

def add_stanford(context_skeleton, phoneme):
  """Adds stanford parse information to a phoneme context."""
  c = context_skeleton
  ###### Stanford Parse Information ######
  #Part of speech of word
  w = phoneme.parent_word
  w_pos_in_utt = w.pos_in_utt()
  if w_pos_in_utt > 0:
    lw = w.parent_utt.words[w_pos_in_utt - 1]
  else:
    lw = "xx"
  diff = w.parent_utt.num_words() - 1 - w_pos_in_utt
  if diff > 0:
    rw = w.parent_utt.words[w_pos_in_utt + 1]
  else:
    rw = "xx"
  if lw == "xx":
    c.add("lwpos", "xx")
  else:
    c.add("lwpos", lw.pos)
  c.add("cwpos", w.pos)
  if rw == "xx":
    c.add("rwpos", "xx")
  else:
    c.add("rwpos", rw.pos)
  #Word parent phrase
  c.add("wpp", w.parent_phrase.label)
  #Word grandpparent phrase
  c.add("wgpp", w.grandparent_phrase.label)
  #Word greatgrandparent phrase
  c.add("wggpp", w.greatgrandparent_phrase.label)
  #Word relational position in parent phrase
  c.add("wfwrppp", str(to_relational(w.parent_phrase.pos_in_parent, w.parent_phrase.num_siblings, True, True)))
  c.add("wbwrppp", str(to_relational(w.parent_phrase.pos_in_parent, w.parent_phrase.num_siblings, False, True)))
  #Word relational position in grandparent phrase
  c.add("wfwrgppp", str(to_relational(w.grandparent_phrase.pos_in_parent, w.grandparent_phrase.num_siblings, True, True)))
  c.add("wbwrgppp", str(to_relational(w.grandparent_phrase.pos_in_parent, w.grandparent_phrase.num_siblings, False, True)))
  #Word relational position in greatgrandparent phrase
  c.add("wfwrggppp", str(to_relational(w.greatgrandparent_phrase.pos_in_parent, w.greatgrandparent_phrase.num_siblings, True, True)))
  c.add("wbwrggppp", str(to_relational(w.greatgrandparent_phrase.pos_in_parent, w.greatgrandparent_phrase.num_siblings, False, True)))

#Returns a question set and a GV/utt question set.
#context_skeleton = The type of question set to output.
#qformat = Return the set in HMM format ("HMM") or Neural Network format ("NN").
#fit_contexts = If False creates generic question set, if True creates
#               question set adapted to contexts passed to contexts_to_fit.
#contexts_to_fit = The set of contexts to produce a fitted question set to.
def get_question_sets(context_skeleton, qformat, fit_contexts=False, contexts_to_fit=None, HHEd_fix=False):
  #Should be unnecessary due to argparse, but just to be sure.
  if qformat not in ["NN", "HMM"]:
    print "Error: Invalid question format! " + qformat
    print "Must be either HMM or NN!"
    sys.exit()
  c = context_skeleton
  c_utt = copy.deepcopy(context_skeleton)
  questions = []
  if fit_contexts == True:
    #First we obtain a dict containing a list of all used values for each context feature.
    for context in contexts_to_fit:
      for key in context.added_contexts:
        c.add_multiple(key, context.added_contexts[key])
        #Check if this should be in the GV context set
        if getattr(c, key) and "utt" in getattr(c, key):
          c_utt.add_multiple(key, context.added_contexts[key])
    #Then we create questions based on these
    qs = make_questions(c, qformat, False, HHEd_fix)
    q_utt = make_questions(c_utt, qformat, False, HHEd_fix)
    return (qs, q_utt)
  else:
    print "Error: Not Implemented yet! (Not fitting contexts for question set.)"
    sys.exit()

#Returns a list of questions for the appropriate feature.
#If generic is True outputs a generic set which may or may not cover your dataset.
#If generic is False it only output questions fitting the values in the
#added_contexts dict (do remember to add_multiple these from your dataset first).
#qformat = Return the questions in HMM format ("HMM") or Neural Network format ("NN").
#generic = Return a generic question set not fitted to the data.
#HHEd_fix = Make current phoneme context -phoneme+ as this is hardcoded in HHEd.
def make_questions(context_skeleton, qformat, generic=True, HHEd_fix=False):
  context_dict = context_skeleton.added_contexts
  if qformat not in ["NN", "HMM"]:
    print "Error: Invalid question format! " + qformat
    print "Must be either HMM or NN!"
    sys.exit()
  questions = []
  if generic == False:
    for key in context_dict:
      qtype = getattr(context_skeleton, key)
      #Setting it removes duplicates and sorting them is important for HMM question creation
      #(sorting them is also prettier for the NN)
      vals = list(set(context_dict[key]))
      vals.sort()
      if qtype == None:
        pass
      elif qtype == "bool":
        for val in vals:
          #If this is current phoneme id we apply the HHEd_fix
          if HHEd_fix == True and key == "cp":
            val = "-"+str(val)+"+"
          if qformat == "HMM":
            questions.append("QS \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
          elif qformat == "NN":
            questions.append("LQ 0 \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
      elif "float" in qtype:
        if qformat == "HMM":
          questions += make_hmm_relational_qs(vals, key, qtype)
        elif qformat == "NN":
          for val in vals:
            #HHEd's pattern matching for both NN and HMM's uses '.' as a special
            #character. We therefore use the int version of the float value in the
            #search pattern. But we have to check for xx first.
            if val == "xx":
              questions.append("LQ 1 0.0 \""+key+"-xx\" {*|"+key+":xx|*}")
            else:
              questions.append("LQ 1 "+str(val)+" \""+key+"-"+strintify(val)+"\" {*|"+key+":"+strintify(val)+"|*}")
      elif "int" in qtype:
          if qformat == "HMM":
            questions += make_hmm_relational_qs(vals, key, qtype)
          elif qformat == "NN":
            for val in vals:
              #The NN relies on floats for the actual value so we use that there
              #and the int in the naming. But we have to check for xx first.
              if val == "xx":
                questions.append("LQ 1 0.0 \""+key+"-xx\" {*|"+key+":xx|*}")
              else:
                questions.append("LQ 1 "+strfloatify(val)+" \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
      else:
        print "Error: Odd question type, should not exist - "+qtype
        sys.exit()
  else:
    print "Error: Not implemented yet! (Outputting generic question set)"
  return questions

#This assumes that values are already sorted in ascending order!
def make_hmm_relational_qs(values, key, qtype):
  questions = []
  #Add xx question if appropriate else ignore
  if "xx" in values:
    if "xx" in qtype:
      questions.append("QS \""+key+"-xx\" {*|"+key+":xx|*}")
    else:
      print "Error: xx in values but not in qtype {0} for key {1} - why?".format(qtype,key)
      sys.exit()
    values.remove("xx")
  for i, val in enumerate(values):
    if "float" in qtype:
      val = strintify(val)
    questions.append("QS \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
    #If val is more than one we make a less than question
    #If we count 0 then we start at 0
    if "0" in qtype:
      start = 0
    else:
      start = 1
    if int(val) > start:
      #Prep the less than string
      s = "QS \""+key+"<="+str(val)+"\" {"
      #Make the less than string
      #Get tens and remainder
      tens = int(val)/10
      remainder = int(val)%10
      if tens > 0:
        #Make singles
        for n in range(start, 10):
          s += "*|"+key+":"+str(n)+"|*,"
        #Make tens
        for n in range(1, tens):
          s += "*|"+key+":"+str(n)+"?|*,"
        for n in range(remainder+1):
          if n != remainder:
            s += "*|"+key+":"+str(tens)+str(n)+"|*,"
          else:
            s += "*|"+key+":"+str(tens)+str(n)+"|*}"
            questions.append(s)
      else:
        #Just make singles
        for n in range(start, int(val)+1):
          s += "*|"+key+":"+str(n)+"|*"
          if n != int(val):
            s += ","
          else:
            s += "}"
            questions.append(s)
  return questions
