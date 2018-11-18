import random

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
	'''
	print ""
	for i in range(0,length,1):
		print 'client' + str(i)+':    '+str(randomMatrix[i])
	print ""
	'''
	return randomMatrix	


def findXorfile(numberOfFile, numberOfClient, randomMatrix, randomAskFile, memorySizeRatio):

	xorFilename = []
	notXorFilename = []
	numberOfSeperatefile = numberOfFile/memorySizeRatio
	'''
	print ''
	print randomAskFile
	print ''
	'''
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
								
				
	'''			
	print 'tempMatrix,after sending the XOR file, the client has this file of his asking file:'
	print ''
	length = len(tempMatrix)
	print ""
	for i in range(0,length,1):
		print 'client' + str(i)+':    '+str(randomAskFile[i])+'     '+str(tempMatrix[i])
	print ""
	'''
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
	
	'''
	print ''
	print 'this files will be XOR: '
	print xorFilename
	print ''
	print 'this files will not be XOR:'
	print notXorFilename
	print ''
	'''
	return xorFilename, notXorFilename#, xorFileSimuFlag, notXorFileSimuFlag


def randaskfile(numberOfFile, numberOfClient):
	randomAskFile = []
	tempRange = range(0, numberOfFile, 1)
	
	for i in range(0, numberOfClient, 1):
		temp = random.sample(tempRange, 1)
		randomAskFile.append(temp[0])
	
	#randomAskFile = random.sample(tempRange, numberOfClient)
	#print randomAskFile
	return randomAskFile



def main():
	totalLength = []
	numberOfFile = 100
	numberOfClient = 20

	for i in range(1,2,1):
		xorFilenameLength = 0
		notXorFilenameLength = 0
		memorySizeRatio  = i
		if numberOfFile % memorySizeRatio == 0:
			for j in range(0,500,1):
				randomMatrix = randomfile(numberOfFile, numberOfClient, memorySizeRatio)
				randomAskFile = randaskfile(numberOfFile, numberOfClient)
				xorFilename, notXorFilename = findXorfile(numberOfFile, numberOfClient, randomMatrix, randomAskFile, 						memorySizeRatio)
			
				xorFilenameLength = xorFilenameLength + len(xorFilename)			
				notXorFilenameLength = notXorFilenameLength + len(notXorFilename)
				'''
				#print 'randomMatrix:      ',randomMatrix
				print 'randomAskFile:     ',randomAskFile
				print 'xorFilename:       ',xorFilename		
				print 'notXorFilename:    ',notXorFilename
				print ''
				raw_input('please input the name of the file>')
				
				print ''
				print xorFilename
				print notXorFilename
				raw_input('please input the name of the file>')
				'''
			
			xorFilenameLength = xorFilenameLength/2/500
			notXorFilenameLength = notXorFilenameLength/500
			numOfSeper = numberOfFile / memorySizeRatio
			#print xorFilenameLength + notXorFilenameLength
			lengthTemp = float(xorFilenameLength + notXorFilenameLength) / numOfSeper #(numOfSeper * numberOfClient)
			totalLength.append(str(numOfSeper)+'::'+str(lengthTemp))

	
	lengthTemp = len(totalLength)
	for i in range(0, lengthTemp, 1):
		print totalLength[i]

if __name__ == "__main__":
    main()


'''
100::15.59
50::14.6
25::13.24
20::13.05
10::11.6
5::9.4
4::8.5
2::5.0
1::0.0


'''
