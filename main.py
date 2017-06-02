import psycopg2
import sys
import pprint

#Nicely explained video: https://www.youtube.com/watch?v=Z9txOWCWMwA
def main(): #keeping main function to connect. More here: https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
	#Define our connection string
	conn_string = "host='localhost' dbname='unicarbkb' user='postgres'"

	# get a connection, if a connect cannot be made an exception will be raised here
	conn = psycopg2.connect(conn_string)

	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cur = conn.cursor()

	#To visualize table:
	cur.execute("SELECT * FROM uckb.uniprot_isoform")
	records = cur.fetchall()
	#testing some logic:
	# if records[0][2] > 1:
	# 	pprint.pprint(records)
	#print(records[0][0])
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



main()
