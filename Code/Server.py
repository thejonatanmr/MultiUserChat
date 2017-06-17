import socket
import thread
import datetime


# a class used to save the data sent by the client and to divide it to easy to use fields
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


# the main thread
class ChatServer(socket.socket):
    clients = []
    name_dic = {}

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

    # this function runs in a loop and adds new clients that tries to enter the server
    # when a new client is excepted a new thread is opened to handle the client's input
    def accept_clients(self):
        while True:
            (client_socket, address) = self.accept()
            print "got new connection"
            self.clients.append(client_socket)
            thread.start_new_thread(self.receive, (client_socket,))

    # this function is called in a loop. waiting for client input and when input is found divides it to data fields
    def receive(self, client):
        while True:
            data = client.recv(1024)
            if data == '':
                break

            data_fields = DataFields(data)

            if data_fields.message.lower() == "quit":
                self.on_message(client, data_fields)
                self.disconnect(self, client, data_fields)
                break

            if not self.on_message(client, data_fields):
                break
        thread.exit()

    # when a new message from a client is found this function is called to handle the message
    def on_message(self, client, data_fields):
        if self.check_name(client, data_fields):
            if data_fields.operation == "01":
                self.broadcast(data_fields, client)
            return True
        else:
            data_fields.message = "your name is unavailable please change it"
            self.disconnect(client, data_fields)
            return False

    # this function broadcasts a message to all clients connected to the server except the sender
    def broadcast(self, data_fields, blacklisted_client):
        for client in self.clients:
            if client is not blacklisted_client:
                client.send(str(data_fields))

    # this function checks the client's name. returns true if the name is available or the name is registered to the
    # client, returns false if the name is unavailable
    def check_name(self, client, data_fields):
        if self.name_dic:
            if data_fields.name in self.name_dic:
                if self.name_dic[data_fields.name] == client:
                    return True
                else:
                    return False
        self.name_dic[data_fields.name] = client
        return True

    # disconnects a client and sends him a message
    def disconnect(self, client, data_fields):
        del self.name_dic[data_fields.name]
        data_fields.name = "server"
        client.send(str(data_fields))
        self.clients.remove(client)
        client.close()


def main():
    server = ChatServer()
    server.run()


if __name__ == "__main__":
    main()
