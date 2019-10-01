# -*- coding: utf-8-unix ; tab-width: 2 -*-
# Version: Python 3.6.7

### Imports
from websocket_server import WebsocketServer
import base64
from tensorflow.keras.models import load_model#,Model
from tensorflow import get_default_graph

from BaumCutter import BaumCutter

### Global variables
server = WebsocketServer( 8080, "10.10.10.11" )
#server = WebsocketServer( 8080, "192.168.0.10" )

IsRecievingFacesNow = False
TotalNumberOfFaces = 0
RecievedNumberOfFaces = 0

# modelName = "saved_model.h5"
# model = load_model(modelName)

### FAIRCUT-Server functions
def onCompleteRevieveFaces():
  print( "Complete recieving face images!\n" )
  
  # Add cutting processes here
  users = TotalNumberOfFaces
  cutter = BaumCutter( users )
  cutter.execCutting()
  
  # Send BMI-percentages to Mac
  print(cutter.message2mac)
  server.send_message_to_all( cutter.message2mac )
  #server.send_message_to_all( "BMI:40,30,20,10" )
  

def BeginTransmissionForFaces( message ):
  global IsRecievingFacesNow
  global TotalNumberOfFaces
  global RecievedNumberOfFaces
  
  IsRecievingFacesNow = True
  TotalNumberOfFaces = int(message[-1])
  RecievedNumberOfFaces = 0
  print( "Begin" )

def EndTransmissionForFaces( message ):
  global IsRecievingFacesNow
  global TotalNumberOfFaces
  global RecievedNumberOfFaces

  onCompleteRevieveFaces()
  
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

def ws_message_received( client, server, message ):
  if "BeginTransmissionForFaces" in message:
    BeginTransmissionForFaces( message )
    
  elif "EndTransmissionForFaces" == message:
    EndTransmissionForFaces( message )

  elif len( message ) > 200:
    if IsRecievingFacesNow:
      StoreFaceDataAsPNG( message )
      
  else:
    print( "Client(%d) said unknown message: %s" % ( client['id'], message ) )
    

### Main function 
def main():
  
	
  server.set_fn_new_client( ws_new_client ) 
  server.set_fn_client_left( ws_client_left ) 
  server.set_fn_message_received( ws_message_received )
  server.run_forever()


if __name__ == "__main__":
  main()
  
