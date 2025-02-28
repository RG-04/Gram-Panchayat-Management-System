-- Insert sample households
INSERT INTO Households (HouseholdID, Address) VALUES
(1, 'House No. 123, North Ward, Sundarpur'),
(2, 'House No. 456, South Ward, Sundarpur'),
(3, 'House No. 789, Riverside Ward, Chandanagar'),
(4, 'House No. 101, East Ward, Sundarpur'),
(5, 'House No. 202, West Ward, Chandanagar'),
(6, 'House No. 303, Central Ward, Sundarpur'),
(7, 'House No. 404, North Ward, Chandanagar'),
(8, 'House No. 505, South Ward, Sundarpur'),
(9, 'House No. 606, Riverside Ward, Chandanagar'),
(10, 'House No. 707, East Ward, Sundarpur');

-- Insert sample citizens
INSERT INTO Citizen (Aadhaar, Name, DOB, MotherID, FatherID, Gender, Income, HouseholdID, Occupation, Phone) VALUES
('123456789012', 'Amit Patel', '1980-05-15', NULL, NULL, 'Male', 350000, 1, 'Farmer', '9876543213'),
('234567890123', 'Sunita Sharma', '1985-08-22', NULL, NULL, 'Female', 280000, 2, 'Teacher', '9876543214'),
('345678901234', 'Mohamed Ali', '1975-02-10', NULL, NULL, 'Male', 320000, 3, 'Shopkeeper', '9876543215'),
('456789012345', 'Raj Kumar', '1982-11-05', NULL, NULL, 'Male', 420000, 1, 'Government Employee', '9876543216'),
('567890123456', 'Priya Singh', '1988-04-18', NULL, NULL, 'Female', 450000, 2, 'Government Employee', '9876543217'),
-- Parents
('678901234567', 'Lakshmi Devi', '1979-06-25', NULL, NULL, 'Female', 290000, 4, 'Tailor', '9876543218'),
('789012345678', 'Ramesh Kumar', '1977-09-12', NULL, NULL, 'Male', 310000, 4, 'Driver', '9876543219'),
('890123456789', 'Anita Verma', '1983-01-30', NULL, NULL, 'Female', 275000, 5, 'Nurse', '9876543220'),
('901234567890', 'Suresh Patel', '1981-07-08', NULL, NULL, 'Male', 330000, 5, 'Electrician', '9876543221'),

-- School-age children (with parent references)
('012345678901', 'Ravi Kumar', '2010-03-17', '678901234567', '789012345678', 'Male', 0, 4, 'Student', NULL),
('123456789013', 'Meena Kumar', '2012-11-05', '678901234567', '789012345678', 'Female', 0, 4, 'Student', NULL),
('234567890124', 'Ajay Verma', '2013-08-22', '890123456789', '901234567890', 'Male', 0, 5, 'Student', NULL),
('345678901235', 'Neha Verma', '2009-04-10', '890123456789', '901234567890', 'Female', 0, 5, 'Student', NULL),

-- Teenagers/Young adults (some still in school, some recently graduated)
('456789012346', 'Vikram Singh', '2005-12-03', NULL, NULL, 'Male', 15000, 6, 'Student', '9876543222'),
('567890123457', 'Pooja Gupta', '2007-05-19', NULL, NULL, 'Female', 0, 7, 'Student', '9876543223'),
('678901234568', 'Arjun Reddy', '2006-09-27', NULL, NULL, 'Male', 0, 8, 'Student', NULL),
('789012345679', 'Kavita Rao', '2004-02-14', NULL, NULL, 'Female', 18000, 9, 'Part-time Clerk', '9876543224');


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
INSERT INTO Schools (SchoolID, Name, Capacity, Income) VALUES
(1, 'Sundarpur Primary School', 500, 5000000),
(2, 'Chandanagar High School', 800, 3000000);

