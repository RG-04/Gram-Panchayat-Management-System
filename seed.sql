-- Insert sample households
INSERT INTO Households (HouseholdID, Address) VALUES
(1, 'House No. 123, North Ward, Sundarpur'),
(2, 'House No. 456, South Ward, Sundarpur'),
(3, 'House No. 789, Riverside Ward, Chandanagar');

-- Insert sample citizens
INSERT INTO Citizen (Aadhaar, Name, DOB, MotherID, FatherID, Gender, Income, HouseholdID, Occupation, Phone) VALUES
('123456789012', 'Amit Patel', '1980-05-15', NULL, NULL, 'Male', 350000, 1, 'Farmer', '9876543213'),
('234567890123', 'Sunita Sharma', '1985-08-22', NULL, NULL, 'Female', 280000, 2, 'Teacher', '9876543214'),
('345678901234', 'Mohamed Ali', '1975-02-10', NULL, NULL, 'Male', 320000, 3, 'Shopkeeper', '9876543215'),
('456789012345', 'Raj Kumar', '1982-11-05', NULL, NULL, 'Male', 420000, 1, 'Government Employee', '9876543216'),
('567890123456', 'Priya Singh', '1988-04-18', NULL, NULL, 'Female', 450000, 2, 'Government Employee', '9876543217');

-- Insert monitors
INSERT INTO Monitors (MonitorID, Name) VALUES
(1, 'Shrikant Verma'),
(2, 'Anjali Desai');

-- Insert users (password: pwd)
-- Hash: f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b
INSERT INTO "User" (CitizenID, MonitorID, username, password, auth, salt) VALUES
('123456789012', NULL, 'citizen1', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'citizen', 'salt123'),
('234567890123', NULL, 'citizen2', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'citizen', 'salt123'),
('345678901234', NULL, 'citizen3', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'citizen', 'salt123'),
('456789012345', NULL, 'employee1', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'employee', 'salt123'),
('567890123456', NULL, 'employee2', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'employee', 'salt123'),
(NULL, 1, 'monitor1', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'monitor', 'salt123'),
(NULL, 2, 'monitor2', 'f55559344d26d83676c3183f75a9445009b296158aaa20ec4375b6bb5a9db35b', 'monitor', 'salt123');

-- Insert EmployeeCitizens
INSERT INTO EmployeeCitizens (EmployeeID, CitizenID, StartDate, TermDuration) VALUES
(1, '456789012345', '2020-06-01', 36),
(2, '567890123456', '2021-03-15', 36);

-- Insert schools
INSERT INTO Schools (SchoolID, Name, Capacity) VALUES
(1, 'Sundarpur Primary School', 500),
(2, 'Chandanagar High School', 800);

-- Insert hospitals
INSERT INTO Hospitals (HospitallD, Name, Address) VALUES
(1, 'Sundarpur Primary Health Center', 'Near Bus Stand, Sundarpur'),
(2, 'Chandanagar General Hospital', 'Main Road, Chandanagar');

-- Insert schemes
INSERT INTO Schemes (SchemeID, Description) VALUES
(1, 'Rural Housing Scheme'),
(2, 'Farmers Subsidy Program'),
(3, 'Education Scholarship');

-- Insert land records
INSERT INTO Land (LandID, OwnerID, Size, Location) VALUES
(1, '123456789012', 2.5, 'North of Sundarpur'),
(2, '234567890123', 1.5, 'East of Sundarpur'),
(3, '345678901234', 3.0, 'Riverside, Chandanagar');

-- Insert certificates
INSERT INTO Certificates (Type, CitizenID, DateIssued, File) VALUES
('Birth Certificate', '123456789012', '1980-06-10', NULL),
('Income Certificate', '234567890123', '2023-01-15', NULL),
('Land Ownership', '345678901234', '2022-05-20', NULL);

-- Insert forms
INSERT INTO Forms (FormID, SchemeID, Fee) VALUES
(1, 1, 100.00),
(2, 2, 50.00),
(3, 3, 75.00);

-- Insert scheme enrollments
INSERT INTO SchemeEnrollment (SchemeID, CitizenID, Date) VALUES
(1, '123456789012', '2023-02-10'),
(2, '123456789012', '2023-03-15'),
(3, '234567890123', '2023-01-05');

-- Insert school attendance records
INSERT INTO AttendsSchool (CitizenID, SchoolID, Qualification, PassDate) VALUES
('123456789012', 1, 'Primary', '1990-04-15'),
('234567890123', 2, 'High School', '2000-03-20');