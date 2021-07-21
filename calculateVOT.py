import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s: %(message)s')

file_handler = logging.FileHandler("VOT-CP.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


import os
import sys
import argparse
import tempfile
import subprocess
import parselmouth
from praatio import tgio
from collections import Counter



def approvedFileFormat(wav, TextGrid):

	# remove file path from file names if present, for reporting purposes
	TextGrid = TextGrid.split("/")[-1]
	wav = wav.split("/")[-1]

	wavExt = os.path.splitext(wav)[1]
	textgridExt = os.path.splitext(TextGrid)[1]

	# verify input contains the expected extensions
	if wavExt != ".wav" or textgridExt != ".TextGrid":
		return False
	else:
		print()
		logger.info("Processing {} and {}...\n".format(wav, TextGrid))
		return True

def processParameters(
	startPadding, 
	endPadding, 
	stops, 
	TextGrid
	): 

	# remove file path from TG name if present, for reporting purposes
	TextGrid = TextGrid.split("/")[-1]

	# adjust long padding values
	if startPadding > 25:
		logger.info("A startPadding of {} ms exceeds the maximum. It was adjusted to 25 ms.\n"\
			.format(startPadding))
		startPadding = 0.025
	elif startPadding < -25:
		logger.info("A startPadding of {} ms exceeds the minimum. It was adjusted to -25 ms.\n"\
			.format(startPadding))
		startPadding = -0.025
	else:
		startPadding = startPadding/1000

	if endPadding > 25:
		logger.info("An endPadding of {} ms exceeds the maximum. It was adjusted to 25 ms.\n"\
			.format(endPadding))
		endPadding = 0.025
	elif endPadding < -25:
		logger.info("An endPadding of {} ms exceeds the minimum. It was adjusted to -25 ms.\n"\
			.format(endPadding))
		endPadding = -0.025
	else:
		endPadding = endPadding/1000

	# specify stop categories
	ipaStops = ['p', 'b', 't', 'd', 'ʈ', 'ɖ', 'c', 'ɟ', 'k', 'g', 'q', 'ɢ', 'ʔ', "p'", "t'", "k'", 
				'ɓ', 'ɗ', 'ʄ', 'ɠ', 'ʛ']
	voicelessStops = ['p', 't', 'ʈ', 'c', 'k', 'q', 'ʔ', "p'", "t'", "k'", 'pp', 'tt', 'ʈʈ', 'cc', 
				'kk', 'qq', 'ʔʔ']
	
	# define stops of interest
	if len(stops) == 0:
		stops = voicelessStops
	else:
		vettedStops, nonStops = [], []
		for stopSymbol in stops:
			if stopSymbol[0].lower() in ipaStops:
				vettedStops.append(stopSymbol)
			else:
				nonStops.append(stopSymbol)

		if len(nonStops) == 1:
			logger.info("'{}' is not (or does not start with) a stop sound. This symbol will be ignored "\
				"in file {}.\n".format(nonStops[0], TextGrid))
		elif len(nonStops) > 1:
			logger.info("'{}' are not (or do not start with) stop sounds. These symbols will be ignored "\
				"in file {}.\n".format("', '".join(nonStops), TextGrid))

		if len(vettedStops) == 0:
			if len(stops) == 1:
				logger.warning("The sound you entered is not classified as a stop sound by the IPA.")
			elif len(stops) == 2:
				logger.warning("Neither of the sounds you entered is classified as a stop sound by the IPA.")
			else:
				logger.warning("None of the sounds you entered is classified as a stop sound by the IPA.")
			logger.info("The program will continue by analyzing all voiceless stops recognized by the IPA.\n")
			stops = voicelessStops
		else:
			stops = vettedStops
	return startPadding, endPadding, stops

def addStopTier(
	TextGrid, 
	startPadding, 
	endPadding, 
	stops, 
	outputPath
	):

	# open textgrid
	tg = tgio.openTextgrid(TextGrid)

	# remove file path from TG name if present, for reporting purposes
	TextGrid = TextGrid.split("/")[-1]

	# verify that no 'AutoVOT' or 'stops' tiers exist. Reject TG with unnamed tiers
	for tierName in tg.tierNameList:
		if tierName == "AutoVOT":
			logger.warning("A tier named 'AutoVOT' already exists. Said tier will be renamed as "\
				"'autovot - original' to avoid a naming conflict.\n")
			tg.renameTier("AutoVOT", "autovot - original")
		elif tierName[-5:] == "stops":
			logger.error("There is a tier with the word 'stops' in its label in {}. You must "\
				"relabel said tier before continuing.\n".format(TextGrid))
			raise RuntimeError("    *** Process incomplete. ***")
		elif tierName == "":
			logger.error("At least one tier in file {} has no name. Fix the issue before continuing.\n"\
				.format(TextGrid))
			raise RuntimeError("    *** Process incomplete. ***")
	
	# convert tier labels to lowercase
	tg.tierNameList = [tierName.lower() for tierName in tg.tierNameList]
	tg.tierDict = dict((k.lower(), v) for k, v in tg.tierDict.items())

	# collect all word tiers or terminate process if none exists
	allWordTiers = [tierName for tierName in tg.tierNameList if "word" in tierName]
	if len(allWordTiers) == 0:
		logger.error("{} does not contain any tier labeled 'words'.\n".format(TextGrid))
		raise RuntimeError("    *** Process incomplete. ***")

	# collect all phone tiers or terminate process if none exists
	allPhoneTiers = [tierName for tierName in tg.tierNameList if "phone" in tierName]
	if len(allPhoneTiers) == 0:
		logger.error("{} does not contain any tier labeled 'phones'.\n".format(TextGrid))
		raise RuntimeError("    *** Process incomplete. ***")

	# verify that an equal number of word and phone tiers exists before continuing
	if len(allWordTiers) == len(allPhoneTiers):

		voicedTokens =[]
		totalSpeakers = len(allPhoneTiers)
		currentSpeaker = 0
		lastSpeaker =	False
		populatedTiers = 0

		# add stop tier
		for tierName in allPhoneTiers:
			currentSpeaker += 1
			if tierName.replace("phone", "word") in allWordTiers:
				speakerName = tierName.split("phone")
				if speakerName[1].lower().startswith('s'):
					speakerName[1] = speakerName[1][1:]
				phoneTier = tg.tierDict[tierName]
				wordTier = tg.tierDict[tierName.replace("phone", "word")]
				wordStartTimes = [int(entry[0]*100000) for entry in wordTier.entryList]
				if totalSpeakers == currentSpeaker:
					lastSpeaker = True
				newTier = processStopTier(
						phoneTier, 
						stops, 
						wordStartTimes, 
						voicedTokens, 
						startPadding, 
						endPadding, 
						TextGrid, 
						lastSpeaker, 
						speakerName
						)
				if newTier:
					tg.addTier(newTier)
					populatedTiers += 1
				else:
					continue
			
			else:
				logger.error("The names of the 'word' and 'phone' tiers are inconsistent in file {}. "\
					"Fix the issue before continuing.\n".format(TextGrid))
				raise RuntimeError("    *** Process incomplete. ***")
	
	else:
		logger.error("There isn't an even number of 'phone' and 'word' tiers per speaker in file {}. "\
			"Fix the issue before continuing.\n".format(TextGrid))
		raise RuntimeError("    *** Process incomplete. ***")

	if populatedTiers == 0:
		logger.error("There were no voiceless stops found in {}.\n".format(TextGrid))
		raise RuntimeError("    *** Process incomplete. ***")

	# generate list of all stop tiers created
	stopTiers = [tierName for tierName in tg.tierNameList if "stops" in tierName]

	# save the new textgrid that contains one or more 'stops' tiers, using long form
	saveName = TextGrid.split(".TextGrid")[0]+"_output.TextGrid"
	tg.save(os.path.join(outputPath, saveName), useShortForm=False)
	
	return stopTiers, saveName

def processStopTier(
	phoneTier, 
	stops, 
	wordStartTimes, 
	voicedTokens, 
	startPadding, 
	endPadding, 
	TextGrid, 
	lastSpeaker, 
	speakerName
	):

	# specify voiced stops
	voicedStops = ['b', 'd', 'ɖ', 'ɟ', 'g', 'ɢ', 'ɓ', 'ɗ', 'ʄ', 'ɠ', 'ʛ']

	# gather stops of interest from TextGrid
	stopEntryList = []
	for entry in phoneTier.entryList:
		entryStart = int(entry[0]*100000)
		if (entry[-1].lower() in stops or entry[-1] in stops) and entryStart in wordStartTimes:
			stopEntryList.append(entry)
			if entry[-1][0].lower() in voicedStops:
				voicedTokens.append(entry[-1].lower())

	# apply padding
	extendedEntryList = []
	for start, stop, label in stopEntryList:
		extendedEntryList.append([start+startPadding, stop+endPadding, label])

	# check for and resolve length requirements and timing conflicts
	for interval in range(len(extendedEntryList)-1):
		currentPhone = extendedEntryList[interval]
		nextPhone = extendedEntryList[interval+1]
		startTime, endTime = 0, 1

		if currentPhone[endTime] > nextPhone[startTime]:  # check if there is an overlap between phones
			logger.error("In file {} (after adding padding), the segment starting at {:.3f} sec overlaps "\
				"with the segment starting at {:.3f}."\
				"\nYou might have to decrease the amount of padding and/or manually adjust segmentation to "\
				"solve the conflicts."\
				"\n\nProcess incomplete.\n".format(TextGrid, currentPhone[startTime], nextPhone[startTime]))
			raise RuntimeError("    *** Process incomplete. ***")
		elif currentPhone[endTime] - currentPhone[startTime] < 0.025:  # check if currentPhone is under 25ms
			if nextPhone[startTime] - currentPhone[endTime] <= 0.020:  # check if nextPhone is within 20ms
				currentPhone[endTime] = currentPhone[startTime] + 0.025  # make currentPhone 25ms long
				nextPhone[startTime] = currentPhone[endTime] + 0.021  # shift nextPhone 21ms after currentPhone
				logger.warning("In File {}, the phone starting at {:.3f} was elongaged to 25 ms because it "\
					"did not meet length requirements, and the phone starting at {:.3f} was shifted forward "\
					"due to a proximity issue. Please, verify manually that the modified windows still capture "\
					"the segments accurately.\n".format(TextGrid, currentPhone[startTime], nextPhone[startTime]))
			else:
				currentPhone[endTime] = currentPhone[startTime] + 0.025  # make currentPhone 25ms long
				logger.warning("In File {}, the phone starting at {:.3f} was elongaged to 25 ms because it did "\
					"not meet length requirements.\n".format(TextGrid, currentPhone[startTime]))
		else:
			if nextPhone[startTime] - currentPhone[endTime] <= 0.020:  # check if nextPhone is within 20ms
				nextPhone[startTime] = currentPhone[endTime] + 0.021  # shift nextPhone 21ms after currentPhone
				logger.warning("In File {}, the phone starting at {:.3f} was shifted forward due to a proximity "\
					"issue.\n".format(TextGrid, nextPhone[startTime]))

		if interval == len(extendedEntryList)-1 and nextPhone[endTime] - nextPhone[startTime] < 0.025:  # last segment
			nextPhone[endTime] = nextPhone[startTime] + 0.025  # shift last phone's endTime 25 ms after startTime

	# provide warning for voiced tokens
	if len(list(set(voicedTokens))) == 1 and lastSpeaker:  # print only once, for last speaker
		logger.warning("You're trying to obtain VOT calculations of the following voiced stop: '{}'"\
		.format(*list(set(voicedTokens))))
		logger.info("Note that AutoVOT's current model only works on voiceless stops; "\
			"prevoicing in the productions may result in inaccurate calculations.\n")
	elif len(list(set(voicedTokens))) > 1 and lastSpeaker:  # print only once, for last speaker
		logger.warning("You're trying to obtain VOT calculations of the following voiced stops: '{}'"\
			.format("', '".join(list(set(voicedTokens)))))
		logger.info("Note that AutoVOT's current model only works on voiceless stops; "\
			"prevoicing in the productions may result in inaccurate calculations.\n")

	# construct the stop tier if stops were identified
	if len(extendedEntryList) > 0:
		stopTier = phoneTier.new(name = speakerName[0]+"stops"+speakerName[1], entryList = extendedEntryList)
		return stopTier		
	else:
		return False

def getPredictions(wav, stopTiers, annotatedTextgrid, preferredChannel, distinctChannels, trainedModel):

	# track whether or not predictions were calculated
	processComplete = False

	# assign AutoVOT's pretrained model
	if not trainedModel:
		trainedModel = "autovot/models/vot_predictor.amanda.max_num_instances_1000.model"

	# make temporary directory to process predictions
	with tempfile.TemporaryDirectory() as tempDirectory:

		# process the sound file
		psnd = parselmouth.Sound(wav)
		wav = wav.split("/")[-1]  # remove file path if present, for reporting purposes
		tempSound = os.path.join(tempDirectory, wav)
		if psnd.get_sampling_frequency() != 16000:
			psnd = psnd.resample(16000)

		if distinctChannels:  # if multiple channels -- ie: one microphone per speaker
			
			channels = psnd.extract_all_channels()
			channelNumber = 0

			if len(channels) != len(stopTiers):
				logger.error("You enabled the parameter 'distinctChannels', but there isn't an equal number of "\
					"channels and speakers in the file {}. Fix the issue before continuing.\n".format(wav))
				raise RuntimeError("    *** Process incomplete. ***")

			# run VOT predictor
			for channel in channels:
				channel.save(tempSound, "WAV")

				subprocess.run([
					"python", "autovot/auto_vot_decode.py", 
					"--vot_tier", stopTiers[channelNumber], 
					"--vot_mark", "*", 
					tempSound, 
					annotatedTextgrid, 
					trainedModel, 
					"--ignore_existing_tiers"
					])

				channelNumber += 1
				processComplete = True

		else:
	
			if psnd.get_number_of_channels() != 1:
				psnd = psnd.extract_channel(preferredChannel)
			psnd.save(tempSound, "WAV")
			
			# run VOT predictor
			for tierName in stopTiers:
				subprocess.run([
					"python", "autovot/auto_vot_decode.py", 
					"--vot_tier", tierName, 
					"--vot_mark", "*", 
					tempSound, 
					annotatedTextgrid, 
					"autovot/models/vot_predictor.amanda.max_num_instances_1000.model", 
					"--ignore_existing_tiers"
					])

				processComplete = True

	# rename repeated labels of AutoVOT prediction tiers
	if len(stopTiers) > 1:  # if multiple speakers
		with open(annotatedTextgrid, "r") as TG:
			newTG = []
			tierNumber = 0
			for line in TG:
				if "AutoVOT" in line:
					nameBookEnds = stopTiers[tierNumber].split("stops")
					line = line.replace("AutoVOT", nameBookEnds[0]+"AutoVOT"+nameBookEnds[1])
					tierNumber += 1
				newTG.append(line)
		with open(annotatedTextgrid, "w") as TG:
			TG.writelines(newTG)
	
	return processComplete

def calculateVOT(
	wav, 
	TextGrid, 
	stops=[], 
	outputDirectory="output", 
	startPadding=0, 
	endPadding=0, 
	preferredChannel=1, 
	distinctChannels=False, 
	trainedModel=""
	):

	# verify file format
	if not approvedFileFormat(wav, TextGrid):
		print()
		logger.error("{} must be a wav file and {} must be a TextGrid file. One or both files do "\
			"not meet format requirements.\n".format(wav.split("/")[-1], TextGrid.split("/")[-1]))
		raise RuntimeError("    *** Process incomplete. ***")

	# process variable parameters
	startPadding, endPadding, stops = processParameters(startPadding, endPadding, stops, TextGrid)

	# create directory to output files
	outputPath = os.path.join(os.getcwd(), outputDirectory)
	if not os.path.exists(outputPath):
		os.mkdir(outputPath)

	# add stop tier populated with tokens of interest
	stopTiers, saveName = addStopTier(TextGrid, startPadding, endPadding, stops, outputPath)

	# specify where the annotated TG is located 
	annotatedTextgrid = os.path.join(outputDirectory, saveName)

	# apply AutoVOT prediction calculations
	processComplete = getPredictions(wav, stopTiers, annotatedTextgrid, preferredChannel, distinctChannels, trainedModel)

	# remove file path from file names if present, for reporting purposes
	TextGrid = TextGrid.split("/")[-1]
	wav = wav.split("/")[-1]

	if processComplete:
		print()
		logger.info("Process for {} and {} is complete.\n".format(wav, TextGrid))
	else:
		print()
		logger.error("Something went wrong while trying to obtain VOT predictions for files {} and {}.\n"\
			.format(wav, TextGrid))
		raise RuntimeError("    *** Process incomplete. ***")

	return

def calculateVOTBatch(
	inputDirectory, 
	stops=[], 
	outputDirectory="output", 
	startPadding=0, 
	endPadding=0, 
	preferredChannel=1, 
	distinctChannels=False, 
	trainedModel=""
	):
	
	fileNames = []
	
	try:
		for file in os.listdir(inputDirectory):
			fileName, fileExt = os.path.splitext(file)
			if fileExt == ".wav" or fileExt == ".TextGrid":
				fileNames.append(fileName)
	except FileNotFoundError:
		logger.error("The directory you entered for the parameter 'inputDirectory' does not exist.")
		raise RuntimeError("    *** Process incomplete. ***")

	for fileGroup in Counter(fileNames).items():
		if fileGroup[1] == 2:
			wavFilePath = os.path.join(inputDirectory,fileGroup[0]+".wav")
			TextGridFilePath = os.path.join(inputDirectory,fileGroup[0]+".TextGrid")
			try:
				calculateVOT(
					wavFilePath, 
					TextGridFilePath, 
					stops, 
					outputDirectory, 
					startPadding, 
					endPadding, 
					preferredChannel, 
					distinctChannels
					)
			except Exception as e:
				print(e)

	return



if __name__ == "__main__":
	# parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--wav', default='', help="An audio file with a '.wav' extension.")
    parser.add_argument('--TextGrid', default='', help="A labeled TextGrid file containing stops to measured VOT.")
    parser.add_argument('--inputDirectory', default='', help="A string-based path where data corpus is located.")
    parser.add_argument('--stops', default='', help="A list of phone labels to look for and process.", nargs="*")
    parser.add_argument('--outputDirectory', default='output', help="A string to be used as the name of the directory "
        "where the output will be sored.")
    parser.add_argument('--startPadding', default=0, help="A number to indicate the amount of time, in milliseconds, "
        "to be added to (or reduced from) the phone's start boundary. The maximum is 25 ms (or 0.025 sec), and the "
        "minimum is -25 ms (or -0.025 sec). Note that a negative value will shift the boundary left (that is, increase "
        "the segment window) and a positive value will shift the boundary right (that is, decrease the segment window).",
        type=int)
    parser.add_argument('--endPadding', default=0, help="A number to indicate the amount of time, in milliseconds, to "
        "be added to (or reduced from) the phone's end boundary. The maximum is 25 ms (or 0.025 sec), and the minimum "
        "is -25 ms (or -0.025 sec). Note that a negative value will shift the boundary left (that is, decrease the "
        "segment window) and a positive value will shift the boundary right (that is, increase the segment window).",
        type=int)
    parser.add_argument('--preferredChannel', default=1, help="A number (an integer) that indicates the channel from "
        "the wav file to be used when obtaining VOT predictions.", type=int)
    parser.add_argument('--distinctChannels', default=False, help="a boolean (ie, True or False) that indicates whether "
        "or not there are different speakers in the recording and transcription, each with a distinct channel.", type=bool)
    parser.add_argument('--trainedModel', default='', help="a string-based path that indicates the location of a trained "
        "model for your corpus.")

    args = parser.parse_args()

    if args.wav and args.TextGrid:
	    try:
	    	calculateVOT(
	        	args.wav, 
	        	args.TextGrid, 
	        	args.stops, 
	        	args.outputDirectory, 
	        	args.startPadding, 
	        	args.endPadding, 
	        	args.preferredChannel, 
	        	args.distinctChannels, 
	        	args.trainedModel
	        	)
	    except Exception:
	    	pass
    elif args.inputDirectory:
        calculateVOTBatch(
        	args.inputDirectory, 
        	args.stops, 
        	args.outputDirectory, 
        	args.startPadding, 
        	args.endPadding, 
        	args.preferredChannel, 
        	args.distinctChannels, 
        	args.trainedModel
        	)
    else:
    	print()
    	logger.error("The required positional arguments were not provided. Provide a wav and TextGrid files for single-pair "
    		"processing or an input directory for batch processing.\nIf you need help, type 'calculateVOT.py -h' in your "
    		"terminal.\n")
    	sys.exit()







