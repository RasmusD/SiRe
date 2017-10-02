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

#Methods for loading utterances
import utterance, utterance_utils, phoneme_features, parsetrees, os, dictionary
from error_messages import SiReError
import re

#Create a prototype utterance from a lab from an aligned mlf.
#Note this assumes the following:
#1. Stops are split into closure and release.
#   The closure is written as [stop]_cl and the release just as the stop.
#2. 'sil' is the first and last phoneme.
#3. 'sp' marks word boundaries and if time length is above 0 a between
#   word pause.
#4. '#1' precedes a primary stressed phoneme in a syll.
#   This tends to be a vowel and should have no duration (tee model).
#5. '#2' precedes a secondary stressed phoneme in a syll.
#   This tends to be a vowel and should have no duration (tee model).
#6. '.' marks intra-word syllable boundaries.
#   This should have no duration (tee model).
#7. Each line is one phoneme which can be split on whitespace and
#   [0] is the phoneme start time in HTK format where 10000 is 1ms.
#   [1] is the phoneme end time in HTK format where 10000 is 1ms.
#   [-1] is the phoneme id.
#   Anything in between is ignored.
def proto_from_align_lab(lab):
  proto = {}
  proto["id"] = lab[0]
  lab.pop(0)
  #We make a temporary utterance bottom up starting with
  #reforming phonemes split for alignment.
  proto["utt"] = remake_stops(lab)
  #Then make the phonemes with stress, start, end times.
  proto["utt"] = make_phonemes(proto["utt"])
  #Then syllables with start end times and stress.
  proto["utt"] = make_sylls(proto["utt"])
  #Then words with start and end times.
  proto["utt"] = make_words(proto["utt"])

  return proto

#This makes some assumptions about the lab format which is sampled below:
#0 50000 s2 -78.739014 # -2090.613281 #
#50000 200000 s3 -249.214050
#200000 250000 s4 -84.849785
#250000 300000 s5 -83.583138
#300000 1400000 s6 -1594.227295
#1400000 2200000 s2 -1361.197754 uh -1675.521729 uh
#2200000 2250000 s3 -85.047012
#2250000 2300000 s4 -75.808914
#2300000 2350000 s5 -74.904594
#2350000 2400000 s6 -78.563576
#I.e.:
#StateStart StateEnd State2 Prob Phone1 Prob Phone1
#StateStart StateEnd State3 Prob
#StateStart StateEnd State4 Prob
#StateStart StateEnd State5 Prob
#StateStart StateEnd State6 Prob
#StateStart StateEnd State2 Prob Phone2 Prob Phone2
#Etc.
def proto_from_state_align_lab(lab):
  proto = {}
  proto["id"] = lab[0]
  lab.pop(0)
  #We make a temporary utterance bottom up
  ###Note this is currently not done as it creates complications
  ###With the timings of each state. (phones tend not to be split in this case)
  #Then reforming phonemes split for alignment.
  #proto["utt"] = remake_stops(lab)
  #Then make the phonemes with stress, start, end times and state information.
  stress = 0
  for i, p in enumerate(lab):
    if p[0][-1] == "#1":
      stress = 1
      lab[i] = "out"
    elif p[0][-1] == "#2":
      stress = 2
      lab[i] = "out"
    else:
      lab[i] = {"stress":stress, "id":lab[i][0][-1], "start":int(lab[i][0][0]), "end":int(lab[i][-1][1]), "states":lab[i]}
      stress = 0
  while "out" in lab:
    lab.remove("out")
  proto["utt"] = lab
  #Then syllables with start end times and stress.
  proto["utt"] = make_sylls(proto["utt"])
  #Then words with start and end times.
  proto["utt"] = make_words(proto["utt"])

  return proto

