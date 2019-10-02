# -*- coding: utf-8-unix ; tab-width: 2 -*-
# Version: Python 3.6.7

### System modules
from websocket_server import WebsocketServer
import base64
import numpy as np
from tensorflow.keras.models import load_model#,Model
from tensorflow.keras.preprocessing.image import load_img, img_to_array, array_to_img

import tensorflow as tf
from tensorflow.keras.backend import set_session, clear_session

### User modules
from CutterControl import CutterControl


### Global instances
#server = WebsocketServer( 8080, "10.10.10.11" )   # Ethernet
server = WebsocketServer( 8080, "192.168.0.10" )   # WiFi

### Global flags
IsRecievingFacesNow = False
TotalNumberOfFaces = 0
RecievedNumberOfFaces = 0


### FAIRCUT-Server functions
def onCompleteRevieveFaces( sess, graph, model ):
  print( "Complete recieving face images!\n" )
  users = TotalNumberOfFaces
  usersArray = range( users )
  xArray = []
  
  # Get images from saved pictures
  for user in usersArray:
    imgfile = "image_#" + str( user ) + ".png"
    img = load_img( imgfile, target_size=( 224, 224 ) )
    img_array = img_to_array( img )
    xArray.append( img_array )
    
  xArray = np.array( xArray )
  xArray = xArray.astype( "float32" ) / 255.0
  
  # Predict
  ration = []

  set_session( sess )
  with sess.as_default():
    with graph.as_default():
      #model = load_model( "saved_model.h5" )
      predicted = model.predict( xArray, batch_size=None, verbose=1, steps=None )
      print(predicted)
      for user in usersArray:
        ration.append( predicted[user].argmax() )
      print( ration )
  clear_session()
  
  ## Cutter
  cutter = CutterControl()
  percentages = cutter.convertRation2Percent( ration )
  cutter.send_message_to_mbed( percentages )
  message4mac = cutter.message_to_mac( percentages )
  
  # Send BMI-percentages to Mac
  print( message4mac )
  server.send_message_to_all( message4mac )
  #server.send_message_to_all( "BMI:40,30,20,10" )    # test string
  
def BeginTransmissionForFaces( message ):
  global IsRecievingFacesNow
  global TotalNumberOfFaces
  global RecievedNumberOfFaces
  
  IsRecievingFacesNow = True
  TotalNumberOfFaces = int( message[-1] )
  RecievedNumberOfFaces = 0
  print( "Begin" )

def EndTransmissionForFaces( message, sess, graph, model ):
  global IsRecievingFacesNow
  global TotalNumberOfFaces
  global RecievedNumberOfFaces
  
  onCompleteRevieveFaces( sess, graph, model )
  
  IsRecievingFacesNow = False
  TotalNumberOfFaces = 0
  RecievedNumberOfFaces = 0
  
  print( "End" )

def StoreFaceDataAsPNG( message ):
  global RecievedNumberOfFaces
  
  with open( "image_#" + str( RecievedNumberOfFaces ) + ".png", "wb" )  as fh:
    fh.write( base64.b64decode( message ) )
    RecievedNumberOfFaces = RecievedNumberOfFaces + 1
    print( "Saved: image_#" + str( RecievedNumberOfFaces ) + ".png" )



### WebSockets callbacks
def ws_new_client( client, server ):
  print( "New client connected and was given id %d" % client['id'] )
  #server.send_message_to_all( "Hey all, a new client has joined us" ) 

def ws_client_left( client, server ):
  print( "Client(%d) disconnected" % client['id'])

def ws_message_received( client, server, message, sess, graph, model ):
  if "BeginTransmissionForFaces" in message:
    BeginTransmissionForFaces( message )
    
  elif "EndTransmissionForFaces" == message:
    EndTransmissionForFaces( message, sess, graph, model )
    
  elif len( message ) > 200:
    if IsRecievingFacesNow:
      StoreFaceDataAsPNG( message )
      
  else:
    print( "Client(%d) said unknown message: %s" % ( client['id'], message ) )
    
    
### Main function 
def main():
  # Load the model
  clear_session()
  config = tf.ConfigProto(
    gpu_options=tf.GPUOptions(
      visible_device_list="",
      allow_growth=True,
      per_process_gpu_memory_fraction=0.4
    )
  )
  sess = tf.Session( config=config )
  set_session( sess )
  model = load_model( "saved_model.h5" )
  model._make_predict_function()
  graph = tf.get_default_graph()
  
  server.set_fn_new_client( ws_new_client ) 
  server.set_fn_client_left( ws_client_left ) 
  server.set_fn_message_received( lambda c, s, m, sess=sess, graph=graph, model = model: ws_message_received( c, s, m, sess, graph, model ) )
  server.run_forever()


if __name__ == "__main__":
  main()
