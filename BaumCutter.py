import numpy as np

from tensorflow.keras.preprocessing.image import load_img, img_to_array, array_to_img
from tensorflow.keras.models import load_model#,Model
import serial

class BaumCutter:
  def __init__(self, users):
    
    self.users = range(users)
    self.x = []

    
    basename = "image_#"
    filetype= ".png"
    
    self.message2mac = ""
    
    # Get images from saved pictures
    for user in self.users:
          
      imgfile = basename + str(user) + filetype
      img = load_img(imgfile, target_size=(224,224) )
      img_array = img_to_array(img)
      
      self.x.append(img_array)
      
    self.x = np.array(self.x)
    self.x = self.x.astype("float32") / 255.0
        
    
  def execCutting(self):
    bmiPredict = BMIpredict()
    cutter = CutterControl()
    
    ration = bmiPredict.bmiPrediction(self.x, self.users)
    
    print(ration)
    percentages = cutter.convertRation2Percent(ration)
    
    self.message2mac = cutter.message_to_mac(percentages)
    cutter.send_message_to_mbed(percentages)
    
class BMIpredict:
  def __init__(self):
    modelName = "saved_model.h5"
    self.model = load_model(modelName)
    self.model._make_predict_function()
    
  def bmiPrediction( self, faceData, users ):
    predicted_classes = []
    predicted = self.model.predict(faceData)#, batch_size=None, verbose=0, steps=None)
    print(predicted)
    for user in users:
      predicted_classes.append(predicted[user].argmax())
      
    return predicted_classes


class CutterControl:
    def convertRation2Percent(self, ration):
      rationSum = sum(ration)
      percentage = []
      for recipient in range(len(ration)):
        percentage.append(int(ration[recipient]/rationSum*100))
          
      return percentage


    def message_to_mac(self, percentage):
      message = "BMI:"
      for per in percentage:
        message = message + str(per) + ","
      message = message.rstrip(",")
      return message


    def send_message_to_mbed(self,percentage):
      ba = bytearray()
      ba.append(ord('@'))
      ba.append(11)
      checksum = 0
      ba.append(1)
      checksum = checksum + 1
      
      for i in range(len(percentage)):
        ba.append(percentage[i])
        checksum = checksum + percentage[i]

      for i in range(10-len(percentage)):
        ba.append(0)
        checksum = checksum + 0

      ba.append(checksum & 0xFF)

      ba.append(ord("\n"))

      with serial.Serial('/dev/ttyS0', 112500) as ser:
        ser.write(ba)



##### Main function for test#########################################################
'''
def main():
    print( "Test code for prediction from picrures!\n" )

  # Add cutting processes here
    users = 3
    cutter = BaumCutter( users )
    cutter.execCutting()

    print("aaaa")
    print(cutter.message2mac)

if __name__ == "__main__":
    main()
'''