#Create a prototype utterance from a SiRe label which has had at least the basic set of features added.
#Note that this will not load e.g. parsing information. Only the basic set is loaded from this and everything else must be added later!
#TODO - support the loading of other features, e.g. parsing from these labels.
def proto_from_sire_lab(lab, context_type, HHEd_fix):
  proto = {"utt":[]}
  proto["id"] = lab[0]
  lab.pop(0)
  c_word = {"id":"", "syllables":[]}
  c_syll = {"id":"", "phonemes":[], "stress":None}
  for i, line in enumerate(lab):
    c_phon = {"id":None, "stress":None, "start":None, "end":None}
    # Create phonemes
    if HHEd_fix == True:
      c_phon["id"] = line[-1].split("|cp:-")[1].split("+|rp:")[0]
    else:
      c_phon["id"] = line[-1].split("|cp:")[1].split("|rp:")[0]
    c_phon["start"] = line[0]
    c_phon["end"] = line[1]
    # SiRe labs do not currently contain stress information at the phoneme level as a standard
    # This could have been added if an alignment MLF containing this info was used originially
    c_phon["stress"] = None
    # Add phonemes to syll
    # If phonemes is beginning of syll prev syll is done
    #This depends on what type of positional context was used to create the labels
    beg_syll = False
    if context_type == "absolute":
      if line[-1].split("|pfwsp:")[1].split("|")[0] in ["0"]:
        beg_syll = True
    elif context_type == "relational":
      #0 should be used for silence positions in the relational case, with "100" for normal things
      if line[-1].split("|pfwsp:")[1].split("|")[0] in ["0", "100"]:
        beg_syll = True
    elif context_type == "categorical":
      if line[-1].split("|cpsp:")[1].split("|")[0] in ["xx", "beg", "one"]:
        beg_syll = True
    else:
      raise SiReError("Unsupported context_type {0}!".format(context_type))
    if beg_syll == True:
      for p in c_syll["phonemes"]:
        c_syll["id"] += p["id"]
      # Add syll to word
      c_word["syllables"].append(c_syll)
      # If new syll is beginning of word, prev word is done
      #This depends on what type of positional context was used to create the labels
      beg_word = False
      if context_type == "absolute":
        if line[-1].split("|pfwwp:")[1].split("|")[0] in ["0"]:
          beg_word = True
      elif context_type == "relational":
        #0 should be used for silence positions in the relational case, with "100" for normal things
        if line[-1].split("|pfwwp:")[1].split("|")[0] in ["0", "100"]:
          beg_word = True
      elif context_type == "categorical":
        if line[-1].split("|cpwp:")[1].split("|")[0] in ["xx", "beg", "one"]:
          beg_word = True
      else:
        raise SiReError("Unsupported context_type {0}!".format(context_type))
      if beg_word == True:
        for s in c_word["syllables"]:
          c_word["id"] += s["id"]
        proto["utt"].append(c_word)
        c_word = {"id":"", "syllables":[]}
      c_syll = {"id":"", "phonemes":[c_phon], "stress":line[-1].split("|css:")[1].split("|")[0]}
    else:
      c_syll["phonemes"].append(c_phon)
    # If this is the last phoneme we are done
    if i == len(lab) - 1:
      for p in c_syll["phonemes"]:
        c_syll["id"] += p["id"]
      c_word["syllables"].append(c_syll)
      for s in c_word["syllables"]:
          c_word["id"] += c_syll["id"]
      proto["utt"].append(c_word)
  # The first is empty so we can pop
  proto["utt"].pop(0)
  return proto

