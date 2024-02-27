DND custom loot table small test program

This program demonstrates how RabbitMQ can be used to facilitate communication between a microservice and client. This uses AMQP (advanced messaging queuing protocol)

dnd_client.py: Sends request to microservice to create custom loot tables
dnd_microservice.py: receives requests from client to create custom loot tables, stores data

How to run:
1. Ensure RabbitMQ is installed and configured. This can be done from their official website
2. Run both .py files (see how to run dnd_client.py below)
3. Then it will be printed in a .json file, this will automcatically create a file

How to add custom:
In terminal write this: python dnd_client.py add-loot --name "____" --rarity "____" --cost ___
Ex.  python dnd_client.py add-loot --name "Sword" --rarity "Legendary" --cost 1000

How to delete an item:
ex. python dnd_client.py delete-loot --name "____"

UML diagram:
![image](https://github.com/ashleykmm1/partner-project1/assets/130413779/49912539-5f02-40f7-b19f-e4ccfbafa1d2)

