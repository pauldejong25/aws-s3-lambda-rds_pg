## Build Lambda Layer

# Toevoegen van Lambda Layer om postgres module psycopg2 te kunnen toevoegen (Lambda->Layer)
  - name: postgresLayer
  - compatible runtimes: python3.13
  - compatible architecture: x86_64
  - create from zipfile
# Zip file maken via CloudShell
  - Ga naar AWS->Cloudshell
  - Maak postgresLayer en daaronder python library aan
  - Vanuit postgresLayer dir: pip3 install psycopg2-binary -t python
  - Zippen: zip -r postgresLayer3.13.zip python
  - Check of python directory in de root staat
  - Downloaden van zip: Actions->Download file en vul naam zip in
