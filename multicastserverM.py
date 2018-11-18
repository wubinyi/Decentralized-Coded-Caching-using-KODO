import kodo
import socket
import struct
import sys
import time
import os
import random

#MCAST_GRP = '224.1.1.1'
MCAST_GRP = '239.192.1.100'
MCAST_PORT = 5007
RECE_MCAST_PORT = 5008
BUFFER_SIZE = 1024
TCP_IP = '192.168.1.103'
TCP_PORT = 31500
SYMBOLSIZE = 512
BUFFERSIZE = BUFFER_SIZE

FILE_PATH = []
ORIGINAL_FILE_PATH = '/home/wubinyi/Kodo-Workspace/'
SERVER_FILE_PATH = '/home/wubinyi/Kodo-Workspace/serverfile/'

# set tcp server
def server_tcp(numberOfClient):
	address = (TCP_IP, TCP_PORT)
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(address)
	server.listen(numberOfClient)
	return server

# set multicast receiver
def multicast_receiver():

	sock_receiver = socket.socket(
		family=socket.AF_INET,
		type=socket.SOCK_DGRAM,
		proto=socket.IPPROTO_UDP)

	sock_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	sock_receiver.bind(('', RECE_MCAST_PORT))
	mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

	sock_receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	
	return sock_receiver

		
# set multicast sender
def multicast_sender():
	sock_sender = socket.socket(
		family=socket.AF_INET,
		type=socket.SOCK_DGRAM,
		proto=socket.IPPROTO_UDP)

	sock_sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)	
	
	return sock_sender

# seperate the file, it is better to cashing
# K files, N clients, K size of the whole file
# memorySize(M) = memorySizeRatio(R) * S = R * S = RS;
# M/k size for every file in placement phase [RS/K]
# every file will be seperated into {S/(RS/K) = K/R}
# the name like this : ---------------------------------> xxx|xxx
def fileSperate(filePath, memorySizeRatio):

	numberOfFile = len(filePath)
	#default memorySizeRatio = 1, so the caching memory size of a client is S
	numberOfSeperatefile = numberOfFile/memorySizeRatio

	for fileSequence in range(0, numberOfFile, 1):
		#caculate the size of seperate file
		fileSize = os.path.getsize(filePath[fileSequence])
		seperatefileSize = fileSize / numberOfSeperatefile
		if fileSize % numberOfSeperatefile:
			seperatefileSize = seperatefileSize + 1
		lengthOfZero = seperatefileSize * numberOfSeperatefile - fileSize

		#begin to seperate the file, every seperate file's size is 'seperatefileSize'
		fread = open(FILE_PATH[fileSequence], "rb")
		for filePart in range(0, numberOfSeperatefile - 1, 1):
			f = open(SERVER_FILE_PATH + str(fileSequence) + '|' + str(filePart), 'wb')
			f.write(fread.read(seperatefileSize))
			f.close()

		# the last seperate file need to add some '\x00'
		f = open(SERVER_FILE_PATH + str(fileSequence) + '|' + str(filePart + 1), 'wb')
		f.write(fread.read())
		f.write(lengthOfZero * '\x00')
		f.close()
		fread.close()
	
	return seperatefileSize


def randomfile(numberOfFile, numberOfClient, memorySizeRatio):
	
	#statement 
	randomMatrix = []
	numberOfSeperatefile = numberOfFile/memorySizeRatio

	#creat the random matrix, each client has a part of all files 
	tempRange = range(0, numberOfSeperatefile, 1)
	for i in range(0, numberOfClient, 1):
		matrixElement = []
		for fileSequence in range(0, numberOfFile, 1):
			tempRandom = random.sample(tempRange, 1)
			matrixElement.append(str(fileSequence) + '|' +str(tempRandom[0]))
		randomMatrix.append(matrixElement)

	# print the randon matrix for every client
	length = len(randomMatrix)
	print ""
	for i in range(0,length,1):
		print 'client' + str(i)+':    '+str(randomMatrix[i])
	print ""

	return randomMatrix			 


