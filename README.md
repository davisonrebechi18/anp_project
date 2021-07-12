ANP Fuel Sales ETL
================

### Solution:

The solution I used to work with the resources of the Python packages available 
and dealing with a spreadsheet in the old format, through the exploration and 
discovery of the data, environment of development I used operating system Linux 
and LibreOffice application to convert the .xls spreadsheet to a new version of 
the .xlsx file, making it possible to start the work through the raw data.

<br/>
<br/>

### Process


<img src="image_overview.png"
     alt="Process"
     style="float: left; margin-right: 10px;" />


<br/>
<br/>


The process starts reading excel file "vendas-combustiveis-m3.xlsx" with library 
pandas from Python and all manipulation of data happens into script python. 


### Metadata from file

<br/>
<br/>

Column        | Type          | Description
------------- | ------------- | -------------
COMBUSTÍVEL   | string        | Type of fuel (HYDROUS ETHANOL, PETROL C, PETROL OF AVIATION, etc)
ANO           | integer       | Year
REGIÃO        | string        | region of Brazil
STATE         | string        | State of region
UNIDADE       | string        | Unit of measurement
JANEIRO       | double        | Total sold in January
FEVEREIRO     | double        | total sold in February
MARÇO         | double        | total sold in March
ABRIL         | double        | total sold in April
MAIO          | double        | total sold in May
JUNHO         | double        | total sold in June
JULHO         | double        | total sold in July
AGOSTO        | double        | total sold in August
SETEMBRO      | double        | total sold in September
OUTUBRO       | double        | total sold in October
NOVEMBRO      | double        | total sold in November
DEZEMBR       | double        | total sold in December
TOTAL         | double        | total sold in year


<br/>
<br/>


The process extracts 2 tables:

 - Sales of oil derivative fuels by UF and product;
 - Sales of diesel by UF and type;
 
<br/>
<br/>
 

### Schema 

Column | Type
------------- | -------------
year_month  | date
uf          | string
product     | string
unit        | string
volume      | double
created_at  | timestamp
            |
          
          
