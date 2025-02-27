INSERT INTO household (address, total_members, total_income) VALUES
('House No. 1, Main Road, Phulera', 0, 0),
('House No. 2, Temple Street, Phulera', 0, 0),
('House No. 3, Near Post Office, Phulera', 0, 0),
('House No. 4, School Lane, Phulera', 0, 0),
('House No. 5, Mango Orchard, Phulera', 0, 0),
('House No. 6, Railway Colony, Phulera', 0, 0),
('House No. 7, Bus Stand Road, Phulera', 0, 0),
('House No. 8, Canal Side, Phulera', 0, 0),
('House No. 9, Station Road, Phulera', 0, 0),
('House No. 10, Subhash Chowk, Phulera', 0, 0),
('House No. 11, Near Panchayat Office, Phulera', 0, 0),
('House No. 12, Bazar Street, Phulera', 0, 0),
('House No. 13, Village Square, Phulera', 0, 0),
('House No. 14, Field Lane, Phulera', 0, 0),
('House No. 15, Well Side, Phulera', 0, 0),
('House No. 16, Near Water Tank, Phulera', 0, 0),
('House No. 17, Hanuman Gali, Phulera', 0, 0),
('House No. 18, Market Road, Phulera', 0, 0),
('House No. 19, Near Primary School, Phulera', 0, 0),
('House No. 20, Grain Storage, Phulera', 0, 0),
('House No. 21, Shiv Mandir Lane, Phulera', 0, 0),
('House No. 22, Kachha Rasta, Phulera', 0, 0),
('House No. 23, Paddy Field View, Phulera', 0, 0),
('House No. 24, Behind Police Station, Phulera', 0, 0),
('House No. 25, East Corner, Phulera', 0, 0),
('House No. 26, Near Brick Kiln, Phulera', 0, 0),
('House No. 27, Small Lake Road, Phulera', 0, 0),
('House No. 28, Opposite Bus Depot, Phulera', 0, 0),
('House No. 29, Main Road, Fakauli', 0, 0),
('House No. 30, Near Gram Sabha, Fakauli', 0, 0),
('House No. 31, Temple Lane, Fakauli', 0, 0),
('House No. 32, East Farm Road, Fakauli', 0, 0),
('House No. 33, Banyan Tree Street, Fakauli', 0, 0),
('House No. 34, Back of Panchayat Bhawan, Fakauli', 0, 0),
('House No. 35, North Gali, Fakauli', 0, 0),
('House No. 36, Near Local Pond, Fakauli', 0, 0),
('House No. 37, West End, Fakauli', 0, 0),
('House No. 38, Well Side, Fakauli', 0, 0),
('House No. 39, Near Water Tank, Phulera', 0, 0); 
-- Populate Citizens Table
INSERT INTO citizens (name, dob, gender, isDisabled, occupation, income, household_id, educational_qualification, mother_id, father_id) VALUES
('Raghunath Patil', '1945-06-18', 'male', false, 'Farmer', 10000, 1, '5th', NULL, NULL),    
('Savitri Patil', '1948-10-25', 'female', false, 'Housewife', 0, 1, '5th', NULL, NULL),     
('Shankar Patil', '1985-02-12', 'male', false, 'Farmer', 45000, 1, '10th', 2, 1),           
('Lakshmi Patil', '1988-07-04', 'female', false, 'Housewife', 0, 1, '10th', NULL, NULL),   
('Ravi Patil', '2014-08-15', 'male', false, 'Student', 0, 1, '4th', 4, 3),
('Arjun Patil', '2020-03-09', 'male', false, 'Student', 0, 1, NULL, 4, 3),
--------
('Hariram Sharma', '1940-04-10', 'male', false, 'Retired', 0, 2, '5th', NULL, NULL), -- owns land_id:4
('Kamala Sharma', '1943-12-01', 'female', false, 'Housewife', 0, 2, '5th', NULL, NULL),
('Mahesh Sharma', '1982-11-22', 'male', false, 'Grocery Shop Owner', 30000, 2, '8th', 8, 7),
('Sunita Sharma', '1986-05-05', 'female', false, 'Tailor', 5000, 2, '8th', 2, 1),
('Rahul Sharma', '2015-01-30', 'male', false, 'Student', 0, 2, '3rd', 10, 9),
('Kunal Sharma', '2020-10-18', 'male', false, 'Student', 0, 2, NULL, 10, 9),
--------
('Ramesh Iyer', '1982-03-15', 'male', false, 'Farmer', 25000, 3, '10th', NULL, NULL),
('Meena Iyer', '1985-09-22', 'female', false, 'Housewife', 0, 3, '10th', NULL, NULL),
('Anjali Iyer', '2000-07-10', 'female', false, 'Nurse', 45000, 3, '11th', 14, 13),
('Priya Iyer', '2008-11-03', 'female', false, 'Student', 0, 3, '10th', 14, 13),
('Rohit Iyer', '2015-06-25', 'male', false, 'Student', 0, 3, '3rd', 14, 13),
--------
('Ramesh Kumar', '1977-05-12', 'male', FALSE, 'Farmer', 30000, 4, 'None', NULL, NULL),
('Sunita Devi', '1980-08-15', 'female', FALSE, 'Homemaker', 0, 4, 'None', NULL, NULL),
('Aarti', '2000-03-25', 'female', FALSE, 'Teacher', 15000, 4, 'Graduate', 19, 18),
('Vikram', '2005-07-18', 'male', FALSE, 'Student', 0, 4, 'Undergraduate', 19, 18),
('Ravi', '2007-01-15', 'male', FALSE, 'Student', 0, 4, '11th', 19, 18),
--------
('Amar Singh', '1969-09-10', 'male', FALSE, 'Tractor Driver', 25000, 5, 'None', NULL, NULL),
('Kiran Singh', '1974-02-20', 'female', FALSE, 'Handloom Worker', 5000, 5, 'None', NULL, NULL),
('Rohit', '1996-11-30', 'male', FALSE, 'IT Professional', 100000, 5, 'Graduate', 24, 23),
('Pooja', '1999-02-05', 'female', FALSE, 'Nurse', 15000, 5, 'Nursing Degree', 24, 23),
('Chandni', '2024-03-25', 'female', FALSE, NULL, 0, 5, 'None', 26, 25),
--------
('Prakash Yadav', '1984-12-15', 'male', FALSE, 'Fisherman', 25000, 6, 'None', NULL, NULL),
('Geeta Yadav', '1986-03-20', 'female', FALSE, 'Homemaker', 0, 6, 'None', NULL, NULL),
('Anjali', '2014-06-10', 'female', FALSE, 'Student', 0, 6, '5th', 29, 28),
('Sunil', '2017-09-01', 'male', FALSE, NULL, 0, 6, '1st', 29, 28),
--------
('Manohar Naik', '1950-12-05', 'male', false, 'Retired Farmer', 0, 7, '5th', NULL, NULL),
--------
('Radha Das', '1983-04-16', 'female', false, 'Tailor', 15000, 8, '10th', NULL, NULL),
('Rita Das', '2007-08-12', 'female', false, NULL, 0, 8, NULL, 33, NULL),
('Arjun Das', '2010-01-28', 'male', false, NULL, 0, 8, NULL, 33, NULL),
--------
('Ravi Pillai', '1985-06-30', 'male', false, 'Carpenter', 25000, 9, '8th', NULL, NULL),
('Sita Pillai', '1989-11-21', 'female', false, 'Seamstress', 12000, 9, '10th', NULL, NULL),
--------
('Rajesh Sharma', '1978-03-11', 'male', false, 'Government Officer', 60000, 10, 'Bachelors Degree', NULL, NULL),
('Kartik Sharma', '2006-09-07', 'male', false, 'Student', 10000, 10, '12th', NULL, 1),
--------
('Firoz Khan', '1987-02-03', 'male', true, 'Daily Wage Worker', 5000, 11, '5th', NULL, NULL), --40
--------
('Surendra Roy', '1960-10-12', 'male', false, 'Panchayat Pradhan', 90000, 12, 'UG', NULL, NULL), --41
('Kavita Roy', '1962-03-19', 'female', false, 'Teacher', 18000, 12, 'UG', NULL, NULL),
('Alok Roy', '1985-05-17', 'male', false, 'Accountant', 40000, 12, 'UG', 42, 41),
('Meera Roy', '1988-11-08', 'female', false, 'Teacher', 10000, 12, '12th', 42, 41),
('Rohit Roy', '1991-12-22', 'male', false, 'Salesman', 30000, 12, '12th', 42, 41),
---------
('Ramu Verma', '1968-12-05', 'male', false, 'Watchman', 7000, 13, '8th', NULL, NULL),
--------
('Shivam Yadav', '1985-06-10', 'male', false, 'Electrician', 20000, 14, '10th', NULL, NULL),
('Radha Yadav', '1990-03-25', 'female', false, 'Beautician', 12000, 14, '10th', NULL, NULL),
--------
('Mohan Patel', '1978-04-16', 'male', false, 'Farm Owner', 45000, 15, '10th', NULL, NULL), -- owns land_id:1
('Ananya Patel', '2005-09-12', 'female', false, 'Student', 0, 15, '12th', NULL, 49),
('Amit Patel', '2008-01-20', 'male', false, 'Student', 0, 15, '10th', NULL, 49),
--------
('Dharam Singh', '1945-02-14', 'male', false, 'Retired Farmer', 0, 16, '5th', NULL, NULL), -- owns land_id:3
('Kamla Singh', '1948-06-18', 'female', false, 'Housewife', 0, 16, '5th', NULL, NULL),
--------
('Akash Kumar', '1995-11-07', 'male', false, 'Panchayat Secretary', 30000, 17, '12th', NULL, NULL),
--------
('Harish Singh', '1980-11-23', 'male', false, 'Shopkeeper', 25000, 18, '10th', NULL, NULL),
('Suman Singh', '1985-05-04', 'female', false, 'Housewife', 0, 18, '8th', NULL, NULL),
('Pooja Singh', '2012-07-10', 'female', false, NULL, 0, 18, '5th', 56, 55),
('Ravi Singh', '2016-09-17', 'male', false, NULL, 0, 18, '2nd', 56, 55),
--------
('Ganga Devi', '1940-08-09', 'female', false, 'Retired', 0, 19, '5th', NULL, NULL),
--------
('Rahul Sharma', '1982-12-12', 'male', true, 'School Teacher', 30000, 20, 'Bachelors Degree', NULL, NULL),
('Sneha Sharma', '1988-04-22', 'female', false, 'Housewife', 0, 20, '10th', NULL, NULL),
('Vikram Sharma', '2015-01-30', 'male', false, 'Student', 0, 20, '3rd', 61, 60),
--------
('Rajesh Gupta', '1960-03-21', 'male', false, 'Panchayat Up-Pradhan', 70000, 21, 'Bachelors Degree', NULL, NULL), -- owns land_id:2
('Kavita Gupta', '1965-08-15', 'female', false, 'Doctor', 120000, 21, 'MBBS', NULL, NULL),
('Aditi Gupta', '1990-12-18', 'female', false, 'Dance Teacher', 0, 21, '10th', 64, 63),
('Rohan Gupta', '1992-06-25', 'male', false, 'Salesman', 0, 21, '10th', 64, 63),
('Aryan Gupta', '1995-03-05', 'male', false, 'Salesman', 0, 21, '10th', 64, 63),
--------
('Sarita Rao', '1980-05-10', 'female', false, 'Tailor', 12000, 22, '8th', NULL, NULL),
--------
('Ram Prasad', '1986-09-11', 'male', false, 'Daily Wage Worker', 8000, 23, '5th', NULL, NULL),
('Meera Prasad', '1990-02-19', 'female', false, 'Housewife', 0, 23, '5th', NULL, NULL),
('Pinky Prasad', '2013-08-20', 'female', false, NULL, 0, 23, NULL, 70, 69),
('Rahul Prasad', '2017-04-15', 'male', false, NULL, 0, 23, NULL, 70, 69),
--------
('Vikram Rao', '1982-06-10', 'male', true, 'Carpenter', 10000, 24, '5th', NULL, NULL),
--------
('Amit Mehta', '1992-05-10', 'male', false, 'Shopkeeper', 15000, 25, '10th', NULL, NULL),
('Sunita Mehta', '1994-07-12', 'female', false, 'Housewife', 0, 25, '10th', NULL, NULL),
--------
('Ganesh Iyer', '1942-03-30', 'male', false, 'Retired Teacher', 0, 26, 'Bachelors Degree', NULL, NULL),
('Lakshmi Iyer', '1945-10-11', 'female', false, 'Housewife', 0, 26, '10th', NULL, NULL),
--------
('Ravi Tiwari', '1978-09-19', 'male', false, 'Farmer', 20000, 27, '8th', NULL, NULL),
('Sita Tiwari', '1982-12-14', 'female', false, 'Housewife', 0, 27, '5th', NULL, NULL),
('Manoj Tiwari', '2010-07-12', 'male', false, 'Student', 0, 27, '9th', 79, 78),
--------
('Arun Khanna', '1976-04-22', 'male', false, 'Business Owner', 200000, 28, 'Bachelors Degree', NULL, NULL),
('Priya Khanna', '1980-06-18', 'female', false, 'Lawyer', 120000, 28, 'LLB', NULL, NULL),
('Aarav Khanna', '2012-01-09', 'male', false, 'Student', 0, 28, '6th', 82, 81),
--------
('Radha Devi', '1980-03-20', 'female', false, 'Cook', 10000, 29, '5th', NULL, NULL),
('Poonam Devi', '2009-09-22', 'female', false, NULL, 0, 29, '8th', 84, NULL),
('Anil Devi', '2013-04-12', 'male', false, 'Student', 0, 29, '4th', 84, NULL),
--------
('Ashok Kumar', '1975-10-15', 'male', false, 'Pharmacist', 30000, 30, 'Bachelors Degree', NULL, NULL),
('Sunita Kumar', '1980-08-20', 'female', false, 'Housewife', 0, 30, '10th', NULL, NULL),
('Priya Kumar', '2010-05-12', 'female', false, 'Student', 0, 30, '8th', 88, 87),
--------
('Ramesh Yadav', '1982-03-05', 'male', false, 'Milkman', 15000, 31, '5th', NULL, NULL),
('Kamla Yadav', '1985-12-10', 'female', false, 'Housewife', 0, 31, '5th', NULL, NULL),
('Ravi Yadav', '2012-07-08', 'male', false, 'Student', 0, 31, '6th', 91, 90),
('Ankit Yadav', '2015-02-19', 'male', false, 'Student', 0, 31, '3rd', 91, 90),
--------
('Mohan Lal', '1978-11-25', 'male', false, 'Vegetable Seller', 12000, 32, '5th', NULL, NULL),
('Shanti Lal', '1981-09-30', 'female', false, 'Housewife', 0, 32, '5th', NULL, NULL),
('Pooja Lal', '2008-05-14', 'female', false, NULL, 0, 32, NULL, 95, 94),
('Neha Lal', '2010-03-22', 'female', false, NULL, 0, 32, NULL, 95, 94),
('Ritika Lal', '2013-01-11', 'female', false, NULL, 0, 32, NULL, 95, 94),
--------
('Ravi Sharma', '1985-06-14', 'male', false, 'Grocery Shopkeeper', 20000, 33, '10th', NULL, NULL),
('Anita Sharma', '1988-09-05', 'female', false, 'Housewife', 0, 33, '10th', NULL, NULL), --100
--------
('Gopal Das', '1970-07-18', 'male', false, 'Sweet Shop Owner', 35000, 34, '8th', NULL, NULL),
('Sita Das', '1975-12-12', 'female', false, 'Housewife', 0, 34, '5th', NULL, NULL),
('Amit Das', '2000-09-01', 'male', false, 'Assistant', 10000, 34, '12th', 102, 101),
('Neetu Das', '2003-11-08', 'female', false, 'Student', 0, 34, 'Bachelors Degree', 102, 101),
('Sonu Das', '2007-02-20', 'male', false, 'Student', 0, 34, '11th', 102, 101),
--------
('Bharat Singh', '1980-08-25', 'male', false, 'Chappal-Wala', 15000, 35, '5th', NULL, NULL),
('Gita Singh', '1983-10-15', 'female', false, 'Housewife', 0, 35, '8th', NULL, NULL),
('Rohit Singh', '2011-12-10', 'male', false, NULL, 0, 35, '5th', 107, 106),
('Riya Singh', '2013-09-18', 'female', false, 'Student', 0, 35, '6th', 107, 106),
--------
('Manoj Gupta', '1985-01-22', 'male', false, 'Clothes Shopkeeper', 25000, 36, '10th', NULL, NULL),
('Neha Gupta', '1990-04-30', 'female', false, 'Housewife', 0, 36, '10th', NULL, NULL),
--------
('Dr. Suresh Mehta', '1975-02-14', 'male', false, 'Doctor', 120000, 37, 'MBBS', NULL, NULL),
('Dr. Priya Mehta', '1978-08-20', 'female', false, 'Doctor', 110000, 37, 'MBBS', NULL, NULL),
('Anjali Mehta', '2008-05-25', 'female', false, 'Student', 0, 37, '11th', 113, 112),
('Karan Mehta', '2013-10-14', 'male', false, 'Student', 0, 37, '6th', 113, 112),
--------
('Adv. Arjun Verma', '1980-07-30', 'male', false, 'Lawyer', 85000, 38, 'LLB', NULL, NULL),
('Shalini Verma', '1985-02-10', 'female', false, 'Teacher', 30000, 38, 'Bachelors Degree', NULL, NULL),
('Rohan Verma', '2015-12-12', 'male', false, 'Student', 0, 38, '4th', 117, 116),
--------
('Birju Kumar', '1968-04-05', 'male', false, 'Retired', 0, 39, NULL, NULL, NULL),
('Girja Kumar', '1998-10-14', 'female', false, 'Eatables Seller', 10000, 39, '5th', NULL, 119),
('Raj Kumar', '1995-07-07', 'male', false, 'Chauffer', 60000, 39, '10th', NULL, NULL),
('Govind Kumar', '2024-05-01', 'male', false, NULL, 0, 39, NULL, 120, 121);
-- Populate Land Table
INSERT INTO land (land_area, land_address) VALUES
(0.25, 'Near Main Market, Phulera'),
(1.10, 'Behind Primary School, Phulera'),
(1.30, 'Adjacent to Panchayat Bhavan, Phulera'),
(2.00, 'On Highway Road, Phulera'),
(1.50, 'Near Krishna Temple, Phulera'),
--------
(1.40, 'Next to Water Tank, Fakauli'),
(1.80, 'Close to Village Entry Gate, Fakauli'),
(0.75, 'Behind Village Market, Fakauli'),
--------
(1.60, 'Adjacent to High School, Lothal'),
(0.20, 'Near Post Office, Lothal'),
--------
(1.25, 'Near Village Square, Mahodiya'),
(1.50, 'Close to River, Mahodiya'),
(0.75, 'Behind Old Temple, Mahodiya'),
(0.40, 'Next to School, Mahodiya');
-- Populate Land Role Table
INSERT INTO land_role (citizen_id, land_id, role) VALUES
(49, 1, 'Owner'),
(63, 2, 'Owner'),
(52, 3, 'Owner'),
(7, 4, 'Owner'),
(18, 4, 'Caretaker');
-- Populate Agricultural Land Table
INSERT INTO agricultural_land (land_id, crop, season, seasonal_output, revenue, isOrganic) VALUES
(1, 'Rice', 'Kharif', 1500.50, 30000.00, true),
(3, 'Rice', 'Kharif', 1300.00, 26000.00, false),
(5, 'Wheat', 'Rabi', 2000.75, 40000.00, true),
(6, 'Wheat', 'Rabi', 1800.60, 36000.00, false),
(10, 'Maize', 'Kharif', 900.25, 18000.00, true);
-- Populate Panchayat Employees Table
INSERT INTO panchayat_employees (citizen_id, salary, role) VALUES
(54, 30000, 'Panchayat Secretary'),
(63, 50000, 'Panchayat Up-Pradhan'),
(41, 70000, 'Panchayat Pradhan');
-- Populate Assets Table
INSERT INTO assets (name, type, location, value, installment_date, isGovernmentOwned, owner_id) VALUES
('Street Light 1', 'Infrastructure', 'Phulera Main Road', 20000, '2023-04-15', true, NULL),
('Street Light 2', 'Infrastructure', 'Phulera Market Area', 18000, '2024-02-10', true, NULL),
('Street Light 3', 'Infrastructure', 'Fakauli Outer Road', 21000, '2022-06-20', true, NULL),
('Street Light 4', 'Infrastructure', 'Lothal Main Road', 22000, '2021-07-12', true, NULL),
-- Water Pumps (Infrastructure)
('Water Pump 1', 'Infrastructure', 'Phulera Village Center', 15000, '2020-08-05', true, NULL),
('Water Pump 2', 'Infrastructure', 'Phulera North Road', 14000, '2018-09-10', true, NULL),
('Water Pump 3', 'Infrastructure', 'Fakauli Village Square', 17000, '2019-10-25', true, NULL),
('Water Pump 4', 'Infrastructure', 'Lothal Central Park', 16000, '2023-11-15', true, NULL),
-- Schools (Education)
('Primary School 1', 'Education', 'Phulera Near Market', 35000, '2017-01-10', true, NULL),
('Primary School 2', 'Education', 'Fakauli Center', 33000, '2021-02-12', true, NULL),
('High School 1', 'Education', 'Lothal Outer Road', 50000, '2018-03-05', true, NULL),
('High School 2', 'Education', 'Mahodiya Village Square', 52000, '2022-04-08', true, NULL),
-- Hospitals (Healthcare)
('Health Center 1', 'Healthcare', 'Phulera South Road', 45000, '2020-05-20', true, NULL),
('Health Center 2', 'Healthcare', 'Fakauli East Side', 43000, '2016-06-25', true, NULL),
('Community Health Center', 'Healthcare', 'Lothal Old Village', 48000, '2022-07-18', true, NULL),
('Medical Center', 'Healthcare', 'Mahodiya Central Area', 47000, '2024-08-30', true, NULL),
-- Roads (Infrastructure)
('Road 1', 'Infrastructure', 'Phulera Outer Ring', 60000, '2019-09-15', true, NULL),
('Road 2', 'Infrastructure', 'Fakauli North Road', 58000, '2015-10-01', true, NULL),
('Road 3', 'Infrastructure', 'Lothal Main Road', 64000, '2023-11-10', true, NULL),
('Road 4', 'Infrastructure', 'Mahodiya New Market', 62000, '2021-12-05', true, NULL),
-- Additional assets for variety
('Public Toilet 1', 'Infrastructure', 'Phulera Bus Stop', 8000, '2018-05-25', true, NULL),
('Public Toilet 2', 'Infrastructure', 'Fakauli Park', 8200, '2019-07-01', true, NULL),
('Public Toilet 3', 'Infrastructure', 'Lothal Main Square', 7800, '2020-08-18', true, NULL),
('Public Toilet 4', 'Infrastructure', 'Mahodiya Central Park', 8500, '2021-09-23', true, NULL);
-- Populate Vaccinations Table with 8 records for citizen ids: 5, 11, 30, 62, 71, 93, 109, 115
INSERT INTO vaccinations (citizen_id, vaccine_type, date_administered) VALUES
(5, 'Tetanus', '2024-10-25'),
(16, 'Td', '2024-08-17'),
(30, 'Tetanus', '2024-08-17'),
(62, 'Tetanus', '2023-12-28'),
(71, 'Tetanus', '2023-12-28'),
(51, 'Td',  '2025-01-20'),
(93, 'Tetanus', '2023-12-28'),
(109, 'Tetanus', '2023-12-28'),
(115, 'Tetanus', '2023-12-28'),
(96, 'Td', '2024-08-17'),
(114, 'Td', '2024-08-17');  
INSERT INTO census_data (household_id, citizen_id, event_type, event_date)
SELECT household_id, citizen_id, 'Birth', dob
FROM citizens
WHERE dob > '1950-01-01';
INSERT INTO census_data (household_id, citizen_id, event_type, event_date) VALUES
(5, 25, 'Marriage', '2023-01-14'),
(36, 110, 'Marriage', '2012-12-22'),
(39, 120, 'Marriage', '2022-12-08'),
(29, 83, 'Divorce', '2010-04-13');