AWS Install steps

1. Deploy a lambda function (python)
2. Postgres RDS instance aanmaken en deze via een lambda functie benaderen

1 Deploy a lambda function (python)

Lambda Handler parameters:
Event:
Bevat informatie van het event waardoor het getriggerd wordt:
- Event in de lambda event handler is voor python altijd van het type "dict"
- De trigger bepaalt welke sleutels (keys) erin zitten
Context:
Bevat meta informatie over de functie
- Context is van het python type object
- function_name, function_version, aws_request_id, memory_limit_in_mb, invoked_function_arn
Trigger:
Wat veroorzaakt het uitvoeren van de lambda (hier uploaden van file)
Destination:
Wat doe ik met het resultaat (json) van de lambda (bijvoorbeeld als het fout gaat loggen naar een SQS)
Dit is bedoeld voor de workflow

Toevoegen van Lambda Function
- Name: ogS3ObjectCreated
- Runtime: Python 3.13
- Toevoegen van nieuwe S3 bucket: amzn-s3-lambdademo-bucket
- Toevoegen van S3 Trigger
  Bucket: amzn-s3-lambdademo-bucket en Eventtype s3:ObjectCreated:*
- Code: print meta informatie van event en context. Van elk geupload bestand print de metadata (naam, extensie, lengte)
- Test: maak een synchroon testEvent: testEventUpload met de json van sample_event.json
- Controleer de werking via Deploy en Test button

Boto3: SDK functionaliteit van AWS voor Python
Toevoegen van autorisatie in IAM
- Vind de rol die de Lamba functie mag uitvoeren (hier: logS3ObjectCreated-role-fq7z4thh)
- Voeg een inline policy toe die de autorisaties s3:ListBucket en s3:GetObject toekent aan bucket s3-lambdademo-bucket 
Aanpassen code
- Import boto3 libarary in Python: import boto3
- Maak een connectie met S3: s3 = boto3.client('s3')
- Doe een API call naar een S3 functie zoals: s3.head_object of s3.get_object
- Print de content en metadata van het response object (een python "dict")
Testen
- Deploy en Test
- Upload een testbestand in s3-lambdademo-bucket (Test_Lambda6.txt) en check de logging in CloudWatch

Directe (synchrone) aanroep via CLI
- aws login
- maak een event.json (vergelijkbaar met code in test event)
- voer uit: aws lambda invoke --function-name logS3ObjectCreated --cli-binary-format raw-in-base64-out --payload file://event.json --invocation-type RequestResponse response.json
- check de response.json
Asynchroon:
- voer uit: aws lambda invoke --function-name logS3ObjectCreated --cli-binary-format raw-in-base64-out --payload file://event.json --invocation-type Event response.json

Vanuit Visual Studio
- Installeer boto3: python -m pip install boto3
- Installeer botocore[crt]: python -m pip install "botocore[crt]"
- Schrijf python programma LogS4ObjectCreated.py
- Invoke van Lambda (synchroon)
  # maak connectie naar AWS service lambda
  lambda_client = boto3.client("lambda")
  response = lambda_client.invoke(
    FunctionName="logS3ObjectCreated",
    InvocationType="RequestResponse",
    Payload=json.dumps(event)
)

AWS Policy simulator: https://policysim.aws.amazon.com/

Select hier role "logS3ObjectCreated-role-fq7z4thh". Deze is automatisch aangemaakt voor Lambda logS3ObjectCreated

aws iam get-role-policy --role-name logS3ObjectCreated-role-fq7z4thh --policy-name ListReadS3LambdaDemoBucket

Deze role moet de inline Policies ListBucket en ReadObjects bevatten. Deze moeten indien nodig toegevoegd worden en zijn nodig voor resp. s3.get_object (objectdata) en s3.head_object (metadata)

2. Postgres RDS instance aanmaken en deze via een lambda functie benaderen

- Nieuwe RDS voor Postgres

- Database aangemaakt via Tutorial. Daarbij gekozen voor de optie Full Configuration!

Belangrijke parameters:

- pg engine: 18.3
- instance class: db.t4g.micro (voor kleine demo omgeving)
- storage: General Purpose SSD (snel genoeg)
- multi az: no 
- public access: ja (om vanuit client tools connectie te kunnen maken)
- backup retention: 1 dag (meer niet mogelijk)
- credentials management: Self managed (maak geen gebruik van AWS secrets manager ivm extra kostenpost)
- aws kms key: aws/rds (default), dit voor versleuteling van data. Deze key wordt nu door AWS geregeld.
- encryption: aan (default)
- minor version upgrade: true (default), upgrade van bv 18.1 naar 18.2 worden automatisch uitgevoerd
- delete protection: off (default)

- db-instance naam: pg-database-1
- initial database naam: aws_training
- master username: paul
- master password: **************
- hostname: pg-database-1.creqygw4e1vd.eu-north-1.rds.amazonaws.com
- port: 5432