def findXorfile(numberOfFile, numberOfClient, randomMatrix, randomAskFile, memorySizeRatio):

	xorFilename = []
	notXorFilename = []
	numberOfSeperatefile = numberOfFile/memorySizeRatio
	
	print ''
	print randomAskFile
	print ''

	# indication of client x, just for simulation
	clientSimu = 0
	xorFileSimuFlag = []
	notXorFileSimuFlag = []  
	
	# copy the randomMatrix to the copyRandomMatrix(because of pointer)
	copyRandomMatrix = []	
	for i in range(0, len(randomMatrix), 1):
		temp = []
		for j in range(0, len(randomMatrix[i]), 1):
			temp.append(randomMatrix[i][j])
		
		copyRandomMatrix.append(temp)

	
	# use to record which part of the ask file client has
	tempMatrix = []
	for i in range(0, numberOfClient, 1):
		tempMatrix.append([])

	
	# find the xor file from two client which has the same ask file
	for sourceClient in range(0, numberOfClient, 1):
		askFile = randomAskFile[sourceClient]
		# begin to search the client after the sourceClient
		for targetClient in range(sourceClient+1, len(randomAskFile), 1):			
			# askFile locate in the line 'askFile'
			# compare the 'askFile' -------------------------------------------> True
			# the cached file of the two client are not same-------------------> True
			logicalResult = copyRandomMatrix[sourceClient][askFile] != copyRandomMatrix[targetClient][askFile]
			if randomAskFile[targetClient] == askFile and logicalResult:				
				# askedOfSourceClient: the source client has which part of the ask file
				# askedOfTargetClient: the target client has which part of the ask file
				askedOfSourceClient = ','.join( tempMatrix[sourceClient] )
				askedOfTargetClient = ','.join( tempMatrix[targetClient] )				
				# the two client do not have the part of ask file from each other
				logicalResult_1 = askedOfSourceClient.find( copyRandomMatrix[targetClient][askFile] ) == -1
				logicalResult_2 = askedOfTargetClient.find( copyRandomMatrix[sourceClient][askFile] ) == -1
				if logicalResult_1 and logicalResult_2:
					xorFilename.append( copyRandomMatrix[sourceClient][askFile] )
					xorFilename.append( copyRandomMatrix[targetClient][askFile] )
					tempMatrix[sourceClient].append( copyRandomMatrix[targetClient][askFile] )
					tempMatrix[targetClient].append( copyRandomMatrix[sourceClient][askFile] )
					# for simulation
					if sourceClient == clientSimu: 
						xorFileSimuFlag.append(True)
					else:
						xorFileSimuFlag.append(False)

	# find the xor file from two client which has the different ask file
	for sourceClient in range(0, numberOfClient, 1):
		for cacheFile in range(0, numberOfFile, 1):
			# get the file sequence number of the cachefile
			# the cacheFile indicate the file sequence number
			fileSequenNumber = cacheFile
			cacheFileSourceClient = cacheFile
			# tempMatrix record the part of the ask file which already have
			# if the file sequence number is the same as the ask file of client, record it
			# and we do not need to search the matrix, because we have done this before
			# only if the file sequence number is not same as the ask file of client, you search the matrix
			if fileSequenNumber == randomAskFile[sourceClient]:
				tempMatrix[sourceClient].append(copyRandomMatrix[sourceClient][cacheFile])
			else:
				# search the client after the source client
				for targetClient in range(sourceClient+1, numberOfClient, 1):
					askFileOfTarg = randomAskFile[targetClient]
					# if the target client ask the 'cacheFileSourceClient' 
					# we may be can find the xor file
					if askFileOfTarg == cacheFileSourceClient:
						askFileOfSour = randomAskFile[sourceClient]
						# the target(xor) file of each client muss not be owned by the other
						# fLogR -> first logical result ; sLogR -> second logical result
						fLogR = copyRandomMatrix[targetClient][askFileOfSour] != copyRandomMatrix[sourceClient][askFileOfSour]
						sLogR = copyRandomMatrix[targetClient][askFileOfTarg] != copyRandomMatrix[sourceClient][askFileOfTarg]
						if fLogR and sLogR: 
							# askedOfSourceClient: the source client has which part of the ask file
							# askedOfTargetClient: the target client has which part of the ask file
							askedOfSourceClient = ','.join(tempMatrix[sourceClient])
							askedOfTargetClient = ','.join(tempMatrix[targetClient])
							# the two client do not have the part of ask file from each other	
							fLogR = askedOfSourceClient.find( copyRandomMatrix[targetClient][askFileOfSour] ) == -1
							sLogR = askedOfTargetClient.find( copyRandomMatrix[sourceClient][askFileOfTarg] ) == -1	
							if fLogR and sLogR:
								xorFilename.append( copyRandomMatrix[sourceClient][askFileOfTarg] )
								xorFilename.append( copyRandomMatrix[targetClient][askFileOfSour] )
								tempMatrix[sourceClient].append( copyRandomMatrix[targetClient][askFileOfSour] )
								tempMatrix[targetClient].append( copyRandomMatrix[sourceClient][askFileOfTarg] )
								# for simulation
								if sourceClient == clientSimu: 
									xorFileSimuFlag.append(True)
								else:
									xorFileSimuFlag.append(False)
								
				
				
	print 'tempMatrix,after sending the XOR file, the client has this file of his asking file:'
	print ''
	length = len(tempMatrix)
	print ""
	for i in range(0,length,1):
		print 'client' + str(i)+':    '+str(randomAskFile[i])+'     '+str(tempMatrix[i])
	print ""

	# creat a full matrix, which contains the whole ask file of every client
	# use to compare with tempMatrix, then we can find out the not xor files
	fullMatrix = []
	for i in range(0, numberOfClient, 1):
		fullMatrix.append([])
	for i in range(0, numberOfClient, 1):
		for j in range(0, numberOfSeperatefile, 1):
			fullMatrix[i].append(str(randomAskFile[i]) + '|' + str(j))
	
	# filenameMatrix is used to store the not xor files
	# but filenameMatrix is a matrix, at last change it to vector
	notXorFileSimuTemp = []
	filenameMatrix = []
	for i in range(0, numberOfFile, 1):
		filenameMatrix.append([])
	for i in range(0, numberOfClient, 1):
		templist_1 = ','.join(filenameMatrix[randomAskFile[i]])
		templist_2 = ','.join(tempMatrix[i])
		for j in range(0, numberOfSeperatefile, 1):
			if templist_1.find(fullMatrix[i][j]) == -1 and templist_2.find(fullMatrix[i][j]) == -1:
				filenameMatrix[randomAskFile[i]].append(fullMatrix[i][j])
				# for simulation
				if i == clientSimu: 
					notXorFileSimuTemp.append(fullMatrix[i][j])


	# store the not xor files from matrix(filenameMatrix) to vector(notXorFilename)
	for i in range(0, len(filenameMatrix), 1):
		for j in range(0, len(filenameMatrix[i]), 1):
			notXorFilename.append(filenameMatrix[i][j])
			# for simulation
			if ','.join(notXorFileSimuTemp).find(filenameMatrix[i][j]) != -1:
				notXorFileSimuFlag.append(True)
			else:
				notXorFileSimuFlag.append(False)
	
	
	print ''
	print 'this files will be XOR: '
	print xorFilename
	print ''
	print 'this files will not be XOR:'
	print notXorFilename
	print ''
	return xorFilename, notXorFilename, xorFileSimuFlag, notXorFileSimuFlag


