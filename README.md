# 🏋️‍♂️ Automated Gym Class Booking System

This project provides an automated workflow designed to manage weekly gym class reservations with precision and reliability. It focuses on identifying specific sessions, performing the appropriate booking actions, and validating that all reservations were successfully registered.

---

## 🎯 Purpose

The system was created to:

- **Automate recurring bookings** for predefined days and times.  
- **Detect relevant sessions** within the weekly schedule.  
- **Handle booking states** such as *Booked*, *Waitlisted*, or *Join Waitlist*.  
- **Verify completed reservations** through the user’s booking history.

---

## 🧠 Key Features

- **Automatic authentication**  
  The system logs in and navigates to the scheduling area without manual interaction.

- **Smart class filtering**  
  Only sessions matching specific days (Tuesday and Thursday) and a specific time (6 PM) are processed.

- **Dynamic state interpretation**  
  Each class is analyzed to determine whether it should be booked, waitlisted, or skipped.

- **Robust retry mechanism**  
  Critical actions are retried automatically to handle temporary interface issues.

- **Cross‑page validation**  
  The system confirms that all processed bookings appear correctly in the “My Bookings” section.

---

## 📊 Workflow Overview

1. **Login sequence**  
   The system authenticates and waits until the schedule becomes available.

2. **Weekly schedule scan**  
   All visible classes are inspected to find those matching the target criteria.

3. **Action per class**  
   Depending on the current state, the system books the class, joins the waitlist, or records that it was already processed.

4. **Summary tracking**  
   Counts are maintained for new bookings, new waitlist entries, and previously processed classes.

5. **Final verification**  
   The system checks the user’s booking history to ensure all expected reservations are present.

---

## 📁 Logical Structure

- **Authentication module**  
- **Class processing module**  
- **State management**  
- **Retry handler**  
- **Verification module**  

Each component is designed to be modular, predictable, and resilient to temporary UI inconsistencies.

---

## ✔️ Benefits

- Eliminates repetitive manual booking tasks.  
- Ensures no desired class is missed due to timing or oversight.  
- Handles temporary page issues gracefully.  
- Confirms that all reservations match the expected outcome.