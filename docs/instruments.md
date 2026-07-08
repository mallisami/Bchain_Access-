# Blank Evaluation Instruments

This document contains the exact evaluation instruments administered to the ten domain experts during the BCHAIN-ACCESS prototype study:

1. **System Usability Scale (SUS)**
2. **Accessibility Questionnaire**
3. **Cognitive Walkthrough Task Script**

---

## 1. System Usability Scale (SUS)
Each item is scored on a standard 5-point Likert scale:
* `1` = Strongly Disagree
* `2` = Disagree
* `3` = Neutral
* `4` = Agree
* `5` = Strongly Agree

### Statements:
1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

---

## 2. Accessibility Questionnaire
Each item is scored on a 5-point Likert scale (1 = Strongly Disagree, 5 = Strongly Agree), designed to evaluate the prototype's WCAG 2.1 Level AA conformance from a user experience standpoint:
1. I found the navigation consistent and predictable.
2. I found the instructions and labels easy to understand.
3. I was able to access all features using only the keyboard.
4. I found the colour contrast adequate for reading.
5. I found the error messages helpful and clear.
6. I felt in control while using the system.
7. I would feel comfortable using this system independently.
8. I found the system forgiving if I made a mistake.
9. I understood the information presented to me.
10. I found the system responsive and fast enough.

---

## 3. Cognitive Walkthrough Task Script
The expert panel followed these 8 tasks sequentially to evaluate the end-to-end user flow:

* **Task 1: Biometric Unlock**
  * *Instruction:* "Authenticate and unlock your health dashboard using the simulated fingerprint/biometric reader on the landing screen."
* **Task 2: View Record**
  * *Instruction:* "Locate your 'MRI Brain Scan' record on the dashboard and view its metadata details."
* **Task 3: Access Verification**
  * *Instruction:* "Verify the current list of authorized providers for this record to ensure no unauthorized access is active."
* **Task 4: Access Initiation**
  * *Instruction:* "Select Dr. Sarah Chen from the provider directory and initiate a 'View Only' access grant for your MRI Brain Scan record."
* **Task 5: Review Cooldown**
  * *Instruction:* "Review the pending access grant details and inspect the active 60-second safety cooldown window."
* **Task 6: Access Confirmation**
  * *Instruction:* "Wait for the 60-second safety countdown to expire, then confirm the access grant to finalize it on-chain."
* **Task 7: Access Revocation**
  * *Instruction:* "Immediately revoke Dr. Sarah Chen's access permissions to verify that access is cut off with no pending delay."
* **Task 8: Help & FAQ Search**
  * *Instruction:* "Navigate to the FAQ section and locate the explanation for the question 'What is blockchain?'."
