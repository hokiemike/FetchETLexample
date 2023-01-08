
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

    print(f"Number of messages received: {len(response.get('Messages', []))}")
    return response.get("Messages", [])

#transform the queue item into a row
def transform_message(message):
        print(f"Receipt Handle: {message['ReceiptHandle']}")
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
    for msg in extract_message():
        row = transform_message(msg)
        load_message_into_db(row)


if __name__ == "__main__":
    main()