def proto_from_hts_lab(lab, state):
  proto = {"utt":[]}
  proto["id"] = lab[0]
  lab.pop(0)
  # Create split lib

  if state:

      delims = ["^","-","+","=","@","_","/A:","_","_","/B:","-","-","@","-","&","-","#","-","$","-","!","-",";","-","|","/C:","+","+","/D:","_","/E:","+","@","+","&","+","#","+","/F:","_","/G:","_","/H:","=","@","=","|","/I:","=","/J:","+","-","[","]"]

      c_syll = {"id":"", "phonemes":[], "stress":None}
      c_word = {"id":"", "syllables":[]}

      state_count = 0

      for i, line in enumerate(lab):

        line[-1] = split_hts_lab(line[-1], delims)
        line[-1].pop(53)
        line[-1].pop(54)
        if state_count == 0:
            c_phon = {"id":None, "stress":None, "start":None, "end":None, "states":{}}
            c_phon["start"] = line[0]
        c_phon["id"] = line[-1][2]
        # VCTK HTS labs do not contain stress information at the phoneme level
        c_phon["stress"] = None
        c_phon["states"][state_count] = [line[0], line[1]]

        if state_count < 4:
            state_count += 1
        else:
            state_count = 0
            c_phon["end"] = line[1]
            # Add phonemes to syll
            # If phonemes is beginning of syll prev syll is done
            if line[-1][5] in ["xx", "1"]:
              for p in c_syll["phonemes"]:
                # print "Earlier P", p
                c_syll["id"] += p["id"]

              # Add syll to word
              c_word["syllables"].append(c_syll)
              # If new syll is beginning of word, prev word is done
              if line[-1][13] in ["xx", "1"]:
                for s in c_word["syllables"]:
                  c_word["id"] += s["id"]
                #   print "New S", s
                proto["utt"].append(c_word)
                c_word = {"id":"", "syllables":[]}
              c_syll = {"id":"", "phonemes":[c_phon], "stress":line[-1][10]}
            else:
              c_syll["phonemes"].append(c_phon)
            # If this is the last phoneme we are done
            # print "This is I", i
            if i == len(lab) - 1:
              for p in c_syll["phonemes"]:
                c_syll["id"] += p["id"]
              c_word["syllables"].append(c_syll)
              for s in c_word["syllables"]:
                  c_word["id"] += c_syll["id"]
              proto["utt"].append(c_word)
            #   print "C_Word", c_word["id"]
      # The first is empty so we can pop
      proto["utt"].pop(0)

      return proto
  else:
      delims = ["~","-","+","=",":","_","/A/","_","_","/B/","-","-",":","-","&","-","#","-","$","-",">","-","<","-","|","/C/","+","+","/D/","_","/E/","+",":","+","&","+","#","+","/F/","_","/G/","_","/H/","~",":","=","&","/I/","_","/J/","+","-"]
      for i, line in enumerate(lab):
        c_phon = {"id":None, "stress":None, "start":None, "end":None}
        line[-1] = split_hts_lab(line[-1], delims)
        # Create phonemes
        c_phon["id"] = line[-1][2]
        c_phon["start"] = line[0]
        c_phon["end"] = line[1]
        # VCTK HTS labs do not contain stress information at the phoneme level
        c_phon["stress"] = None
        # Add phonemes to syll
        # If phonemes is beginning of syll prev syll is done
        if line[-1][5] in ["xx", "1"]:
          for p in c_syll["phonemes"]:
            c_syll["id"] += p["id"]
          # Add syll to word
          c_word["syllables"].append(c_syll)
          # If new syll is beginning of word, prev word is done
          if line[-1][13] in ["xx", "1"]:
            for s in c_word["syllables"]:
              c_word["id"] += s["id"]
            proto["utt"].append(c_word)
            c_word = {"id":"", "syllables":[]}
          c_syll = {"id":"", "phonemes":[c_phon], "stress":line[-1][10]}
        else:
          c_syll["phonemes"].append(c_phon)
        # If this is the last phoneme we are done
        if i == len(lab) - 1:
          for p in c_syll["phonemes"]:
            c_syll["id"] += p["id"]
          c_word["syllables"].append(c_syll)
          for s in c_word["syllables"]:
              c_word["id"] += c_syll["id"]
          proto["utt"].append(c_word)
      # The first is empty so we can pop
      proto["utt"].pop(0)
      return proto


