import sys
import snappy
import re
import stemmer

def stemming(tokens,stopwords):
    p = stemmer.PorterStemmer()
    output_list=[]
    for f in tokens:
        if(f is not "" and f not in stopwords):
            output_list.append(p.stem(f.lower(), 0,len(f)-1))
    return output_list
def tokenization(text):
    return re.split(r'[,.:;"`\'\(\)\{\}\[\] ]+|\n',text)

def c0_decoding(byte_string,list_docno):
    le=len(byte_string)//4
    ll=[]
    sum=0
    for i in range (0,le):
        t=int(int.from_bytes(byte_string[4*i:4*(i+1)],'big'))
        sum+=t
        ll.append(list_docno[sum])
    return ll
def c1_decoding(byte_string,list_docno):
    le=len(byte_string)
    ll=[]
    for i in range (0,le):
        st="{0:8b}".format(byte_string[i])
        t=""
        for j in range (0,8):
            if(st[j]=="1"):
                t+="1"
            else:
                t+="0"
        ll.append(t)
        # print(t)
    lll=[]
    stt=""
    for i in range (0,len(ll)):
        if(ll[i][0]=='1'):
            stt+=ll[i][1:]
        else:
            stt+=ll[i][1:]
            ij=int(stt,2)
            lll.append(ij)
            stt=""
    # print(stt)
    sum=lll[0]
    for i in range (1,len(lll)):
        # print (lll[i])
        sum+=lll[i]
        lll[i]=sum
    lt=[]
    for i in range (0,len(lll)):
        # print(len(list_docno),lll[i])
        lt.append(list_docno[lll[i]])
    return lt
    



def c1_decoding1(byte_string,list_docno):
    le=len(byte_string)
    ll=[]
    sum=0
    i=0
    while i<le:
        s=""
        while(i<le-1 and byte_string[i]>=128):
            st="{0:7b}".format(byte_string[i]-128)
            t=""
            for j in range (0,7):
                if(st[j]=="1"):
                    t+="1"
                else:
                    t+="0"
            s+=t
            i+=1
        st="{0:7b}".format(byte_string[i])
        t=""
        for j in range (0,7):
            if(st[j]=="1"):
                t+="1"
            else:
                t+="0"
        s+=t
        sum+=int(s,2)
        print(sum,len(list_docno))
        ll.append(list_docno[sum])
    return ll
def c2_helper(s,list_docno):
    l_lx=1
    ll=[]
    i=0
    while i<len(s):
        # print("i",i)
        if(s[i]=="0"):
            # print(i,l_lx)
            if(l_lx==1):
                ll.append(1)
            else:
                uni=l_lx-1
                temp_str=s[i+1:i+1+uni]
                temp_str="1"+temp_str
                lx=int(temp_str,2)
                temp_str=s[i+1+uni:i+uni+lx]
                temp_str="1"+temp_str
                x=int(temp_str,2)
                # print(i,x)
                ll.append(x)
                i+=uni+lx-1
                # print(i)
                l_lx=1
        else:
            l_lx+=1
        i+=1
    for i in range (0,len(ll)):
        ll[i]-=1
    sum=ll[0]
    for i in range (1,len(ll)):
        sum+=ll[i]
        ll[i]=sum
    l=[]
    for i in range (0,len(ll)):
        l.append(list_docno[ll[i]])
    return l

    
def c2_decoding(byte_string,list_docno):
    le=len(byte_string)
    s=""
    for i in range (0,le):
        # s+="{0:8b}".format(int.from_bytes(byte_string[i],'big'))
        # print(byte_string[i])
        st="{0:8b}".format(byte_string[i])
        z=""
        for j in range(0,8):
            if(st[j]=="1"):
                z+="1"
            else:
                z+="0"
        s+=z
    return c2_helper(s,list_docno)

def c3_decoding(byte_string,list_docno): 
    st=snappy.decompress(byte_string)
    return c0_decoding(st,list_docno)