def kodoencoder(data):
	# Set the number of symbols (i.e. the generation size in RLNC
	# terminology) and the size of a symbol in bytes
	dataSize = len(data)
	print 'block data size: ',dataSize
	symbols = dataSize / SYMBOLSIZE
	if dataSize%SYMBOLSIZE:
		symbols = symbols + 1
	
	# In the following we will make an encoder factory.
	# The factories are used to build actual encoder
	encoder_factory = kodo.FullVectorEncoderFactoryBinary(
		max_symbols=symbols,
		max_symbol_size=SYMBOLSIZE)

	encoder = encoder_factory.build()
	
	# Assign the data buffer to the encoder so that we can
	# produce encoded symbols
	encoder.set_const_symbols(data)

	return encoder, symbols
'''
def kodoencoder(filepath):

	# Check file.
	if not os.path.isfile(filepath):
		print("{} is not a valid file.".format(filepath))
		sys.exit(1)
	
	# Set the number of symbols (i.e. the generation size in RLNC
	# terminology) and the size of a symbol in bytes
	file_size = os.path.getsize(filepath)
	print 'kodo filesize: ',file_size
	symbols = file_size / SYMBOLSIZE
	if file_size%SYMBOLSIZE:
		symbols = symbols + 1
	#print symbols
	
	# In the following we will make an encoder factory.
	# The factories are used to build actual encoder
	encoder_factory = kodo.FullVectorEncoderFactoryBinary(
		max_symbols=symbols,
		max_symbol_size=SYMBOLSIZE)

	encoder = encoder_factory.build()
	
	# Get the data to encode.
	encodeFile = open(filepath, 'rb')
	data_in = encodeFile.read()
	encodeFile.close()

	# Assign the data buffer to the encoder so that we can
	# produce encoded symbols
	encoder.set_const_symbols(data_in)

	return encoder, symbols
'''

