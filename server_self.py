import socket, select
from collections import defaultdict 
 

#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
	#Do not send the message to master socket and the client who has send us the message
	for socket in CONNECTION_LIST:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				# broken socket connection may be, chat client pressed ctrl+c for example
				socket.close()
				CONNECTION_LIST.remove(socket)
				
		
if __name__ == "__main__":

	# List to keep track of socket descriptors
	CONNECTION_LIST = []
	nicknames_address_map = defaultdict(list)
	#nicknames_address_map.setDefault(key, []).append(value)
	chatrooms = []
	chatrooms_member_map={}
	RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
	PORT = 4555
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# this has no effect, why ?
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("127.0.0.1", PORT))
	server_socket.listen(10)
 
	# Add server socket to the list of readable connections
	CONNECTION_LIST.append(server_socket)
 
	print "Chat server started on port " + str(PORT)
 
	while 1:
		# Get the list sockets which are ready to be read through select
		read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
		for sock in read_sockets:
			#New connection
			if sock == server_socket:
				# Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				print "Client (%s, %s) connected" % addr
				
				broadcast_data(sockfd, "We have someone here !!! \n")
				
			#Some incoming message from a client
			else:
				# Data recieved from client, process it
				try:
					#In Windows, sometimes when a TCP program closes abruptly,
					# a "Connection reset by peer" exception will be thrown
					data = sock.recv(RECV_BUFFER)
					input = data.split()
					if 'NICK' in data:
						name = data.split()[1]
						nicknames_address_map[str(sock.getpeername())] = name
						#broadcast_data(sock, "\r" + nicknames_address_map[str(sock.getpeername())]+"\n")
						sock.sendall("Welcome "+ nicknames_address_map[str(sock.getpeername())] + "\n")
					
					elif 'CREATE' in data:
						room_name = data.split()[1]
						create_room(room_name,sock)
					
					elif 'LISTROOMS' in data:
						sock.sendall("\n ROOMS LIST\n")
						for room in chatrooms:
							msg = "\t" + room 
							newline="\n"
							sock.sendall(room)
							sock.sendall(newline)
										 
				except:
					broadcast_data(sock, "Client (%s, %s) is offline" % addr)
					print "Client (%s, %s) is offline" % addr
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue
	 
	server_socket.close()
	
	def create_room(self,room_name,sock):
		self.chatrooms.append(room_name)
		sock.sendall(room_name + " created\n")
		if room_name in self.chatrooms_member_map.keys():
			self.chatrooms_member_map[room_name].append(self.nicknames_address_map[str(sock.getpeername())])
		else:
			self.chatrooms_member_map[room_name] = self.nicknames_address_map[str(sock.getpeername())]