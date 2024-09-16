
data
`data/FDdata`文件夹下包含17类apps对应的开源apps信息。
`data/Saved_Commit_Data.csv`包含我们获得的1495441个commit_link中的信息。
`data/Saved_Commit_Data_After_First_Filter.csv`包含通过heuristic filter后的1167775个commit_link中的信息。
`data/Saved_Commit_Data_After_Second_Filter.csv`包含通过NLP filter后的41604个commit_link中的信息。
`data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv`包含通过PI classification filter后并且进行PI类别统一之后的14467个commit links中的信息。
`data/perfobench_without_human_check.csv`包含我们得到的Matched APK-Project Pairs信息。
`data/perfobench`包含我们经过human check之后得到的816个APKs和他们对应的1051个commit 中的相关信息组成的benchmark PerfoBench.

code
运行`stage_1_1_crawl_GitHub_Repos.py`, `stage_1_2_crawl_GitHub_Commits.py`, `stage_1_3_get_all_commits_info.py`从Fdroid中获得所有github仓库和他们中的commits。
运行`stage_2_1_heuristic_filtering.py`, `stage_2_2_NLP_filtering.py`, `stage_2_3_NLP_filtering_result_handling.py`, `stage_2_4_PI_Classification.py`, `stage_2_5_PI_Classification_result_handling.py`进行commit link的过滤和PI分类。
运行`stage_3_PI_info_identification.py`获得PI的详细信息。



please install ollama
