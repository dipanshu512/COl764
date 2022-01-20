import sys
import re
import snappy
import stemmer
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup

def c4_encoding(value):
    k=6
    b=64
    q=(value-1)//b
    uni=""
    for i in range (0,q):
        uni+="1"
    uni+="0"
    r=value-q*b-1
    t="{0:b}".format(r)
    while len(t)<6:
        t="0"+t
    return uni+t

def c3_encoding(value):
    return snappy.compress(value)
def c2_encoding(value):
    bin1="{0:b}".format(value)#bin(value).replace("0b", "")
    l_x=len(bin1)
    bin2="{0:b}".format(l_x)
    l_lx=len(bin2)
    s=""
    for i in range(0,l_lx-1):
        s+="1"
    s+="0"
    s+=bin2[1:]+bin1[1:]
    return s
    # r=le%8
    # t=""
    # if(r!=le):
    #     s=s[0:le-r+1]+s[le-r+1:]
    # else:
    #     s=s[0:]
    # return s

def c1_encoding(value):
    ret=[]
    binString = "{0:b}".format(value)
    while(len(binString)%7!=0):
	    binString = '0'+binString
    word = ''
    j=0
    while(j<=len(binString)-8):
    	word += binString[j]
    	j+=1
    	if(len(word) == 7):
		    ret.append('1'+word)
		    word = ''
    last = '0' + binString[-7:]
    ret.append(last)
    s=""
    for i in range (0,len(ret)):
        s+=ret[i]
    return s

def dump(file_no,Temp_Dict,Dict):
    start=0
    # print(file_no)
    f=open("dic"+str(file_no),"wb")
    # print(sorted(Temp_Dict.items()))
    for (key,listl) in sorted(Temp_Dict.items()):
        ll=(start,start+4*len(listl)-1)
        # if(key=="$1" or key=="$1 "):
        #     print("nayi key aayi")
        #     print(listl)
        for x in listl:
            f.write(x.to_bytes(4,byteorder='big'))
            # print(x)
        start=start+4*len(listl)
        lll=(file_no,ll)
        if key in Dict:
            Dict[key].append(lll)
        else:
            Dict[key]=[lll]
    f.close()
    return Dict   
def tokenization(text):
    return re.split(r'[,.:;"`\'\(\)\{\}\[\] ]+|\n',text)
    # return re.split(r'[,.:;"`\'\(\)\{\}\[\] ]+|\n',text)
def stemming(tokens,stopwords):
    p = stemmer.PorterStemmer()
    output_list=[]
    for f in tokens:
        if(f is not "" and f not in stopwords):
            output_list.append(p.stem(f.lower(), 0,len(f.lower())-1))
    return output_list
def process(path,file_no,count_doc,word_count,stopwords,useful_tags,Temp_Dict,Dict):
    file = open(path,"r")
    contents = file.read()
    contents="<cover>" + contents +"</cover>"
    soup = BeautifulSoup(contents,'xml')
    docs = soup.find_all('DOC')
    for doc in docs:
            fulltext=""
            docnos=doc.find_all('DOCNO')
            docno=docnos[0].get_text()
            list_docno.append(docno)
            for tag in useful_tags[1:]:
                tag_text=doc.find_all(tag)
                for x in tag_text:
                    fulltext+=(x.get_text()+" ")
    
         #need to make a map between docno and integer
            tokens=tokenization(fulltext)
            words=stemming(tokens,stopwords)
            final_words=set(words)
            for f in final_words:
                if f not in stopwords:
                    word_count+=1
                    if(f in Temp_Dict):
                        Temp_Dict[f].append(count_doc)
                    else:
                        Temp_Dict[f]=[count_doc]
                if(word_count==1000000):
                    Dict=dump(file_no,Temp_Dict,Dict)
                    Temp_Dict={}
                    word_count=0
                    file_no+=1      
            count_doc+=1 
    return file_no, word_count, count_doc, Temp_Dict, Dict   
     
