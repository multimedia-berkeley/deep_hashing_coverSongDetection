# Cover Song Detection

This is a music informatics retrieval project based on TJ's paper of live song detection. This proejct changes the focus to cover song detection using K-pop dataset, and tries to achieve the following goals:

1. Reconstruct TJ's hashprint framework in Python

2. Optimize parameters of hashprint framework for K-pop dataset live song detection and cover song detection

3. Find a fast and systematic way to optimize parameters of hashprint framework

4. Develop additional methods to compare with and improve this existing framework

5. Develop a real world application/platform based on completed design


# Database

## Database Structure

Due to the limitation of Korean characters, all singers and music names are preprocessed and converted to index and saved in `artist_index.json` and `title_index.json`, and the `music_annotation.db` file is converted to `music_indexed.db`. These are done by `cleanDatabase.py`.

| column    | description                                   |
|-----------|-----------------------------------------------|
| title     | title of the song                             |
| title_id  | title_id of the song                          |
| artist    | artist of the song                            |
| artist_id | artist_id of the song                         |
| cover     | 1 if is cover song, else 0                    |
| vid       | youtube video download link                   |
| soundsrc  | content of the song, specified by index below |
(Only relevant columns are listed)

| index | meaning                              |
|-------|--------------------------------------|
| 0     | master                               |
| 1     | master with little noise             |
| 2     | noisy track                          |
| 3     | live performance/non-live instrument |
| 4     | live performance/live instrument     |
| 5     | MR                                   |
| 6     | Karaoke                              |
| 7     | Instrumental                         |
| 8     | master+instrument                    |
| 9     | remix                                |
| 10    | unrelated                            |

## Downloaded Music File Directory Structure

All the files are downloaded into the following directory structure by file `downloadMusic.py`, the audio files are in .mp3 format downloaded by `youtube-dl` and converted to mp3 by `ffmpeg` and `ffprobe`

```
> pwd
/home/jackye/hashprint

> tree
.
├── music_annotation.db
│ 
├── music_indexed.db
│ 
├── artist_index.json
│ 
├── title_index.json
│ 
├── master (content == 0 or 1)
│   ├── singer1
│   │   ├── music1.mp3
│   │   ├── music2.mp3
│   │   ├── music...
│   ├── singer2
│   │   ├── music1.mp3
│   │   ├── music2.mp3
│   │   ├── music...
│   ├── singer...
├── live (content == 3 or 4)
│   ├── singer1
│   │   ├── music1.mp3
│   │   ├── music2.mp3
│   │   ├── music...
│   ├── singer2
│   │   ├── music1.mp3
│   │   ├── music2.mp3
│   │   ├── music...
│   ├── singer...
├── cover (cover == 1 and title.matchOriginalSinger())
│   ├── singer1
│   │   ├── music1.mp3
│   │   ├── music2.mp3
│   │   ├── music...
│   ├── singer2
│   │   ├── music1.mp3
│   │   ├── music2.mp3
│   │   ├── music...
│   ├── singer...

```

# Task 1: Reconstruct TJ's hashprint framework in Python

Original framework is in MATLAB, and this new Python framework is implemented using `librosa` audio analysis library and standard `numpy` libraries.

## Documentation

* `runHashprint.py`

Main function for whole testing program, use `python3 runHashprint.py` to start

* `testMap.py`

Test configuration file, control number and types of tests involved in the run

* `AudioTransform.py`

Contains classes that produce audio transformation functions, such as producing spectrograms, pitch-shift, time-stretch effects

* `Hashprint.py`

Contains core functions that implement the hashprint algorithm

* `CacheUtils.py`

Contains caching functions for easy use

* `ResultAnalysis.py`

Contains analysis classes and saves results to `results` folder `csv` files

* `extendQuery.py`

Contains functions that extend existing database files by transformations

## Cache Format

In testMap, there're two maps specifying (1) types of audio transformation to produce spectrogram (referred as `audioTransFun`) and (2) types of audio effects applied for hashprint sets of each song (referred as `hashprintTransFun`). For example, the cached files are in the format:
```
CQT_TJ_HOP64/
├── PITCH_SHIFT_3
│   ├── 11
│   │   ├── 1.mp3
│   │   │   ├── hashprint_CQT_TJ_HOP64_PITCH_SHIFT_3_11_1.mp3_0.npy
│   │   │   ├── hashprint_CQT_TJ_HOP64_PITCH_SHIFT_3_11_1.mp3_1.npy
├── master
│   ├── 11
│   │   ├── 1.mp3.npy (spectrogram)
│   │   └── 2.mp3.npy
│   └── 22
│       └── 3.mp3.npy
├── model
│    ├── 11.npy
│    └── 22.npy
├── live
│   ├── 11
│   │   ├── hashprint_CQT_TJ_HOP64_PITCH_SHIFT_3_11_1.mp3_0.npy
│   │   └── hashprint_CQT_TJ_HOP64_PITCH_SHIFT_3_11_2.mp3_0.npy
│   └── 22
│       └── hashprint_CQT_TJ_HOP64_PITCH_SHIFT_3_11_3.mp3_0.npy

```

where `CQT_TJ_HOP64` is a type of `audioTransFun`, and  `PITCH_SHIFT_3` is a type of `hashprintTransFun`. Because for each `audioTransFun`, the model and query hashprint does not change, and for each `hashprintTransFun` underneath, we can define one database for matching.

## Result Format

All analysis results are stored in `results` folder. File `analysis.csv` gives aggregated result for comparison, and each individual analysis file gives detailed decomposition score of each artist.

`analysis.csv` has columns `audioTransName`, `hashprintTransName`, `testName`, `total accuracy`, `mean accuracy of artists`, `number queries`, `number artists`

