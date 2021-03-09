# Don't forget to change this file's name before submission.
import sys
import os
import enum
import socket
import struct

class TftpProcessor(object):


    class TftpPacketType(enum.Enum):
        RRQ = 1
        WRQ=2
        DATA=3
        ACK=4
        ERROR=5
    def __init__(self,ipadress,text,soc):
        self.ipadress=ipadress
        self.type='octet'
        self.text=text
        self.packet_buffer = []
        self.soc=soc


    def process_udp_packet(self, packet_data, packet_source):


        er = packet_data[0:2]
        ermsg = packet_data[2:4]
        if int.from_bytes(er, byteorder='big') == 5:
            if int.from_bytes(ermsg, byteorder='big') == 0:
                print("Not defined, see error message (if any).")
            elif int.from_bytes(ermsg, byteorder='big') == 1:
                print("File not found")
            elif int.from_bytes(ermsg, byteorder='big') == 2:
                print("Access violation.")
            elif int.from_bytes(ermsg, byteorder='big') == 3:
                print("Disk full or allocation exceeded")
            elif int.from_bytes(ermsg, byteorder='big') == 4:
                print("Illegal TFTP operation.")
            elif int.from_bytes(ermsg, byteorder='big') == 5:
                print("Unknown transfer ID.")
            elif int.from_bytes(ermsg, byteorder='big') == 6:
                print("File already exists.")
            elif int.from_bytes(ermsg, byteorder='big') == 7:
                print("No such user.")
            exit(-1)
        print(f"Received a packet from {packet_source}")

        ack=struct.pack("!BBBB",0,4,packet_data[2],packet_data[3])
        self.soc.sendto(ack,packet_source)
        cont = packet_data[4:]
        self.packet_buffer.append(cont)




    def get_next_output_packet(self):
        return self.packet_buffer.pop(0)

    def has_pending_packets_to_be_sent(self):
      return len(self.packet_buffer) != 0



    def request_file(self, file_path_on_server):
        sp = struct.pack('!BB'+str(len(bytes(file_path_on_server, 'utf-8')))+'sB5sB',0,1, bytes(file_path_on_server, 'utf-8'), 0, bytes(self.type, 'utf-8'), 0)
        self.soc.sendto(sp, (self.ipadress, 69))
        while True:
            data, serve = self.soc.recvfrom(516)
            self.process_udp_packet(data,serve)
            if len(data) < 516:
                break
        file =open("filename.txt","wb")
        i=0
        while i!=len(self.packet_buffer):
         file.write(self.packet_buffer[i])
         i+=1
    def upload_file(self, file_path_on_server):
        sp = struct.pack('!BB'+str(len(bytes(file_path_on_server, 'utf-8')))+'sB5sB',0, 2, bytes(file_path_on_server, 'utf-8'), 0, bytes(self.type, 'utf-8'), 0)
        self.soc.sendto(sp, (self.ipadress, 69))
        f = open("filename.txt", 'rb')
        data, serve = self.soc.recvfrom(600)
        er = data[0:2]
        ermsg = data[2:4]
        if int.from_bytes(er, byteorder='big') == 5:
            if int.from_bytes(ermsg, byteorder='big') == 0:
                print("Not defined, see error message (if any).")
            elif int.from_bytes(ermsg, byteorder='big') == 1:
                print("File not found")
            elif int.from_bytes(ermsg, byteorder='big') == 2:
                print("Access violation.")
            elif int.from_bytes(ermsg, byteorder='big') == 3:
                print("Disk full or allocation exceeded")
            elif int.from_bytes(ermsg, byteorder='big') == 4:
                print("Illegal TFTP operation.")
            elif int.from_bytes(ermsg, byteorder='big') == 5:
                print("Unknown transfer ID.")
            elif int.from_bytes(ermsg, byteorder='big') == 6:
                print("File already exists.")
            elif int.from_bytes(ermsg, byteorder='big') == 7:
                print("No such user.")
            exit(-1)
        elif int.from_bytes(er, byteorder='big') == 4:
          lines = f.read()
          print(lines)
          self.packet_buffer = [lines[i:i + 512] for i in range(0, len(lines), 512)]
          while self.has_pending_packets_to_be_sent():
            wr = bytearray(data[0:4])
            testBytes = wr[2:4]
            inttobytes = int.from_bytes(testBytes, byteorder='big') + 1
            vs=self.get_next_output_packet()
            send_to = struct.pack("!BBh"  +str(len(vs))+ 's', 0, 3, inttobytes,vs)
            self.soc.sendto(send_to, serve)
            data, serve = self.soc.recvfrom(600)
            if int.from_bytes(er, byteorder='big') == 5:
                if int.from_bytes(ermsg, byteorder='big') == 0:
                    print("Not defined, see error message (if any).")
                elif int.from_bytes(ermsg, byteorder='big') == 1:
                    print("File not found")
                elif int.from_bytes(ermsg, byteorder='big') == 2:
                    print("Access violation.")
                elif int.from_bytes(ermsg, byteorder='big') == 3:
                    print("Disk full or allocation exceeded")
                elif int.from_bytes(ermsg, byteorder='big') == 4:
                    print("Illegal TFTP operation.")
                elif int.from_bytes(ermsg, byteorder='big') == 5:
                    print("Unknown transfer ID.")
                elif int.from_bytes(ermsg, byteorder='big') == 6:
                    print("File already exists.")
                elif int.from_bytes(ermsg, byteorder='big') == 7:
                    print("No such user.")
                exit(-1)
            elif int.from_bytes(er, byteorder='big') == 4:
                continue
            else:
                print("Malformed packet")
                exit(-1)
        else :
             print("Malformed packet ")
             exit(-1)

def check_file_name():
    script_name = os.path.basename(__file__)
    import re
    matches = re.findall(r"(\d{4}_)+lab1\.(py|rar|zip)", script_name)
    if not matches:
        print(f"[WARN] File name is invalid [{script_name}]")
    pass

def parse_user_input(address, operation, file_name):
    soc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    soc.bind((IPAddr, 52378))
    ram=TftpProcessor(address,file_name,soc)
    if operation == "push":
        print(f"Attempting to upload [{file_name}]...")
        ram.upload_file(file_name)
    elif operation == "pull":
        print(f"Attempting to download [{file_name}]...")
        ram.request_file(file_name)
    else:
        exit(1)



def get_arg(param_index, default):
    """
        Gets a command line argument by index (note: index starts from 1)
        If the argument is not supplies, it tries to use a default value.
        If a default value isn't supplied, an error message is printed
        and terminates the program.
    """
    try:
        return sys.argv[param_index]
    except IndexError as e:
        if default:
            return default
        else:
            print(e)
            print(
                f"[FATAL] The comamnd-line argument #[{param_index}] is missing")
            exit(-1)    # Program execution failed.


def main():
    """
     Write your code above this function.
    if you need the command line arguments
    """
    print("*" * 50)
    print("[LOG] Printing command line arguments\n", ",".join(sys.argv))
    check_file_name()
    print("*" * 50)

    # This argument is required.
    # For a server, this means the IP that the server socket
    # will use.
    # The IP of the server, some default values
    # are provided. Feel free to modify them.
    ip_address = get_arg(1, "192.168.1.113")
    operation = get_arg(2, "pull")
    file_name = get_arg(3, "test.txt")
    print(ip_address)
    # Modify this as needed.
    parse_user_input(ip_address, operation, file_name)


if __name__ == "__main__":
    main()