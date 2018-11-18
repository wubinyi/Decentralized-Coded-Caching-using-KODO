import kodo
import socket
import struct
import os
import random

#MCAST_GRP = '224.0.0.1'
MCAST_GRP = '239.192.1.100'
MCAST_PORT_RECE = 5007
SEND_MCAST_PORT = 5008
TCP_IP = '192.168.1.103'
TCP_PORT = 31500
BUFFER_SIZE = 1024
FILE_PATH = '/home/wubinyi/Kodo-Workspace/file/'
CLIENTNUM = 0
SYMBOLSIZE = 512
BUFFERSIZE = BUFFER_SIZE


def client_tcp():
	address = (TCP_IP, TCP_PORT)
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(address)
	return client


# set multicast receiver
def multicast_receiver():
	sock_receiver = socket.socket(
		family=socket.AF_INET,
		type=socket.SOCK_DGRAM,
		proto=socket.IPPROTO_UDP)

	mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
	sock_receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	sock_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock_receiver.bind(('', MCAST_PORT_RECE))

	return sock_receiver


# set multicast sender
def multicast_sender():	
	sock_sender = socket.socket(
		family=socket.AF_INET,
		type=socket.SOCK_DGRAM,
		proto=socket.IPPROTO_UDP)

	sock_sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)	
	
	return sock_sender

def filecreat(askFile,askFileSize):
	completefile = open(FILE_PATH+str(askFile+1),"wb")
	partSequenNum = 0
	referenceSize = int(askFileSize)
	while True:
		seperFilepath = FILE_PATH+str(askFile)+'|'+str(partSequenNum)
		if not os.path.isfile(seperFilepath):
			break
		seperatefileSize = os.path.getsize(seperFilepath)
		if seperatefileSize >= referenceSize:
			f = open(seperFilepath,"rb")
			data = f.read(referenceSize)
			completefile.write(data)
			f.close()
			break
		referenceSize = referenceSize - seperatefileSize
		f = open(seperFilepath,"rb")
		data = f.read()
		completefile.write(data)
		f.close()
		partSequenNum = partSequenNum + 1
	completefile.close()



def kododecoder(blockSize):
	
	# Set the number of symbols (i.e. the generation size in RLNC
	# terminology) and the size of a symbol in bytes
	#file_size = os.path.getsize(FILE_ORIGINAL_PATH)
	print 'kodo block Size: ', blockSize
	symbols = blockSize / SYMBOLSIZE
	if blockSize % SYMBOLSIZE:
		symbols = symbols + 1
	#print 'symbolsize,symbols: ',SYMBOLSIZE, symbols

	# In the following we will make an decoder factory.
	# The factories are used to build actual decoder
	decoder_factory = kodo.FullVectorDecoderFactoryBinary(
		max_symbols=symbols,
		max_symbol_size=SYMBOLSIZE)

	decoder = decoder_factory.build()
	print 'symbolsize, symbols ', SYMBOLSIZE, symbols
	return decoder

def fileInfojudge(data):
	# if data from server include '-' and '|' 
	# and the length of data shorter als 128 bytes
	# means this data is about file infomation
	fileInfoFlag = data.find('-') > -1 and data.find('|') > -1 and len(data) < 56
	return fileInfoFlag

