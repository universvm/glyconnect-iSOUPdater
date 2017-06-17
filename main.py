#Packages:
import psycopg2
import sys
import datetime
import pprint
import urllib,urllib2
from collections import defaultdict

#Lists:
checked = [] #this is used later on, to delete obsolete entries

#Dictionaries:
uniprotdata = defaultdict(str) #creating empty dictionary with Uniprot Accession number and uniprotID(to link with the db)
seqDict = defaultdict(str) #contains uniprot accession and length

#Export for the log files:
export = open("data/log{0}.csv".format(datetime.date.today()), "w") #keeping a log file
export.write("SoupDate (YY-MM-DD):,{0}\n".format(datetime.date.today())) #Header

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
	"Creates a call to the API with the given UniProtAC (acc_n) to return the length of a protein."
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
		export.write("Error with API for {0}\n".format(acc_n))
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
	uniprotAC = line[1] #uniprot Accession
	uniprotdata[uniprotAC] += str(line[0]) #Long number which connects to accession Uniprot (uniprotID)
	uniprotAPI(uniprotAC)

#To select the isoTable:
cur.execute("SELECT * FROM uckb.uniprot_isoform")
isoTable = cur.fetchall()

#Update old entries:
export.write("Updated sequences: OLD Data, NEW Length,\n") #Header
for sequence in seqDict.keys():
	#check each sequenceDictionary against each sequenceDB and do the logic
	for i in isoTable: #Guide i[0] = id in uniprot_isoform; i[1] = uniprot accession; i[2] = uniprot id link; i[3] = length of the protein.
		if "-" not in sequence: #even if it doesn't have the "-", it may have isoforms, so we try checking by adding -1
			#remove entries with no isoforms here:
			isoCheck = sequence + "-2" #if the isoform of the sequence is in the dictionary
			if isoCheck not in seqDict.keys(): #if the isoform of the sequence is not in the dictionary
				try:
					del seqDict[sequence] #delete the entry from dictionary because no isoforms are available
				except KeyError:
					continue
			else: #sequence has isoforms
				if sequence == i[1]: #if the sequence finds the corresponding entry in the DB
					if seqDict[sequence] == str(i[3]): #if they have the same length
						checked.append(i[1]) #checked sequence so entry is not obsolete
						try:
							del seqDict[sequence] #deleting entry from the dictionary
						except KeyError:
							continue
					elif seqDict[sequence] == '': #the string is empty
						continue #continue the loop
					else: #if the length is different, i.e. our entry is outdated
						cur.execute("UPDATE uckb.uniprot_isoform SET length=%s WHERE isoform=%s",(long(seqDict[sequence]),i[1])) #updated the db with the new length
						checked.append(i[1]) #checked sequence so entry is not obsolete
						export.write("{0}, {1}\n".format(i, seqDict[sequence]))
						try:
							del seqDict[sequence] #deleting entry from the dictionary
						except KeyError:
							continue

		else: #if sequence is an isoform "accession-*" where "*" is a whole number >= 1
			if sequence == i[1]: #if the sequence finds the corresponding entry in the DB
				# print("Seems to be working")
				if seqDict[sequence] == str(i[3]): #if they have the same length
					checked.append(i[1]) #checked sequence so entry is not obsolete
					try:
						del seqDict[sequence] #deleting entry from the dictionary
					except KeyError:
						continue
				elif seqDict[sequence] == '': #the string is empty
					continue #continue the loop
				else: #if the length is different, i.e. our entry is outdated
					export.write("{0}, ({1})\n".format(i, seqDict[sequence]))
					cur.execute("UPDATE uckb.uniprot_isoform SET length=%s WHERE isoform=%s",(long(seqDict[sequence]),i[1])) #updated the db with the new length
					checked.append(i[1]) #checked sequence so entry is not obsolete
					try:
						del seqDict[sequence] #deleting entry from the dictionary
					except KeyError:
						continue
#Now the dictionary only contains new entries since checked/updated sequences have been deleted.
#Adding new entries:
export.write("New entries: (format: isoform, uniprot_id, length)\n") #Header
for sequence in seqDict.keys():
	cur.execute("INSERT INTO uckb.uniprot_isoform (isoform, uniprot_id, length) VALUES (%s, %s, %s)",(sequence,long(uniprotdata[sequence]), long(seqDict[sequence])))
	checked.append(sequence)
	export.write("{0}, {1}, {2}\n".format(sequence,uniprotdata[sequence], seqDict[sequence]))
	try:
		del seqDict[sequence] #deleting entry from the dictionary
	except KeyError:
		continue

#Deleting obsolete entries:
export.write("Deleted entries:\n") #Header
for i in isoTable:
	if i[1] in checked:
		continue
	else:
		cur.execute("DELETE FROM uckb.uniprot_isoform WHERE isoform = %s", [i[1]]) #isoform must be around "[]" for indexing
		export.write("{0}\n".format(i))

#Closing:
conn.commit() #Saves changes in the database.
cur.close()
conn.close()
