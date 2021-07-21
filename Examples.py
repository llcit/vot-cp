from calculateVOT import *

## note that these tests only look for a few stops, to speed up the process.

# single-pair processing for 'p'
calculateVOT("Examples/spanish_corpus/ALL_129_F_SPA_SPA_NWS.wav",
	"Examples/spanish_corpus/ALL_129_F_SPA_SPA_NWS.TextGrid", 
	['p'])


# explicitly indicate the channel for 't'
calculateVOT("Examples/cantonese_corpus/VM34A_Cantonese_I1_20191028.wav",
	"Examples/cantonese_corpus/VM34A_Cantonese_I1_20191028.TextGrid", 
	['t'],
	preferredChannel = 1)

# indicate that two speakers are present, each with their own channel
calculateVOT("Examples/english_corpus/DP_EN_03_EN_05_EN_EN_03_DP_EN_03_EN_05_EN_EN_05.wav", 
	"Examples/english_corpus/DP_EN_03_EN_05_EN_EN_03_DP_EN_03_EN_05_EN_EN_05.TextGrid",
	['P'],
	distinctChannels = True)

# batch processing for 't T tt'
calculateVOTBatch("Examples/arabic_corpus", ['t', 'T', 'tt'])