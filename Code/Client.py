import socket
from threading import Thread


class Client:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect(('127.0.0.1', 542))
        self.name = ""
        self.read_thread = Thread(target=self.read_form_server).start()
        self.write_thread = Thread(target=self.write_to_server).start()

    def read_form_server(self):
        while True:
            data = self.socket.recv(1024)
            print data

    def write_to_server(self):
        while True:
            if self.name is "":
                self.name = self.get_new_name()
            else:
                data = raw_input()
                data_to_send = self.set_data_to_send(data, self.name)
                self.socket.send(data_to_send)

    def set_data_to_send(self, data, client_name):
        name_length = str(len(client_name)).rjust(2, '0')
        data_length = str(len(data)).rjust(3, '0')

        return "{}{}01{}{}".format(name_length, client_name, data_length, data)

    def get_new_name(self):
        current_name = raw_input("please enter your name")
        if current_name[0] is not "@":
            return current_name
        else:
            print "the name is insufficient please try again"
            return self.get_new_name()


def main():
    client = Client()


if __name__ == "__main__":
    main()
