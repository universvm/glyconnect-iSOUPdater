#Packages:
import psycopg2
import sys
import pprint
import urllib,urllib2
from collections import defaultdict

#Lists:
checked = [] #this is used later on, to delete obsolete entries

#Dictionaries:
uniprotdata = defaultdict(str) #creating empty dictionary with uniprot data and glyconnectID
seqDict = defaultdict(str) #contains uniprot accession and length

#Export for the log files:
export = open("data/log.csv", "w") #keeping a log file
export.write("isoform;uniprot_id;length\n") #Header

#Parameters: To keep the main structure of API to work (email address is needed).
params = {
'from':'ID',
'to':'P_REFSEQ_AC',
'format':'tab',
'query':''
}

#Functions:
def parsER(page): #Defining uniprotAPI
    "Parses the fasta file given from the the uniprotAPI function"
    #Variables:
    acc_no = ""
    seq = ""
    count = 0
    #Loop:
    for line in page: #for each line of the page
        if line.startswith('<') or line.startswith('\n'): #ignoring comments such as "<addinfourl at 4456409208 "
            continue
        elif line.startswith('>'): #if line is accession number (>)
            if count > 0: #if it has already parsed a sequence once the next > is encountered
                seqDict[acc_no] += str(len(seq))
                seq = ""
                count = 0
            header = line.rstrip("\r\n")
            header = header.split("|")
            acc_no = header[1]
        else:
            seq += line.rstrip("\r\n") #since it is read line by line, each line is a bit of a sequence.
                                       #which is then added to seq
            count += 1
    #Adding the last entry:
    seqDict[acc_no] += str(len(seq))

def uniprotAPI(acc_n): #Defining uniprotAPI
    "Creates a call to the API with the given UniProtID (acc_n) to return the length of a protein."
    settings = urllib.urlencode(params) #calling parameters
    try: #tries to call the API.
        url = 'http://www.uniprot.org/uniprot/{0}.fasta?include=yes'.format(acc_n) #URL format to include isoforms
        request = urllib2.Request(url, settings)
        contact = "email" # Please set your email address here to help us debug in case of problems.
        request.add_header('User-Agent', 'Python %s' % contact)
        response = urllib2.urlopen(request)
	parsER(response) #parsing the response
    except urllib2.HTTPError: #if API call fails, it displays which one of the entry has a problem
        print("There is an error for the {0} entry".format(acc_n))

#Connection to the DB: Useful > https://www.youtube.com/watch?v=Z9txOWCWMwA, https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
conn_string = "host='localhost' dbname='unicarbkb' user='postgres'"

# get a connection, if a connect cannot be made an exception will be raised here
conn = psycopg2.connect(conn_string)

# conn.cursor will return a cursor object, you can use this cursor to perform queries
cur = conn.cursor()

#To select the table:
cur.execute("SELECT * FROM uckb.uniprot")
data = cur.fetchall()

#Main Loop 1:
for line in data: #for each line in the database
    uniprotID = line[1]
    uniprotdata[uniprotID] += str(line[0]) #Long number which connects to accession Uniprot
    uniprotAPI(uniprotID)

#To select the isoTable:
cur.execute("SELECT * FROM uckb.uniprot_isoform")
isoTable = cur.fetchall()

