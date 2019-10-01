# -*- coding: utf-8-unix -*-
# Version: Python 3.6.7

### User modules
import serial
    
class CutterControl:
  def convertRation2Percent( self, ration ):
    rationSum = sum( ration )
    percentage = []
    for recipient in range( len( ration ) ):
      percentage.append( int( ration[recipient] / rationSum * 100 ) )
      
    return percentage

  def message_to_mac( self, percentage ):
    message = "BMI:"
    for per in percentage:
      message = message + str( per ) + ","
    message = message.rstrip( "," )
    return message
    
  def send_message_to_mbed( self, percentage ):
    ba = bytearray()
    ba.append( ord( '@' ) )
    ba.append( 11 )
    checksum = 0
    ba.append( 1 )
    checksum = checksum + 1
    
    for i in range( len( percentage ) ):
      ba.append( percentage[i] )
      checksum = checksum + percentage[i]

    for i in range( 10 - len( percentage ) ):
      ba.append( 0 )
      checksum = checksum + 0

    ba.append( checksum & 0xFF )
    ba.append( ord( "\n" ) )

    with serial.Serial( '/dev/ttyS0', 112500 ) as ser:
      ser.write( ba )

