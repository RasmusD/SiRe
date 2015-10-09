#Methods for loading utterances
import utterance, utterance_utils, sys, phone_features, parsetrees, os, dictionary

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

def proto_from_hts_lab(lab):
  proto = {"utt":[]}
  proto["id"] = lab[0]
  lab.pop(0)
  # Create split lib
  delims = ["~","-","+","=",":","_","/A/","_","_","/B/","-","-",":","-","&","-","#","-","$","-",">","-","<","-","|","/C/","+","+","/D/","_","/E/","+",":","+","&","+","#","+","/F/","_","/G/","_","/H/","~",":","=","&","/I/","_","/J/","+","-"]
  c_word = {"id":"", "syllables":[]}
  c_syll = {"id":"", "phonemes":[], "stress":None}
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

#Create a proto utterance from text. Note that all phonemes are given a phony 100ms duration - this is expected to be overridden by the back-end duration prediction system.
def proto_from_txt(lab, args):
  #Create words
  proto = {"utt":[]}
  proto["id"] = lab[0].split("/")[-1]
  #Make words and look up in dictionary
  #If no parse exists (i.e. no pos tags) we will simply grab the first pronunciation we can find that is not reduced (if one exist).
  #We also forget the pos tag of that in the process.
  if not args.stanfordparse:
    for word in lab[1:]:
      proto["utt"].append({"id":word, "syllables":[args.dictionary.get_single_entry(word)]})
  else: #Else a parse should exist and we can get the pos tags from that.
    tree = parsetrees.stanfordtree()
    tree.make_tree(args.parsedict[proto["id"]])
    leafs = tree.get_leafs()
    #In this case we need to do some merging
    if len(leafs) != len(lab[1:]):
      print "WARNING! Merging not implemented yet - the current is a non-complete hack!"
      print "Check if this sentences was done correctly - {0}".format(proto["id"])
      for i, l in enumerate(lab[1:]):
        if l == "i'm":
          p2 = leafs[i+1].label.split("-")[0]
          leafs.pop(i+1)
          leafs[i].label = leafs[i].label.split("-")[0]+"|"+p2+"-i'm"
    for i, leaf in enumerate(leafs):
      pos, word = leaf.label.lower().split("-")
      if word != lab[i+1]:
        print "ERROR: Parse and text does not match in {0}!".format(lab)
        print "{0} != {1}".format(word, lab[i+1])
        sys.exit()
      c_best = args.dictionary.get_single_entry(word)
      proto["utt"].append({"id":word, "syllables":[c_best]})
  #Make syllables and split dictionary format
  #Phony phoneme duration counter
  cur_dur = 0
  for word in proto["utt"]:
    sylls = [x.strip("()") for x in word["syllables"][0].split(") (")]
    word["syllables"] = []
    for syll in sylls:
      c_syll = {"id":"", "phonemes":[], "stress":None}
      syll = syll.split(") ")
      c_syll["stress"] = syll[1]
      #Make the phonemes
      for phon in syll[0].split():
        c_phon = {"id":None, "stress":None, "start":None, "end":None}
        c_phon["id"] = phon
        c_phon["start"] = cur_dur
        #Add 100ms in HTK lab format
        cur_dur += 1000000
        c_phon["end"] = cur_dur
        #Phone stress not encoded directly in combilex dict.
        c_phon["stress"] = None
        c_syll["phonemes"].append(c_phon)
      c_syll["id"] = syll[0].replace(" ", "")
      word["syllables"].append(c_syll)
  return proto

#Add parse information from a stanford parsed sentence
def load_stanford_parse(utt, parse):
  if utt.words == None:
    print "Error: No words in utterance! Please load an mlf or txt (not implemented yet) file first!"
    sys.exit()
  tree = parsetrees.stanfordtree()
  tree.make_tree(parse)
  leafs = tree.get_leafs()
  if len(leafs) != utt.num_words_no_pau():
    #First we try to see if this is due to differences in how words are
    #dealt with in parsing and annotation. 
    #Prime example is using 's in e.g. there's for transcription instead of there is.
    #Parsing splits there's into two whereas in e.g. combilex there's is one word.
    #If this is the case we split the WORD into two with the 's being a single phoneme
    #single syllable word. In other cases the contraction straddles two words and
    #we add a "phony" word which affects contexts but adds no phonemes.
    utterance_utils.try_split_words(utt)
    if len(leafs) != utt.num_words_no_pau():
      print "Error! Number of leaves ({0}) not equal to number of words ({1})!".format(len(leafs), utt.num_words_no_pau())
      print utt.id
      for w in utt.words:
        print w.id
      sys.exit()
  #Match each word with parse
  for i, word in enumerate(utt.get_words_no_pau()):
    l = leafs[i].label.split("-")
    word.id = l[1]
    word.pos = l[0]
    #There should always be a parent
    word.parent_phrase = leafs[i].parent
    #But there might not be more than one
    if word.parent_phrase.parent != None:
      word.grandparent_phrase = word.parent_phrase.parent
    else:
      word.grandparent_phrase = parsetrees.get_fake_stanford_parse()
    #And certainly we might be done here
    if word.grandparent_phrase.parent in [None, "xx"] or word.grandparent_phrase.parent.label == "xx":
      word.greatgrandparent_phrase = parsetrees.get_fake_stanford_parse()
    else:
      word.greatgrandparent_phrase = word.grandparent_phrase.parent
  
  #Now add fake parse for sil, pau and #
  for word in utt.words:
    if word.id in phone_features.get_sil_phonemes():
      word.parent_phrase = parsetrees.get_fake_stanford_parse()
      word.grandparent_phrase = parsetrees.get_fake_stanford_parse()
      word.greatgrandparent_phrase = parsetrees.get_fake_stanford_parse()
      word.pos = "sil"


#Get word ids from text.
def load_txt(utt, txtpath):
  txt = open(txtpath, "r").read()
  for x in ["!", ".", "?", ",", "--"]:
    txt = txt.replace(x, "")
  #We lower case because other methods use word name
  #and we don't care about case there.
  txt = txt.lower()
  txt = txt.split()
  if len(txt) != utt.num_words_no_pau():
    print "Error: Text length ({0}) and number of words in utt ({1}) does not match!".format(len(txt), utt.num_words_no_pau())
    print utt.id
    sys.exit()
  #Now replace the phoneme based ids with txt based.
  i = 0
  for w in utt.words:
    if w.id not in phone_features.get_sil_phonemes():
      w.id = txt[i]
      i += 1
  utt.txtloaded = True

#Collapse closure and release to the corresponding stop from align lab.
def remake_stops(lab):
  remove = []
  for i, l in enumerate(lab):
    if "_cl" in l[-1]:
      if lab[i+1][-1]+"_cl" != l[-1]:
        print "Error: Closure not preceding release!"
        print lab
        sys.exit()
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
          print "Error: Syllable already stressed!"
          print syll
          sys.exit()
        syll["stress"] = 1
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
        print "Error: Boundary silence not of any length!"
        print word
        sys.exit()
      word = {"id":"", "syllables":[]}
    else:
      word["syllables"].append(s)
      word["id"] += s["id"]
  return words

#Splits an HTS style label based on its delimiters.
def split_hts_lab(lab, delims):
  values = {}
  for i, delim in enumerate(delims):
    s = lab.split(delim)
    s = [s[0], delim.join(s[1:])]
    if i+1 != len(delims):
      values[i] = s[0]
      lab = s[1]
    else:
      values[i] = s[0]
      values[i+1] = s[1]
  return values
