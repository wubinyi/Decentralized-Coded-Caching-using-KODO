import random

def findXorfile3(numberOfFile, numberOfClient, randomMatrix, randomAskFile, memorySizeRatio):

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
			fullMatrix[i].append(str(randomAskFile[i]) + str(j))
	
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

def randomfile(fileNumber, numberOfClient, seperateNumber):
	#print 'fileNumber, seperateNumber',fileNumber, seperateNumber
	randomMatrix = []
	
	tempRange = range(0, seperateNumber, 1)

	for i in range(0, numberOfClient, 1):
		matrixElement = []
		#tempRandom = random.sample(tempRange, seperateNumber)
		tempRandom = random.sample(tempRange, 1)
		for j in range(0, fileNumber, 1):
			matrixElement.append(str(j) + str(tempRandom[0]))
		randomMatrix.append(matrixElement)

	length = len(randomMatrix)
	'''
	print ""
	for i in range(0,length,1):
		print 'client' + str(i)+':    '+str(randomMatrix[i])
	print ""
	'''
	return randomMatrix



def findXorfile(fileNumber, numberOfClient, randomMatrix,randomAskFile,seperateNumber):

	xorFilename = []
	filename = []
	'''
	print ''
	print randomAskFile
	print ''
	'''
	#copy the randomMatrix to the copyRandomMatrix(because of pointer)
	copyRandomMatrix = []	
	for i in range(0, len(randomMatrix), 1):
		temp = []
		for j in range(0, len(randomMatrix[i]), 1):
			temp.append(randomMatrix[i][j])
		
		copyRandomMatrix.append(temp)

	#===========================
	
	#use to record the client has which part of the asked file 
	tempMatrix = []
	for i in range(0, numberOfClient, 1):
		tempMatrix.append([])


	#find the xor find between the user with the same asking file
	for i in range(0, numberOfClient, 1):
		temp = randomAskFile[i]
		for j in range(i, len(randomAskFile), 1):
			
			# the client has the same asked file and the cached file of the asking file is not the same
			if randomAskFile[j] == temp and (copyRandomMatrix[i][randomAskFile[i]] != copyRandomMatrix[j][randomAskFile[i]]):
				
				tempdata_1 = ','.join(tempMatrix[i])
				tempdata_2 = ','.join(tempMatrix[j])

				#judge if one of them has the cached file from the other
				if not (tempdata_1.find(copyRandomMatrix[j][randomAskFile[i]]) > -1 or tempdata_2.find(copyRandomMatrix[i][randomAskFile[i]]) > -1):
					xorFilename.append(copyRandomMatrix[i][randomAskFile[i]])
					xorFilename.append(copyRandomMatrix[j][randomAskFile[i]])
					tempMatrix[j].append(copyRandomMatrix[i][randomAskFile[i]])
					tempMatrix[i].append(copyRandomMatrix[j][randomAskFile[i]])


	for i in range(0, numberOfClient, 1):
		for j in range(0, fileNumber, 1):

			if copyRandomMatrix[i][j][0] == str(randomAskFile[i]):
				tempMatrix[i].append(copyRandomMatrix[i][j])
			
			for l in range(0, len(randomAskFile), 1):
				if randomAskFile[l] == int(copyRandomMatrix[i][j][0]):
					row = l

					temp1 = copyRandomMatrix[row][randomAskFile[i]][0]
					temp2 = copyRandomMatrix[i][randomAskFile[i]][0]
					if copyRandomMatrix[row][randomAskFile[i]] != copyRandomMatrix[i][randomAskFile[i]] and copyRandomMatrix[row][j] != copyRandomMatrix[i][j]: 
						
						tempdata = ','.join(xorFilename)
						tempdata_1 = ','.join(tempMatrix[row])
						tempdata_2 = ','.join(tempMatrix[i])
						#if tempdata.find(copyRandomMatrix[i][j])==-1  or tempdata.find(copyRandomMatrix[row][randomAskFile[i]])==-1: 						
								
						if not (tempdata_1.find(copyRandomMatrix[i][j]) > -1 or tempdata_2.find(copyRandomMatrix[row][randomAskFile[i]]) > -1):
							xorFilename.append(copyRandomMatrix[i][j])
							xorFilename.append(copyRandomMatrix[row][randomAskFile[i]])
							tempMatrix[row].append(copyRandomMatrix[i][j])
							tempMatrix[i].append(copyRandomMatrix[row][randomAskFile[i]])
							#break
				
	'''			
	print 'tempMatrix,after sending the XOR file, the client has this file of his asking file:'
	print ''
	length = len(tempMatrix)
	print ""
	for i in range(0,length,1):
		print 'client' + str(i)+':    '+str(randomAskFile[i])+'     '+str(tempMatrix[i])
	print ""
	'''

	fullMatrix = []
	for i in range(0, numberOfClient, 1):
		fullMatrix.append([])
	for i in range(0, numberOfClient, 1):
		for j in range(0, seperateNumber, 1):
			fullMatrix[i].append(str(randomAskFile[i]) + str(j))
	#print 'fullMatrix'
	#print fullMatrix
	

	filenameMatrix = []
	for i in range(0, fileNumber, 1):
		filenameMatrix.append([])
	for i in range(0, numberOfClient, 1):
		templist_1 = ','.join(filenameMatrix[randomAskFile[i]])
		templist_2 = ','.join(tempMatrix[i])
		for j in range(0, seperateNumber, 1):
			if templist_1.find(fullMatrix[i][j]) == -1 and templist_2.find(fullMatrix[i][j]) == -1:
				filenameMatrix[randomAskFile[i]].append(fullMatrix[i][j])


	#print 'filenameMatrix'
	#print filenameMatrix





	for i in range(0, len(filenameMatrix), 1):
		for j in range(0, len(filenameMatrix[i]), 1):
			filename.append(filenameMatrix[i][j])
	
	'''
	print ''
	print 'this files will be XOR: '
	print xorFilename
	print ''
	print 'this files will not be XOR:'
	print filename
	print ''
	#print 'copyRandomMatrix will be:'
	#print copyRandomMatrix
	'''
	return xorFilename, filename

