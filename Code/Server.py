import socket
import thread
import datetime


class DataFields:
    def __init__(self, data):
        name_length = data[:2]
        data = data[2:]

        name = data[:int(name_length)]
        data = data[int(name_length):]

        operation = data[:2]
        data = data[2:]

        data_length = data[:3]
        data = data[-int(data_length):]

        self.name = name
        self.message = data
        self.operation = operation

    def __str__(self):
        if self.message.lower() == "quit":
            now = datetime.datetime.now()
            return "{}:{} {} has left the chat!".format(now.hour, now.minute, self.name)
        elif self.message:
            now = datetime.datetime.now()
            return "{}:{} {}: {}".format(now.hour, now.minute, self.name, self.message)
        else:
            return "no message found"


class ChatServer(socket.socket):
    clients = []

    def __init__(self):
        socket.socket.__init__(self)
        self.bind(('0.0.0.0', 542))
        self.listen(5)

    def run(self):
        print "Server started"
        try:
            self.accept_clients()
        except Exception as ex:
            print ex
        finally:
            print "Server closed"
            for client in self.clients:
                client.close()
            self.close()

    def accept_clients(self):
        while True:
            (client_socket, address) = self.accept()
            print "got new connection"
            self.clients.append(client_socket)
            thread.start_new_thread(self.receive, (client_socket,))

    def receive(self, client):
        while True:
            data = client.recv(1024)
            if data == '':
                break

            data_fields = DataFields(data)

            if data_fields.message.lower() == "quit":
                self.on_message(client, data_fields)
                self.clients.remove(client)
                client.close()
                thread.exit()
                print self.clients

            self.on_message(client, data_fields)

    def on_message(self, client, data_fields):
        if data_fields.operation == "01":
            self.broadcast(data_fields, client)

    def broadcast(self, data_fields, blacklisted_client):
        # Sending message to all clients
        for client in self.clients:
            if client is not blacklisted_client:
                client.send(str(data_fields))


def main():
    server = ChatServer()
    server.run()


if __name__ == "__main__":
    main()
