#Packages:
import psycopg2
import sys
import pprint
import urllib,urllib2
from collections import defaultdict

#Dictionaries:
uniprotdata = defaultdict(str) #creating empty dictionary with uniprot data and glyconnectID
seqDict = defaultdict(str)
export = open("data/trying.csv", "w")
export.write("isoform;uniprot_id;length\n") #Header

#Parameters: To keep the main structure of API to work since they need an email address.
params = {
'from':'ID',
'to':'P_REFSEQ_AC',
'format':'tab',
'query':''
}

#Nicely explained video: https://www.youtube.com/watch?v=Z9txOWCWMwA
def database(): #keeping main function to connect. More here: https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
	#Define our connection string
	conn_string = "host='localhost' dbname='unicarbkb' user='postgres'"

	# get a connection, if a connect cannot be made an exception will be raised here
	conn = psycopg2.connect(conn_string)

	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cur = conn.cursor()

	#To visualize table:
	cur.execute("SELECT * FROM uckb.uniprot")
	# records = cur.fetchall()
	d = cur.fetchall()
	#Testing some logic:
	# if records[0][2] > 1:
	# 	pprint.pprint(records)
	# print(records)
	# count = 0
	# for line in records:
	# 	if line[3] == None:
	# 		count += 1
	# print(3.0/2.0)
	# print(len(records))
	# print(count)
	#print line
	#pprint.pprint(records)

	#To create a table: must specify where with "uckb.test"
	#cur.execute("CREATE TABLE uckb.test (id serial PRIMARY KEY, name varchar, age integer);")

	#To insert in a new table:
	#cur.execute("INSERT INTO uckb.test (name, age) VALUES (%s, %s)",("asd ads fdf ", 2))

	#To update records: IMPORTANT - METHOD OF COUNTING IS FROM 1 NOT 0
	#cur.execute("UPDATE uckb.test SET name=10 WHERE id=3") #ID is from the table

	#conn.commit()
	cur.close()
	conn.close()

	return(d)

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

#Main Loop:
data = database() #calling database
for line in data: #for each line in the database
    uniprotID = line[1]
    uniprotdata[uniprotID] += str(line[0]) #Long number which connects to accession Uniprot
    uniprotAPI(uniprotID)

for sequence in seqDict.keys():
    if "-" in sequence: #if it is an isoform
        isoform = sequence.split("-")
        if int(isoform[1]) == 2: #if it is the second isoform
            export.write("{}-1;{};{}\n".format(isoform[0],uniprotdata[isoform[0]],seqDict[isoform[0]]))
        export.write("{};{};{}\n".format(sequence,uniprotdata[isoform[0]],seqDict[sequence]))
