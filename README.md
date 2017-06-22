# glyconnect-iSOUPdater
Glyconnect updater for the isoforms directly in the database. In this case, localhost was used. 

# Environment Variables
Please set the following environment variables in order to connect to the database:


host = 'PG_HOST_UCKB'


port = 'PG_PORT_UCKB'


database = 'PG_DB_UCKB'


user = 'PG_USER_UCKB'


password = 'PG_PASSWORD_UCKB'


# Log File
A log file is created for EVERY action the program does which affects the database (adding new entries, updating, deleting) or is related to failure of the Uniprot API. The format name for the log file is "log$DATE.csv" where $DATE is replaced with the date the iSOUPdater was used. 


# Logic to interact with the Database
Below is the general logic of the main.py file. Although not shown below due to space constraints, the code contacts the UniProt API using data from the UniProt table in UniCarbKB, to retrieve data with the Accession Number (Accession) and the sequence. 
 
 
  The sequence length is calculated and then added to the dictionary with its relative Accession.
  
![alt text](https://github.com/universvm/glyconnect-iSOUPdater/blob/master/logic.png)
Photoshop and Code2Flow were used to produce this.
