import pika
import uuid
import json

class CustomLootTable:
    def __init__(self, name, rarity, value):
        self.name = name
        self.rarity = rarity
        self.value = value

class DNDClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, request):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='dnd_requests',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=request)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def create_custom_loot_table(self, loot_table):
        request = {
            "action": "create_custom_loot_table",
            "loot_table": {
                "name": loot_table.name,
                "rarity": loot_table.rarity,
                "value": loot_table.value
            }
        }
        return self.call(json.dumps(request))

def main():
    client = DNDClient()

    # test, this will print name rarity and value in a json file.
    custom_loot_table = CustomLootTable(name="Sword of Power", rarity="Legendary", value=1000)
    response = client.create_custom_loot_table(custom_loot_table)
    print("Response:", response)

    client.connection.close()

if __name__ == "__main__":
    main()