coll_path=sys.argv[1]
indexfile_name=sys.argv[2]
stopwords=set(open(sys.argv[3],"r").read().split())
compression_type=sys.argv[4]
if(int(compression_type)>=5):
    print("Method Not Implememted")
    exit(1)
xml_tags_info=sys.argv[5]
useful_tags=open(xml_tags_info,'r').read().split()
Temp_Dict ={}
Dict={} #key,[(file,start,end)]
list_docno=[]
onlyfiles = [join(coll_path, f) for f in listdir(coll_path) if isfile(join(coll_path, f))]
n=len(onlyfiles)
file_no=0
word_count=0
count_doc=0
for x in onlyfiles:
    file_no,word_count,count_doc,Temp_Dict,Dict=process(x,file_no,count_doc,word_count,stopwords,useful_tags,Temp_Dict,Dict)
if word_count:
        Dict=dump(file_no,Temp_Dict,Dict)
print("hi5")

final_Dict={}
File_pointers=[]
for i in range (0,file_no+1):
    File_pointers.append(open("dic"+str(i),"rb"))
posting_lists=open(indexfile_name+".idx","wb")
start=0
# print(sorted(Dict.items()))
for word,list_triple in sorted(Dict.items()):
    word_start=start
    previous=0
    st=b""
    s=""
    n=0
    for x,(y,z) in list_triple:
        # print(word,x, y ,z ,previous)
        # print(list_triple)
        for i in range (0,((z+1-y)//4)):
            value=int.from_bytes(File_pointers[x].read(4),byteorder='big')
            # print(value)
            if(compression_type=="0"):
                # if(word is "$1") print(word,value,previous)
                posting_lists.write((value-previous).to_bytes(4,byteorder='big'))
                n+=4
            elif(compression_type=="1"):
                s=c1_encoding(value-previous)
                le=len(s)//8
                n+=le
                for j in range (0,le):
                    posting_lists.write(int(s[8*j:8*(j+1)],2).to_bytes(1,byteorder='big'))
            elif(compression_type=="2"):
                s+=c2_encoding(value-previous+1) 
            elif(compression_type=="3"):
                st+=(value-previous).to_bytes(4,'big')
            elif(compression_type=="4"):
                print("hiiiiiii")
                s+=c4_encoding(value-previous+1)
            previous=value
        
    if(compression_type=="2" or compression_type=="4"):
            print("hi")
            le=len(s)//8
            r=len(s)%8
            if(r==0):
                r=8
            n=(len(s)+8-r)//8
            for i in range (0,le):
                    posting_lists.write(int(s[8*i:8*(i+1)],2).to_bytes(1,byteorder='big'))
            if(r!=8):
                for i in range (0,8-r):
                    s+="1"
                posting_lists.write(int(s[8*le:8*(le+1)],2).to_bytes(1,byteorder='big')) 
    if(compression_type=="3"):
            st=c3_encoding(st)
            n=len(st)
            # for i in range (0,n):
            if(word=="airbu"):
                ft=open("e.txt","wb")
                ft.write(st)
            posting_lists.write(st)
    start+=n
    final_Dict[word]=(word_start,start-1)

# it=open("m.txt","w")
# g=File_pointers[0]
# # g.seek(2148)
# # print(int.from_bytes(g.read(4),'big'))
# g.seek(16)
# for i in range (0,2136//4):
#     it.write(str(int.from_bytes(g.read(4),'big'))+"\n")
index_file=open(indexfile_name+".dict","w")
index_file.write(compression_type)
index_file.write("\n")
# for x in stopwords:
#     index_file.write(x+" ")

# index_file.write("\n")
#write the mapping
for i in list_docno:
    index_file.write(i)
    index_file.write(" ")
    index_file.write("\n")
#write the final_Dict
index_file.write("&")
index_file.write("\n")
for word,(start,end) in sorted(final_Dict.items()):
    index_file.write(word+" "+str(start)+" "+str(end))
    index_file.write("\n")
# index_file.write("&")
# index_file.write("\n")


        




    
    