Opvragen van eigenschappen via CLI
- aws rds describe-db-instances --db-instance-identifier pg-database-1 (controleer of database van buitenaf te benaderen is: "PubliclyAccessible": true) en check de VPC Security Group
- check de eigenschappen van de vpc security group en check of er een inbound rule voor postgres (Protocol = tcp, frompost = 5432, toport = 5432) bestaat
- Indien niet aanwezig voeg in AWS Console (Ec2 / Security Group) een inbound rule voor PostgreSQL (type = PostgreSQL, protocol = tcp, portrange = 5432, source=MyIp)
* De default is geen toegang in AWS, dus de inbound rule moet toegevoegd worden

Testen van connectie via CLI
- Test-NetConnection pg-database-1.creqygw4e1vd.eu-north-1.rds.amazonaws.com -Port 5432

Installatie van DB Clienttool: DBeaver en toevoegen en Postgres connectie opzetten

Aanmaken logtabel in postgres via DBeaver: script: pg_create_tbl_uploaded_files_s3.sql
Aanpassingen in VS:
  - Installatie van extension: AWS Toolkit
  - Installatie van postgres extensie: pip install psycopg2
  - Source editor: spaces=4, Convert indentation to spaces.
  - Nog te doen: installeren Pylance, Amazon Q
Toevoegen van Lambda Layer om postgres module psycopg2 te kunnen toevoegen (Lambda->Layer)
  - name: postgresLayer
  - compatible runtimes: python3.13
  - compatible architecture: x86_64
  - create from zipfile
Zip file maken via CloudShell
  - Ga naar AWS->Cloudshell
  - Maak postgresLayer en daaronder python library aan
  - Vanuit postgresLayer dir: pip3 install psycopg2-binary -t python
  - Zippen: zip -r postgresLayer3.13.zip python
  - Check of python directory in de root staat
  - Downloaden van zip: Actions->Download file en vul naam zip in
Koppelen layer aan Lambda
  - Kies functie
  - Add Layer (Custom), naam = postgresLayer
Lambda via zelfde VPC als RDS Postgres laten uitvoeren
 Wanneer een Lambda in een VPC draait, moet hij netwerkinterfaces kunnen maken. Dit kan door Managed policy AWSLambdaVPCAccessExecutionRole toe te voegen aan lambda execution role
  - IAM -> Roles -> logS3ObjectCreated, Add permissions -> Attach policies
 Lambda function staat open voor internet maar niet voor AWS RDS instance (via VPC)
 Verhelpen door Security Groups te introduceren die elkaar vertrouwen
  - Nieuwe SG voor Lambda: sg_lambda, inbound: leeg, outbound: All traffic
  - Nieuwe SG voor RDS: sg_rds_postgres, inbound: PostgreSQL , 5432, sg_lambda en PostgreSQL, 5432 MyIP (voor DBeaver lokaal)
  - Pas SG voor RDS pg-database-1 aan van default naar sg_rds_postgres
  - Pas VPC van Lambda aan via Configuration->VPC, inclusief 3 subnets en SG = sg_lambda
  - Verwijder inbound rule(s) voor Postgres in SG Default
 Lambda functie loopt nu via VPC, deze heeft geen internettoegang meer. Deze moet via een S3 Gateway Endpoint worden toegevoegd
  - Ga naar VPC dashboard -> Endpoints -> Create Endpoint (niet Endpoint Services)
  - Naam = com.amazonaws.eu-north-1.s3, Type = AWS Services, Service = com.amazonaws.eu-north-1.s3
  - Check: aws ec2 describe-vpc-endpoints --vpc-endpoint-ids vpce-08f8cd0a7d704d0db
           aws ec2 describe-route-tables --route-table-ids rtb-0aa6ed839b741f056
 Het ziet er nu zo uit (zie ook de Routes van de Route table van de VPC)
   Lambda
    │
    ▼
Route table
    │
    ├── local
    ├── Internet Gateway
    └── S3 Gateway Endpoint   ← nieuw
  
Lambda functie code aanpassen
- Maak connectie met postgres
  conn = psycopg2.connect(
        host=credential['host'],
        database=credential['db'],
        user=credential['username'],
        password=credential['password'],
        port=credential['port'],
        connect_timeout=5
      )
- Vul de credential array met waardes vanuit de environment variables (Lambda->Configuration). 
  credential['username'] = os.environ["DB_USER"]
- Vul de postgres tabel uploaded_files_s3 met de data / metadata uit het S3 object via een cursor (insert statement)

Nieuwe structuur:
                    AWS Cloud

                 S3 Bucket
                     │
          ObjectCreated Event
                     │
                     ▼
             Lambda (in VPC)
                     │
             sg-lambda-s3
                     │
                     ▼
          RDS PostgreSQL
          sg-rds-postgres
             ▲
             │
      PostgreSQL 5432
      Source: sg-lambda-s3

Jouw laptop
     │
DBeaver
     │
PostgreSQL 5432
Source: MyIP (/32)  


--------------------------------------
                Upload bestand
                      │
                      ▼
                  Amazon S3
                      │
               ObjectCreated Event
                      │
                      ▼
              AWS Lambda (Python)
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
   get_object()                psycopg2
        │                            │
        └─────────────┬──────────────┘
                      ▼
              Amazon RDS PostgreSQL



