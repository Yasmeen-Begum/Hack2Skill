
Step 1: Create AlloyDB Cluster
Step 3: Create Database
Connect to the instance:
```
CREATE DATABASE wellness_db;
```
Step 4: Create Tables
Switch to your new database:
```
\c wellness_db
```
Then create the schema:
```
CREATE TABLE wellness_plans (
    plan_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    plan_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workouts (
    workout_id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES wellness_plans(plan_id) ON DELETE CASCADE,
    title VARCHAR(255),
    recurrence_rule TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE diet_logs (
    diet_id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES wellness_plans(plan_id) ON DELETE CASCADE,
    meal_date DATE NOT NULL,
    meal_description TEXT,
    calories INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES wellness_plans(plan_id) ON DELETE CASCADE,
    title VARCHAR(255),
    appointment_date TIMESTAMP NOT NULL,
    reminder_minutes_before INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notes (
    note_id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES wellness_plans(plan_id) ON DELETE CASCADE,
    note_title VARCHAR(255),
    note_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
insert sample data
```
-- Wellness Plans (8 users)
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('neha', 'Weekly Health Routine');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('arjun', 'Fitness Boost Plan');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('sara', 'Balanced Lifestyle');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('mike', 'Weight Loss Journey');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('anita', 'Yoga & Mindfulness');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('rahul', 'Strength Training Plan');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('emma', 'Healthy Living Routine');
INSERT INTO wellness_plans (user_id, plan_name) VALUES ('li', 'Cardio & Endurance');

-- Workouts (8 entries)
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (1, 'Gym Session', 'RRULE:FREQ=WEEKLY;BYDAY=MO,WE');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (2, 'Yoga Class', 'RRULE:FREQ=WEEKLY;BYDAY=TU,TH');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (3, 'Morning Run', 'RRULE:FREQ=DAILY;INTERVAL=1');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (4, 'Cycling', 'RRULE:FREQ=WEEKLY;BYDAY=SA');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (5, 'Meditation', 'RRULE:FREQ=DAILY;INTERVAL=1');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (6, 'Strength Training', 'RRULE:FREQ=WEEKLY;BYDAY=MO,FR');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (7, 'Swimming', 'RRULE:FREQ=WEEKLY;BYDAY=SU');
INSERT INTO workouts (plan_id, title, recurrence_rule) VALUES (8, 'HIIT Workout', 'RRULE:FREQ=WEEKLY;BYDAY=TU,TH');

-- Diet Logs (8 entries)
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (1, '2026-04-07', 'Grilled chicken salad', 450);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (2, '2026-04-07', 'Vegetable stir fry', 350);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (3, '2026-04-07', 'Oatmeal with fruits', 300);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (4, '2026-04-07', 'Protein shake', 250);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (5, '2026-04-08', 'Green smoothie', 200);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (6, '2026-04-08', 'Chicken curry with rice', 600);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (7, '2026-04-08', 'Avocado toast', 350);
INSERT INTO diet_logs (plan_id, meal_date, meal_description, calories) VALUES (8, '2026-04-08', 'Salmon with quinoa', 500);

-- Appointments (8 entries)
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (1, 'Doctor Appointment', '2026-04-18 10:00:00', 30);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (2, 'Nutritionist Visit', '2026-04-20 15:00:00', 60);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (3, 'Therapy Session', '2026-04-22 09:00:00', 45);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (4, 'Annual Checkup', '2026-04-25 11:00:00', 30);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (5, 'Yoga Workshop', '2026-04-28 08:00:00', 20);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (6, 'Physiotherapy', '2026-04-30 14:00:00', 30);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (7, 'Dental Cleaning', '2026-05-02 12:00:00', 45);
INSERT INTO appointments (plan_id, title, appointment_date, reminder_minutes_before) VALUES (8, 'Eye Checkup', '2026-05-05 16:00:00', 30);

-- Notes (8 entries)
INSERT INTO notes (plan_id, note_title, note_content) VALUES (1, 'Wellness Journal', 'Started new weekly routine today.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (2, 'Diet Notes', 'Trying more plant-based meals.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (3, 'Workout Log', 'Completed 5km run this morning.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (4, 'Health Notes', 'Tracking sleep quality daily.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (5, 'Meditation Notes', 'Feeling calmer after 10 minutes.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (6, 'Strength Notes', 'Bench press improved by 10kg.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (7, 'Swimming Notes', 'Swam 20 laps today.');
INSERT INTO notes (plan_id, note_title, note_content) VALUES (8, 'HIIT Notes', 'Completed 4 rounds of HIIT.');
```

Verify Data

Run a quick check to confirm each table 
```
SELECT COUNT(*) FROM wellness_plans;
SELECT COUNT(*) FROM workouts;
SELECT COUNT(*) FROM diet_logs;
SELECT COUNT(*) FROM appointments;
SELECT COUNT(*) FROM notes;
```

Explore Data

Try some queries 
1.List all users and thier plans
```
SELECT user_id, plan_name FROM wellness_plans;
```
2.show workouts and their recurrence rules
```
SELECT title, recurrence_rule FROM workouts;
```
3.Meal above 400 calories
```
SELECT meal_date, meal_description, calories
FROM diet_logs
WHERE calories > 400;
```
4.Upcoming appointments
```
SELECT title, appointment_date
FROM appointments
WHERE appointment_date > NOW()
ORDER BY appointment_date ASC;
```
5.Recent tables
```
SELECT note_title, note_content, created_at
FROM notes
ORDER BY created_at DESC
LIMIT 5;
```
6.Join tables
```
-- Show each user’s workouts
SELECT wp.user_id, w.title, w.recurrence_rule
FROM wellness_plans wp
JOIN workouts w ON wp.plan_id = w.plan_id;

-- Show meals with user context
SELECT wp.user_id, d.meal_date, d.meal_description, d.calories
FROM wellness_plans wp
JOIN diet_logs d ON wp.plan_id = d.plan_id;
```
