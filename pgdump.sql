--
-- PostgreSQL database dump
--

-- Dumped from database version 13.18
-- Dumped by pg_dump version 16.6 (Ubuntu 16.6-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: update_household_income(); Type: FUNCTION; Schema: public; Owner: 22CS30045
--

CREATE FUNCTION public.update_household_income() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE Households
    SET Income = (SELECT COALESCE(SUM(Income), 0) FROM Citizen WHERE HouseholdID = NEW.HouseholdID)
    WHERE HouseholdID = NEW.HouseholdID;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_household_income() OWNER TO "22CS30045";

--
-- Name: update_last_surveyed(); Type: FUNCTION; Schema: public; Owner: 22CS30045
--

CREATE FUNCTION public.update_last_surveyed() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update LastSurveyedDate for all assets based on the most recent survey, or default to InstallationDate
    UPDATE assets
    SET LastSurveyedDate = (
        SELECT COALESCE(MAX(SurveyDate), InstallationDate)
        FROM AssetSurveys
        WHERE AssetSurveys.asset_id = assets.asset_id
    );
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.update_last_surveyed() OWNER TO "22CS30045";

--
-- Name: update_modified_column(); Type: FUNCTION; Schema: public; Owner: 22CS30045
--

CREATE FUNCTION public.update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_modified_column() OWNER TO "22CS30045";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.assets (
    asset_id integer NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(100) NOT NULL,
    installationdate date,
    lastsurveyeddate date,
    location text
);


ALTER TABLE public.assets OWNER TO "22CS30045";

--
-- Name: assets_asset_id_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.assets_asset_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assets_asset_id_seq OWNER TO "22CS30045";

--
-- Name: assets_asset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.assets_asset_id_seq OWNED BY public.assets.asset_id;


--
-- Name: assetsurveys; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.assetsurveys (
    asset_id integer NOT NULL,
    surveydate date NOT NULL,
    surveyorid integer,
    surveydata text
);


ALTER TABLE public.assetsurveys OWNER TO "22CS30045";

--
-- Name: attendsschool; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.attendsschool (
    citizenid character varying(16) NOT NULL,
    schoolid integer NOT NULL,
    qualification character varying(100) NOT NULL,
    passdate date
);


ALTER TABLE public.attendsschool OWNER TO "22CS30045";

--
-- Name: certificates; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.certificates (
    category character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    citizenid character varying(16) NOT NULL,
    dateissued date NOT NULL,
    file bytea
);


ALTER TABLE public.certificates OWNER TO "22CS30045";

--
-- Name: citizen; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.citizen (
    aadhaar character varying(16) NOT NULL,
    name character varying(100) NOT NULL,
    dob date,
    motherid character varying(16),
    fatherid character varying(16),
    gender character varying(10),
    income numeric(12,2),
    householdid integer,
    occupation character varying(100),
    migrationstatus character varying(50),
    residencesince date,
    phone character varying(20),
    CONSTRAINT citizen_migrationstatus_check CHECK (((migrationstatus)::text = ANY ((ARRAY['Native'::character varying, 'Immigrant'::character varying])::text[])))
);


ALTER TABLE public.citizen OWNER TO "22CS30045";

--
-- Name: crop; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.crop (
    cropid integer NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(100)
);


ALTER TABLE public.crop OWNER TO "22CS30045";

--
-- Name: crop_cropid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.crop_cropid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.crop_cropid_seq OWNER TO "22CS30045";

--
-- Name: crop_cropid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.crop_cropid_seq OWNED BY public.crop.cropid;


--
-- Name: employeecitizens; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.employeecitizens (
    employeeid integer NOT NULL,
    citizenid character varying(16),
    startdate date NOT NULL,
    termduration integer,
    role character varying(50)
);


ALTER TABLE public.employeecitizens OWNER TO "22CS30045";

--
-- Name: employeecitizens_employeeid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.employeecitizens_employeeid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employeecitizens_employeeid_seq OWNER TO "22CS30045";

--
-- Name: employeecitizens_employeeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.employeecitizens_employeeid_seq OWNED BY public.employeecitizens.employeeid;


--
-- Name: environmentaldata; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.environmentaldata (
    recordid integer NOT NULL,
    timeframe date NOT NULL,
    airquality numeric(5,2),
    rainfallamount numeric(8,2),
    groundwaterlevel numeric(8,2),
    forestcover numeric(8,2),
    waterbodyconditions text,
    recordedby integer,
    notes text
);


ALTER TABLE public.environmentaldata OWNER TO "22CS30045";

--
-- Name: environmentaldata_recordid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.environmentaldata_recordid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.environmentaldata_recordid_seq OWNER TO "22CS30045";

--
-- Name: environmentaldata_recordid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.environmentaldata_recordid_seq OWNED BY public.environmentaldata.recordid;


--
-- Name: hospitalaccount; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.hospitalaccount (
    hospitalid integer NOT NULL,
    annualincome numeric(15,2),
    annualexpenditure numeric(15,2),
    budgetyear integer NOT NULL
);


ALTER TABLE public.hospitalaccount OWNER TO "22CS30045";

--
-- Name: hospitals; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.hospitals (
    hospitalid integer NOT NULL,
    name character varying(100) NOT NULL,
    address text,
    beds integer
);


ALTER TABLE public.hospitals OWNER TO "22CS30045";

--
-- Name: hospitals_hospitalid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.hospitals_hospitalid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hospitals_hospitalid_seq OWNER TO "22CS30045";

--
-- Name: hospitals_hospitalid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.hospitals_hospitalid_seq OWNED BY public.hospitals.hospitalid;


--
-- Name: households; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.households (
    householdid integer NOT NULL,
    address text NOT NULL,
    income numeric(12,2)
);


ALTER TABLE public.households OWNER TO "22CS30045";

--
-- Name: households_householdid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.households_householdid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.households_householdid_seq OWNER TO "22CS30045";

--
-- Name: households_householdid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.households_householdid_seq OWNED BY public.households.householdid;


--
-- Name: land; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.land (
    landid integer NOT NULL,
    ownerid character varying(16),
    size numeric(10,2),
    location text
);


ALTER TABLE public.land OWNER TO "22CS30045";

--
-- Name: land_landid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.land_landid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.land_landid_seq OWNER TO "22CS30045";

--
-- Name: land_landid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.land_landid_seq OWNED BY public.land.landid;


--
-- Name: landcrop; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.landcrop (
    landid integer NOT NULL,
    cropid integer NOT NULL,
    area numeric(10,2),
    annualyield numeric(10,2),
    isorganic boolean,
    irrigationmethod character varying(100),
    waterusage numeric(10,2)
);


ALTER TABLE public.landcrop OWNER TO "22CS30045";

--
-- Name: monitors; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.monitors (
    monitorid integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.monitors OWNER TO "22CS30045";

--
-- Name: monitors_monitorid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.monitors_monitorid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monitors_monitorid_seq OWNER TO "22CS30045";

--
-- Name: monitors_monitorid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.monitors_monitorid_seq OWNED BY public.monitors.monitorid;


--
-- Name: schemeenrollment; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.schemeenrollment (
    schemeid integer NOT NULL,
    citizenid character varying(16) NOT NULL,
    date date NOT NULL,
    enrollmentstatus character varying(50) DEFAULT 'Active'::character varying,
    benefitsreceived numeric(15,2) DEFAULT 0,
    lastbenefitdate date,
    CONSTRAINT schemeenrollment_enrollmentstatus_check CHECK (((enrollmentstatus)::text = ANY ((ARRAY['Active'::character varying, 'Inactive'::character varying, 'Pending'::character varying])::text[])))
);


ALTER TABLE public.schemeenrollment OWNER TO "22CS30045";

--
-- Name: schemes; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.schemes (
    schemeid integer NOT NULL,
    name character varying(100) NOT NULL,
    description text NOT NULL,
    type character varying(100),
    allocatedbudget numeric(15,2),
    targetbeneficiaries integer,
    budgetyear integer
);


ALTER TABLE public.schemes OWNER TO "22CS30045";

--
-- Name: schemes_schemeid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.schemes_schemeid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schemes_schemeid_seq OWNER TO "22CS30045";

--
-- Name: schemes_schemeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.schemes_schemeid_seq OWNED BY public.schemes.schemeid;


--
-- Name: schoolaccount; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.schoolaccount (
    schoolid integer NOT NULL,
    annualincome numeric(15,2),
    annualexpenditure numeric(15,2),
    budgetyear integer NOT NULL
);


ALTER TABLE public.schoolaccount OWNER TO "22CS30045";

--
-- Name: schools; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.schools (
    schoolid integer NOT NULL,
    name character varying(100) NOT NULL,
    capacity integer,
    income integer
);


ALTER TABLE public.schools OWNER TO "22CS30045";

--
-- Name: schools_schoolid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.schools_schoolid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schools_schoolid_seq OWNER TO "22CS30045";

--
-- Name: schools_schoolid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.schools_schoolid_seq OWNED BY public.schools.schoolid;


--
-- Name: users; Type: TABLE; Schema: public; Owner: 22CS30045
--

CREATE TABLE public.users (
    userid integer NOT NULL,
    citizenid character varying(16),
    monitorid integer,
    username character varying(64) NOT NULL,
    password character varying(256) NOT NULL,
    auth character varying(20),
    salt character varying(256) NOT NULL,
    CONSTRAINT one_id_not_null CHECK ((((citizenid IS NULL) AND (monitorid IS NOT NULL)) OR ((citizenid IS NOT NULL) AND (monitorid IS NULL)))),
    CONSTRAINT users_auth_check CHECK (((auth)::text = ANY ((ARRAY['citizen'::character varying, 'employee'::character varying, 'monitor'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO "22CS30045";

--
-- Name: users_userid_seq; Type: SEQUENCE; Schema: public; Owner: 22CS30045
--

CREATE SEQUENCE public.users_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_userid_seq OWNER TO "22CS30045";

--
-- Name: users_userid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: 22CS30045
--

ALTER SEQUENCE public.users_userid_seq OWNED BY public.users.userid;


--
-- Name: assets asset_id; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.assets ALTER COLUMN asset_id SET DEFAULT nextval('public.assets_asset_id_seq'::regclass);


--
-- Name: crop cropid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.crop ALTER COLUMN cropid SET DEFAULT nextval('public.crop_cropid_seq'::regclass);


--
-- Name: employeecitizens employeeid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.employeecitizens ALTER COLUMN employeeid SET DEFAULT nextval('public.employeecitizens_employeeid_seq'::regclass);


--
-- Name: environmentaldata recordid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.environmentaldata ALTER COLUMN recordid SET DEFAULT nextval('public.environmentaldata_recordid_seq'::regclass);


--
-- Name: hospitals hospitalid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.hospitals ALTER COLUMN hospitalid SET DEFAULT nextval('public.hospitals_hospitalid_seq'::regclass);


--
-- Name: households householdid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.households ALTER COLUMN householdid SET DEFAULT nextval('public.households_householdid_seq'::regclass);


--
-- Name: land landid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.land ALTER COLUMN landid SET DEFAULT nextval('public.land_landid_seq'::regclass);


--
-- Name: monitors monitorid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.monitors ALTER COLUMN monitorid SET DEFAULT nextval('public.monitors_monitorid_seq'::regclass);


--
-- Name: schemes schemeid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schemes ALTER COLUMN schemeid SET DEFAULT nextval('public.schemes_schemeid_seq'::regclass);


--
-- Name: schools schoolid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schools ALTER COLUMN schoolid SET DEFAULT nextval('public.schools_schoolid_seq'::regclass);


--
-- Name: users userid; Type: DEFAULT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.users ALTER COLUMN userid SET DEFAULT nextval('public.users_userid_seq'::regclass);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (asset_id);


--
-- Name: assetsurveys assetsurveys_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.assetsurveys
    ADD CONSTRAINT assetsurveys_pkey PRIMARY KEY (asset_id, surveydate);


--
-- Name: attendsschool attendsschool_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.attendsschool
    ADD CONSTRAINT attendsschool_pkey PRIMARY KEY (citizenid, schoolid, qualification);


--
-- Name: certificates certificates_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.certificates
    ADD CONSTRAINT certificates_pkey PRIMARY KEY (category, name, citizenid);


--
-- Name: citizen citizen_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.citizen
    ADD CONSTRAINT citizen_pkey PRIMARY KEY (aadhaar);


--
-- Name: crop crop_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.crop
    ADD CONSTRAINT crop_pkey PRIMARY KEY (cropid);


--
-- Name: employeecitizens employeecitizens_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.employeecitizens
    ADD CONSTRAINT employeecitizens_pkey PRIMARY KEY (employeeid);


--
-- Name: environmentaldata environmentaldata_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.environmentaldata
    ADD CONSTRAINT environmentaldata_pkey PRIMARY KEY (recordid);


--
-- Name: hospitalaccount hospitalaccount_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.hospitalaccount
    ADD CONSTRAINT hospitalaccount_pkey PRIMARY KEY (hospitalid, budgetyear);


--
-- Name: hospitals hospitals_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.hospitals
    ADD CONSTRAINT hospitals_pkey PRIMARY KEY (hospitalid);


--
-- Name: households households_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.households
    ADD CONSTRAINT households_pkey PRIMARY KEY (householdid);


--
-- Name: land land_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.land
    ADD CONSTRAINT land_pkey PRIMARY KEY (landid);


--
-- Name: landcrop landcrop_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.landcrop
    ADD CONSTRAINT landcrop_pkey PRIMARY KEY (landid, cropid);


--
-- Name: monitors monitors_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.monitors
    ADD CONSTRAINT monitors_pkey PRIMARY KEY (monitorid);


--
-- Name: schemeenrollment schemeenrollment_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schemeenrollment
    ADD CONSTRAINT schemeenrollment_pkey PRIMARY KEY (schemeid, citizenid);


--
-- Name: schemes schemes_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schemes
    ADD CONSTRAINT schemes_pkey PRIMARY KEY (schemeid);


--
-- Name: schoolaccount schoolaccount_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schoolaccount
    ADD CONSTRAINT schoolaccount_pkey PRIMARY KEY (schoolid, budgetyear);


--
-- Name: schools schools_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schools
    ADD CONSTRAINT schools_pkey PRIMARY KEY (schoolid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: citizen trigger_update_household_income; Type: TRIGGER; Schema: public; Owner: 22CS30045
--

CREATE TRIGGER trigger_update_household_income AFTER INSERT OR DELETE OR UPDATE ON public.citizen FOR EACH ROW EXECUTE FUNCTION public.update_household_income();


--
-- Name: assetsurveys trigger_update_last_surveyed; Type: TRIGGER; Schema: public; Owner: 22CS30045
--

CREATE TRIGGER trigger_update_last_surveyed AFTER INSERT OR DELETE OR UPDATE ON public.assetsurveys FOR EACH STATEMENT EXECUTE FUNCTION public.update_last_surveyed();


--
-- Name: assetsurveys assetsurveys_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.assetsurveys
    ADD CONSTRAINT assetsurveys_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(asset_id);


--
-- Name: assetsurveys assetsurveys_surveyorid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.assetsurveys
    ADD CONSTRAINT assetsurveys_surveyorid_fkey FOREIGN KEY (surveyorid) REFERENCES public.employeecitizens(employeeid);


--
-- Name: attendsschool attendsschool_citizenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.attendsschool
    ADD CONSTRAINT attendsschool_citizenid_fkey FOREIGN KEY (citizenid) REFERENCES public.citizen(aadhaar);


--
-- Name: attendsschool attendsschool_schoolid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.attendsschool
    ADD CONSTRAINT attendsschool_schoolid_fkey FOREIGN KEY (schoolid) REFERENCES public.schools(schoolid);


--
-- Name: certificates certificates_citizenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.certificates
    ADD CONSTRAINT certificates_citizenid_fkey FOREIGN KEY (citizenid) REFERENCES public.citizen(aadhaar);


--
-- Name: citizen citizen_fatherid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.citizen
    ADD CONSTRAINT citizen_fatherid_fkey FOREIGN KEY (fatherid) REFERENCES public.citizen(aadhaar);


--
-- Name: citizen citizen_householdid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.citizen
    ADD CONSTRAINT citizen_householdid_fkey FOREIGN KEY (householdid) REFERENCES public.households(householdid);


--
-- Name: citizen citizen_motherid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.citizen
    ADD CONSTRAINT citizen_motherid_fkey FOREIGN KEY (motherid) REFERENCES public.citizen(aadhaar);


--
-- Name: employeecitizens employeecitizens_citizenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.employeecitizens
    ADD CONSTRAINT employeecitizens_citizenid_fkey FOREIGN KEY (citizenid) REFERENCES public.citizen(aadhaar);


--
-- Name: environmentaldata environmentaldata_recordedby_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.environmentaldata
    ADD CONSTRAINT environmentaldata_recordedby_fkey FOREIGN KEY (recordedby) REFERENCES public.employeecitizens(employeeid);


--
-- Name: hospitalaccount hospitalaccount_hospitalid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.hospitalaccount
    ADD CONSTRAINT hospitalaccount_hospitalid_fkey FOREIGN KEY (hospitalid) REFERENCES public.hospitals(hospitalid);


--
-- Name: land land_ownerid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.land
    ADD CONSTRAINT land_ownerid_fkey FOREIGN KEY (ownerid) REFERENCES public.citizen(aadhaar);


--
-- Name: landcrop landcrop_cropid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.landcrop
    ADD CONSTRAINT landcrop_cropid_fkey FOREIGN KEY (cropid) REFERENCES public.crop(cropid);


--
-- Name: landcrop landcrop_landid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.landcrop
    ADD CONSTRAINT landcrop_landid_fkey FOREIGN KEY (landid) REFERENCES public.land(landid);


--
-- Name: schemeenrollment schemeenrollment_citizenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schemeenrollment
    ADD CONSTRAINT schemeenrollment_citizenid_fkey FOREIGN KEY (citizenid) REFERENCES public.citizen(aadhaar);


--
-- Name: schemeenrollment schemeenrollment_schemeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schemeenrollment
    ADD CONSTRAINT schemeenrollment_schemeid_fkey FOREIGN KEY (schemeid) REFERENCES public.schemes(schemeid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: schoolaccount schoolaccount_schoolid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.schoolaccount
    ADD CONSTRAINT schoolaccount_schoolid_fkey FOREIGN KEY (schoolid) REFERENCES public.schools(schoolid);


--
-- Name: users users_citizenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_citizenid_fkey FOREIGN KEY (citizenid) REFERENCES public.citizen(aadhaar);


--
-- Name: users users_monitorid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: 22CS30045
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_monitorid_fkey FOREIGN KEY (monitorid) REFERENCES public.monitors(monitorid);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