# return True means it is a xor file
# return Flase means it is a single file
def fileInfoProcess(data, caFiNaStr, deXorFilename, askFile):

	# True means we need this file
	# Flase means we do not need this file
	# after '-' is the second file's name, we can judge from it, if it is xor file
	# xor file has two file name; not xor file has only one file name
	fileIndex = data.find('-')
	if data[fileIndex+1 : fileIndex+2 ] != 'X':
		# for xor files 
		# only one of the two file exist in the cached files
		fFilename = data[:fileIndex]
		sFilename = data[fileIndex+1:]
		fExistFlag = caFiNaStr.find(fFilename) > -1 and caFiNaStr.find(sFilename) == -1
		sExistFlag = caFiNaStr.find(fFilename) == -1 and caFiNaStr.find(sFilename) > -1	
		# at least one of them is part of the ask file
		nameIndex = data.find('|')
		fFilehead = data[:nameIndex]
		nameIndex = data.find('|',nameIndex+1)
		sFilehead = data[fileIndex+1:nameIndex]
		# only one file exist and the not exist file is part of the ask file-----> receive
		receiveFlag = (fExistFlag and sFilehead == str(askFile))\
			or (sExistFlag and fFilehead == str(askFile))	
		# add the part file of the ask file into 'caFiNaStr'
		# it is used by judgement in the receive of not xor file
		# xorFilename is used by dexor
		if receiveFlag:
			if fExistFlag:
				caFiNaStr = caFiNaStr+ ',' + sFilename
				deXorFilename.append(fFilename)
				partFilename =fFilename +'-' + sFilename
			if sExistFlag:
				caFiNaStr = caFiNaStr+ ',' + fFilename
				deXorFilename.append(sFilename)
				partFilename =sFilename +'-' + fFilename
		else:
			fFilename = 'X'
			sFilename = 'X'
			partFilename = 'X'
	else:
		fFilename = data[:fileIndex]
		nameIndex = data.find('|')
		fFilehead = data[:nameIndex]
		sFilename = 'X'
		# the file do not exist in the cache file but is part of the ask file-----> receive
		receiveFlag = fFilehead == str(askFile) and caFiNaStr.find(fFilename) == -1
		if receiveFlag:
			caFiNaStr = caFiNaStr+ ',' + fFilename
			partFilename = fFilename
		else:
			fFilename = 'X'
			partFilename = 'X'

	return receiveFlag, caFiNaStr, partFilename, sFilename



def delivery_receive(askFile, seperatefileSize, cacheFileName):

	# use 'caFiNaStr' to judge which 'xor file' or 'not xor file' should be received
	caFiNaStr = ','.join(cacheFileName)

	receiveFlag = 0
	creatfileFlag = 0
	closefileFlog = 0

	deXorFilename = []
	xorFilename = []
	
	# multicast sender
	address = (MCAST_GRP,SEND_MCAST_PORT)
	sock_sender = multicast_sender()
	
	# multicast receiver
	sock_receiver = multicast_receiver()
	data = sock_receiver.recv(BUFFER_SIZE)

	while data:
		if data == 'new file':

			# receive the 'new file' until filename information
			while data == 'new file':
				receiveFlag = 0
				creatfileFlag = 0
				data = sock_receiver.recv(BUFFER_SIZE)

		
			# receive the filename information
			fileInfoFlag = fileInfojudge(data) 
			while fileInfoFlag:		
				if creatfileFlag == 0:
					
					receiveFlag, caFiNaStr, partFilename, sFilename = fileInfoProcess(data, caFiNaStr, deXorFilename,askFile)
					
					# start to cread a file
					if receiveFlag:
						returnSendData = data
						# a file is to be created only one time 
						# without this flag, programm will creat this file several times
						# because server send file information several times
						creatfileFlag = 1
						# before to creat file, we should close the file, which is opened before			
						if  closefileFlog:
							file_cache.close()
						# distinguish xor file and not xor file, because we creat different file for this two situation
						if sFilename == 'X':
							# not xor file					
							print 'file '+ partFilename + ' is created..................................'
							file_cache = open(FILE_PATH+partFilename,'wb')
						else:
							# xor file
							filename ='temp' + str(closefileFlog) + ':' + partFilename
							xorFilename.append(filename)
							print 'file \''+ filename + '\' is created..................................'
							file_cache = open(FILE_PATH+filename,'wb')


						# change the closefileFlog's value(the first time to creat a file,is not need to close a file)
						closefileFlog = closefileFlog + 1
						#print 'deXorFilename: ',deXorFilename
						#print 'xorFilename: ',xorFilename

				data = sock_receiver.recv(BUFFER_SIZE)
				fileInfoFlag = fileInfojudge(data)

			#=====================================================================================
			lossRange = range(0,10,1)
			
			# without kodo
			# begin to write the data into file
			numberOfLossPacket = 0
			while receiveFlag and data != 'new file' and len(data) > 0:	
				lossFlag = random.sample(lossRange, 1)
				if lossFlag[0]:			
					file_cache.write(data)
				else:
					numberOfLossPacket = numberOfLossPacket + 1
				data = sock_receiver.recv(BUFFER_SIZE)
			if numberOfLossPacket:
				print 'number Of loss packet: ',numberOfLossPacket
			
			
			#==================================================================================
				

		else:
			data = sock_receiver.recv(BUFFER_SIZE)	
			
	
	print ''
	print 'the delivery phase is finish'
	
	if closefileFlog:
		file_cache.close()
	
	sock_receiver.close()
	sock_sender.close()
	
	return deXorFilename, xorFilename