def findXorfile2(numberOfFile, numberOfClient, randomMatrix, randomAskFile, memorySizeRatio):

	xorFilename = []
	notXorFilename = []
	numberOfSeperatefile = numberOfFile/memorySizeRatio


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
			fullMatrix[i].append(str(randomAskFile[i]) + str(j))
	
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


def main():
	fileNumber = 8
	numberOfClient = 6
	#seperateNumber = numberOfClient / 2 
	totalLength = []


	seperateNumber = numberOfClient 

	xorFilenameLength = 0
	filenameLength = 0 
	xorFilenameLength2 = 0
	filenameLength2 = 0

	for j in range(0, 500, 1):
		randomMatrix = randomfile(fileNumber, numberOfClient, seperateNumber)

		randomAskFile = []
		tempRange = range(0, fileNumber, 1)
		for i in range(0, numberOfClient, 1):
			temp = random.sample(tempRange, 1)
			randomAskFile.append(temp[0])

		xorFilename, filename = findXorfile(fileNumber, numberOfClient, randomMatrix, randomAskFile, seperateNumber)
		xorFilenameLength = xorFilenameLength + len(xorFilename)			
		filenameLength = filenameLength + len(filename)

		xorFilename2, filename2 = findXorfile2(fileNumber, numberOfClient, randomMatrix, randomAskFile, 1)
		xorFilenameLength2 = xorFilenameLength2 + len(xorFilename2)			
		filenameLength2 = filenameLength2 + len(filename2)
		
		if xorFilenameLength != xorFilenameLength2 or filenameLength != filenameLength2:
			print 'error:'
			print 'randomMatrix: ',randomMatrix
			print 'randomAskFile: ',randomAskFile
			print '\nfirst find: '
			print 'xorFilename: ',xorFilename
			print 'filename: ',filename
			print '\nsecond find: '
			print 'xorFilename2: ',xorFilename2
			print 'filename2: ',filename2

	xorFilenameLength = float(xorFilenameLength) / 2 / 500
	filenameLength = float(filenameLength) / 500


	xorFilenameLength2 = float(xorFilenameLength2) / 2 / 500
	filenameLength2 = float(filenameLength2) / 500


	print float(xorFilenameLength + filenameLength)/(fileNumber * seperateNumber)
	print float(xorFilenameLength2 + filenameLength2)/(fileNumber * seperateNumber)


	'''
	for l in range(0, numberOfClient, 1):
		xorFilenameLength = 0
		filenameLength = 0
		for j in range(0, 500, 1):
			seperateNumber = numberOfClient / (l+1)
			randomMatrix = randomfile(fileNumber, numberOfClient, seperateNumber)
			randomAskFile = []
			tempRange = range(0, fileNumber, 1)
			for i in range(0, numberOfClient, 1):
				temp = random.sample(tempRange, 1)
				randomAskFile.append(temp[0])

			xorFilename, filename = findXorfile(fileNumber, numberOfClient, randomMatrix, randomAskFile, seperateNumber)
			xorFilenameLength = xorFilenameLength + len(xorFilename)			
			filenameLength = filenameLength + len(filename)
			#print xorFilenameLength,filenameLength

		xorFilenameLength = xorFilenameLength / 2 / 500
		filenameLength = filenameLength / 500
		#print xorFilenameLength,filenameLength

		totalLength.append(float(xorFilenameLength + filenameLength)/(fileNumber * seperateNumber))
	print totalLength
	'''


if __name__ == "__main__":
    main()






'''
for l in range(0, numberOfClient, 1):
	xorFilenameLength = 0
	filenameLength = 0
	for j in range(0, 500, 1):
		seperateNumber = numberOfClient / (l+1)
		randomMatrix = randomfile(fileNumber, numberOfClient, seperateNumber)
		randomAskFile = []
		tempRange = range(0, fileNumber, 1)
		for i in range(0, numberOfClient, 1):
			temp = random.sample(tempRange, 1)
			randomAskFile.append(temp[0])

		xorFilename, filename = findXorfile(fileNumber, numberOfClient, randomMatrix, randomAskFile, seperateNumber)
		xorFilenameLength = xorFilenameLength + len(xorFilename)			
		filenameLength = filenameLength + len(filename)
		#print xorFilenameLength,filenameLength

	xorFilenameLength = xorFilenameLength / 2 / 500
	filenameLength = filenameLength / 500
	#print xorFilenameLength,filenameLength

	totalLength.append(float(xorFilenameLength + filenameLength)/(fileNumber * seperateNumber))
print totalLength
'''
