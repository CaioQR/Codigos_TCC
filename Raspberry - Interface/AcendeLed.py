import RPi.GPIO as GPIO

led_superior_pin = 29
led_inferior_pin = 31
        
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_inferior_pin,GPIO.OUT)
GPIO.setup(led_superior_pin, GPIO.OUT)
        
GPIO.output(led_superior_pin, True)
GPIO.output(led_inferior_pin, True)
        
        