-- Insert hospitals
INSERT INTO Hospitals (HospitalID, Name, Address, Beds) VALUES
(1, 'Sundarpur Primary Health Center', 'Near Bus Stand, Sundarpur', 50),
(2, 'Chandanagar General Hospital', 'Main Road, Chandanagar', 25);

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
INSERT INTO Certificates (Category, Name, CitizenID, DateIssued, File) VALUES
-- Existing certificates from your example
('Education', 'Primary School Certificate', '123456789012', '1990-04-15', NULL),
('Education', 'High School Certificate', '234567890123', '2000-03-20', NULL),
('Vaccination', 'COVID-19', '123456789012', '2022-05-10', NULL),
('Vaccination', 'COVID-19', '234567890123', '2022-05-10', NULL),
('Vaccination', 'Cholera', '345678901234', '2022-05-10', NULL),
('Vaccination', 'Cholera', '234567890123', '2022-05-10', NULL),

-- Additional vaccination certificates (3 diseases only)
-- COVID-19 Vaccination
('Vaccination', 'COVID-19', '345678901234', '2021-05-15', NULL),
('Vaccination', 'COVID-19', '456789012345', '2021-04-10', NULL),
('Vaccination', 'COVID-19', '567890123456', '2021-05-20', NULL),
('Vaccination', 'COVID-19', '678901234567', '2021-06-05', NULL),
('Vaccination', 'COVID-19', '789012345678', '2021-05-18', NULL),
('Vaccination', 'COVID-19', '890123456789', '2021-04-30', NULL),

-- Cholera Vaccination
('Vaccination', 'Cholera', '123456789012', '2022-03-10', NULL),
('Vaccination', 'Cholera', '456789012345', '2022-04-05', NULL),
('Vaccination', 'Cholera', '567890123456', '2022-03-15', NULL),
('Vaccination', 'Cholera', '789012345678', '2022-04-12', NULL),

-- Typhoid Vaccination
('Vaccination', 'Typhoid', '123456789012', '2020-06-15', NULL),
('Vaccination', 'Typhoid', '234567890123', '2020-07-22', NULL),
('Vaccination', 'Typhoid', '345678901234', '2020-06-10', NULL),
('Vaccination', 'Typhoid', '456789012345', '2020-08-05', NULL),
('Vaccination', 'Typhoid', '567890123456', '2020-07-18', NULL),
('Vaccination', 'Typhoid', '678901234567', '2020-06-25', NULL),

-- Additional simplified education certificates
-- Primary School
('Education', 'Primary School Certificate', '345678901234', '1985-03-25', NULL),
('Education', 'Primary School Certificate', '789012345678', '1988-03-30', NULL),

-- Middle School
('Education', 'Middle School Certificate', '789012345678', '1992-03-30', NULL),

-- High School
('Education', 'High School Certificate', '456789012345', '1998-04-10', NULL),
('Education', 'High School Certificate', '789012345679', '2022-03-15', NULL),

-- Higher Education
('Education', 'Bachelor Degree Certificate', '567890123456', '2010-05-22', NULL),
('Education', 'Diploma Certificate', '890123456789', '2002-04-18', NULL);

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
('234567890123', 2, 'High School', '2000-03-20'),
-- Currently studying (NULL PassDate)
('012345678901', 1, 'Primary', NULL),           -- Ravi - primary school student
('123456789013', 1, 'Primary', NULL),           -- Meena - primary school student
('234567890124', 1, 'Primary', NULL),           -- Ajay - primary school student
('345678901235', 2, 'Middle School', NULL),     -- Neha - middle school student
('456789012346', 2, 'High School', NULL),       -- Vikram - high school student
('567890123457', 2, 'Middle School', NULL),     -- Pooja - middle school student
('678901234568', 2, 'High School', NULL),       -- Arjun - high school student

-- Completed education (with PassDate)
('789012345679', 2, 'High School', '2022-03-15'),   -- Kavita - recently graduated high school
('456789012345', 2, 'High School', '1998-04-10'),   -- Raj Kumar - adult with high school education
('567890123456', 2, 'Bachelor Degree', '2010-05-22'), -- Priya Singh - adult with bachelor degree
('345678901234', 1, 'Primary', '1985-03-25'),       -- Mohamed Ali - completed primary education
('890123456789', 2, 'Diploma', '2002-04-18'),       -- Anita Verma - has diploma qualification
('789012345678', 1, 'Middle School', '1992-03-30'); -- Ramesh Kumar - completed middle school