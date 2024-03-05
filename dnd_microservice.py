import pika
import json
import os

# RabbitMQ configurations
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'dnd_requests'

LOOT_TABLE_FILE = 'loot_tables.json'

def handle_request(ch, method, properties, body):
    try:
        request = json.loads(body)
        action = request.get("action")
        if action == "create_custom_loot_table":
            loot_table_data = request.get("loot_table")
            with open(LOOT_TABLE_FILE, 'a') as file:
                file.write(json.dumps(loot_table_data) + '\n')
            response = {"status": "success"}
        elif action == "read_loot_tables":
            with open(LOOT_TABLE_FILE, 'r') as file:
                loot_tables = [json.loads(line) for line in file.readlines()]
            response = {"status": "success", "loot_tables": loot_tables}
        elif action == "update_custom_loot_table":
            response = {"status": "error", "message": "Update not implemented yet"}
        elif action == "delete_custom_loot_table":
            loot_table_name = request.get("loot_table_name")
            with open(LOOT_TABLE_FILE, 'r') as file:
                loot_tables = [json.loads(line) for line in file.readlines()]
            updated_loot_tables = [lt for lt in loot_tables if lt.get("name") != loot_table_name]
            with open(LOOT_TABLE_FILE, 'w') as file:
                for loot_table in updated_loot_tables:
                    file.write(json.dumps(loot_table) + '\n')
            response = {"status": "success"}
        else:
            response = {"status": "error", "message": "Unsupported action"}
    except Exception as e:
        response = {"status": "error", "message": str(e)}

    ch.basic_publish(exchange='', routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=handle_request)
    print("Waiting for requests...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
