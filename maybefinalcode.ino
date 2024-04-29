#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;
int A=170;

int IRs1 = 9;
int IRs2 = 10;
int IRs3 = 11;
//Motor one
#define ENA 6
#define IN1 2
#define IN2 3

//Motor two
#define IN3 4
#define IN4 7
#define ENB 5
int gyroX_offset = -17;
int gyroY_offset = 58;
int gyroZ_offset = -142;
#define Kp 100  // Proportional gain (scaled up)
#define Ki 100  // Integral gain (scaled up)
#define Kd 150  // Derivative gain (scaled up)

#define setpoint 0     // Desired angle (straight path)
#define MAX_SPEED 255  // Maximum motor speed


void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  Wire.begin();
  mpu.initialize();
  // Set IR sensor pins as inputs
  pinMode(IRs1, INPUT);
  pinMode(IRs2, INPUT);
  pinMode(IRs3, INPUT);
}

void loop() {
  int IR1 = digitalRead(IRs1);
  int IR2 = digitalRead(IRs2);
  int IR3 = digitalRead(IRs3);

  if (IR1 == LOW && IR2 == HIGH && IR3 == LOW) {  //Straight path
    Forward();
  } else if (IR1 == HIGH && IR2 == LOW && IR3 == LOW) {  //Left turn
    Left();
  } else if (IR1 == LOW && IR2 == LOW && IR3 == HIGH) {  //Right Turn
    Right();
  } else if (IR1 == HIGH && IR2 == LOW && IR3 == HIGH) {   //T Intersection
    Left();                                                // As left is possible
  } else if (IR1 == HIGH && IR2 == HIGH && IR3 == LOW) {   //Left T Intersection
    Left();                                                // As Left is possible
  } else if (IR1 == LOW && IR2 == HIGH && IR3 == HIGH) {   //Right T Intersection
    Forward();                                             //As Straight path is possible
  } else if (IR1 == LOW && IR2 == LOW && IR3 == LOW) {     //Dead End
    U_Turn();                                              //As no other direction is possible
  } else if (IR1 == HIGH && IR2 == HIGH && IR3 == HIGH) {  //4 Lane intersection
    Left();                                                //As no other direction is possible
  } else if (IR1 == HIGH && IR2 == HIGH && IR3 == HIGH) {  //End of Maze
    Stop();                                                //As no other direction is possible
  } else if (IR1 == HIGH && IR2 == HIGH && IR3 == HIGH) {  //Check for 4-way intersection or end of maze
    Forward();
    delay(100);
    Stop();
    if (IR1 == HIGH && IR2 == HIGH && IR3 == HIGH) {
      Serial.println("END OF MAZE");
      Stop();
    } else {
      Serial.println("FOUR WAY INTERSECTION");
      Left();
    }
  }
}

