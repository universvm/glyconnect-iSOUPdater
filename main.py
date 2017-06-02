import psycopg2
import sys
import pprint

def main(): #keeping main function to connect. More here: https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
	#Define our connection string
	conn_string = "host='localhost' dbname='unicarbkb' user='postgres'"

	# print the connection string we will use to connect
	print("Connecting to database\n	->%s" % (conn_string))

	# get a connection, if a connect cannot be made an exception will be raised here
	conn = psycopg2.connect(conn_string)

	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM uckb.site")
	records = cursor.fetchall()
	pprint.pprint(records)

main()