def send_file(sock_sender, filepath, filename, xorFlag, multicastAddress, sock_receiver, fileSimu):

	numberOfFile = len(filepath)
	# in every delivery phase we need to send 'numOfFile' files	
	for fileSeqNum in range(0, numberOfFile, 1):
		# tell the client: server send the new file
		for temp in range(0,15,1):
			sock_sender.sendto('new file', multicastAddress)
		# xorFlag indicates which type of file do we send: xor files or not xor files
		if xorFlag:
			# wenn we send xor file, we need two files every time
			index = fileSeqNum * 2
			# send to the clients which file will we send
			for temp in range(0,15,1):
				checkRrturnData = filename[index] + '-' + filename[index+1]
				sock_sender.sendto(filename[index] + '-' + filename[index+1], multicastAddress)
			if fileSimu[fileSeqNum]:
				print  '\n' + filename[index] + '  XOR  '+ filename[index+1] + '----------------------------'
			else:
				print  '\n' + filename[index] + '  XOR  '+ filename[index+1]

		else:
			# wenn we send not xor file, we need only one files every time
			index = fileSeqNum * 1
			# send to the clients which file will we send, the second filename position,we use 'X'
			for temp in range(0,15,1):
				checkRrturnData = filename[index]+'-'+'X'
				sock_sender.sendto(filename[index]+'-'+'X', multicastAddress)
			if fileSimu[fileSeqNum]:
				print '\n'+filename[index] + ' will be sended--------------------------------'
			else:
				print '\n'+filename[index] + ' will be sended'

		#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# send data with kodo 

		blockSize = 1024 * SYMBOLSIZE
		filepathtokodo = SERVER_FILE_PATH+filepath[fileSeqNum]
		fileSize = os.path.getsize(filepathtokodo)
		numOfBlock = fileSize / blockSize
		if fileSize % blockSize:
			numOfBlock = numOfBlock + 1

		encodeFile = open(filepathtokodo, 'rb')
		
		for blockSeque in range(0, numOfBlock, 1):
			packet_number = 0
			data_in = encodeFile.read(blockSize)
			encoder, symbols = kodoencoder(data_in)
			print 'symbolsize, symbols ', SYMBOLSIZE, symbols


			while True:
				# Generate an encoded packet
				packet = encoder.write_payload()
				# Send the packet.
				sock_sender.sendto(packet, multicastAddress)
	
				if fileSimu[fileSeqNum]:		
					try:
						data = sock_receiver.recv(BUFFER_SIZE)
					except socket.error:
						pass
		   			else:
						if data == str(blockSeque):
							data = ''
							print 'packet_number: ',packet_number
							break
				else: 
					if packet_number > symbols:
						break	

				packet_number = packet_number + 1
			# begin information
			for temp in range(0,15,1):
				sock_sender.sendto('begin', multicastAddress)		
			#time.sleep(0.2)
	
		encodeFile.close()

		'''
		# send data without kodo
		fread = open(SERVER_FILE_PATH+filepath[fileSeqNum], "rb")	
		data = fread.read(512)		
		#begin to xor the two data until empty
		while data:
			
			sock_sender.sendto(data, multicastAddress)
			
			data = fread.read(512)

		fread.close()
		'''
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		

