// Stream Deck simplifié — Arduino Uno R4 WiFi
// Méthode : envoi série vers script Python

const int NB_BOUTONS = 6;

// Pins des boutons (à adapter selon ton câblage)
const int BOUTONS[NB_BOUTONS] = {2, 3, 4, 5, 6, 7};

// Pins des LEDs (optionnel — mettre -1 si pas de LED)
const int LEDS[NB_BOUTONS] = {8, 9, 10, 11, 12, 13};

bool etatPrecedent[NB_BOUTONS] = {false};

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < NB_BOUTONS; i++) {
    pinMode(BOUTONS[i], INPUT);         // Pull-down externe (résistance 10k vers GND)
    if (LEDS[i] != -1) {
      pinMode(LEDS[i], OUTPUT);
      digitalWrite(LEDS[i], LOW);
    }
  }

  Serial.println("READY");
}

void loop() {
  for (int i = 0; i < NB_BOUTONS; i++) {
    bool etat = digitalRead(BOUTONS[i]) == HIGH;

    // Détection front montant (appui, pas maintien)
    if (etat && !etatPrecedent[i]) {
      Serial.print("BTN:");
      Serial.println(i + 1);   // Envoie BTN:1, BTN:2 ... BTN:6

      // Flash LED feedback
      if (LEDS[i] != -1) {
        digitalWrite(LEDS[i], HIGH);
        delay(80);
        digitalWrite(LEDS[i], LOW);
      }
    }

    etatPrecedent[i] = etat;
  }

  delay(20); // Anti-rebond simple
}