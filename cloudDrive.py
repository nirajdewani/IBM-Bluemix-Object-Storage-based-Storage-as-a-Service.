# -*- coding: utf-8 -*-
import keystoneclient
import swiftclient
import os
import pyDes
from flask import Flask, request, render_template

app = Flask(__name__)

auth_url = "https://identity.open.softlayer.com/v3"
password = "yourPassword"
project_id = "yourProjectID"
user_id = "yourUserID"
region_name = "dallas"
container_name = "containerName"
file_name = "test.txt"
conn = swiftclient.Connection(key=password, authurl=auth_url, auth_version='3', 
							 os_options={"project_id":project_id,
										"user_id":user_id,
										 "region_name":region_name})

@app.route('/uploadFile', methods=['POST'])
def uploadFile():
	fileName = request.files['file'].filename
	fileHandle = request.files['file']
	content = fileHandle.read()
	encryptedContent = encryptText(content)
	conn.put_object(container_name, fileName, contents = encryptedContent, content_type='text/plain')
	fileList = returnContainerContent()
	return render_template("home.html", fileList=fileList)

#App initialization method
def createFolder(name):
	conn.put_container(container_name)
	
def encryptFile(inputFilePath, outputFilePath):
	file = open(inputFilePath)
	data = file.read()
	k = pyDes.des("DESCRYPT", pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
	encryptedData = k.encrypt(data)
	with open(outputFilePath, 'w') as file_handle:
		file_handle.write(encryptedData)

def decryptFile(inputFilePath, outputFilePath):
	file = open(inputFilePath)
	data = file.read()
	k = pyDes.des("DESCRYPT", pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
	decrypted_content = k.decrypt(data)
	with open(outputFilePath, 'w') as file_handle:
		file_handle.write(decrypted_content)

@app.route('/downloadFile', methods=['GET'])		
def downloadFile(containerName, fileName, outputFilePath):	
	downloaded_file = conn.get_object(container_name, file_name)
	with open(outputFilePath, 'w') as file_handle:
		file_handle.write(downloaded_file[1])
		
def returnContainerContent():
	metaData = []
	for container in conn.get_account()[1]:
		for data in conn.get_container(container['name'])[1]:
			metaData.append(data['name'])
			metaData.append(data['bytes'])
	return metaData

@app.route('/deleteFile', methods=['GET'])
def deleteFile():
	fileName = str(request.args.get("fileName"))
	conn.delete_object(container_name, fileName)
	fileList = returnContainerContent()
	return render_template("home.html", fileList=fileList)
	
@app.route('/home')
def home():
	fileList = returnContainerContent()
	return render_template("home.html", fileList=fileList)

def main():
	app.run(debug=True)

if __name__=='__main__':main()