def xor_operation(fData, sData, filename):

	xorResultList=[]
	data = zip(fData, sData)
	for fByte,sByte in data:
		xorResultList.append(chr(ord(fByte) ^ ord(sByte)))

	xorResult = ''.join(xorResultList)
	filePath = SERVER_FILE_PATH + filename
	xorFileR = open(filePath,"wb")
	xorFileR.write(xorResult)
	xorFileR.close()

def delivery_sender(numberOfFile, numberOfClient, randomMatrix, randomAskFile, memorySizeRatio):

	multicastAddress = (MCAST_GRP,MCAST_PORT)

	#setup the multicast using UDP
	sock_sender = multicast_sender()
	raw_input('please press enter, go into the delivery phase')

	#setup the receiver client, unblock
	sock_receiver = multicast_receiver()
	sock_receiver.setblocking(0)
	
	#get the xor files and not xor files
	xorFilename, notXorFilename,xorFileSimu, notXorFileSimu = findXorfile(numberOfFile, numberOfClient, randomMatrix, randomAskFile, 			memorySizeRatio)
		
	#print numberOfFile,numberOfClient  
	#numberOfFile is the N, numberOfClient is the K
	print '\n' + 'N is ' + str(numberOfFile) + ', K is ' + str(numberOfClient)

	#XOR operation
	NumOfXorResultFile = len(xorFilename) / 2
	xorResultFilename = []
	for xorTimes in range(0, NumOfXorResultFile, 1):
		# every time use two files to xor
		index = xorTimes * 2
		fXorFile = open(SERVER_FILE_PATH+xorFilename[index], "rb")
		sXorFile = open(SERVER_FILE_PATH+xorFilename[index+1], "rb")	
		fData = fXorFile.read()
		sData = sXorFile.read()
		fXorFile.close()
		sXorFile.close()
		
		afterXorFilename = 'temp' + str(xorTimes) + ':' + xorFilename[index] + '-' + xorFilename[index+1]
		xor_operation(fData, sData, afterXorFilename)
		xorResultFilename.append(afterXorFilename)

	# send the xor files	
	xorFlag = 1
	print 'xorFileSimu: ',xorFileSimu
	send_file(sock_sender, xorResultFilename, xorFilename, xorFlag, multicastAddress, sock_receiver, xorFileSimu)
	time.sleep(0.5)

	# send the not xor files
	xorFlag = 0
	print 'notXorFileSimu: ',notXorFileSimu
	send_file(sock_sender, notXorFilename, notXorFilename, xorFlag, multicastAddress, sock_receiver, notXorFileSimu)
	time.sleep(0.5)

	# send to client, means finish delivery phase
	for temp in range(0,15,1):
			sock_sender.sendto('',multicastAddress)			
	sock_sender.close()
	sock_receiver.close()	
		

