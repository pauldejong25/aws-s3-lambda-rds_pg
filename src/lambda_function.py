import json
import urllib.parse
import os
import boto3
import psycopg2

def getCredentials():
    credential = {}
    
 #   secret_name = "mysecretname"
 #   region_name = "eu=north-1"
 #   client = boto3.client(
 #     service_name='secretsmanager',
 #     region_name=region_name
 #  )
    
 #  get_secret_value_response = client.get_secret_value(
 #     SecretId=secret_name
 #  )
 #  secret = json.loads(get_secret_value_response['SecretString'])
 #  credential['username'] = secret['username']
 #  credential['password'] = secret['password']
 
    credential['username'] = os.environ["DB_USER"]
    credential['password'] = os.environ["DB_PASSWORD"]
    credential['host'] = os.environ["DB_HOST"]
    credential['db'] = os.environ["DB_NAME"]
    credential['port'] = os.environ["DB_PORT"]
    
    return credential

def readS3Object(s3, bucket_name, object_key):
   
    try:
      #haal de metadata op van het s3 object met de opgegeven bucket_name en object_key
      #response = s3.head_object(
      # Bucket=bucket_name,
      # Key=object_key
      #)

      #haal de metadata en data op van het s3 object met de opgegeven bucket_name en object_key
      print(f"Getting S3 object '{bucket_name} {object_key}...")
      response = s3.get_object(
        Bucket=bucket_name,
        Key=object_key
      )
      print("Fetched S3 object")
      return response

    except FileNotFoundError as e:
      print(f"Bestand niet gevonden: {e}")
      raise
    except Exception as e:
      print(f"Fout bij ophalen bestand: {e}")
      raise

def lambda_handler(event, context):

    print("=== Lambda version 2.1 ===")

    # Print event to CloudWatch logs
    print(json.dumps(event, indent=4))
    # Print context variables to CloudWatch logs
    print(f"Function : {context.function_name}")
    print(f"Version  : {context.function_version}")
    print(f"Memory   : {context.memory_limit_in_mb} MB")
    print(f"Request  : {context.aws_request_id}")
    remaining = context.get_remaining_time_in_millis()
    print(f"Remaining time: {remaining} ms")

    print("Creating S3 client...")
    s3 = boto3.client('s3', region_name="eu-north-1")

    print("Reading credentials...")
    credential = getCredentials()
    print("Database credentials:")
    print(f"Host     : {credential['host']}")
    print(f"Database : {credential['db']}")
    print(f"User     : {credential['username']}")
    print(f"Port     : {credential['port']}")
    print(f"Password length: {len(credential['password'])}")
   
 
    conn = None
    cur = None
    
    try:
      print("Connecting to PostgreSQL...")
      conn = psycopg2.connect(
        host=credential['host'],
        database=credential['db'],
        user=credential['username'],
        password=credential['password'],
        port=credential['port'],
        connect_timeout=5
      )
      print("Connection established")
      cur = conn.cursor()
    except Exception as e:
      print(f"Fout bij connectie maken met RDS PostgreSQL: {e}")
      raise

    # Er kunnen meerdere bestanden in één event zitten
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']

        # Decodeert eventuele spaties (%20) enz.
        object_key = urllib.parse.unquote_plus(
            record['s3']['object']['key']
        )

        object_size = record['s3']['object']['size']

        extension = os.path.splitext(object_key)[1]
        upload_time = record['eventTime']
        event_name = record['eventName']

        print("=" * 60)
        print("S3 Upload Event")
        print(f"Bucket : {bucket_name}")
        print(f"File   : {object_key}")
        print(f"Extension : {extension}")
        print(f"Size   : {object_size} bytes")
        print(f"Event       : {event_name}")
        print(f"Upload time : {upload_time}")
        print("=" * 60)

        S3Object = readS3Object(s3=s3, bucket_name=bucket_name, object_key=object_key)
        content = S3Object["Body"].read().decode("utf-8")
        print("=" * 60)
        print("File contents:")
        print(content)
        print("=" * 60)

        print(f"Content-Type : {S3Object['ContentType']}")
        print(f"LastModified : {S3Object['LastModified']}")
        print(f"ETag         : {S3Object['ETag']}")

        try:
          insert_query = """
      INSERT INTO uploaded_files_s3
      (
            filename,
            extension,
            file_size,
            content_type,
            upload_time,
            last_modified,
            etag,
            bucket_name 
      )
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
      """
          record_to_insert = (object_key, extension, object_size, S3Object['ContentType'], upload_time, S3Object['LastModified'], S3Object['ETag'], bucket_name)

          cur.execute(insert_query, record_to_insert)
          conn.commit()
          print("record inserted successfully into s3objects table")

        except Exception as e:
          print(f"Fout bij toevoegen logrecord : {e}")
            
    if cur:
      cur.close()
    if conn:
      conn.close()
  
    return {
        "statusCode": 200,
        "body": "Event processed successfully"
    }