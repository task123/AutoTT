int linePossitionPWMPin = 11;
int leftMostPhotoDiode = 10;
int rightMostPhotoDiode = 12;

void setup(){
  analogReference(INTERNAL);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);
  pinMode(A6, INPUT);
  pinMode(A7, INPUT);
  pinMode(linePossitionPWMPin, OUTPUT); 
  pinMode(leftMostPhotoDiode, OUTPUT);
  pinMode(rightMostPhotoDiode, OUTPUT);
}

void loop(){

}