# xor operation funktion , in order to restore the original data
def dexor_operation(deXorFilename, xorFilename):

	numOfXorFile = len(xorFilename)
	for xorFileSequNum in range(0,numOfXorFile,1):
		# get the name of the creaded file
		index = xorFilename[xorFileSequNum].find('-')
		createdFilename = xorFilename[xorFileSequNum][index+1:]
		# open the xor file and read
		print 'xor file: ' + xorFilename[xorFileSequNum]
		xorFileR = open(FILE_PATH+xorFilename[xorFileSequNum], "rb")
		xorData = xorFileR.read()
		xorFileR.close()
		# open the dexor file and read
		print 'dexor file: ' + deXorFilename[xorFileSequNum] +'\n'
		deXorFileR = open(FILE_PATH+deXorFilename[xorFileSequNum], "rb")
		deXorData = deXorFileR.read()
		deXorFileR.close()
		# dexor
		xorResult = []
		data = zip(xorData, deXorData)
		for a,b in data:
			xorResult.append(chr(ord(a) ^ ord(b)))
		data = ''.join(xorResult)
		# open the creaded file and write
		fwrite = open(FILE_PATH+createdFilename, "wb")
		fwrite.write(data)
		fwrite.close()


def placement_receive(cacheFileName,client):
	
	# file's sequence number
	fileSequeNum = 0   
	print 'begin to receive file: ' + cacheFileName[fileSequeNum] 
	f = open(FILE_PATH+cacheFileName[fileSequeNum],'wb')

	data = client.recv(BUFFER_SIZE)

	while True:
		if data != 'end' and data != 'finish':
			f.write(data)
			client.send('ok')
			data = client.recv(BUFFER_SIZE)
		
		if data == 'end':
			client.send('ok')
			data = client.recv(BUFFER_SIZE)
			if data == 'finish':
				# muss remember to close the last file
				f.close() 
				break
			fileSequeNum =fileSequeNum + 1
			f.close()
			print 'begin to receive file: ' + cacheFileName[fileSequeNum] 
			f = open(FILE_PATH+cacheFileName[fileSequeNum],'wb')
	
	#the placement phasen is finish, close the tcp client		
	client.close()	


def main():
	
	print "--------------------------placement phase---------------------------"
	print '--------------------------------------------------------------------\n'
	print 'the placement situation will be :'

	#setup tcp client	
	client = client_tcp()
	data = client.recv(BUFFER_SIZE)
	
	#change the CLIENTNUM value, it is the name, which server gives to the client ; get the placement file information
	#index = data.find('begin to send the data...')
	fIndex = data.find(':')
	if fIndex > -1:
		CLIENTNUM = int(data[:fIndex])
		sIndex = data.find('*')
		cacheFileName = data[fIndex+1:sIndex].split(',')
		fIndex = data.find('%')
		seperatefileSize = data[sIndex+1:fIndex]
		sIndex = data.find('&')
		askFile = int(data[fIndex+1:sIndex])
		askFileSize = data[sIndex+1:]
		
		print 'CLIENT: ',CLIENTNUM,'cache files in placement:',',   '.join(cacheFileName)
		client.send('ok')
	
	# begin to receive data
	placement_receive(cacheFileName,client)
	
	print 'placement phase is finish'

	
	#==================================================================================================================================
	print "\n--------------------------delievery phase---------------------------"
	print '--------------------------------------------------------------------\n'
	print 'ask file '+ str(askFile+1)+ ', the size is '+str(askFileSize) + '\n'
	deXorFilename, xorFilename = delivery_receive(askFile, seperatefileSize, cacheFileName)
	print '\ndeXorFilename: ',deXorFilename
	print 'xorFilename: ',xorFilename
	
	#==================================================================================================================================
	print "\n-------------------------------Dexor--------------------------------"
	print '--------------------------------------------------------------------\n'
	dexor_operation(deXorFilename, xorFilename)
	filecreat(askFile,askFileSize)
	print ''
	print 'file ' + str(askFile+1) + ' is created.....'

if __name__ == "__main__":
    main()



