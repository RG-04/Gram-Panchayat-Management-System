DROP TABLE IF EXISTS AttendsSchool CASCADE;
DROP TABLE IF EXISTS SchemeEnrollment CASCADE;
DROP TABLE IF EXISTS EmployeeCitizens CASCADE;
DROP TABLE IF EXISTS Certificates CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS Schemes CASCADE;
DROP TABLE IF EXISTS LandCrop CASCADE;
DROP TABLE IF EXISTS Land CASCADE;
DROP TABLE IF EXISTS Crop CASCADE;
DROP TABLE IF EXISTS SchoolAccount CASCADE;
DROP TABLE IF EXISTS Schools CASCADE;
DROP TABLE IF EXISTS HospitalAccount CASCADE;
DROP TABLE IF EXISTS Hospitals CASCADE;
DROP TABLE IF EXISTS Monitors CASCADE;
DROP TABLE IF EXISTS Citizen CASCADE;
DROP TABLE IF EXISTS Households CASCADE;
DROP TABLE IF EXISTS AssetSurveys CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS EnvironmentalData CASCADE;


CREATE TABLE Households (
    HouseholdID SERIAL PRIMARY KEY,
    Address TEXT NOT NULL,
    Income DECIMAL(12, 2)
);

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
    MigrationStatus VARCHAR(50) CHECK (MigrationStatus IN ('Native', 'Immigrant')),
    ResidenceSince DATE,
    Phone VARCHAR(20)
);

CREATE TABLE Monitors (
    MonitorID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);

CREATE TABLE users (
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

CREATE TABLE EmployeeCitizens (
    EmployeeID SERIAL PRIMARY KEY,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    StartDate DATE NOT NULL,
    TermDuration INTEGER, -- in months
    Role VARCHAR(50)
);

CREATE TABLE Schools (
    SchoolID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Capacity INTEGER,
    Income INTEGER
);

CREATE TABLE SchoolAccount (
    SchoolID INTEGER REFERENCES Schools(SchoolID),
    AnnualIncome DECIMAL(15, 2),
    AnnualExpenditure DECIMAL(15, 2),
    BudgetYear INTEGER,
    PRIMARY KEY (SchoolID, BudgetYear)
);

CREATE TABLE Hospitals (
    HospitalID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Address TEXT,
    Beds INTEGER
);

CREATE TABLE HospitalAccount (
    HospitalID INTEGER REFERENCES Hospitals(HospitalID),
    AnnualIncome DECIMAL(15, 2),
    AnnualExpenditure DECIMAL(15, 2),
    BudgetYear INTEGER,
    PRIMARY KEY (HospitalID, BudgetYear)
);

CREATE TABLE Schemes (
    SchemeID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT NOT NULL,
    Type VARCHAR(100),
    AllocatedBudget DECIMAL(15, 2),
    TargetBeneficiaries INTEGER,
    BudgetYear INTEGER
);

CREATE TABLE Land (
    LandID SERIAL PRIMARY KEY,
    OwnerID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    Size DECIMAL(10, 2),
    Location TEXT
);

CREATE TABLE Crop (
    CropID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(100)
);

CREATE TABLE LandCrop (
    LandID INTEGER REFERENCES Land(LandID),
    CropID INTEGER REFERENCES Crop(CropID),
    Area DECIMAL(10, 2), -- in acres
    AnnualYield DECIMAL(10, 2), -- in kg
    isOrganic BOOLEAN,
    IrrigationMethod VARCHAR(100),
    WaterUsage DECIMAL(10, 2), -- in liters per acre
    PRIMARY KEY (LandID, CropID)
);

CREATE TABLE Certificates (
    Category VARCHAR(100) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    DateIssued DATE NOT NULL,
    File BYTEA, -- Binary data for the file
    PRIMARY KEY (Category, Name, CitizenID)
);

CREATE TABLE SchemeEnrollment (
    SchemeID INTEGER,
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    Date DATE NOT NULL,
    PRIMARY KEY (SchemeID, CitizenID),
    EnrollmentStatus VARCHAR(50) DEFAULT 'Active' CHECK (EnrollmentStatus IN ('Active', 'Inactive', 'Pending')),
    BenefitsReceived DECIMAL(15, 2) DEFAULT 0,
    LastBenefitDate DATE,
    FOREIGN KEY (SchemeID) REFERENCES Schemes(SchemeID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE AttendsSchool (
    CitizenID VARCHAR(16) REFERENCES Citizen(Aadhaar),
    SchoolID INTEGER REFERENCES Schools(SchoolID),
    Qualification VARCHAR(100),
    PassDate DATE,
    PRIMARY KEY (CitizenID, SchoolID, Qualification)
);

CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(100) NOT NULL,
    InstallationDate DATE,
    LastSurveyedDate DATE,
    Location TEXT
);

CREATE TABLE AssetSurveys (
    asset_id INTEGER REFERENCES assets(asset_id),
    SurveyDate DATE,
    SurveyorID INTEGER REFERENCES EmployeeCitizens(EmployeeID),
    SurveyData TEXT,
    PRIMARY KEY (asset_id, SurveyDate)
);

CREATE TABLE EnvironmentalData (
    RecordID SERIAL PRIMARY KEY,
    TimeFrame DATE NOT NULL,
    AirQuality DECIMAL(5, 2),  
    RainfallAmount DECIMAL(8, 2),  
    GroundwaterLevel DECIMAL(8, 2),  
    ForestCover DECIMAL(8, 2), 
    WaterBodyConditions TEXT,
    RecordedBy INTEGER REFERENCES EmployeeCitizens(EmployeeID),
    Notes TEXT
);


DROP TRIGGER IF EXISTS trigger_update_last_surveyed ON AssetSurveys;
DROP FUNCTION IF EXISTS update_last_surveyed();

CREATE OR REPLACE FUNCTION update_last_surveyed()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE assets
    SET LastSurveyedDate = (
        SELECT COALESCE(MAX(SurveyDate), InstallationDate)
        FROM AssetSurveys
        WHERE AssetSurveys.asset_id = assets.asset_id
    );
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_last_surveyed
AFTER INSERT OR UPDATE OR DELETE
ON AssetSurveys
FOR EACH STATEMENT
EXECUTE FUNCTION update_last_surveyed();


DROP TRIGGER IF EXISTS trigger_update_household_income ON Citizen;
DROP FUNCTION IF EXISTS update_household_income();

CREATE OR REPLACE FUNCTION update_household_income()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Households
    SET Income = (SELECT COALESCE(SUM(Income), 0) FROM Citizen WHERE HouseholdID = NEW.HouseholdID)
    WHERE HouseholdID = NEW.HouseholdID;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_household_income
AFTER INSERT OR UPDATE OR DELETE ON Citizen
FOR EACH ROW
EXECUTE FUNCTION update_household_income();

