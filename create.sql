-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS "Attends-School";
DROP TABLE IF EXISTS "Scheme-Enrollment";
DROP TABLE IF EXISTS "Employee-Citizens";
DROP TABLE IF EXISTS Certificates;
DROP TABLE IF EXISTS Forms;
DROP TABLE IF EXISTS "User";
DROP TABLE IF EXISTS Schemes;
DROP TABLE IF EXISTS Land;
DROP TABLE IF EXISTS Schools;
DROP TABLE IF EXISTS Hospitals;
DROP TABLE IF EXISTS Monitors;
DROP TABLE IF EXISTS Citizen;
DROP TABLE IF EXISTS Households;

-- Create Households table
CREATE TABLE Households (
    HouseholdID SERIAL PRIMARY KEY,
    Address TEXT NOT NULL
);

-- Create Citizen table
CREATE TABLE Citizen (
    Aadhaar VARCHAR(16) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    DOB DATE,
    MotherID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    FatherID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    Gender VARCHAR(10),
    Income DECIMAL(12, 2),
    HouseholdID INTEGER REFERENCES Households(HouseholdID),
    Occupation VARCHAR(100),
    Phone VARCHAR(20)
);

-- Create Monitors table
CREATE TABLE Monitors (
    MonitorID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);

-- Create User table
CREATE TABLE "User" (
    UserID SERIAL PRIMARY KEY,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    MonitorID INTEGER REFERENCES Monitors(MonitorID),
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    auth VARCHAR(20) CHECK (auth IN ('citizen', 'employee', 'monitor')),
    salt VARCHAR(256) NOT NULL,
    CONSTRAINT one_id_not_null CHECK (
        (CitizenID IS NULL AND MonitorID IS NOT NULL) OR
        (CitizenID IS NOT NULL AND MonitorID IS NULL)
    )
);

-- Create Employee-Citizens table
CREATE TABLE "Employee-Citizens" (
    EmployeeID SERIAL PRIMARY KEY,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    "Start Date" DATE NOT NULL,
    "Term-Duration" INTEGER -- in months
);

-- Create Schools table
CREATE TABLE Schools (
    SchoolID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Capacity INTEGER
);

-- Create Hospitals table
CREATE TABLE Hospitals (
    HospitallD SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Address TEXT
);

-- Create Schemes table
CREATE TABLE Schemes (
    SchemeID SERIAL PRIMARY KEY,
    Description TEXT NOT NULL
);

-- Create Land table
CREATE TABLE Land (
    LandID SERIAL PRIMARY KEY,
    OwnerID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    Size DECIMAL(10, 2),
    Location TEXT
);

-- Create Certificates table
CREATE TABLE Certificates (
    CertificateID SERIAL PRIMARY KEY,
    Type VARCHAR(50) NOT NULL,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    DateIssued DATE NOT NULL,
    File BYTEA -- Binary data for the file
);

-- Create Forms table
CREATE TABLE Forms (
    FormID SERIAL PRIMARY KEY,
    SchemeID INTEGER REFERENCES Schemes(SchemeID),
    Fee DECIMAL(10, 2)
);

-- Create Scheme-Enrollment table
CREATE TABLE "Scheme-Enrollment" (
    EnrollmentID SERIAL PRIMARY KEY,
    SchemeID INTEGER REFERENCES Schemes(SchemeID),
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    Date DATE NOT NULL
);

-- Create Attends-School table
CREATE TABLE "Attends-School" (
    AttendanceID SERIAL PRIMARY KEY,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    SchoolID INTEGER REFERENCES Schools(SchoolID),
    Qualification VARCHAR(100),
    "Pass Date" DATE
);

-- Create indexes for performance
CREATE INDEX idx_citizen_household ON Citizen(HouseholdID);
CREATE INDEX idx_user_citizen ON "User"(CitizenID);
CREATE INDEX idx_user_monitor ON "User"(MonitorID);
CREATE INDEX idx_employee_citizen ON "Employee-Citizens"(CitizenID);
CREATE INDEX idx_land_owner ON Land(OwnerID);
CREATE INDEX idx_certificates_citizen ON Certificates(CitizenID);
CREATE INDEX idx_scheme_enrollment_citizen ON "Scheme-Enrollment"(CitizenID);
CREATE INDEX idx_scheme_enrollment_scheme ON "Scheme-Enrollment"(SchemeID);
CREATE INDEX idx_attends_school_citizen ON "Attends-School"(CitizenID);
CREATE INDEX idx_attends_school_school ON "Attends-School"(SchoolID);