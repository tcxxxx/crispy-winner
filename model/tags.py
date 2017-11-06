#!/usr/bin/python

import os
import sys

# target_diseases_shouldBePassedIn = ['Ingrowneyelash', 'Acne','rosacea', 'Disease1ForTest', 'Disease2ForTest', 'Disease3ForTest']

def backup_datasetTxt():
    pass

def get_all_diseases(path):
    extension = ".txt"
    disease_dict = {} # disease_name: image set directory
    temp = ''
    for item in os.listdir(path):
        # here we filter all the files
        if extension in item:
        	# The end of each disease files are always: -($TIMESTAMP).txt
        	# for example: melanoma-1507572279.txt, Ingrown-Eyelash-1507728821.txt
        	# So the part before the dot should be: DISEASE-TIMESTAMP
            disease_name = item.split('.')[0][:-11]
            disease_name = temp.join(disease_name.split('-'))
            disease_dict[disease_name.lower()] = item[:-4]
    return disease_dict

def tag_disease(target_diseases):
    path = str(os.getcwd() + '/dataset')
    extension = ".txt"
    lines = []
    disease_dict = get_all_diseases(path)
    # print disease_dict
    for d in target_diseases:
        if d.lower() in disease_dict.keys():
            disease_dir = disease_dict[d.lower()]
            with open(path + '/' + disease_dir + extension, 'r+') as F: 
                lines.append(F.readlines())  	
        else:
            # Add downloading later.
            pass
            
    backup_datasetTxt()
    with open('./' + 'dataset' + extension, 'w+') as F:
        for tagNum in range(0, len(lines)):
            for i in lines[tagNum]:
                F.write(i.strip('\n') + " " + str(tagNum) + "\n")
                
if __name__ == "__main__":
    target_diseases_list = []
    disease_num = len(sys.argv) - 1
    print "number of diseases:" + str(disease_num)
    
    file = open('sub.list')
    sub_list = file.readlines()
    for dNo in range(1, disease_num + 1):
        symptoms_list = []
        print sys.argv[dNo].strip(',')
        for symptom in sub_list:
            if str(dNo) in symptom:
                print symptom.strip('\n')
        target_diseases_list.append(sys.argv[dNo].strip(','))
    print target_diseases_list
    # print sub_list
    file.close()

    # tag_disease(target_diseases_list)
