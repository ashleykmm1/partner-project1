import argparse
import pika
import uuid
import json

class CustomLootTable:
    def __init__(self, name, rarity, cost):  
        self.name = name
        self.rarity = rarity
        self.cost = cost  

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

    def delete_custom_loot_table(self, request):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='dnd_requests',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(request))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

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
                "cost": loot_table.cost  
            }
        }
        return self.call(json.dumps(request))

    def read_loot_tables(self):
        request = {"action": "read_loot_tables"}
        response = self.call(json.dumps(request))
        response_data = json.loads(response)
        if response_data["status"] == "success":
            loot_tables = response_data.get("loot_tables", [])
            print("Existing Loot Tables:")
            for loot_table in loot_tables:
                print(loot_table)
        else:
            print("Error:", response_data["message"])

def add_loot(args):
    client = DNDClient()
    custom_loot_table = CustomLootTable(name=args.name, rarity=args.rarity, cost=args.cost)  
    response = client.create_custom_loot_table(custom_loot_table)
    print("Response:", response)
    client.connection.close()

def update_loot(args):
    client = DNDClient()
    custom_loot_table = CustomLootTable(name=args.name, rarity=args.rarity, cost=args.cost)
    response = client.update_custom_loot_table(custom_loot_table)
    print("Response:", response)
    client.connection.close()

def delete_loot(args):
    client = DNDClient()
    request = {
        "action": "delete_custom_loot_table",
        "loot_table_name": args.name
    }
    response = client.delete_custom_loot_table(request)
    print("Response:", response)
    client.connection.close()

def read_loot_tables(args):
    client = DNDClient()
    client.read_loot_tables()
    client.connection.close()

def main():
    parser = argparse.ArgumentParser(description="Manage custom loot tables")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    parser_add_loot = subparsers.add_parser("add-loot", help="Add a custom loot table")
    parser_add_loot.add_argument("--name", required=True, help="Name of the loot")
    parser_add_loot.add_argument("--rarity", required=True, help="Rarity of the loot")
    parser_add_loot.add_argument("--cost", required=True, type=int, help="Cost of the loot")

    parser_update_loot = subparsers.add_parser("update-loot", help="Update a custom loot table")
    parser_update_loot.add_argument("--name", required=True, help="Name of the loot")
    parser_update_loot.add_argument("--rarity", required=True, help="New rarity of the loot")
    parser_update_loot.add_argument("--cost", required=True, type=int, help="New cost of the loot")

    parser_delete_loot = subparsers.add_parser("delete-loot", help="Delete a custom loot table")
    parser_delete_loot.add_argument("--name", required=True, help="Name of the loot")

    subparsers.add_parser("read-loot-tables", help="Read existing loot tables")

    args = parser.parse_args()

    if args.subcommand == "add-loot":
        add_loot(args)
    elif args.subcommand == "update-loot":
        update_loot(args)
    elif args.subcommand == "delete-loot":
        delete_loot(args)
    elif args.subcommand == "read-loot-tables":
        read_loot_tables(args)


if __name__ == "__main__":
    main()
