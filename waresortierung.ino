const float MAX_WEIGHT = 500;

unsigned int NR_BOXES;
float THRESHOLD;
int *boxes_array;

/**
 * orderly shut down of the entire system
 */
 // to implement
void exitFunction() {
  
}

/**
 * initializing an array of boxes where the number of packages per box are counted.
 */
void initializingArray() {
  // declaration
  boxes_array = (unsigned int*)malloc(NR_BOXES * sizeof(int));
  if(boxes_array == NULL) {
    // error handeling
    exitFunction(); 
  }

  // initialization with 0
  for(int i = 0; i < NR_BOXES; i++){ boxes_array[i] = 0; }
  return;
}

// setup code to run once:
void setup() {
  //NR_BOXES initialisieren
  //THRESHOLD initialisieren
  
  initializingArray();

  // Waage
  // Lichtschranke
  // LED
}

/**
 * send a message to Raspberry
 * 
 * @param message is the message to send
 */
 // to implement
void sendMessage(String message) {
  
}

/**
 * read out the scale and handle errors
 * 
 * @returns weight of package
 */
 // to implement
float scale() {
  
}

/**
 * sorting the package into the right box (Box 0 with least weight)
 * 
 * @param weight is the weight of the package to be sorted
 * @returns number of box
 */
int sort(float weight) { 
  if (weight < THESHOLD) { return 0; }
  return 1;
}

/**
 * read out the photoelectric sensor
 * 
 * @return number of full box or -1 if not triggered
 */
int photoelectricSensor() {
  
}

// main code to run repeatedly:
void loop() {
  float weight = scale();
  int witch_box = sort(weight);
  
  String messageWB = String(witch_box);         // convert int to String: message to be send to raspberry
  sendMessage(messageWB);
  
  boxes_array[witch_box]++;                     // increase the counter for the amount of packages in the box

  // warten auf message das roboter ferig ist

  int full_box = photoelectricSensor();
  // if a box is full send the relevant info to raspberry and terminate program
  if(full_box >= 0) {
    String messageFB = String(full_box);
    sendMessage(messageFB);
    exitFunction();
  }
  
}
