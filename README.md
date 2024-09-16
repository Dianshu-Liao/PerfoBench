
# Data
- `data/FDdata:` Contains information on 17 app categories from open-source apps.
- `data/Saved_Commit_Data.csv:` Includes 1,495,441 commit links.
- `data/Saved_Commit_Data_After_First_Filter.csv:` Includes 1,167,775 commit links after heuristic filtering.
- `data/Saved_Commit_Data_After_Second_Filter.csv:` Contains 41,604 commit links post-NLP filtering.
- `data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv:` Contains 14,467 commit links after PI classification.
- `data/perfobench_without_human_check.csv:` Holds information on matched APK-Project pairs.
- `data/perfobench:` Contains 816 APKs and their corresponding 1,051 commits after human verification.
- `data/all_apks_with_simple_name/:` Contains APKs for the 816 apps in PerfoBench.
- `data/apks_without_human_check/:` Holds APK files before human verification, including 816 APKs from PerfoBench and 265 discarded APKs.


# Code
## 1. Repository and Commit Collection
- `stage_1_1_crawl_GitHub_Repos.py:` Collect repositories from F-Droid.
- `stage_1_2_crawl_GitHub_Commits.py:` Collect commits.
- `stage_1_3_get_all_commits_info.py:` Gather all commit info.

## 2. Commit Link Filtering and PI Classification:
- `stage_2_1_heuristic_filtering.py:` Apply heuristic filtering.
- `stage_2_2_NLP_filtering.py:` Perform NLP-based filtering.
- `stage_2_3_NLP_filtering_result_handling.py:` Handle NLP filtering results.
- `stage_2_4_PI_Classification.py:` Classify PIs.
- `stage_2_5_PI_Classification_result_handling.py:` Handle classification results.

## 3. PI Information Extraction:
- `stage_3_PI_info_identification.py:` Extract PI root causes, solutions, and locations from code diffs.


## 4. APK and Project Code Retrieval:

- `stage_4_1_commit_release_time_crawling.py:` Crawl commit release times.
- `stage_4_2_download_apks_in_Fdroid_pages.py:` Download APKs from F-Droid.
- `stage_4_3_download_apks_in_github_release.py:` Download APKs from GitHub releases.
- `stage_4_4_get_necessary_apks_info.py:` Obtain necessary APK information.
- `stage_4_5_download_commit_project_pairs.py:` Download APK-project pairs.
- `stage_4_6_check_commit_project_pair.py:` Verify APK-project pairs.



# Requirements:
Install [Ollama](https://ollama.com/download) to support Llama3 for running the code.