#Create a proto utterance from text.
#Note that all phonemes are given a phony 100ms duration - this is expected to be overridden by the back-end duration prediction system.
#If pron_reduced is set this will attempt to produce a reduced pronunciation for parts of the sentence as specifiied by reduction_level and
#the scores in reduction_score_file.
#Reduction_level must be minimally 0 (full reduction) and maximally 1 (no reduction).
def proto_from_txt(lab, dictionary, general_sil_phoneme="sil", comma_is_pause=False, stanfordparse=False, pcfgdict=None, pron_reduced=False, lm_score_dir=None, reduction_level=1.0, phoneme_lm_prons=False):
  #Create words
  proto = {"utt":[]}
  proto["id"] = lab[0].split("/")[-1]
  #First we check if we need to reduce some words, and which
  if pron_reduced == True and phoneme_lm_prons == True:
    raise SiReError("Cannot produce reduced pronunciations in combination with phoneme LM based pronunciation choice.")
  elif pron_reduced == True:
    if os.path.isdir(lm_score_dir):
      words = reduce_word_tuples(lab[1:], os.path.join(lm_score_dir, proto["id"]+".scored"), reduction_level)
    else:
      raise SiReError("The directory with reduction scores does not exist!")
  elif phoneme_lm_prons == True:
    if os.path.isdir(lm_score_dir):
      #As we do not keep stress information for the phoneme LM to score we may have a few potential versions of each word.
      words = find_potential_words(lab[1:], os.path.join(lm_score_dir, proto["id"]+".path"))
      raise SiReError("Not implemented yet! Phoneme_lm_scoring. ")
    else:
      raise SiReError("The directory with reduction scores does not exist!")
  else:
    words = [(x, False) for x in lab[1:]]
  #Make words and look up in dictionary
  #If no parse exists (i.e. no pos tags) we will simply grab the first pronunciation we can find that is not reduced (if one exist).
  #We also forget the pos tag of that in the process.
  #We start with silence.
  proto["utt"].append({"id":"sil", "syllables":dictionary.make_entry(general_sil_phoneme, general_sil_phoneme+" 0", False)["syllables"]})
  if not stanfordparse:
    for word in words:
      #If we need to keep some punctuation
      if comma_is_pause == True:
        proto["utt"].append({"id":word[0], "syllables":dictionary.get_single_entry(word[0], reduced=word[1], punct_as_sil=([","], "sil"))["syllables"]})
      else:
        proto["utt"].append({"id":word[0], "syllables":dictionary.get_single_entry(word[0], reduced=word[1])["syllables"]})
  else: #Else a pcfg parse should exist and we can get the pos tags from that.
    tree = parsetrees.stanfordPcfgTree()
    tree.make_tree(pcfgdict[proto["id"]])

    #Do we need some punctuation?
    if comma_is_pause == True:
      leafs = tree.get_leafs(include_punct=[","])
    else:
      leafs = tree.get_leafs()

    #In this case we need to do some merging
    if len(leafs) != len(words):
      leafs = merge(leafs, words, proto["id"])
    for i, leaf in enumerate(leafs):
      pos, word = leaf.label.lower().split("-")
      if word != words[i][0]:
        raise SiReError("Word ({0}) from parse does not match word ({1}) from txt! In {2}.".format(word, words[i][0], proto["id"]))
      else:
        word = words[i]
      if comma_is_pause:
        c_best = dictionary.get_single_entry(word[0], pos, word[1], punct_as_sil=([","], "sil"))
      else:
        c_best = dictionary.get_single_entry(word[0], pos, word[1])
      proto["utt"].append({"id":word[0], "syllables":c_best["syllables"]})
  #We end with silence.
  proto["utt"].append({"id":"sil", "syllables":dictionary.make_entry(general_sil_phoneme, general_sil_phoneme+" 0", False)["syllables"]})
  #Add phony times to phonemes
  #Phony phoneme duration counter
  cur_dur = 0
  for word in proto["utt"]:
    for syll in word["syllables"]:
      #Add phony time to phonemes
      for phon in syll["phonemes"]:
        phon["start"] = cur_dur
        #Add 100ms in HTK lab format
        cur_dur += 1000000
        phon["end"] = cur_dur
  return proto

