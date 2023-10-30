import os
from log_processor import log_processor
import json 
from scipy.stats import mannwhitneyu
import numpy as np
import pdb

def non_stationarity_marks(marks_used, load_interactions_memory):

    result_dict = {'true': 0, 'false': 0, 'ned': 0}
    for marks in marks_used:
        num = 0
        denom = 0
        prob = []
        for data in load_interactions_memory:
            # pdb.set_trace()
            if data[1] == marks:
                num += 1
            denom += 1
            prob.append(round(num / denom, 2))
        
        try:
            mid = int(len(prob) / 2)
            results = mannwhitneyu(prob[:mid:], prob[mid+1: : ])
            # pdb.set_trace()
            # print(results)
            if results.pvalue < 0.05: #True
                result_dict['true'] += 1
            else: #False
                result_dict['false'] += 1
        except ValueError as ve: #NED
            result_dict['ned'] += 1

    max_value = max(result_dict.values())
    argmax = max(result_dict, key=result_dict.get)
    return max_value, argmax

def non_stationarity_attributes(attributes_used, load_interactions_memory):

    result_dict = {'true': 0, 'false': 0, 'ned': 0}
    for attributes in attributes_used:
        num = 0
        denom = 0
        prob = []
        for data in load_interactions_memory:
            # pdb.set_trace()
            if attributes in data[2]:
                num += 1
            denom += 1
            prob.append(round(num / denom, 2))
        
        try:
            mid = int(len(prob) / 2)
            results = mannwhitneyu(prob[:mid:], prob[mid+1: : ])
            # pdb.set_trace()
            # print(results)
            if results.pvalue < 0.05: #True
                result_dict['true'] += 1
            else: #False
                result_dict['false'] += 1
        except ValueError as ve: #NED
            result_dict['ned'] += 1

    max_value = max(result_dict.values())
    argmax = max(result_dict, key=result_dict.get)
    return max_value, argmax

        
cur_dir = os.getcwd()
folder_path = cur_dir + "/interactions/open_ended_interactions/"

movie_data_files = []
car_data_files = []

for file_name in os.listdir(folder_path):
    if file_name.endswith("_p4_logs.json"):
        # print(file_name)
        strs = file_name.split('_')
        if 'b' not in strs[1]:
            movie_data_files.append(file_name)
        else:
            car_data_files.append(file_name)

obj = log_processor()
# interactions = obj.get_interactions(folder_path + "stu6_acf_p4_logs.json")
# for idx, i in enumerate(interactions):
#     print(idx)
#     print(i)

result_marks = {'stationary': 0, 'nonstationary': 0, 'noresult': 0}
result_attributes = {'stationary': 0, 'nonstationary': 0, 'noresult': 0}

cnt_marks = {'stationary': 0, 'nonstationary': 0, 'noresult': 0}
cnt_attributes = {'stationary': 0, 'nonstationary': 0, 'noresult': 0}


avg_vis = 0

# for movie in movie_data_files:
for cars in car_data_files:
    # print(movie)
    marks_used = set()
    attributes_used = set()
    load_interactions_memory = []
    interactions = obj.get_interactions(folder_path + cars)
    # interactions = obj.get_interactions(folder_path + movie)
    for idx, i in enumerate(interactions):
        data = i
        mark = data['mark']
        marks_used.add(mark)
        # fields_name = list(data['encoding'].keys())
        attributes = []
        for field_name in ['x', 'y', 'size']:
            if field_name in data['encoding'].keys():
                if 'field' in data['encoding'][field_name]:
                    attributes_used.add(data['encoding'][field_name]['field'])
                    attributes.append(data['encoding'][field_name]['field'])
        load_interactions_memory.append((idx, mark, attributes))
        # print(idx, mark, attributes)
        # pdb.set_trace()
    avg_vis += len(interactions)
    ns_cnt, ns_res = non_stationarity_marks(marks_used, load_interactions_memory)
    # print(movie, end = " ")
    print(cars, end=" ")
    if(ns_res == 'false'):
        result_marks['stationary'] += 1
        cnt_marks['stationary'] += ns_cnt
    else:
        result_marks['nonstationary'] += 1
        cnt_marks['nonstationary'] += ns_cnt

    print(ns_res, end = " ")
    ns_cnt, ns_res = non_stationarity_attributes(attributes_used, load_interactions_memory)
    if(ns_res == 'false'):
        result_attributes['stationary'] += 1
        cnt_attributes['stationary'] += ns_cnt
    else:
        result_attributes['nonstationary'] += 1
        cnt_attributes['nonstationary'] += ns_cnt
  
    print(ns_res)
    
print(result_marks)
print(cnt_marks)
print(result_attributes)
print(cnt_attributes)
print("Average number of visualizations: ", round(avg_vis / len(movie_data_files), 2))