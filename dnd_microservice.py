import pika
import json

# RabbitMQ configurations
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'dnd_requests'

LOOT_TABLE_FILE = 'loot_tables.json'

def handle_request(ch, method, properties, body):
    try:
        request = json.loads(body)
        if request.get("action") == "create_custom_loot_table":
            loot_table_data = request.get("loot_table")
            with open(LOOT_TABLE_FILE, 'a') as file:
                file.write(json.dumps(loot_table_data) + '\n')
            response = {"status": "success"}
        else:
            response = {"status": "error", "message": "Unsupported action"}
    except Exception as e:
        response = {"status": "error", "message": str(e)}

    ch.basic_publish(exchange='', routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

# 
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=handle_request)
    print("Waiting for requests...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
