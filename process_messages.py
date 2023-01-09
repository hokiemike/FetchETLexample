
import localstack_client.session
import json
import psycopg2

from OutputRow import OutputRow

QUEUE_URL = "http://localhost:4566/000000000000/login-queue"


#get an item from the queue
def extract_message():
    session = localstack_client.session.Session()
    sqs_client = session.client('sqs')
    response = sqs_client.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )
    messages = response.get('Messages', [])
    message = None
    if len(messages) > 0:
        message = messages[0]
        receipt_handle = message["ReceiptHandle"]

        # Delete received message from queue
        #sqs_client.delete_message(
        #    QueueUrl=QUEUE_URL,
        #    ReceiptHandle=receipt_handle
        #)
        print('Received and deleted message: %s' % message)
    
    return message

#transform the queue item into a row
def transform_message(message):
        message_body = json.loads(message["Body"])
        print(f"Message body: {message_body}")
        return OutputRow(message_body)

#insert a record into the database
def load_message_into_db(row):
    print(f"Inserting row into DB: {row}")
    connection = None
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="127.0.0.1",
                                    port="5432")
        cursor = connection.cursor()
        postgres_insert_query = """ INSERT INTO user_logins 
                                    (user_id, 
                                    device_type, 
                                    masked_ip, 
                                    masked_device_id, 
                                    locale, 
                                    app_version,
                                    create_date) 
                                    VALUES (%s,%s,%s, %s, %s, %s, now())"""
        record_to_insert = (row.user_id, row.device_type, row.ip, row.device_id, row.locale, row.app_version)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
        count = cursor.rowcount
                
        print(count, "Record inserted successfully into table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into mobile table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def main():
        msg = extract_message()
        while msg is not None:
            row = transform_message(msg)
            if (row.validRow):
                load_message_into_db(row)
            msg = extract_message()



if __name__ == "__main__":
    main()