void CALCULATE_SHORTEST_PATH(char MAZE_ARRAY[], int SIZE_OF_ARRAY) {
  char ACTION;

  for (int i = 0; i <= SIZE_OF_ARRAY - 2; i++) {
    ACTION = MAZE_ARRAY[i];

    if (ACTION == 'B') {
      if (MAZE_ARRAY[i - 1] == 'L' && MAZE_ARRAY[i + 1] == 'R') {
        MAZE_ARRAY[i] = 'B';
        MAZE_ARRAY[i - 1] = 0;
        MAZE_ARRAY[i + 1] = 0;
        REARRANGE(MAZE_ARRAY, SIZE_OF_ARRAY, i - 1, i, i + 1);
      }

      if (MAZE_ARRAY[i - 1] == 'L' && MAZE_ARRAY[i + 1] == 'S') {
        MAZE_ARRAY[i] = 'R';
        MAZE_ARRAY[i - 1] = 0;
        MAZE_ARRAY[i + 1] = 0;
        REARRANGE(MAZE_ARRAY, SIZE_OF_ARRAY, i - 1, i, i + 1);
      }

      if (MAZE_ARRAY[i - 1] == 'R' && MAZE_ARRAY[i + 1] == 'L') {
        MAZE_ARRAY[i] = 'B';
        MAZE_ARRAY[i - 1] = 0;
        MAZE_ARRAY[i + 1] = 0;
        REARRANGE(MAZE_ARRAY, SIZE_OF_ARRAY, i - 1, i, i + 1);
      }

      if (MAZE_ARRAY[i - 1] == 'S' && MAZE_ARRAY[i + 1] == 'L') {
        MAZE_ARRAY[i] = 'R';
        MAZE_ARRAY[i - 1] = 0;
        MAZE_ARRAY[i + 1] = 0;
        REARRANGE(MAZE_ARRAY, SIZE_OF_ARRAY, i - 1, i, i + 1);
      }

      if (MAZE_ARRAY[i - 1] == 'S' && MAZE_ARRAY[i + 1] == 'S') {
        MAZE_ARRAY[i] = 'B';
        MAZE_ARRAY[i - 1] = 0;
        MAZE_ARRAY[i + 1] = 0;
        REARRANGE(MAZE_ARRAY, SIZE_OF_ARRAY, i - 1, i, i + 1);
      }

      if (MAZE_ARRAY[i - 1] == 'L' && MAZE_ARRAY[i + 1] == 'L') {
        MAZE_ARRAY[i] = 'S';
        MAZE_ARRAY[i - 1] = 0;
        MAZE_ARRAY[i + 1] = 0;
        REARRANGE(MAZE_ARRAY, SIZE_OF_ARRAY, i - 1, i, i + 1);
      }

      i = -1;
    }

    delay(100);
  }
}

void Forward() {
  int16_t gyroX, gyroY, gyroZ;
  mpu.getRotation(&gyroX, &gyroY, &gyroZ);  // Get gyro rotation data from MPU6050

  // Adjust gyro readings by subtracting offsets
  gyroX -= gyroX_offset;
  gyroY -= gyroY_offset;
  gyroZ -= gyroZ_offset;

  // Compute PID
  int error = setpoint - gyroY;  // Assuming gyroY represents the yaw angle
  static long integral = 0;
  static int previous_error = 0;
  long derivative = error - previous_error;
  integral += error;
  previous_error = error;

  int output = (Kp * error + Ki * integral + Kd * derivative) / 10;  // Scale down the output
  output = constrain(output, -MAX_SPEED, MAX_SPEED);                 // Constrain output within maximum motor speed

  int leftMotorSpeed = MAX_SPEED - output;
  int rightMotorSpeed = MAX_SPEED + output;

  // Set motor speeds based on PID output
  analogWrite(ENA, leftMotorSpeed);
  analogWrite(ENB, rightMotorSpeed);

  // Set motors to move forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}
void Left() {
  // Set left motor to turn backward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  // Stop right motor
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, A);
  analogWrite(ENB, A);
  delay(200);
}
void Right() {
  // Set left motor to turn backward
  digitalWrite(IN2, LOW);
  digitalWrite(IN1, HIGH);

  // Stop right motor
  digitalWrite(IN4, HIGH);
  digitalWrite(IN3, LOW);

  analogWrite(ENA, A);
  analogWrite(ENB, A);
  delay(200);
}

void U_Turn() {
  // Set left motor to turn backward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  // Stop right motor
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, A);
  analogWrite(ENB, A);
}
void Stop() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  // Stop right motor
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}
// Define the REARRANGE function

void REARRANGE(char MAZE_ARRAY[], int SIZE_OF_ARRAY, int index1, int index2, int index3) {
    // Implement the logic to rearrange the array elements here
    // Example implementation:
    char temp = MAZE_ARRAY[index1];
    MAZE_ARRAY[index1] = MAZE_ARRAY[index2];
    MAZE_ARRAY[index2] = MAZE_ARRAY[index3];
    MAZE_ARRAY[index3] = temp;
}
