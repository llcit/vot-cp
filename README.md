
VOT-CP (VOT coding and predictions)
=======

Ernesto R. Gutiérrez Topete (ernesto.gutierrez@berkeley.edu), **lead developer**.\
Richard Medina, **project lead**.


## Description

VOT-CP is a Python program that allows for the automatic codification of phonetically aligned data in order to obtain voice onset time (VOT) predictions. This program makes use of [AutoVOT](https://github.com/mlml/autovot)'s model for generating the VOT calculations. When provided with a TextGrid that contains a word and phone tier, the program will identify all word-initial stop consonants of interest. VOT-CP will then generate and populate a new tier that can be used by AutoVOT to find the burst and onset of voicing for all selected segments. 

The program takes in:

1. `.wav` files, and
2. `.TextGrid` files with time-aligned word and phone tiers.

And it returns

1. a new TextGrid file that contains: 
  * the original word and phone tiers,
  * a tier with all the stops of interest, and 
  * a tier with VOT predictions generated by AutoVOT's model.

This program is designed to work with cross-linguistic data, and with data in various formats, for example:
  * multiple speakers in the same recording, 
  * audio files with duplicate or distinct channels, 
  * audio files with various sampling frequencies, 
  * and more.

VOT-CP does not modify the original files in any way. However, users are advised to keep a backup of all files processed with this software. Please see below for more information on the input format that is allowed or not allowed for the data processed with this program; note that some of these requirements differ from the AutoVOT program's input requirements.

This is a beta version. Any reports of bugs, suggestions for improvements to the software or the documentation, or questions are welcome and greatly appreciated. Please direct all communication to Ernesto R. Gutiérrez Topete (@egutierrez, ernesto.gutierrez@berkeley.edu).

---

### Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Tutorial](#tutorial)
    * [Python script usage](#python-script-usage)
    * [Command-line usage](#command-line-usage)
4. [Citing VOT-CP](#Citing)
5. [Acknowledgements](#acknowledgements)
6. [License](#license)

## Installation

### Dependencies

In order to use this program, you will need the following installed in your machine:
* [GCC, the GNU Compiler Collection](http://gcc.gnu.org/install/download.html)
  - (Only if needed -- most systems already have this installed)
* [Python (3)](https://www.python.org/downloads/)
* Python dependencies:
  - (see instructions below)
* For macOS users, complete either of the next two steps (if needed):
  - Install [Xcode](http://itunes.apple.com/us/app/xcode/id497799835?ls=1&mt=12)
  - Download the [Command-line Tools for Xcode](http://developer.apple.com/downloads) as a stand-alone package.

### Command-line installation

_VOT-CP is available from Github_.

Open a Terminal window and navigate to the directory (ie, folder) where you would like to install the program. Then run the following command: (RM will add this [final address below])

  ```
  $ git clone https://github.com/...
  ```

After installing the program, navigate to the directory where the software is installed and run the following command in your terminal window to install all dependencies: 

  ```
  $ pip install -r "requirements.txt"
  ```

To update the VOT-CP software when newer versions are released, navigate to the directory where the software is installed and then run:

  ```
  $ git pull origin main
  ```


If you are new to Github, you can find helpful tutorials and tips for getting started here:

https://help.github.com/articles/set-up-git


## Usage

### User-provided files

VOT-CP allows for more flexibility when processing your data, for it manages certain format settings that AutoVOT does not. However, there are still certain limitations to the format of the data that can be submitted as input to the software. 

#### Audio files:

What is **allowed**:
* Can be any length (note that longer files will likely take longer to process).
* Can have one or multiple channels (see below for instructions on selecting particular channels).
* Can have any sampling frequency (provided that it is accepted by [Praat](https://www.fon.hum.uva.nl/praat/)).

What is **required**:
* Must be `.wav` files; other formats are not accepted.
* Must have a sample width of 2.
* Must not be compressed files.
* Must have stop segments in the 'phone' tier that are at least 25 ms long.
  - if this is not a severe violation (eg, 22-ms segment), VOT-CP will automatically make corrections.
* Must have stop segments that are over 20 ms apart from each other.
  - if this is not a severe violation (eg, 18 ms apart), VOT-CP will automatically make corrections.

#### TextGrid files:

What is **allowed**:
* Tier names can have any capitalization, for example:
  - WORDS
  - Words
  - words
  - wOrDs
* Tier names can have any arbitrary name (provided that the word and phone tiers match), for example:
  - 'Word', 'Phone' [both singular]
  - 'words', 'phones' [both plural]
  - 'Mary - words', 'Mary - phones' [consistent spelling and spacing]
  - 'Word-john', 'phone-John' [both singular; identifying information '-john' is placed and spelled consistently; capitalization is irrelevant for tier names]

What is **required**:
* Must be `.TextGrid` files in [full text format](https://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html)(ie, the default); other formats are not accepted.
* Must have a time-aligned word tier
* Must have a time-aligned phone tier
* Must have an identical interval boundary (not close enough, identical) between word onset and start of first phone
* While the orthography (ie, alphabet) of the word tier does not matter, the label of the phone tier must use the Latin alphabet or IPA.
* Phone labels can use any romanization system (if the language does not use Latin orthography), as long as the initial element of a stop label is a stop character (ie, \<p>, \<t>, \<k>, <ʈ>, <ɟ>, etc.), for example:
  - Allowed: 't', 'p0', 'kw', 'kk', etc.
  - Not allowed: 'at', '1p', '-k', etc.

*Note that phone labels that don't use IPA or romanization will be ignored. Furthermore, any other tiers that do not contain the name 'phone(s)' or 'word(s)' (eg, 'lexical items', 'notes' or 'utterances') will also be ignored.

What is **prohibited**:
* Tier names with inconsistent naming, for example:
  - 'Word', 'Phones' [mixture of singular and plural]
  - 'words', 'phone' [mixture of singular and plural]
  - 'Mary's - words', 'Mary - phones' [inconsistent spelling]
  - 'Mary - words', 'Mary-phones' [inconsistent spacing]
* Unequal number of word and phone tiers, for example:
  - 'Phones', 'Words-Mary', 'Phones-Mary' [an additional 'Phones' tier]
* Using the word 'stops' in any of the tier names, for example:
  - 'stops'
  - 'stops tier'
  - 'Tier stops'
  - 'ThisIsMyStopsTier'
* Any tiers with repeated names, for example:
  - 'phones', 'words', 'phones', 'words'
* Any tiers with no name.

*Note that, to ensure precise matching of the phone and word tiers, both tiers must be identical in spelling, changing only in the words 'phone(s)' and 'word(s)'.

### Using VOT-CP

**VOT-CP can be used to process one pair of wav and TextGrid files at a time or it can be used to process an entire corpus at once. See the sections below for more information.**

#### Single wav-TextGrid pair processing

In Python, to process one pair of wav and TextGrid files at a time, use the function 
```
calculateVOT(wav, TextGrid)
```
The positional arguments for this function are: `wav` and `TextGrid`, the two files that will be processed. See below for more information on the optional arguments.

***It is recommended that new users first try the single-pair processing on a couple of data to identify the desired parameters for your corpus, before proceeding to process the entire corpus. Depending on the corpus size, the program may take a long time to process all of the data. Single-pair processing will take less time, allowing the user to make re-adjustments to the parameters quickly, in order to find the desired settings.*

#### Batch processing

To process multiple wav and TextGrid files at once, use the function
```
calculateVOTBatch(input)
```
The sole positional argument for this function is: `inputDirectory`, a string-based path which indicates the name (and location) of the directory where the wav and TextGrid files are located. If no such directory exists or if the directory name that was entered leads to an empty directory, the program will terminate immediately.

Note that this function will iterate through all items in the corpus and identify all wav and TextGrid files, ignoring any files with other extensions or any sub-directories. Once wav and TextGrid files are identified, they will be paired with each other on the basis of their names; that is why it is important that the files match in name, for example:

  * Allowed: `S01_interview.wav` and `S01_interview.TextGrid` as well as `John.wav` and `John.TextGrid`
  * Not allowed: `S01_interview.wav` and `S1_intvw.TextGrid` nor `Mary-audio.wav` and `Mary-transcription.TextGrid`

While capitalization will be irrelevant in matching wav and TextGrid files, spelling, punctuation, and spacing will be essential.

***It is recommended that new users first try the single-pair processing on a couple of data to identify the desired parameters for your corpus, before proceeding to process the entire corpus. Depending on the corpus size, the program may take a long time to process all of the data. Single-pair processing will take less time, allowing the user to make re-adjustments to the parameters quickly, in order to find the desired settings.*

#### Arguments

The optional arguments for single-pair processing and batch processing are: 

| Arguments          | Description |
| :---               | :---        |
| `stops`            | a list of phone labels to look for and process. For example: `['p','k']` if only bilabial and velar stops are of interest. Remember that the labels entered in this argument must match the labels in the TextGrid file, for example `['pp',"t'",'kw']` (two \<p>, a \<t> plus an apostrophe, and a \<k> plus a \<w>)). If nothing is entered for this parameter, the program will default to all voiceless singleton stops recognized by the IPA (and their geminate forms): `['p', 't', 'ʈ', 'c', 'k', 'q', 'ʔ', "p'", "t'", "k'", 'pp', 'tt', 'ʈʈ', 'cc', 'kk', 'qq', 'ʔʔ']`. <br> <br> **Note that the program (1) is case-sensitive to the phone labels and (2) looks for an exact match, so type the labels as they appear in your TextGrid.* |
| `outputDirectory`  | a string to be used as the name for the directory (ie, folder) where the output will be stored. If the directory already exists, the output will be stored there; otherwise, a new directory will be created with the name provided. If nothing is entered for this parameter, the program will default to `'output/'`. |
| `startPadding`     | a number to indicate the amount of time, *in milliseconds*, to be added to (or reduced from) the phone's start boundary. The maximum is 25 ms (or 0.025 sec), and the minimum is -25 ms (or -0.025 sec). Note that a negative value will shift the boundary left (that is, increase the segment window) and a positive value will shift the boundary right (that is, decrease the segment window). This parameter can be used when a corpus consistently marks the start boundary in its stops a little too early or a little too late. If nothing is entered for this parameter, the program will default to `0` ms (ie, no padding). |
| `endPadding`       | a number to indicate the amount of time, *in milliseconds*, to be added to (or reduced from) the phone's end boundary. The maximum is 25 ms (or 0.025 sec), and the minimum is -25 ms (or -0.025 sec). Note that a negative value will shift the boundary left (that is, decrease the segment window) and a positive value will shift the boundary right (that is, increase the segment window). This parameter can be used when a corpus consistently marks the end boundary in its stops a little too early or a little too late. If nothing is entered for this parameter, the program will default to `0` ms (ie, no padding). |
| `preferredChannel` | a number (*an integer*) that indicates the channel from the wav file to be used when obtaining VOT predictions. This parameter should be used if and only if the wav file contains multiple channels, and the first channel is not the one that contains the acoustic information. If nothing is entered for this parameter, the program will default to channel `1`. |
| `distinctChannels` | a boolean (ie, `True` or `False`) that indicates whether or not there are different speakers in the recording and transcription, each with a distinct channel. This occurs when two speakers are recorded simultaneously with different microphones. If nothing is entered for this parameter, the program defaults to `False`, indicating that the acoustic information for the speaker(s) in the transcription can be found in the `preferredChannel`. If the value `True` is entered for this parameter, the program will assume that there are as many channels in the wav file as there are speakers in the TextGrid file; it will then proceed to match the first pair of 'phone' and 'word' tiers to the first channel and any subsequent tier pairs to subsequent channels. |
| `trainedModel`     | a string-based path that indicates the location of a trained model for your corpus. If nothing is entered in this parameter, the program will default to AutoVOT's latest pre-trained model (v. 0.94). Otherwise, the program will use the newly trained model you indicate. |

### Additional notes

1. VOT-CP is able to process data from multiple speakers within a TextGrid (ie, multiple 'phone' and 'word' tiers in the same file), regardless of the number of channels in the wav file. In fact, if multiple phone-word tier pairs are identified in the TextGrid file, the program will automatically process all of them.

2. This program makes use of AutoVOT's latest VOT prediction model ([AutoVOT v. 0.94](https://github.com/mlml/autovot/releases/tag/0.94)). 
    * When accurately aligned data are fed to this model, it provides VOT predictions with high accuracy. If the data are not aligned accurately or if the segment windows are too big or too small, the accuracy of the predictions will decrease.
    * The current model has been trained to predict VOT for voiceless stops; in its current form, it does not support calculations of negative VOT (ie, lead voicing). 
      - Although I can say, anecdotally, that accuracy of VOT predictions for negative VOT is above chance, it is not as high as prediction accuracy for positive VOT. However, I have not investigated this issue systematically.
      - If voiced stops (eg, 'b' or 'g') are entered for processing using VOT-CP, the program will show a `WARNING` about lead voicing. The warning is only presented once during single-pair processing, but it will be presented once for each pair processed during batch processing.
        - If the language you study uses pre-voicing, you can still obtain VOT calculation for voiced stops using this program; however, manual verification and corrections of the output is **strongly** encouraged.
        - If you study a language that does not produce (much) pre-voicing, you can enter voiced labels (eg, 'd' or 'g' produced with short-lag voicing) and ignore the warning.
        - Finally, if you enter voiced stop labels for processing, but they are not found in the corpus, the program will not present the warning.

3. After processing your data, look for any `ERROR` messages printed on the screen. They will indicate if any data were not processed and the reason why. Users are specially encouraged to look for error messages during batch processing. Also, look for `WARNING` messages; they will indicate if something was off about your data but corrected by VOT-CP.

4. The user is advised to manually check the output data from this program. Although AutoVOT's model provides high accuracy predictions, occasional manual corrections may be required.

5. If VOT-CP does not meet your current needs based on particular transcription norms for the language(s) you study or corpus format, get in touch with me to see how the program can be re-adjusted to meet those needs.

## Tutorial

VOT-CP is a Python library that can be used within another Python script or directly from your terminal window. Both methods support single-pair and batch processing. Below is a brief tutorial for using this program from another Python script, followed by another tutorial that performs the same actions directly from the command line.

### Python script usage

The following code blocks exemplify how to use the VOT-CP program, under different conditions, in your Python script. Make sure your script is located in the same directory where you saved the VOT-CP program.

\
**1. Single-pair processing with all default settings:**
```
from calculateVOT import * 

calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid")
```

Note that you first need to import the program. For this execution, the program will default to (1) all voiceless (singleton and geminate) stops, (2) the `output/` directory, (3) no padding to the start and end boundaries for the stop segments, and (4) channel `1` of the audio for all speakers identified in the TextGrid.

\
**2.1. Single-pair processing with specific stops:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", ['p'])
```

For this execution, the program will only look for (word-initial) 'p' tokens and process them. This execution will ignore any other stops found in the transcription.

\
**2.2. Single-pair processing with specific stops:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", ['t', 'T', 'tt'])
```

For this execution, the program will only look for phone labels 't', 'T', and 'tt'. Use this approach if the TextGrid contains labels that are lowercase and uppercase. This is done, for example, in corpora to distinguish between non-emphatic (ie, plain) and emphatic (ie, pharyngealized) stops, as well as geminate stops.

\
**2.3. Single-pair processing with specific stops:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", ['k', 'kw'])
```

For this execution, the program will only look for the phone labels 'k', and 'kw'. Use this approach if the TextGrid contains labels that specify additional features. This is done, for example, in some corpora to distinguish between plain and labialized stops.

\
**3. Single-pair processing with a specific output directory name:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", [], "vot-predictions")
```
or
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", outputDirectory = "vot-predictions")
```

Both of these executions provide the name "vot-predictions" for the name of the output directory, as opposed to using the default "output" name. Note that you need to include a parameter for `stops`, even if it's an empty list, to avoid writing the parameter names; otherwise use the argument name to specify the specific parameter.

\
**4. Single-pair processing with added padding:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", startPadding=-20, endPadding=20)
```

This execution moves the start boundary to the left by 20 ms (increasing the phone window) and the end boundary to the right by 20 ms (increasing the phone window even further).

\
**5. Single-pair processing with specific channel:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", preferredChannel = 2)
```

This execution identifies the second channel in the audio file as the channel to be looked at when obtaining VOT calculations. Regardless of how many speakers are present in the TextGrid (ie, one or more pairs of phone-word tiers), all data will be analyzed using the acoustic information in the second channel. The first channel will be ignored completely.

\
**6. Single-pair processing with distinct channels:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", distinctChannels=True)
```

This execution tells VOT-CP that there are multiple channels present in the audio file and multiple speakers represented in the TextGrid. The program will continue by linking the first channel to the first pair of phone-word tiers, the second channel to the second pair of phone-word tiers, and so on. 

Note that if `distinctChannels` is set to `True` and there isn't an equal number of channels and tier pairs (eg, two channels and one tier pair), the program will terminate immediately.

\
**7. Single-pair processing with newly trained model:**
```
calculateVOT("S01_map-task.wav", "S01_map-task.TextGrid", trainedModel = "myVOTmodel.model")
```

For this execution, VOT-CP will use the model that you have trained (using AutoVOT's program) for your data and indicated in the function call. Refer to AutoVOT's documentation for more information on how to train your own model.

\
**8. Batch processing with all default settings:**
```
calculateVOTBatch("input_corpus")
```

For this execution, the program will iterate through all files in the directory `input_corpus/` in order to begin pairing files and processing them. The output files will be returned to the `output/` directory. 

Note that you can adjust the rest of the parameters for `calculateVOTBatch` just as you would with the `calculateVOT` function (ie, single-pair processing).

### Command-line usage

The following code blocks exemplify how to use the VOT-CP program, under different conditions, directly from your terminal window.

Below are the arguments accepted through this mode. The two dashes plus the lowercase word is a mandatory keyword indicating the argument, and the uppercase word is to be replaced by the argument you are passing for processing.

```
[--wav WAV]
[--TextGrid TEXTGRID]
[--inputDirectory INPUTDIRECTORY] 
[--stops STOPS]
[--outputDirectory OUTPUTDIRECTORY]
[--startPadding STARTPADDING] 
[--endPadding ENDPADDING]
[--preferredChannel PREFERREDCHANNEL]
[--distinctChannels DISTINCTCHANNELS]
[--trainedModel TRAINEDMODEL]
```

Although all arguments are marked as optional, the program will automatically engage single-pair processing mode if a wav file and a TextGrid file are *both* submitted for processing. If these arguments are left blank (or at least one) but instead an inputDirectory path is submitted, the program will automatically engage batch processing mode. Note that if all three arguments are submitted (wav, TextGrid, and inputDirectory), the program will only engage single-pair processing, ignoring the inputDirectory. For more help with these and other optional arguments, type 'calculateVOT.py -h' in your terminal.

To use command-line processing, open a Terminal window and navigate to the directory where you have stored the VOT-CP program.

\
**1. Single-pair processing with all default settings:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid
```

For this execution, the program will default to (1) all voiceless (singleton and geminate) stops, (2) the `output/` directory, (3) no padding to the start and end boundaries for the stop segments, and (4) channel `1` of the audio for all speakers identified in the TextGrid.

\
**2.1. Single-pair processing with specific stops:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --stops p k
```

For this execution, the program will only look for (word-initial) 'p' and 'k' tokens and process them. This execution will ignore any other stops found in the transcription. Note that in this case, all stops are presented without quotes, separated only by a blank space.

\
**2.2. Single-pair processing with specific stops:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --stops t T tt
```

For this execution, the program will only look for phone labels 't', 'T', and 'tt'. Use this approach if the TextGrid contains labels that are lowercase and uppercase. This is done, for example, in corpora to distinguish between non-emphatic (ie, plain) and emphatic (ie, pharyngealized) stops, as well as geminate stops.

\
**2.3. Single-pair processing with specific stops:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --stops k kw
```

For this execution, the program will only look for the phone labels 'k', and 'kw'. Use this approach if the TextGrid contains labels that specify additional features. This is done, for example, in some corpora to distinguish between plain and labialized stops.

\
**3. Single-pair processing with a specific output directory name:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --outputDirectory "vot-predictions"
```

This execution provides the name "vot-predictions" for the name of the output directory, as opposed to using the default "output" name.

\
**4. Single-pair processing with added padding:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --startPadding -20 --endPadding 20
```

This execution moves the start boundary to the left by 20 ms (increasing the phone window) and the end boundary to the right by 20 ms (increasing the phone window even further).

\
**5. Single-pair processing with specific channel:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --preferredChannel 1
```

This execution identifies the second channel in the audio file as the channel to be looked at when obtaining VOT calculations. Regardless of how many speakers are present in the TextGrid (ie, one or more pairs of phone-word tiers), all data will be analyzed using the acoustic information in the second channel. The first channel will be ignored completely.

\
**6. Single-pair processing with distinct channels:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --distinctChannels True
```

This execution tells VOT-CP that there are multiple channels present in the audio file and multiple speakers represented in the TextGrid. The program will continue by linking the first channel to the first pair of phone-word tiers, the second channel to the second pair of phone-word tiers, and so on. 

Note that if `distinctChannels` is set to `True` and there isn't an equal number of channels and tier pairs (eg, two channels and one tier pair), the program will terminate immediately.

\
**7. Single-pair processing with newly trained model:**
```
python calculateVOT.py --wav S01_map-task.wav --TextGrid S01_map-task.TextGrid --trainedModel "myVOTmodel.model"
```

For this execution, VOT-CP will use the model that you have trained (using AutoVOT's program) for your data and indicated in the command line. Refer to AutoVOT's documentation for more information on how to train your own model.

\
**8. Batch processing with all default settings:**
```
python calculateVOT.py --inputDirectory "input_corpus"
```

For this execution, the program will iterate through all files in the directory `input_corpus/` in order to begin pairing files and processing them. The output files will be returned to the `output/` directory. 

Note that you can adjust the rest of the parameters just as you would with single-pair processing.

## Citing VOT-CP

VOT-CP is a general purpose program and doesn't need to be cited, but if you feel inclined, it can be cited in this way:

...(?) RM: I'll add this after we move the repo to its permanent location.

However, if you use this program to analyze data that are presented at conferences or published, it is recommended that you [cite the AutoVOT program](https://github.com/mlml/autovot/blob/master/README.md#citing).

## Acknowledgements

This software was developed as part of a summer internship hosted by [The Language Flagship Technology Innovation Center (Tech Center)](https://thelanguageflagship.tech/). 

#### Development support

* Dr. Richard Medina, from the Tech Center, was the primary research advisor who guided the development of this program.
* Dr. Suzanne Freynik and Dr. Aitor Arronte Alvarez, both from the Tech Center, also provided support during the development phase.

#### Programming support

* I want to acknowledge Yannick Jadoul, Dr. Thea Knowles, and Dr. Joseph Keshet who answered questions regarding their own programs ([Parselmouth](https://parselmouth.readthedocs.io/en/stable/) and [AutoVOT](https://github.com/mlml/autovot)).
* I especially want to thank Yannick Jadoul for providing invaluable support in other aspects that aided in the development of the VOT-CP program.

#### Cross-linguistic corpora

Finally, I want to thank all the researchers (listed below in alphabetical order of the language), who have made their own corpora available to the public or shared them with me to allow me to test VOT-CP with cross-linguistic data. I also want to acknowledge Dr. Nawar Halabi and Khia A. Johnson for answering questions regarding the languages they study and their corpora.

* Arabic: [Arabic Speech Corpus](http://en.arabicspeechcorpus.com/)
  - Dr. Nawar Halabi
* Cantonese: [SpiCE: Speech in Cantonese and English](https://dataverse.scholarsportal.info/dataset.xhtml?persistentId=doi:10.5683/SP2/MJOXP3)
  - Khia A. Johnson
* (American & Indian) English: [The Wildcat Corpus of Native and Foreign-Accented English](https://groups.linguistics.northwestern.edu/speech_comm_group/wildcat/)
  - Dr. Ann Bradlow (and colleagues)
* Korean: [Seoul Corpus](http://www.tyoon.net/scripts/praat/exphon2/SeoulCorpus.pdf)
  - Dr. Kyuchul Yoon and Dr. Weonhee Yun (and colleagues)
* Russian: [MaSS - Multilingual corpus of Sentence-aligned Spoken utterances](https://github.com/getalp/mass-dataset)
  - Marcely Zanon Boito (and colleagues)
* Spanish: [Archive of L1 and L2 Scripted and Spontaneous Transcripts And Recording (ALLSSTAR) Corpus](https://speechbox.linguistics.northwestern.edu/#!/home)
  - Dr. Ann Bradlow (and colleagues)


## License

*add license* RM: I'll add this later, but it will probably be MIT (https://choosealicense.com/licenses/mit/)