def main():
	#read the file in disk automatic 
	index = 1
	while True:
		fullpath = ORIGINAL_FILE_PATH + str(index) + '.mp4'
		if not os.path.isfile(fullpath):
			break
		else:
			FILE_PATH.append(fullpath)
		index = index + 1
	print 'number of files: ', (index-1)
	print ''

	# here can change the file number of the server: N
	while True:
		name = raw_input('please input the name of the file>')
		if name:
			fullpath = ORIGINAL_FILE_PATH + name
			if not os.path.isfile(fullpath):
				print("{} is not a valid file.".format(fullpath))
			else:
				FILE_PATH.append(fullpath)
				index = index + 1
		else:
			break
	print 'N : ', (index-1)
	print ''

	# here can change the number of the user: K
	numberOfClient = index-1
	while True:
		data = raw_input('please input the number of the clients>')
		if data:
			numberOfClient = int(data)
		else:
			break
	print 'K : ', numberOfClient
	print ''
	
	# here can change the memory size of the client: M
	# memorySizeRatio = 1 means M = size of a file
	memorySizeRatio = 1
	print 'Note: memorySizeRatio = 1 means M = size of a file'
	data = raw_input("please input the value of 'memorySizeRatio'>")
	if data:
		memorySizeRatio = int(data)
	print 'memorySizeRatio : ', memorySizeRatio
	print ''

	# begin to seperate the file
	seperatefileSize = fileSperate(FILE_PATH, memorySizeRatio)
	numberOfFile = len(FILE_PATH)
	
	# get random file for difference client
	print "--------------------------placement phase---------------------------"
	print '--------------------------------------------------------------------\n'
	print 'the placement situation will be :'
	randomMatrix = randomfile(numberOfFile, numberOfClient, memorySizeRatio)	

	# creat the ask file uniform randomly
	randomAskFile = []
	tempRange = range(0, numberOfFile, 1)
	for i in range(0, numberOfClient, 1):
		temp = random.sample(tempRange, 1)
		randomAskFile.append(temp[0])

	# use tcp to realize placement phase	
	server = server_tcp(numberOfClient)


	for clientSequNum in range(0,numberOfClient,1):
		# waiting for connection
		connection, clientAdress = server.accept()
		print 'got connected from',clientAdress

		# send the placement file information to the client and check the client
		fileNameOfCient = randomMatrix[clientSequNum]
		fileNameString = ','.join(fileNameOfCient)
		askFileSize = os.path.getsize(FILE_PATH[randomAskFile[clientSequNum]])
		dataToClient = str(clientSequNum) + ':' + fileNameString + '*'+str(seperatefileSize)\
			+'%'+str(randomAskFile[clientSequNum])+'&'+str(askFileSize)
		connection.send(dataToClient)
		data_rece = connection.recv(BUFFER_SIZE)

		# begin to send the data
		print 'client'+str(clientSequNum)+' :' + '  ' + ',   '.join(fileNameOfCient)
		if data_rece == 'ok':
			for fileSequNum in range(0,numberOfFile,1):
				print 'file ' + fileNameOfCient[fileSequNum] + ' begin to transfer'
				fread = open(SERVER_FILE_PATH+fileNameOfCient[fileSequNum], "r")
				fileData = fread.read(512)
				# read the file until empty
				while fileData:
					connection.send(fileData)
					data_rece = connection.recv(BUFFER_SIZE)
					fileData = fread.read(512)
					
				fread.close()
				# indicate this file is finish 
				connection.send('end')
				data_rece = connection.recv(BUFFER_SIZE)
			# indicate the cashing is finish
			connection.send('finish')

			print ('the placement of client%d is finish!\n' %clientSequNum)
			# this two line code just for simulation
			if clientSequNum == 0:
				break
		else:
			print "error in connection:",connection,clientAdress
		
		connection.close()

	# close the tcp server funktion
	server.close()	
	print 'placement phase is finish'

	#===================================================================================================================================
	
	#delivery phase
	print "\n---------------------------delivery phase---------------------------"
	print '--------------------------------------------------------------------\n'
	print 'the delivery situation will be :'
	delivery_sender(numberOfFile, numberOfClient, randomMatrix, randomAskFile, memorySizeRatio)
	print ''
	print 'delibery phase is finish'

if __name__ == "__main__":
    main()