#Main Loop 2:
export.write("Updated sequences; length:\n") #Header
for sequence in seqDict.keys():
	#check each sequenceDictionary against each sequenceDB and do the logic
	for i in isoTable: #Guide i[0] = id in uniprot_isoform; i[1] = uniprot accession; i[2] = uniprot id link; i[3] = length of the protein.
		if "-" not in sequence: #even if it doesn't have the "-", it may have isoforms, so we try checking by adding -1
			sequence += "-1"
			if sequence == i[1]: #if the sequence finds the corresponding entry in the DB
				if seqDict[sequence] == i[3]: #if they have the same length
                	checked.append(i[1]) #checked sequence so entry is not obsolete
				else: #if the length is different, i.e. our entry is outdated
					cur.execute("UPDATE uckb.uniprot_isoform SET length=%s WHERE isoform_id=%s",(int(i[3]),long(float(i[0])))) #updated the db with the new length
                    export.write("{0}\n".format(i)) #log file
                    checked.append(i[1]) #checked sequence so entry is not obsolete
            else:
                #since a lot of sequences with no isoform will be rejected before, they will go here, together with new entries.
                #thus we check if an isoform 2 exists in our dictionary, if it does not, then the protein has no isoforms, i.e. it doesn't need to be added to the isoform db
                isoCheck = sequence.replace(sequence[-2::], "-2")
                if isoCheck in seqDict.keys(): #meaning if any of the entries in the dictionary has an isoform 2.
				    cur.execute("INSERT INTO uckb.uniprot_isoform (isoform, uniprot_id, length) VALUES (%s, %s, %s)",(sequence,long(float(i[0])),int(i[3])))# add the current sequence in the db as it is not present
                    export.write("{0}\n".format(i)) #log file
                    checked.append(sequence)#added sequence so entry is not obsolete
        else: #if it is an isoform
			if sequence == i[1]: #if the sequence finds the corresponding entry in the DB
				if seqDict[sequence] == i[3]: #if they have the same length
                	checked.append(i[1]) #checked sequence so entry is not obsolete
				else: #if the length is different, i.e. our entry is outdated
					cur.execute("UPDATE uckb.uniprot_isoform SET length=%s WHERE isoform_id=%s",(int(i[3]),long(float(i[0])))) #updated the db with the new length
                    export.write("{0}\n".format(i)) #log file
                    checked.append(i[1]) #checked sequence so entry is not obsolete
            else:
                #since a lot of sequences with no isoform will be rejected before, they will go here, together with new entries.
                #thus we check if an isoform 2 exists in our dictionary, if it does not, then the protein has no isoforms, i.e. it doesn't need to be added to the isoform db
                isoCheck = sequence.replace(sequence[-2::], "-2")
                if isoCheck in seqDict.keys(): #meaning if any of the entries in the dictionary has an isoform 2.
				    cur.execute("INSERT INTO uckb.uniprot_isoform (isoform, uniprot_id, length) VALUES (%s, %s, %s)",(sequence,long(float(i[0])),int(i[3])))# add the current sequence in the db as it is not present
                    export.write("{0}\n".format(i)) #log file
                    checked.append(sequence)#added sequence so entry is not obsolete








            isoform = sequence.split("-")
            #Log file:
            if int(isoform[1]) == 2: #if it is the second isoform
                export.write("{}-1;{};{}\n".format(isoform[0],uniprotdata[isoform[0]],seqDict[isoform[0]]))
            export.write("{};{};{}\n".format(sequence,uniprotdata[isoform[0]],seqDict[sequence]))

# #Main Loop 2:
# for s in isoTable:
#     if s[1] in checked:
#         continue
#     else:




    #TODO:
	# - Check if entry (isoform Uniprot ID) already exists in iso: - if it does not, add it. =]> Checked
	# 													  - if it does exist Check if the length changed, if so => update it. =]> Checked
	# - else the entry does not exist add it. =]> Checked
	# - obsolete entries => if the entry is obsolete, then it wouldn't have been checked
# TODO: delete entries
	#Export of the isoform:

#COMMANDS
#To create a table: must specify where with "uckb.test"
#cur.execute("CREATE TABLE uckb.test (id serial PRIMARY KEY, name varchar, age integer);")

#To insert in a new table:
#cur.execute("INSERT INTO uckb.test (name, age) VALUES (%s, %s)",("asd ads fdf ", 2))

#To update records: IMPORTANT - METHOD OF COUNTING IS FROM 1 NOT 0
#cur.execute("UPDATE uckb.test SET name=10 WHERE id=3") #ID is from the table

#Closing:
#conn.commit() #Saves changes in the database.
cur.close()
conn.close()
