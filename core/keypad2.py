#!/usr/bin/python
#
# keypad.py
#
# Apr 16/2024
#
# 4x4 matrix keypad via MCP23017 I2C I/O expander  Python library for the Raspberry Pi.
#
#
# If the smbus module is re-entrant (ie allows multiple Python clients, keypad
# supports multiple keypad modules simultaneously, requires one port of an
# MCP23017 I2C I/O port expander per keypad)
#

import smbus2
import time

class keypad_module:

  I2CADDR    = 0x27   	# valid range is 0x20 - 0x27
  UPSIDEDOWN = 0      	# direction keypad is facing in
  PORT       = 0      	# 0 for GPIOA, 1 for GPIOB
  IODIRA = 0x00		# I/O direction register base address
  PULUPA = 0x0C		# PullUp enable register base address
  GPIOA  = 0x12		# GPIO pin register base address
  OLATA  = 0x14		# Output Latch register base address
  DEFVALA  = 0x06
  GPINTENA =0x04
  INTCONA=0x08
  INTFA=0x0E
  IOCONA=0x0A
  INTCAPA=0x10
  # Keypad Column output values
  KEYCOL = [0b11110111,0b11111011]
  # Keypad Keycode matrix
  KEYCODE  = [['1','2'], # KEYCOL0
              ['3','4']] # KEYCOL1
  # Decide the row
  DECODE = [0,0,0,0, 0,0,0,0, 0,0,0,0 ,0,1,0,0]
  # initialize I2C comm, 1 = rev2 Pi / New Pi, 0 for Rev1 Pi / Old Pi
  i2c = smbus2.SMBus(0)
  # get a keystroke from the keypad
  def getch(self):
    keyvalue = self.i2c.read_byte_data(self.I2CADDR, self.INTFA+self.port)
    self.i2c.read_byte_data(self.I2CADDR, self.INTCAPA+self.port)
    self.i2c.read_byte_data(self.I2CADDR, self.GPIOA+self.port)
    interrupt_status=self.i2c.read_byte_data(self.I2CADDR, self.INTFA+self.port)
    print("keyvalue")
    print(keyvalue)
    print("Interrupt_status")
    print(interrupt_status)
    if interrupt_status==0:
       return keyvalue
    else:
       return 0
  def output_enable(self):
    print("Buzzer Enabled")
    self.i2c.write_byte_data(self.I2CADDR,self.GPIOA+self.port,0x1F)

  def output_disable(self):
    print("Buzzer Disabled")
    self.i2c.write_byte_data(self.I2CADDR,self.GPIOA+self.port,0x0F)
 
 # initialize the keypad class
  def __init__(self,addr,ioport,upside):
    self.I2CADDR = addr
    self.UPSIDEDOWN = upside
    self.port = ioport
    self.i2c.write_byte_data(self.I2CADDR,self.IODIRA+self.port,0x0F) # upper 4 bits are inputs
    self.i2c.write_byte_data(self.I2CADDR,self.PULUPA+self.port,0x0F) # enable upper 4 bits pullups
    self.i2c.write_byte_data(self.I2CADDR,self.INTCONA+self.port,0x0F)
    self.i2c.write_byte_data(self.I2CADDR,self.DEFVALA+self.port,0x0F)
    self.i2c.write_byte_data(self.I2CADDR,self.GPINTENA+self.port,0x0F)

    self.keyvalue=0
#    self.run()
'''
  def run(keyvalue): 
#  keypad = keypad_module(0x27,0,0) 
    while True:
      keyvalue = self.getch()
      print(keyalue)
      return keyvalue

#    if ch == 'D':
#      exit
'''
'''
if __name__ == '__main__':
#  main()
     keypadevent = keypad_module(0x27,0,0)
     while True:
       keyvalue = keypadevent.getch()
       print(keyvalue)
       pass

'''
