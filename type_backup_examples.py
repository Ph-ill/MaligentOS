import time,os,sys

def typingPrint(text):
  for character in text:
    sys.stdout.write(character)
    sys.stdout.flush()
    time.sleep(0.05)
  
def typingInput(text):
  for character in text:
    sys.stdout.write(character)
    sys.stdout.flush()
    time.sleep(0.05)
  value = input()  
  return value  
  
def clearScreen():
  os.system("clear")
    
typingPrint("Hello world...\n")
time.sleep(1)
typingPrint("You've entered the Matrix!\n")
time.sleep(1)

pillColor = typingInput("Will you take the blue or the red pill? (Type b for blue, r for red)")

if pillColor == "b":
  typingPrint("You took the blue pill! ")
  typingPrint("You are leaving the Matrix and going back to the real world!\n")
elif pillColor == "r":
  typingPrint("You took the red pill! ")
  typingPrint("You will be stuck in the Matrix forever!\n")
else:
  typingPrint("Invalid answer!")

time.sleep(1)  
typingPrint("Good bye!\n")
typingPrint("This screen will clear itself in 3..")
time.sleep(1)
typingPrint("2..")
time.sleep(1)
typingPrint("1..")
time.sleep(1)
clearScreen()

