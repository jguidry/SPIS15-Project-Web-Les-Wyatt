#!/usr/bin/env python

import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
from werkzeug import secure_filename
from flask import jsonify
from flask import session
from PIL import Image, ImageDraw
import tempfile


# Initialize the Flask application
app = Flask(__name__)

app.secret_key = 'pioaug7OIG3"LOi^fg'

@app.route('/')
def renderMain():
    return render_template('home.html') 

@app.route('/startOver')
def startOver():
    session.clear()
    return redirect(url_for('renderMain'))

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif', 'bmp'])
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

# If the file you are trying to upload is too big, you'll get this message
@app.errorhandler(413)
def request_entity_too_large(error):
    message = 'The file is too large, my friend.<br>'
    maxFileSizeKB = app.config['MAX_CONTENT_LENGTH']/(1024)
    message += "The biggest I can handle is " + str(maxFileSizeKB) + "KB"
    message += "<a href='" + url_for("index") + "'>Try again</a>"
    return message, 413

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# The root where we ask user to enter a file
@app.route('/encode')
def encode():
    return render_template('context.html')

@app.route('/hidden')
def hidden():
    return render_template('hidden.html')

@app.route('/decode')
def decode():
    return render_template('decode.html')
@app.route('/finishedImage')
def finishedImage():
    return render_template('finishedImage.html')
@app.route('/finishedDecode')
def decodedImage():
    return render_template('finishedDecode.html')

##@app.route('/Error')
##def ErrorMessage():
##    return render_template('Error.html')



def check_file(file):
    # Check if the file is one of the allowed types/extensions
    if not allowed_file(file.filename):
        print "Block 1"
        message = "Sorry. Only files that end with one of these "
        message += "extensions is permitted: " 
        message += str(app.config['ALLOWED_EXTENSIONS'])
        message += "<a href='" + url_for("index") + "'>Try again</a>"
        return message
    elif not file:
        print "block 2"
        message = "Sorry. There was an error with that file.<br>"
        message += "<a href='" + url_for("index") + "'>Try a vvgain</a>"
        return message
    return ''


 #Route that will process the file upload
@app.route('/upload1', methods=['POST'])
def upload1():
    print "inside upload1"
    # Get the name of the uploaded file
    file = request.files['contextFile']
    print "after file"
    result = check_file(file)
    if result != '':
        return result
    else:
        print "block 3"
        # Make the filename safe, remove unsupported chars
        filename = getTempFileName(secure_filename(file.filename))
        fullFilename = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['contextFile'] = fullFilename
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(fullFilename)
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
    
    return redirect(url_for('hidden'))

##############Image encoding#################
def embedDigits2( contextVal, messageVal):
    '''embeds the message value into the context picture'''
    #clears the last two bits of the context image and inserts the bits from the message
    return ((contextVal >> 2)<<2) + (messageVal)


def mostSignificant2(num):
    '''Returns the two most significant bits of an 8-bit binary number'''
    #shifts the number over 6 bits so only the two most significant bits remain
    return num >> 6



def getTempFileName(myPrefix):
    f = tempfile.NamedTemporaryFile(suffix = ".bmp", prefix = myPrefix, delete=False, dir=app.config['UPLOAD_FOLDER'])
    f.close()
    return f.name

def decodeSecretImage(context):
    contextImage = Image.open(context)
    return recoverSecretMessage2Bits(contextImage)

def getLeastSignificant2(num):
    return num % 4
    
def recoverSecretMessage2Bits(context):
    picCopy = Image.new('RGB',context.size,(0,0,0))
    for x in range(context.size[0]):
        for y in range(context.size[1]):
            (r,g,b) = context.getpixel( (x, y) )
            
            r = getLeastSignificant2(r)<<6
            g = getLeastSignificant2(g)<<6
            b = getLeastSignificant2(b)<<6
            picCopy.putpixel( (x,y), ( r, g, b ) )
    nameDecoded = getTempFileName("decodedImage")
    #print "In  hideSecretMessage2Bits, name =", name
    picCopy.save(nameDecoded)
    return nameDecoded
   

def hideSecretMessage(contextFilename, hiddenFilename):
    context = Image.open(contextFilename)
    message = Image.open(hiddenFilename)
    return hideSecretMessage2Bits(context, message)


def hideSecretMessage2Bits(context, message):
    
    picCopy = Image.new('RGB',message.size,(0,0,0))
    if context.size[0] > message.size[0] or context.size[1] > message.size[1]:
        for x in range(message.size[0]):
            for y in range(message.size[1]):
                (r,g,b) = context.getpixel( (x, y) )
                (r2,g2,b2) = message.getpixel( (x, y) )
                message_r = mostSignificant2(r2)
                message_g = mostSignificant2(g2)
                message_b = mostSignificant2(b2)
                r = embedDigits2(r, message_r)
                g = embedDigits2(g, message_g)
                b = embedDigits2(b, message_b)
                picCopy.putpixel( (x,y), ( r, g, b ) )
    
        name = getTempFileName("encodedimage")
        print "In  hideSecretMessage2Bits, name =", name
        picCopy.save(name)
        return name
    else:
        for x in range(context.size[0]):
            for y in range(context.size[1]):
                (r,g,b) = context.getpixel( (x, y) )
                (r2,g2,b2) = message.getpixel( (x, y) )
                message_r = mostSignificant2(r2)
                message_g = mostSignificant2(g2)
                message_b = mostSignificant2(b2)
                r = embedDigits2(r, message_r)
                g = embedDigits2(g, message_g)
                b = embedDigits2(b, message_b)
                picCopy.putpixel( (x,y), ( r, g, b ) )
    
        name = getTempFileName("encodedimage")
        print "In  hideSecretMessage2Bits, name =", name
        picCopy.save(name)
        return name

@app.route('/upload2', methods=['POST'])
def upload2():
    # Get the name of the uploaded file
    file = request.files['hiddenFile']
    # Check if the file is one of the allowed types/extensions
    result = check_file(file )
    if result != '':
        return result
    else:
        # Make the filename safe, remove unsupported chars
        filename = getTempFileName(secure_filename(file.filename))
        fullFileName = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['hiddenFile'] = fullFileName
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(fullFileName)
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        session["encodedimage"] = hideSecretMessage(session['contextFile'], session['hiddenFile'])
        return render_template('finishedImage.html', filename = fixFileName(session['encodedimage']))


def fixFileName(stupidfilename):
    '''change a file name such as
    home/linux/ieng6/spis15/spis15ak/github/SPIS15-Project-Web-Sierra-Lauren/uploads/newImagehMICau.jpg
    into /uploads/newImagehMICau.jpg'''
    goodfilename = "/" + app.config['UPLOAD_FOLDER'] + os.path.basename(stupidfilename)
    return goodfilename


#FinishedDecode page
@app.route('/upload3', methods=['POST'])
def upload3():
    # Get the name of the uploaded file
    file = request.files['returnFile']
    # Check if the file is one of the allowed types/extensions
    result = check_file(file )
    if result != '':
        return result
    else:
        # Make the filename safe, remove unsupported chars
        filename = getTempFileName(secure_filename(file.filename))
        fullFileName = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['returnFile'] = fullFileName
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(fullFileName)
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        session["decodedimage"] = decodeSecretImage(session['returnFile'])
        return render_template('finishedDecode.html', filename = fixFileName(session['decodedimage']))

    
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload



@app.route('/uploads/<filename>/')
def uploaded_file(filename):
    #To do: change this to the page where we do something with the file
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=1114,debug= False)


#



