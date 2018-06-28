# RecSys_Challenge_2018_JKU_Gamma
Source code for generating the final submission of JKU Gamma for the RecSys challenge 2018.

For generating the submission file, multiple files have to be generated first:
1. pidtotracks file with createTrackDict.create_pid_dict(number of files to consider)
2. fullModeD2Vxxx file with module_cluster.generate_doc2vec_files(file list)
3. wordDict_withoutIrrelevant file with module_names_removeIrrelevantWords.create_wordDict()
4. lookupdict file with readData.create_lookup()
5. count_chain_file_dict file with module.markov.init_pickle_files()

After that, executing module_controller_trackSubmission.py generates the submission.