#Add parse information from a stanford pcfg parsed sentence
def load_stanford_pcfg_parse(utt, parse, comma_is_pause=False):
  if utt.words == None:
    raise SiReError("No words in utterance! Please load an mlf or txt file first!")
  tree = parsetrees.stanfordPcfgTree()
  tree.make_tree(parse)
  if comma_is_pause == True:
    leafs = tree.get_leafs(include_punct=[","])
  else:
    leafs = tree.get_leafs()
  num_w = utt.num_words_no_pau(comma_is_pause)
  if len(leafs) != num_w:
    #First we try to see if this is due to differences in how words are
    #dealt with in parsing and annotation.
    #Prime example is using 's in e.g. there's for transcription instead of there is.
    #Parsing splits there's into two whereas in e.g. combilex there's is one word.
    #If this is the case we split the WORD into two with the 's being a single phoneme
    #single syllable word. In other cases the contraction straddles two words and
    #we add a "phony" word which affects contexts but adds no phonemes.
    utterance_utils.try_split_words(utt)
    #Update num_w
    num_w = utt.num_words_no_pau(comma_is_pause)
    if len(leafs) != num_w:
      for w in utt.words:
        print w.id
      raise SiReError("Number of leaves ({0}) not equal to number of words ({1})! In utt ({2})!".format(len(leafs), num_w, utt.id))
  #Match each word with parse
  words = utt.get_words_no_pau(comma_is_pause)
  for i, word in enumerate(words):
    l = leafs[i].label.split("-")
    word.id = l[1]
    word.pos = l[0]
    #There should always be a parent
    word.parent_phrase = leafs[i].parent
    #But there might not be more than one
    if word.parent_phrase.parent != None:
      word.grandparent_phrase = word.parent_phrase.parent
    else:
      word.grandparent_phrase = parsetrees.get_fake_stanford_pcfg_parse()
    #And certainly we might be done here
    if word.grandparent_phrase.parent in [None, "xx"] or word.grandparent_phrase.parent.label == "xx":
      word.greatgrandparent_phrase = parsetrees.get_fake_stanford_pcfg_parse()
    else:
      word.greatgrandparent_phrase = word.grandparent_phrase.parent

  #Now add fake parse for sil, pau and #
  for word in utt.words:
    if word.id in utt.phoneme_features.get_sil_phonemes():
      word.parent_phrase = parsetrees.get_fake_stanford_pcfg_parse()
      word.grandparent_phrase = parsetrees.get_fake_stanford_pcfg_parse()
      word.greatgrandparent_phrase = parsetrees.get_fake_stanford_pcfg_parse()
      word.pos = "sil"

#Add parse information from a stanford dependency parse
def load_stanford_dependency_parse(utt, parse):
  if utt.words == None:
    raise SiReError("No words in utterance! Please load an mlf or txt file first!")
  tree = parsetrees.stanfordDependencyTree()
  tree.make_tree(parse)
  #As each word is at a node not at a leaf we get the nodes.
  nodes = tree.get_nodes(utt_sorted=True)
  if len(nodes) != utt.num_words_no_pau():
    #First we try to see if this is due to differences in how words are
    #dealt with in parsing and annotation.
    #Prime example is using 's in e.g. there's for transcription instead of there is.
    #Parsing splits there's into two whereas in e.g. combilex there's is one word.
    #If this is the case we split the WORD into two with the 's being a single phoneme
    #single syllable word. In other cases the contraction straddles two words and
    #we add a "phony" word which affects contexts but adds no phonemes.
    utterance_utils.try_split_words(utt)
    if len(nodes) != utt.num_words_no_pau():
      for node in nodes:
        print node.label
      raise SiReError("Number of nodes ({0}) not equal to number of words ({1})! In utt ({2})!".format(len(nodes), utt.num_words_no_pau(), utt.id))
  #Match each word with parse
  for i, word in enumerate(utt.get_words_no_pau()):
    #As we may have split words the parse contains the id
    word.id = nodes[i].label
    #But as we may have punctuation the word itself contains the utt_pos
    nodes[i].utt_pos = word.pos_in_utt()
    #There should always be itself
    word.parent_dependency = nodes[i]
    #And there should always be a parent
    word.grandparent_dependency = word.parent_dependency.parent
    #But there might not be more than one
    if word.grandparent_dependency.parent != None:
      word.greatgrandparent_dependency = word.grandparent_dependency.parent
    else:
      word.greatgrandparent_dependency = parsetrees.stanfordDependencyTree()

  #Now add empty parse for sil, pau and #
  for word in utt.words:
    if word.id in utt.phoneme_features.get_sil_phonemes()+[","]:
      word.parent_dependency = parsetrees.stanfordDependencyTree()
      word.grandparent_dependency = parsetrees.stanfordDependencyTree()
      word.greatgrandparent_dependency = parsetrees.stanfordDependencyTree()

