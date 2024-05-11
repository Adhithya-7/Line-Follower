# Line Follower Bot with PID Control

This project involves the development of an autonomous line follower bot capable of navigating and following a line on the ground. The bot utilizes various components, including infrared (IR) sensors, motors, motor drivers, an Arduino Nano, and an MPU6050 sensor for PID control.

## Features

- Autonomous line following using the left-hand rule algorithm
- PID control for stability and smooth movement
- Intersection and dead-end handling
- Shortest path optimization (future improvement)

## Components

- Arduino Nano
- 3x IR Sensors
- L298N Motor Driver
- 2x DC Motors
- MPU6050 Inertial Measurement Unit (IMU)
- Chassis
- Power source (batteries)

## Installation

1. Clone the repository:
   git clone https://github.com/your-username/line-follower-bot.git
2. Open the project in the Arduino IDE.
3. Connect the Arduino Nano to your computer.
4. Upload the code to the Arduino Nano.

## Usage

1. Assemble the bot according to the circuit diagram and connections provided in the documentation.
2. Place the bot on the line or maze to be navigated.
3. Power on the bot, and it will autonomously follow the line while maintaining stability using PID control.

## Acknowledgments

- [Arduino](https://www.arduino.cc/) for the development platform.
- [MPU6050 Library](https://github.com/jrowberg/i2cdevlib) for interfacing with the MPU6050 sensor.
