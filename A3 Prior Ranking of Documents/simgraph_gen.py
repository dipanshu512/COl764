# imports
import sys
import os
import re
import math
import stemmer
import codecs
# import sknetwork as skn
# from sknetwork.utils import edgelist2adjacency
# from sknetwork.ranking import PageRank
#jaccard
def jaccard(set1,set2):
    l_u=len(set1 | set2)
    l_i=len(set1 & set2)
    return l_i/l_u
# cosine
def cosine(dict1,dict2):
    ret = 0
    sqrt1 = 0
    sqrt2 = 0
    for word in dict1:
        if(word in dict2):
            ret += dict1[word]*dict2[word]
    for word in dict1:
        sqrt1 += dict1[word]*dict1[word]
    for word in dict2:
        sqrt2 += dict2[word]*dict2[word]
    if(sqrt1 == 0):
        return 0
    if(sqrt2 == 0):
        return 0
    sqrt1 = math.sqrt(sqrt1)
    sqrt2 = math.sqrt(sqrt2)
    return ret/(sqrt1*sqrt2)

def tokenization(string):
    delims = [' ',",",".",":",";","'","\"","@","#","+","!","_","~","&","*","%","^","=","`","|","$","\n","(",")",">","<"]
    for delim in delims:
        string = string.replace(delim," ")
    return string.split()
def stemming(tokens):
    p = stemmer.PorterStemmer()
    output_list=[]
    for f in tokens:
        if(f !=""):
            output_list.append(p.stem(f.lower(), 0,len(f.lower())-1))
    return output_list
def process(typ,file_paths,file_names,out):
    if(typ=="jaccard"):
        #make set of all files
        all_sets=[]
        for x in file_paths:
            file = codecs.open(x, 'r',encoding='utf-8', errors='ignore')
            text = file.read()
            tokens=tokenization(text)
            words=stemming(tokens)
            all_sets.append(set(words))
        g=open(out+".txt",'w')
        for i in range (len(all_sets)):
            for j in range(i+1,len(all_sets)):
                jac_sim=jaccard(all_sets[i],all_sets[j])
                g.write(file_names[i])
                g.write(" ")
                g.write(file_names[j])
                g.write(" ")
                g.write(str('%.4f'%jac_sim))
                # G.append((i,j,jac_sim))
                g.write("\n")
        g.close()
        # return G
    elif(typ=="cosine"):
        all_dicts=[]
        global_dict={}
        for x in file_paths:
            temp={}
            file = codecs.open(x, 'r',encoding='utf-8', errors='ignore')
            text = file.read()
            tokens=tokenization(text)
            for tk in tokens:
                if tk in temp:
                    temp[tk]+=1
                else:
                    temp[tk]=1
                if tk in global_dict:
                    global_dict[tk]+=1
                else:
                    global_dict[tk]=1
            all_dicts.append(temp)
        for dict in all_dicts:
            for tk in dict:
                idf=math.log(1+(len(file_paths)/global_dict[tk]),2)
                tf=math.log(1+dict[tk],2)
                dict[tk]=tf*idf
        g=open(out+".txt",'w')
        for i in range (len(all_dicts)):
            for j in range (i+1,len(all_dicts)):
                cosine_sim=cosine(all_dicts[i],all_dicts[j])
                g.write(file_names[i])
                g.write(" ")
                g.write(file_names[j])
                g.write(" ")
                g.write(str('%.4f'%cosine_sim))
                # G.append((i,j,cosine_sim))
                g.write("\n")
        g.close()
        # return G
    else:
        print("INVALID INPUT")


#main function to start with
if __name__ == "__main__":
    typ=sys.argv[1]
    coll_dir=sys.argv[2]
    l=len(coll_dir)
    out_name=sys.argv[3]
    file_paths=[]
    file_names=[]
    g=[]
    for subdir, dirs, files in os.walk(coll_dir):
        for file in files:
            filepath = subdir + os.sep + file
            file_paths.append(filepath)
            file_names.append(filepath[l+1:])
    process(typ,file_paths,file_names,out_name)
    # graph = edgelist2adjacency(g, undirected=True)
    # pagerank = PageRank()
    # scores = pagerank.fit_transform(graph)
    # pairs = [(file_names[i], scores[i]) for i in range(len(file_names))]
    # pairs.sort(key= lambda x: -x[1])
    # file = open("pageranks_"+typ+".txt", 'w')
    # for i in range(len(pairs)):
    #     file.write(pairs[i][0])
    #     file.write(" "+str(pairs[i][1])+"\n")