Each specific analysis file has columns `artistID`, `accuracy`, `number queries`, `number masters`


# Task 2: Optimize parameters of hashprint framework for K-pop dataset live song detection and cover song detection

## Improvements of the testing framework

From September to mid November, all tests are done using MATLAB framework with small size K-pop database. The Result was 72.3% accuracy in general, and by increasing pitch shifts the accuracy was increased to 75.0%. However, the testing framework had the following flaws:

1. database contain too few songs, and most artists only have 2 songs in database, so even a random guess can reach 50% accuracy. By examing some artists in detail, even for artists with more than 2 songs, lots of them are duplicates (having the same title name), which further decreases the reliability of the accuracy.

2. pitch shift was done using SOX framework, which has a fast but badly implemented pitch shift algorithm

3. it was hard to find an open framework to extend pitch shift to more variations in timbre domian

4. the whole live/cover song is passed in as query, which is not really possible for real world applications, and also not fit TJ's query setting that used 6-second duplicates with wihte noise of one live song. 

5. in TJ's MATLAB hashprint algorithm, the raw audio is loaded as steoro, and then the two channels are added together to form mono, and then audio is mannually downsampled using a parameter. The mono and downsample conversion might not yield expected spectrogram due to the limitation of MATLAB CQT framework

From mid November to early December, the python testing framework is designed, and these problems are fixed in the following ways:

1. by obtaining a bigger database, only artists with at least 5 distinct songs are selected for testing

2. the framework compared pitch shift of SOX, Librosa, Audacity, the later ones have same algorithm and produces pitch shift closer to original timbre, so are used in testing.

3. it was still a problem finding a good timbre change framework, so the test right now only have pitch shift and time stretch extensions tested

4. the tests are designed to test both whole song as query, and clips of 10, 20, 30, 40 seconds to see how it affects the result

5. in Python Librosa framework, the mono and downsample can be done with a simple function call, which directly downsample through raw audio read during raw audio sampling phase, so the result should be more reliable, but the tests test both ways and compare results.


## Testing results (keep updating as tests progress)

Current highest test accuracy:

`Live`: **80.2%**

`Cover`: **72.3%**


### Audio transformation tuning 

The accuracy is highest when pitch shift = 3 for both live and cover. the value 3 means 3 up shift and 3 down shift (6 variation copies in total). The time stretch is added further to pitch shift, for example, with 6 variation of pitch shifts, 3 time stretches (half speed, original speed, double speed) are calculated for each song, resulting 18 copies in total. However, too many copies seem not increase the accuracy at all.


### Audio query transformation tuning

The accuracy is highest with 40 second clips, which both increases the accuracy and also increases the query speed. Surprisingly, the accuracy is not very low even with a 10-20 second query (which gives 72% accuracy for live and 67% accuracy for cover). By taking advantage of the this prediction accuracy with small duration audio, the speed of query can be significantly improved, and further real-time stream analysis algorithm can be developed based on this idea.


### Spectrogram parameters tuning

The accuracy of use of Librosa library is indeed much higher than TJ's original manual mono and downsample conversion, as (76.6% vs 46.0%), and (72.3% vs 22.3%) difference for live and cover. The use of Librosa facilitates the tuning of parameters and also significantly increased the database construction speed. Currently the best parameter uses 12 bins each octive, with 96 pitchs per frame.

During TJ's spectrogram to covariance transformation, he did not take care about the cast from complex number spectrogram values to real covariance values, and system automatically discard the imaginary part which may loose information and need to be tested.


### Voting algorithm accuracy boost

Voting algorithm is constructed as: clip audio to X second pieces, run query on each single piece of clip, get the mode of choice as the final query output. This method takes advantage of the accuracy of small clips and try to boost the accuracy. The result shows that this algorithm works for live to boost its accuracy by 5%, but did not work for cover (decrease of 0.03%). 

By investigating the detailed distribution of accuracy, this algorithm turns out to work well for artists with high accuracy but poorly for ones not. Because cover song artists has a more sparse distribution of prediction accuracy, this method did not help boost accuracy after all. Therefore, live song boost proves this is a feasiable algorithm, but more focus will be put to first increase individual artist accuracy for cover songs.



### Possible further speed improvement

1. lots of processes can be processed in parallel which is not yet implemented

2. currently uses grid search method to find optimum, should develop better methods after analyzing the behavior of accuracy in Task 2

3. currently hashprint increases its accuracy by duplicating variations of raw audio and compare against query audio, but this consumes lots of time and space to calculate. One better way might be to standardize the raw audio and query audio (eg. all to C pitch) so comparison only happen once

### Possible further accuracy improvement

1. current model only addresses query against known single artist, but not very practical especially regarding cover song case, because if user knows the artist and the coversong, it's unlikely he/she does not know the original song. TJ states that, different artists have different features so formulate different hashprints, and the features (eigenvectors) are his key tool to compute hashprints. Using this idea, the concept of "artist" can be changed to "genre", or any other categorization methods that can formulate distinct features. Because user might not know the artist, but usually can supply information like what type of music it is, which country, etc.

2. This testing algorithm does not test the hyperparameters for hashprint eigenvector calculation, there're in total 5 parameters (which I assume already optimized by TJ according to his paper) but can still try tuning.

3. try other transformations (STFT, MFCC, etc.) rather than CQT to compute hashprint

4. Currently only top 64 eigenvector features are selected which is not sure enough or too much, and if suitable for all artists. Try develop learning methods like LSTM or one-shot learning neural networks might get better features for computing hashprint, which might be a better fit to use as feature vectors