#Get word ids from text.
def load_txt(utt, txtpath, emphasis):
  txt = open(txtpath, "r").read()
  for x in ["!", ".", "?", ",", "--"]:
    txt = txt.replace(x, "")

  #We lower case because other methods use word name
  #and we don't care about case there.

  # if not using emphasis, lowercase like normal
  if not emphasis:
      txt = txt.lower()
  txt = txt.split()
  # if using emphasis, lower case all but words with two or more capitalised letters
  if emphasis:
      temp_txt = []
      upper_reg = re.compile(r'[A-Z][A-Z]+')
      for i in txt:
          if re.search(upper_reg, i) != None:
              temp_txt.append(i)
          else:
              i = i.lower()
              temp_txt.append(i)
      txt = temp_txt

  if len(txt) != utt.num_words_no_pau():
    for w in utt.words:
      print w.id
      print txt
    raise SiReError("Text length ({0}) and number of words ({1}) in utt ({2}) does not match!".format(len(txt), utt.num_words_no_pau(), utt.id))
  #Now replace the phoneme based ids with txt based.
  i = 0
  for w in utt.words:
    if w.id not in utt.phoneme_features.get_sil_phonemes():
      w.id = txt[i]
      i += 1
  utt.txtloaded = True

#Collapse closure and release to the corresponding stop from align lab.
def remake_stops(lab):
  remove = []
  for i, l in enumerate(lab):
    if "_cl" in l[-1]:
      if lab[i+1][-1]+"_cl" != l[-1]:
        raise SiReError("Closure not preceding release! In {0}".format(lab))
      else:
        lab[i+1][0] = l[0]
        remove.append(l)
  for r in remove:
    lab.remove(r)
  return lab

#Creates phonemes and their info from align lab
def make_phonemes(lab):
  stress = 0
  for i, p in enumerate(lab):
    if p[-1] == "#1":
      stress = 1
      lab[i] = "out"
    elif p[-1] == "#2":
      stress = 2
      lab[i] = "out"
    else:
      lab[i] = {"stress":stress, "id":lab[i][-1], "start":int(lab[i][0]), "end":int(lab[i][1])}
      stress = 0
  while "out" in lab:
    lab.remove("out")
  return lab

#Makes the sylls in an align lab word
def make_sylls(utt):
  sylls = []
  syll = {"id":"", "stress":0, "phonemes":[]}
  for i, p in enumerate(utt):
    #. marks midword syll boundaries
    #sp marks word boundaries and possible silence segments
    #sil marks silence segments between words
    if p["id"] in [".", "sil", "sp"]:
      if len(syll["phonemes"]) > 0:
        syll["start"] = syll["phonemes"][0]["start"]
        syll["end"] = syll["phonemes"][-1]["end"]
        sylls.append(syll)
      syll = {"id":"", "stress":0, "phonemes":[]}
      #Sil and sp are also markers of word boundaries and
      #may be their own entity so should be kept
      if p["id"] in ["sil", "sp"]:
        sylls.append({"id":p["id"], "stress":0, "phonemes":[p], "start":p["start"], "end":p["end"]})
    else:
      syll["phonemes"].append(p)
      syll["id"] += p["id"]
      if p["stress"] > 0:
        if syll["stress"] != 0:
          raise SiReError("Syllable ({0}) already stressed! In utt ({1})".format(syll, utt.id))
        syll["stress"] = p["stress"]
      if i == len(utt)-1:
        syll["start"] = syll["phonemes"][0]["start"]
        syll["end"] = syll["phonemes"][-1]["end"]
        #If we're at the end of the utt the last syll is done
        sylls.append(syll)
  return sylls

