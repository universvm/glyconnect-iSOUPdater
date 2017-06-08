# glyconnect-iSOUPdater
Glyconnect updater for the isoforms directly in the database. In this case, localhost was used. 

# Logic to interact with the Database
Below is the general logic of the main.py file. Although not shown below due to space constraints, the code contacts the UniProt API using data from the UniProt table in UniCarbKB, to retrieve data with the Accession Number (Accession) and the sequence. 
 
 
  The sequence length is calculated and then added to the dictionary.
  
![alt text](https://github.com/universvm/glyconnect-iSOUPdater/blob/master/logic.png)

