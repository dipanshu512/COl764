import math
import sys
from types import DynamicClassAttribute
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as  pd
import numpy as np
import string
import json
import re
from bs4 import BeautifulSoup
from math import log


def get_queries(q_file):
    file = open(q_file,"r")
    contents = file.read()
    contents="<cover>" + contents +"</cover>"
    soup = BeautifulSoup(contents,'xml')
    queries = soup.find_all('query')
    final_queries=[]
    for x in queries:
        final_queries.append(x.get_text())
    return final_queries


def idf(td,ja):
    return math.log(td/ja)

def extract_doc_names(docnames):
    for i in range(0,len(docnames)):
        a=docnames[i].split()
        if(len(a)>1):
            docnames[i]=a[2]
    return docnames

def make_paths(d_file):
    Dict={}
    c_file=pd.read_csv(d_file+"smalldata.csv",sep=',') #have to change to metadata.csv
    pmc=c_file["pmc_json_files"]
    # "cord_uid", "title", "abstract","pdf_json_files",
    pdf=c_file["pdf_json_files"]
    cord_uid=c_file["cord_uid"]
    for i in range (len(c_file)):
        if(not pd.isna(pmc[i])):
            Dict[str(cord_uid[i])]=d_file+pmc[i]
            continue
        elif(not pd.isna(pdf[i])):
            Dict[str(cord_uid[i])]=d_file+pdf[i]
            continue
    #dict contains uid->name of document conating this
    return Dict   
    
    

# def make_tf_idf_dict(Dict1,doc):

if __name__ == '__main__':
    q_file=sys.argv[1]
    top_100file=open(sys.argv[2],'r')
    c_file=sys.argv[3]
    # o_file=sys.argv[4]
    queries=get_queries(q_file)
    docnames=extract_doc_names(top_100file.readlines())
    Dict=make_paths(c_file)
    relevant_doc_text={}
    #make vocabulary 
    #which tags we need to take from the json files?
    Dict1={} #this is (word, [(docno,tf)]), first generate the vocabulary
    for x in Dict:
        with open(Dict[x],'r') as f:
            data=json.load(f)
        bodytext=data['body_text']
        content=""
        for y in bodytext:
            content+=y['text']+" "
        temp_text_array=content.split()
        if x in docnames:
            relevant_doc_text[x]=temp_text_array
        temp={}
        le=len(temp_text_array)
        for j in temp_text_array:
            if j not in temp:
                temp[j]=1
            else:
                temp[j]+=1
        for k in temp:
            if k in Dict1:
                Dict1[k].append((x,temp[k]/le))
            else:
                Dict1[k]=[(x,temp[k]/le)]
        temp.clear()
    Dict2={}
    for z in Dict1:
        Dict2[z]=(Dict1[z], idf(len(Dict),len(Dict1[z])))
    
    alpha=1
    beta=0.7
    gamma=0.1
    qms=[]
    for i in range (len(queries)):
        q_m={}
       #first term 
        q_dict={}
        words_q=queries[i].split()
        for w in words_q:
            if w in q_dict:
                q_dict[w]+=1
            else:
                q_dict[w]=1
        for w in words_q:
            if w in q_dict and w in Dict2:
                q_m[w]=(alpha*q_dict[w]*Dict2[w][1])/len(words_q)
        #second term
        r_doc={}
        for j in range (i*100,(i+1)*100):
            if docnames[j] in r_doc:
                r_doc[docnames[j]]+=1
            else:
                r_doc[docnames[j]]=1
        for lk in Dict2:
            if lk in q_m:
                lis=Dict2[lk][0]
                tf=0
                for jh in lis:
                    if jh in r_doc:
                        tf+=jh[1]
                q_m[lk]+=(beta*tf*Dict2[lk][1])/100
            else:
                lis=Dict2[lk][0]
                tf=0
                for jh in lis:
                    if jh in r_doc:
                        tf+=jh[1]
                q_m[lk]=(beta*tf*Dict2[lk][1])/100
        #third term
        for lk in Dict2:
            if lk in q_m:
                lis=Dict2[lk][0]
                tf=0
                for jh in lis:
                    tf+=jh[1]
                q_m[lk]-=(gamma*tf*Dict2[lk][1])/len(Dict)
            else:
                lis=Dict2[lk][0]
                tf=0
                for jh in lis:
                    tf+=jh[1]
                q_m[lk]=0-(gamma*tf*Dict2[lk][1])/len(Dict)
        qms.append(q_m)
        sums=[]
        for j in range (i*100,(i+1)*100):
            di=docnames[j]
            dic_for_this_doc={}
            words_in_doc=[]
            if di in relevant_doc_text:
                words_in_doc=relevant_doc_text[di]
            for wj in words_in_doc:
                ls=Dict2[wj][0]
                it = iter(ls)
                ls = dict(zip(it, it))
                dic_for_this_doc[wj]=(ls[wj]*Dict2[wj][1])
            
            #dot product of this vector with relevant qm
            #store the necessary info and sort and print
            t_m=qms[i]
            sum=0
            for wi in t_m:
                if wi in dic_for_this_doc:
                    sum+=t_m[wi]*dic_for_this_doc[wi]
            sums.append(sum)
        print(sums)



            
    


                
    # har query se q_m banana hai
    #     avg_dn nikalna
    # avg dr har 40 query 

    
    
    
        