#Finds the words in an align lab
def make_words(utt):
  words = []
  word = {"id":"", "syllables":[]}
  for i, s in enumerate(utt):
    #The check for len phonemes is necessary as the syll id is composed
    #of phoneme ids and all of "s", "i", "l" and "p" are valid ids.
    #Thus a syllable of the phonemes "s" and "p" has the id "sp".
    if s["id"] in ["sil", "sp"] and len(s["phonemes"]) == 1:
      if word["syllables"] != []:
        word["start"] = word["syllables"][0]["start"]
        word["end"] = word["syllables"][-1]["end"]
        words.append(word)
      #If the silence is of any length it should be kept.
      if s["end"] - s["start"] > 0:
        words.append({"id":s["id"], "syllables":[s], "start":s["start"], "end":s["end"]})
      elif i == 0 or i == len(utt)+1:
        #Something is likely fishy
        raise SiReError("Boundary silence not of any length in word ({0})!".format(word))
      word = {"id":"", "syllables":[]}
    else:
      word["syllables"].append(s)
      word["id"] += s["id"]
  return words

#Splits an HTS style label based on its delimiters.
def split_hts_lab(lab, delims):
  values = {}
  for i, delim in enumerate(delims):
    # print "Delims", delims
    # print "Loopers", i, delim
    # print "lab", lab
    s = lab.split(delim)
    # print "Splitting", lab.split(delim)
    # print "S", s
    s = [s[0], delim.join(s[1:])]
    # print "New S", s
    if i+1 != len(delims):
      values[i] = s[0]
      lab = s[1]
    else:
      values[i] = s[0]
      values[i+1] = s[1]
  # print "values", values
  return values

#Takes a list of words and a path to a file with LM scores for each word.
#Returns a list of tuples (word, to_reduce?) based on the reduction level (1.0 fully pronounced, 0.0 fully reduced).
def reduce_word_tuples(words, score_file, reduction_level):
  #Our initial assumption is nothing needs reduction
  w_l = [[word, False] for word in words]
  #If we don't reduce we just return all unreduced
  if reduction_level == 1.0:
    return w_l
  #If the reduction_level is not between 0 and 1 we fail
  elif reduction_level > 1.0 or reduction_level < 0.0:
    raise SiReError("Reduction level must be between 1.0 and 0.0 but was {0}".format(reduction_level))
  #As words may appear more than once we make a dict indexed on word pos.
  scores = {}
  for i, x in enumerate(open(score_file, "r").readlines()):
    scores[i] = x.strip().split()

  if len(scores) != len(words):
    raise SiReError("I seem to have a mismatching set of words ({0}) and LM scores ({1}) for {2}".format(len(words), len(scores), score_file))

  #The number of words to reduce
  n_to_reduce = int(round(len(words)*(1-reduction_level), 0))

  #A list of dict entry tuples ordered by score in descending order
  ranked = sorted(scores.items(), key=lambda (k, v): v[1])

  #Now mark the appropriate ones to be reduced
  for i in range(n_to_reduce):
    w_l[ranked[i][0]][1] = True

  return w_l


def merge(leafs, words, utt_id):
  print "WARNING! Merging not implemented yet - the current is a non-complete hack!"
  print "Check if this sentences was done correctly - {0}".format(utt_id)
  for i, l in enumerate(words):
    l = l[0]
    if l == "i'm":
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-i'm"
    elif "'ll" in l: #While the ' endings may cover unintended words it should be safe as we only try and merge if there is a potential problem
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-"+l
    elif l == "gonna":
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-gonna"
    elif l == "wanna":
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-wanna"
    elif "'s" in l:
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-"+l
    elif "'ve" in l:
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-"+l
    elif "'re" in l:
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-"+l
    elif "'d" in l:
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-"+l
    elif "n't" in l:
      p2 = leafs[i+1].label.split("-")[0]
      leafs.pop(i+1)
      leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-"+l
  return leafs
