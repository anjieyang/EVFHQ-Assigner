import os
import psycopg2
import pika
import json


def setup_database_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )


def setup_rabbitmq_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST'),
            port=os.getenv('RABBITMQ_PORT')
        ))
    channel = connection.channel()
    return connection, channel


def fetch_unassigned_video(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT video_id FROM videos WHERE location IS NULL AND server_id IS NULL LIMIT 1;")
        row = cur.fetchone()
        return row[0] if row else None


def assign_task_to_downloader(video_id, channel, conn, server_id):
    with conn.cursor() as cur:
        message = json.dumps({'video_id': video_id, 'server_id': server_id})
        channel.basic_publish(
            exchange='',
            routing_key='video_download_queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        cur.execute(
            "UPDATE videos SET server_id = %s WHERE video_id = %s;", (-1, video_id))
        conn.commit()
        print(f"Task for video_id {video_id} assigned to server.")


def handle_task_request(channel, method, properties, body):
    server_id = json.loads(body.decode())['server_id']
    conn = setup_database_connection()
    video_id = fetch_unassigned_video(conn)
    if video_id:
        assign_task_to_downloader(video_id, channel, conn, server_id)
    else:
        print("No videos left to process.")
    channel.basic_ack(delivery_tag=method.delivery_tag)


def update_video_status(channel, method, properties, body):
    data = json.loads(body.decode())
    conn = setup_database_connection()
    with conn.cursor() as cur:
        if data['status_code'] == 0:
            cur.execute(
                "UPDATE videos SET location = %s, server_id = %s WHERE video_id = %s;",
                (data['location'], data['server_id'], data['video_id']))
        else:
            cur.execute(
                "UPDATE videos SET location = %s, server_id = %s WHERE video_id = %s;",
                ("FAILED", data['server_id'], data['video_id']))
        conn.commit()
    print(
        f"Video {data['video_id']} processed {'SUCCESSFULLY' if data['status_code'] == 0 else 'FAILED'} by server {data['server_id']}.")

    video_id = fetch_unassigned_video(conn)
    server_id = data['server_id']
    if video_id:
        assign_task_to_downloader(video_id, channel, conn, server_id)
    else:
        print("No videos left to process.")

    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    conn = setup_database_connection()
    connection, channel = setup_rabbitmq_connection()
    channel.queue_declare(queue="task_request_queue", durable=True)
    channel.queue_declare(queue="video_download_queue", durable=True)
    channel.queue_declare(queue="video_download_response_queue", durable=True)

    channel.basic_consume(
        queue="task_request_queue",
        on_message_callback=handle_task_request,
        auto_ack=False
    )
    channel.basic_consume(
        queue="video_download_response_queue",
        on_message_callback=update_video_status,
        auto_ack=False
    )

    print("Assigner is running. Waiting for task requests and processing responses...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping assigner.")
    finally:
        connection.close()
        conn.close()


if __name__ == "__main__":
    main()