def c4_helper(s,list_docno):
    l_lx=1
    q=0
    i=0
    ll=[]
    while i<len(s):
        # print("i",i)
        if(s[i]=="0"):
                q=l_lx-1  
                st=s[i+1:i+7]
                r=int(st,2)
                ll.append(r+1+q*64) 
        else:
            l_lx+=1
        i+=1
    for i in range (0,len(ll)):
        ll[i]-=1
    sum=ll[0]
    for i in range (1,len(ll)):
        sum+=ll[i]
        ll[i]=sum
    l=[]
    for i in range (0,len(ll)):
        l.append(list_docno[ll[i]])
    return l
    
    

def c4_decoding(byte_string,list_docno):
    le=len(byte_string)
    s=""
    for i in range (0,le):
        # s+="{0:8b}".format(int.from_bytes(byte_string[i],'big'))
        # print(byte_string[i])
        st="{0:8b}".format(byte_string[i])
        z=""
        for j in range(0,8):
            if(st[j]=="1"):
                z+="1"
            else:
                z+="0"
        s+=z
    return c4_helper(s,list_docno)
def single_word(compression_type,q,final_Dict,index_file,list_docno):
    # do something
    s=q[0]
    if(s not in final_Dict):
        return []
    a,b=final_Dict[s]
    index_file.seek(a)
    # print(str(a)+" "+str(b))
    byte_string=index_file.read(b-a+1)
    # print(s,byte_string)
    if(compression_type==0):
        return c0_decoding(byte_string,list_docno)
    elif(compression_type==1):
        return c1_decoding(byte_string,list_docno)
    elif(compression_type==2):
        return c2_decoding(byte_string,list_docno)
    elif(compression_type==3):
        return c3_decoding(byte_string,list_docno)
    elif(compression_type==4):
        return c4_decoding(byte_string,list_docno)
        

# def multipleword(compression_type,q,final_Dict,index_file,list_docno):
#     # do something










query_file=open(sys.argv[1],"r")
result=open(sys.argv[2],"w")
index_file=open(sys.argv[3],"rb")
dict_file=open(sys.argv[4],"r")
l=dict_file.readline().split()
compression_type=int(l[0])
list_docno=[]
l=dict_file.readline().split()
while(l[0]!="&"):
    list_docno.append(l[0])
    l=dict_file.readline().split()
# list_docno=list_docno[:-1]



# s=["10000110","11100100","00001111"]
# for i in range(0,3):
#     s[i]=int(s[i],2)
# t=b""
# t+=s[0].to_bytes(1,'big')
# t+=s[1].to_bytes(1,'big')
# t+=s[2].to_bytes(1,'big')
# t+=t
# c1_decoding(t,list_docno)



final_Dict={}
posting_list=[]
l=dict_file.readline().split()
while(len(l)!=0):
    final_Dict[l[0]]=(int(l[1]),int(l[2]))
    l=dict_file.readline().split()
# print(final_Dict)
# de=b''
# de+=int("10000110",2).to_bytes(1,'big')
# de+=int("11100100",2).to_bytes(1,'big')
# de+=int("00001111",2).to_bytes(1,'big')
# decoded(de)
# de=int(",2).to_bytes(3,'big')
# print(c1_decoding(de,list_docno))
# exit(1)
q=tokenization(query_file.readline())
q=stemming(q,[])
query_no=0
while(q):
    if(len(q)==1):
        posting_list=single_word(compression_type,[q[0]],final_Dict,index_file,list_docno)
    else:
        posting_lists=[]
        for i in range (0,len(q)):
            tt=single_word(compression_type,[q[i]],final_Dict,index_file,list_docno)
            posting_lists.append(set(tt))
        set_final=posting_lists[0]
        if len(posting_lists)>=1:
            for i in range (1,len(posting_lists)):
                set_final=set_final.intersection(posting_lists[i])
            posting_list=set_final
    # print("s ")
    # print(posting_list)
    for x in posting_list:
        result.write("Q"+str(query_no)+" "+x+" 1.0\n")
    # result.write()
    query_no+=1
    q=tokenization(query_file.readline())
    q=stemming(q,[])
    

