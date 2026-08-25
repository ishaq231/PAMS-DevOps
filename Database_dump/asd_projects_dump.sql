-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: asd-database-ishaq-2403.e.aivencloud.com    Database: defaultdb
-- ------------------------------------------------------

CREATE DATABASE IF NOT EXISTS `asd_poject`;
USE `asd_poject`;

-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
#SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
#SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

#SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '12dcb23d-1967-11f1-b99e-eeb9f33cb7ac:1-72,
#3929a573-18a6-11f1-bf48-862e1606612d:1-141,
#f8497402-17cc-11f1-9c45-52787aa40f13:1-27';

--
-- Table structure for table `Invoice`
--

DROP TABLE IF EXISTS `Invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Invoice` (
  `invoiceID` int NOT NULL AUTO_INCREMENT,
  `leaseID` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `due_date` date DEFAULT NULL,
  `status` enum('Paid','Pending','Overdue','Partial') DEFAULT 'Pending',
  `issue_date` date DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`invoiceID`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Invoice`
--

/*!40000 ALTER TABLE `Invoice` DISABLE KEYS */;
INSERT INTO `Invoice` VALUES (1,1,1200.00,'2026-01-31','Paid','2026-01-01','Monthly rent — January 2026'),(2,1,1200.00,'2026-02-28','Paid','2026-02-01','Monthly rent — February 2026'),(3,1,1200.00,'2026-03-31','Paid','2026-03-01','Monthly rent — March 2026'),(4,2,1800.00,'2026-01-31','Paid','2026-01-01','Monthly rent — January 2026'),(5,2,1800.00,'2026-02-28','Paid','2026-02-01','Monthly rent — February 2026'),(6,2,1800.00,'2026-03-31','Pending','2026-03-01','Monthly rent — March 2026'),(7,3,2500.00,'2026-01-31','Pending','2026-01-01','Monthly rent — January 2026'),(8,3,2500.00,'2026-02-28','Paid','2026-02-01','Monthly rent — February 2026'),(9,3,2500.00,'2026-03-31','Paid','2026-03-01','Monthly rent — March 2026'),(10,4,1900.00,'2026-01-31','Paid','2026-01-01','Monthly rent — January 2026'),(11,4,1900.00,'2026-02-28','Overdue','2026-02-01','Monthly rent — February 2026'),(12,4,1900.00,'2026-03-31','Pending','2026-03-01','Monthly rent — March 2026'),(13,5,1400.00,'2026-01-31','Paid','2026-01-01','Monthly rent — January 2026'),(14,5,1400.00,'2026-02-28','Paid','2026-02-01','Monthly rent — February 2026'),(15,5,1400.00,'2026-03-31','Pending','2026-03-01','Monthly rent — March 2026'),(16,6,1700.00,'2026-01-31','Paid','2026-01-01','Monthly rent — January 2026'),(17,6,1700.00,'2026-02-28','Overdue','2026-02-01','Monthly rent — February 2026'),(18,6,1700.00,'2026-03-31','Pending','2026-03-01','Monthly rent — March 2026'),(19,3,2500.00,'2025-05-31','Paid','2025-05-01','Monthly rent — May 2025'),(20,1,1000.00,'2026-07-06','Pending','2026-03-06','Monthly Rent'),(21,1,3000.00,'2026-03-06','Overdue','2026-03-06','Monthly rent'),(22,1,15000.00,'2026-03-06','Pending','2026-03-06','Rent'),(23,1,2000.00,'2026-03-06','Pending','2026-03-06','Rent'),(24,2,20000.00,'2026-03-06','Pending','2026-03-06','Monthly rent');
/*!40000 ALTER TABLE `Invoice` ENABLE KEYS */;

--
-- Table structure for table `amenity`
--

DROP TABLE IF EXISTS `amenity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `amenity` (
  `amenity_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`amenity_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `amenity`
--

/*!40000 ALTER TABLE `amenity` DISABLE KEYS */;
INSERT INTO `amenity` VALUES (1,'Gym','On-site fitness centre with modern equipment'),(2,'Parking','Secure underground parking space included'),(3,'WiFi','High-speed fibre broadband included'),(4,'Balcony','Private balcony with city or garden views'),(5,'Dishwasher','Built-in dishwasher in kitchen'),(6,'Air Conditioning','Multi-zone air conditioning system'),(7,'Concierge','24/7 concierge and security service'),(8,'Rooftop Terrace','Shared rooftop terrace with panoramic views'),(9,'Pet Friendly','Pets welcome with prior approval'),(10,'Storage Unit','Private locked storage unit in basement');
/*!40000 ALTER TABLE `amenity` ENABLE KEYS */;

--
-- Table structure for table `apartment`
--

DROP TABLE IF EXISTS `apartment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartment` (
  `apartment_id` int NOT NULL AUTO_INCREMENT,
  `apartment_number` int DEFAULT NULL,
  `monthly_rent` decimal(10,2) DEFAULT NULL,
  `location_id` int NOT NULL,
  `type` varchar(45) DEFAULT NULL,
  `square_footage` varchar(45) DEFAULT NULL,
  `occupation_status` enum('Occupied','Vacant','Maintenance') DEFAULT NULL,
  `number_of_rooms` int DEFAULT NULL,
  PRIMARY KEY (`apartment_id`),
  KEY `FK_Apartment_location_idx` (`location_id`),
  CONSTRAINT `FK_Apartment_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartment`
--

/*!40000 ALTER TABLE `apartment` DISABLE KEYS */;
INSERT INTO `apartment` VALUES (1,101,1200.00,1,'1-Bed','550','Maintenance',2),(2,102,1500.00,1,'2-Bed','750','Occupied',3),(3,103,900.00,1,'Studio','380','Vacant',1),(4,201,1800.00,2,'2-Bed','800','Vacant',3),(5,202,2200.00,2,'3-Bed','1100','Vacant',4),(6,203,950.00,2,'Studio','400','Maintenance',1),(7,301,2500.00,3,'Penthouse','1800','Occupied',5),(8,302,1900.00,3,'2-Bed','850','Occupied',3),(9,303,1100.00,3,'1-Bed','520','Vacant',2),(10,401,1400.00,4,'1-Bed','600','Occupied',2),(11,402,1700.00,4,'2-Bed','780','Occupied',3),(12,403,2100.00,4,'3-Bed','1050','Vacant',4);
/*!40000 ALTER TABLE `apartment` ENABLE KEYS */;

--
-- Table structure for table `apartment_amenity`
--

DROP TABLE IF EXISTS `apartment_amenity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartment_amenity` (
  `apartmentID` int NOT NULL,
  `amenityID` int NOT NULL,
  PRIMARY KEY (`apartmentID`,`amenityID`),
  KEY `amenity_idx` (`amenityID`),
  CONSTRAINT `amenity` FOREIGN KEY (`amenityID`) REFERENCES `amenity` (`amenity_id`) ON DELETE CASCADE,
  CONSTRAINT `apartment` FOREIGN KEY (`apartmentID`) REFERENCES `apartment` (`apartment_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartment_amenity`
--

/*!40000 ALTER TABLE `apartment_amenity` DISABLE KEYS */;
INSERT INTO `apartment_amenity` VALUES (2,1),(5,1),(7,1),(11,1),(12,1),(1,2),(2,2),(4,2),(5,2),(7,2),(8,2),(10,2),(11,2),(12,2),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),(4,4),(5,4),(7,4),(11,4),(12,4),(2,5),(8,5),(10,5),(4,6),(5,6),(7,6),(8,6),(12,6),(7,7),(7,8),(1,9),(9,9),(7,10),(12,10);
/*!40000 ALTER TABLE `apartment_amenity` ENABLE KEYS */;

--
-- Table structure for table `complaint`
--

DROP TABLE IF EXISTS `complaint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaint` (
  `complaint_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `date_filed` date NOT NULL,
  `subject` varchar(255) NOT NULL,
  `description` text,
  `status` enum('Open','Under Review','Resolved','Closed') DEFAULT 'Open',
  PRIMARY KEY (`complaint_id`),
  KEY `FK_complaint_tenant` (`tenant_id`),
  CONSTRAINT `FK_complaint_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint`
--

/*!40000 ALTER TABLE `complaint` DISABLE KEYS */;
INSERT INTO `complaint` VALUES (1,7,'2025-11-20','Noise from neighbouring unit late at night','There is persistent loud music and noise coming from apartment 102 after midnight on weekdays. It has disrupted my sleep on multiple occasions.','Resolved'),(2,8,'2025-12-10','Heating system not working properly','The central heating in apartment 201 has been intermittent since early December. The radiators in the bedroom do not heat up at all.','Resolved'),(3,10,'2026-01-15','Lift out of service — no notice given','The main lift has been out of service for three days with no advance notice or estimated repair time communicated to residents. I carry heavy equipment for work.','Under Review'),(4,11,'2026-01-28','Communal bin area not being cleaned regularly','The bin area on the ground floor is consistently overflowing and has not been cleared for over a week. It is creating an unpleasant smell in the entrance hallway.','Under Review'),(5,12,'2026-02-03','Parking space occupied by unauthorised vehicle','My assigned parking space (bay 12) has been used by an unknown vehicle on three separate occasions this month. I have had to park elsewhere.','Open'),(6,9,'2026-02-14','Post and parcels going missing from communal area','Multiple packages addressed to me have not been received over the past month. I believe they are being left unattended in the communal entrance and may have been taken.','Open'),(7,7,'2026-02-25','Water pressure in shower very low','The shower in the main bathroom has had noticeably low water pressure since the start of February. The maintenance request raised was closed without the issue being fully resolved.','Open'),(8,8,'2026-03-01','Rude conduct by a member of staff','During my visit to the front desk on 28 February I felt I was spoken to dismissively when raising a concern about my lease renewal. I would like this to be formally noted.','Open'),(9,10,'2026-03-06','Early Lease Termination Request','i have no money','Open');
/*!40000 ALTER TABLE `complaint` ENABLE KEYS */;

--
-- Table structure for table `enquiry`
--

DROP TABLE IF EXISTS `enquiry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enquiry` (
  `enquiry_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int DEFAULT NULL,
  `tenant_name` varchar(100) DEFAULT NULL,
  `enquiry_details` text NOT NULL,
  `handled_by` varchar(100) DEFAULT NULL,
  `date_logged` date NOT NULL,
  PRIMARY KEY (`enquiry_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enquiry`
--

/*!40000 ALTER TABLE `enquiry` DISABLE KEYS */;
INSERT INTO `enquiry` VALUES (1,7,'Oliver Thompson','Asked about the process for renewing his lease which expires in January 2026. Advised on renewal timelines and directed to the manager.','James Wilson','2025-11-05'),(2,8,'Emma Clarke','Enquired whether she can sublet a room in apartment 201. Informed that subletting is not permitted under the standard lease agreement.','James Wilson','2025-11-18'),(3,9,'Liam Murphy','Asked about the status of his expired lease and options for signing a new agreement. Advised to schedule a meeting with the manager.','James Wilson','2025-12-03'),(4,10,'Sophie Williams','Enquired about obtaining a second parking permit for a visiting family member. Informed that visitor permits are issued at the front desk on request.','James Wilson','2026-01-09'),(5,11,'Daniel Khan','Asked when the January invoice would be generated and how to access payment history. Directed to the tenant portal and explained the billing cycle.','James Wilson','2026-01-20'),(6,12,'Zoe Henderson','Enquired about adding a cat to the apartment. Confirmed apartment 402 is pet-friendly and advised her to submit a written request for management approval.','James Wilson','2026-02-06'),(7,7,'Oliver Thompson','Requested a letter confirming his tenancy for a mortgage application. Letter prepared and emailed within the same day.','James Wilson','2026-02-19'),(8,8,'Emma Clarke','Asked about early termination of her lease. Explained the 30-day notice requirement and 5% early termination penalty as per the lease agreement.','James Wilson','2026-03-02'),(9,9,'Liam Murphy','User reported broken lights','Front Desk Staff','2026-03-06');
/*!40000 ALTER TABLE `enquiry` ENABLE KEYS */;

--
-- Table structure for table `lease_agreement`
--

DROP TABLE IF EXISTS `lease_agreement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lease_agreement` (
  `leaseID` int NOT NULL AUTO_INCREMENT,
  `tenantID` int NOT NULL,
  `apartmentID` int NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `monthly_rent` decimal(10,2) NOT NULL,
  `deposit_amount` decimal(10,2) DEFAULT NULL,
  `lease_term_months` int DEFAULT NULL,
  `status` enum('ACTIVE','PENDING','TERMINATED','EXPIRED') DEFAULT 'PENDING',
  `termination_date` date DEFAULT NULL,
  `early_termination_notice` int DEFAULT NULL,
  `termination_penalty_percent` decimal(5,2) DEFAULT '5.00',
  PRIMARY KEY (`leaseID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lease_agreement`
--

/*!40000 ALTER TABLE `lease_agreement` DISABLE KEYS */;
INSERT INTO `lease_agreement` VALUES (1,7,1,'2025-01-01','2026-01-01',1200.00,1200.00,12,'ACTIVE',NULL,30,5.00),(2,8,4,'2025-03-01','2026-03-01',1800.00,1800.00,12,'ACTIVE',NULL,30,5.00),(3,9,7,'2024-06-01','2025-06-01',2500.00,2500.00,12,'EXPIRED',NULL,30,5.00),(4,10,8,'2025-07-01','2026-07-01',1900.00,1900.00,12,'ACTIVE',NULL,30,5.00),(5,11,10,'2025-02-15','2026-02-15',1400.00,1400.00,12,'ACTIVE',NULL,30,5.00),(6,12,11,'2025-09-01','2026-09-01',1700.00,1700.00,12,'ACTIVE',NULL,30,5.00),(7,10,2,'2026-03-06','2027-03-06',1500.00,1500.00,12,'TERMINATED','2026-03-06',30,5.00);
/*!40000 ALTER TABLE `lease_agreement` ENABLE KEYS */;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `city` varchar(50) NOT NULL,
  `manager` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location`
--

/*!40000 ALTER TABLE `location` DISABLE KEYS */;
INSERT INTO `location` VALUES (1,'Bristol','Sarah Chen'),(2,'Cardiff','David Okafor'),(3,'London','Priya Sharma'),(4,'Manchester','Tom Briggs'),(5,'Leeds','Sarah Chen');
/*!40000 ALTER TABLE `location` ENABLE KEYS */;

--
-- Table structure for table `maintenance_log`
--

DROP TABLE IF EXISTS `maintenance_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `request_id` int NOT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `description` text,
  `parts_used` text,
  `cost_breakdown` varchar(255) DEFAULT NULL,
  `technician_notes` text,
  PRIMARY KEY (`log_id`),
  KEY `FK_log_request` (`request_id`),
  CONSTRAINT `FK_log_request` FOREIGN KEY (`request_id`) REFERENCES `maintenance_request` (`request_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_log`
--

/*!40000 ALTER TABLE `maintenance_log` DISABLE KEYS */;
INSERT INTO `maintenance_log` VALUES (1,1,'2026-03-01 08:00:00','2026-03-01 10:00:00','fixed broken pipe','new pipe','£50','used high quality pipe so problem doesnt occur again.');
/*!40000 ALTER TABLE `maintenance_log` ENABLE KEYS */;

--
-- Table structure for table `maintenance_request`
--

DROP TABLE IF EXISTS `maintenance_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_request` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `apartment_id` int NOT NULL,
  `reportedByTenant_id` int NOT NULL,
  `assignedStaff_id` int DEFAULT NULL,
  `description` text NOT NULL,
  `priority` enum('Low','Medium','High','Emergency') DEFAULT 'Low',
  `status` enum('Open','In Progress','Resolved','Closed') DEFAULT 'Open',
  `report_date` datetime DEFAULT NULL,
  `resolved_date` datetime DEFAULT NULL,
  `cost` decimal(10,2) DEFAULT '0.00',
  `scheduled_date` date DEFAULT NULL,
  `category` varchar(50) DEFAULT 'General',
  PRIMARY KEY (`request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_request`
--

/*!40000 ALTER TABLE `maintenance_request` DISABLE KEYS */;
INSERT INTO `maintenance_request` VALUES (1,1,7,5,'Boiler not producing hot water','High','Resolved','2025-11-15 09:00:00','2026-03-06 00:00:00',180.00,NULL,'General'),(2,4,8,6,'Bathroom tap dripping constantly','Medium','In Progress','2025-12-01 10:30:00','2025-12-02 11:00:00',45.00,NULL,'General'),(3,8,10,5,'Kitchen extractor fan making loud noise','Medium','In Progress','2026-01-10 08:00:00',NULL,0.00,NULL,'General'),(4,10,11,6,'Window latch broken on bedroom window','Low','In Progress','2026-02-05 13:00:00',NULL,0.00,NULL,'General'),(5,11,12,6,'Damp patch appearing on living room ceiling','High','In Progress','2026-02-20 09:30:00',NULL,0.00,NULL,'General'),(6,6,9,6,'Front door lock jammed — cannot enter apartment','Emergency','In Progress','2025-10-08 18:00:00','2025-10-08 20:30:00',220.00,NULL,'General'),(7,1,7,6,'Light fixture in hallway flickering','Low','In Progress','2026-03-01 11:00:00',NULL,0.00,NULL,'General'),(8,8,10,6,'Oven heating element not working','Medium','Open','2026-03-03 14:00:00',NULL,0.00,NULL,'General'),(9,10,11,NULL,'Heating not working','High','Open','2026-03-06 15:57:02',NULL,0.00,NULL,'Heating');
/*!40000 ALTER TABLE `maintenance_request` ENABLE KEYS */;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `recipient_id` int NOT NULL,
  `message` text NOT NULL,
  `notification_date` date NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `notification_type` enum('Payment','Maintenance','Lease','General') DEFAULT 'General',
  PRIMARY KEY (`notification_id`),
  KEY `FK_notification_user` (`recipient_id`),
  CONSTRAINT `FK_notification_user` FOREIGN KEY (`recipient_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (1,7,'Your invoice #1 for £1,200.00 has been marked as Paid.','2026-01-31',1,'Payment'),(2,7,'Your invoice #2 for £1,200.00 has been marked as Paid.','2026-02-28',1,'Payment'),(3,7,'New invoice #3 for £1,200.00 due on 2026-03-31.','2026-03-01',0,'Payment'),(4,7,'Maintenance request #1 (Boiler not producing hot water) has been resolved.','2025-11-16',1,'Maintenance'),(5,7,'Maintenance request #7 submitted (Low priority). We will review it shortly.','2026-03-01',0,'Maintenance'),(6,7,'Your complaint \'Noise from neighbouring unit late at night\' status has been updated to \'Resolved\'.','2025-12-05',1,'General'),(7,7,'Your complaint \'Water pressure in shower very low\' (#7) has been filed and is now Open.','2026-02-25',0,'General'),(8,8,'Your invoice #4 for £1,800.00 has been marked as Paid.','2026-01-31',1,'Payment'),(9,8,'Your invoice #5 for £1,800.00 has been marked as Paid.','2026-02-28',1,'Payment'),(10,8,'New invoice #6 for £1,800.00 due on 2026-03-31.','2026-03-01',0,'Payment'),(11,8,'Maintenance request #2 (Bathroom tap dripping) has been resolved.','2025-12-02',1,'Maintenance'),(12,8,'Your complaint \'Heating system not working properly\' status has been updated to \'Resolved\'.','2025-12-20',1,'General'),(13,8,'Your complaint \'Rude conduct by a member of staff\' (#8) has been filed and is now Open.','2026-03-01',0,'General'),(14,8,'Your lease has been created. Start: 2025-03-01, End: 2026-03-01.','2025-03-01',1,'Lease'),(15,9,'Maintenance request #6 (Front door lock jammed) has been resolved.','2025-10-08',1,'Maintenance'),(16,9,'Your complaint \'Post and parcels going missing\' (#6) has been filed and is now Open.','2026-02-14',0,'General'),(17,9,'Invoice #19 for £2,500.00 is overdue (due 2025-05-31). Please pay immediately.','2025-06-01',0,'Payment'),(18,9,'Your lease (2024-06-01 to 2025-06-01) has expired.','2025-06-01',1,'Lease'),(19,10,'Your invoice #10 for £1,900.00 has been marked as Paid.','2026-01-31',1,'Payment'),(20,10,'Your invoice #11 for £1,900.00 has been marked as Paid.','2026-02-28',1,'Payment'),(21,10,'New invoice #12 for £1,900.00 due on 2026-03-31.','2026-03-01',0,'Payment'),(22,10,'Maintenance request #3 status updated to \'In Progress\'.','2026-01-12',0,'Maintenance'),(23,10,'Maintenance request #8 submitted (Medium priority). We will review it shortly.','2026-03-03',0,'Maintenance'),(24,10,'Your complaint \'Lift out of service — no notice given\' status has been updated to \'Under Review\'.','2026-01-20',0,'General'),(25,10,'Your lease has been created. Start: 2025-07-01, End: 2026-07-01.','2025-07-01',1,'Lease'),(26,11,'Your invoice #13 for £1,400.00 has been marked as Paid.','2026-01-31',1,'Payment'),(27,11,'New invoice #15 for £1,400.00 due on 2026-03-31.','2026-03-01',0,'Payment'),(28,11,'Maintenance request #4 submitted (Low priority). We will review it shortly.','2026-02-05',0,'Maintenance'),(29,11,'Your complaint \'Communal bin area not being cleaned\' status has been updated to \'Under Review\'.','2026-02-05',0,'General'),(30,11,'Your lease has been created. Start: 2025-02-15, End: 2026-02-15.','2025-02-15',1,'Lease'),(31,12,'Your invoice #16 for £1,700.00 has been marked as Paid.','2026-01-31',1,'Payment'),(32,12,'New invoice #18 for £1,700.00 due on 2026-03-31.','2026-03-01',0,'Payment'),(33,12,'Maintenance request #5 status updated to \'In Progress\'.','2026-02-22',0,'Maintenance'),(34,12,'Your complaint \'Parking space occupied by unauthorised vehicle\' (#5) has been filed and is now Open.','2026-02-03',0,'General'),(35,12,'Your lease has been created. Start: 2025-09-01, End: 2026-09-01.','2025-09-01',1,'Lease'),(36,10,'Your new lease has been created. Start: 2026-03-06, End: 2027-03-06, Monthly rent: £1,500.00.','2026-03-06',0,'Lease'),(37,10,'Your early termination request for lease #7 has been processed. The lease is now terminated.','2026-03-06',0,'Lease'),(38,7,'New invoice #20 for £1,000.00 due on 2026-07-06.','2026-03-06',1,'Payment'),(39,7,'Payment of £1,200.00 recorded for invoice #3. Receipt: 1013.','2026-03-06',0,'Payment'),(40,7,'New invoice #21 for £3,000.00 due on 2026-03-06.','2026-03-06',0,'Payment'),(41,7,'New invoice #22 for £15,000.00 due on 2026-03-06.','2026-03-06',0,'Payment'),(42,7,'New invoice #23 for £2,000.00 due on 2026-03-06.','2026-03-06',0,'Payment'),(43,8,'New invoice #24 for £20,000.00 due on 2026-03-06.','2026-03-06',0,'Payment'),(44,9,'Invoice #19 status updated to \'Paid\'.','2026-03-06',0,'Payment'),(45,9,'Invoice #9 status updated to \'Paid\'.','2026-03-06',0,'Payment'),(46,10,'Invoice #11 status updated to \'Overdue\'.','2026-03-06',0,'Payment'),(47,12,'Invoice #17 status updated to \'Overdue\'.','2026-03-06',0,'Payment'),(48,7,'Invoice #21 status updated to \'Overdue\'.','2026-03-06',0,'Payment'),(49,10,'Your invoice #11 for £1,900.00 (due 2026-02-28) is overdue. Please pay immediately to avoid further charges.','2026-03-06',0,'Payment'),(50,12,'Your invoice #17 for £1,700.00 (due 2026-02-28) is overdue. Please pay immediately to avoid further charges.','2026-03-06',0,'Payment'),(51,7,'Your invoice #21 for £3,000.00 (due 2026-03-06) is overdue. Please pay immediately to avoid further charges.','2026-03-06',0,'Payment'),(52,11,'Maintenance request #9 submitted (High priority). We will review it shortly.','2026-03-06',0,'Maintenance'),(53,7,'Maintenance request #1 status updated to \'In Progress\'.','2026-03-06',0,'Maintenance'),(54,8,'Maintenance request #2 status updated to \'In Progress\'.','2026-03-06',0,'Maintenance'),(55,9,'Maintenance request #6 status updated to \'In Progress\'.','2026-03-06',0,'Maintenance'),(56,11,'Maintenance request #4 status updated to \'In Progress\'.','2026-03-06',0,'Maintenance'),(57,7,'Maintenance request #1 status updated to \'Resolved\'.','2026-03-06',0,'Maintenance'),(58,9,'Invoice #7 status updated to \'Pending\'.','2026-03-10',0,'Payment');
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int NOT NULL,
  `amount_paid` decimal(10,2) NOT NULL,
  `payment_date` date DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `transaction_ref` varchar(100) DEFAULT NULL,
  `receipt_number` int DEFAULT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `FK_payment_invoice_idx` (`invoice_id`),
  CONSTRAINT `FK_payment_invoice` FOREIGN KEY (`invoice_id`) REFERENCES `Invoice` (`invoiceID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,1,1200.00,'2026-01-31','Bank Transfer','TXN-2026-1001',1001),(2,2,1200.00,'2026-02-28','Bank Transfer','TXN-2026-1002',1002),(3,4,1800.00,'2026-01-31','Debit Card','TXN-2026-1003',1003),(4,5,1800.00,'2026-02-28','Debit Card','TXN-2026-1004',1004),(5,7,2500.00,'2026-01-31','Bank Transfer','TXN-2026-1005',1005),(6,8,2500.00,'2026-02-28','Bank Transfer','TXN-2026-1006',1006),(7,10,1900.00,'2026-01-31','Credit Card','TXN-2026-1007',1007),(8,11,1900.00,'2026-02-28','Credit Card','TXN-2026-1008',1008),(9,13,1400.00,'2026-01-31','Bank Transfer','TXN-2026-1009',1009),(10,14,1400.00,'2026-02-28','Bank Transfer','TXN-2026-1010',1010),(11,16,1700.00,'2026-01-31','Debit Card','TXN-2026-1011',1011),(12,17,1700.00,'2026-02-28','Debit Card','TXN-2026-1012',1012),(13,3,1200.00,'2026-03-06','Bank Transfer','TXN-3494',1013);
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;

--
-- Table structure for table `staff_member`
--

DROP TABLE IF EXISTS `staff_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_member` (
  `employee_id` int NOT NULL,
  `salary` decimal(10,2) DEFAULT NULL,
  `role` varchar(45) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  PRIMARY KEY (`employee_id`),
  KEY `FK_location_idx` (`location_id`),
  KEY `fk_staff_role_idx` (`role`),
  CONSTRAINT `FK_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`) ON DELETE SET NULL,
  CONSTRAINT `FK_staff_id` FOREIGN KEY (`employee_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_staff_role` FOREIGN KEY (`role`) REFERENCES `staff_role` (`role_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_member`
--

/*!40000 ALTER TABLE `staff_member` DISABLE KEYS */;
INSERT INTO `staff_member` VALUES (1,52000.00,'Administrator','2020-01-10',1),(2,48000.00,'Manager','2019-03-15',1),(3,28000.00,'Front Desk Staff','2021-06-01',2),(4,42000.00,'Finance Manager','2020-09-20',3),(5,31000.00,'Maintenance Staff','2022-02-14',1),(6,30500.00,'Maintenance Staff','2023-05-08',4);
/*!40000 ALTER TABLE `staff_member` ENABLE KEYS */;

--
-- Table structure for table `staff_role`
--

DROP TABLE IF EXISTS `staff_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_role` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(45) NOT NULL,
  `signup_code` varchar(20) NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`),
  UNIQUE KEY `signup_code` (`signup_code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_role`
--

/*!40000 ALTER TABLE `staff_role` DISABLE KEYS */;
INSERT INTO `staff_role` VALUES (1,'Administrator','ADMIN2026'),(2,'Manager','MGR2026'),(3,'Front Desk Staff','FRONT2026'),(4,'Finance Manager','FIN2026'),(5,'Maintenance Staff','MAINT2026');
/*!40000 ALTER TABLE `staff_role` ENABLE KEYS */;

--
-- Table structure for table `tenant`
--

DROP TABLE IF EXISTS `tenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenant` (
  `tenant_id` int NOT NULL,
  `lease_status` varchar(45) DEFAULT NULL,
  `occupation` varchar(45) DEFAULT NULL,
  `ni_number` varchar(45) DEFAULT NULL,
  `references` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`tenant_id`),
  CONSTRAINT `tenant` FOREIGN KEY (`tenant_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenant`
--

/*!40000 ALTER TABLE `tenant` DISABLE KEYS */;
INSERT INTO `tenant` VALUES (7,NULL,'Software Engineer','AB123456C','John Doe, +447700900001'),(8,NULL,'Graphic Designer','CD234567D','Jane Smith, +447700900002'),(9,NULL,'Teacher','EF345678E','Paul Brown, +447700900003'),(10,NULL,'Marketing Manager','GH456789F','Lisa Green, +447700900004'),(11,NULL,'Accountant','IJ567890G','Mike White, +447700900005'),(12,NULL,'Nurse','KL678901H','Sandra Black, +447700900006'),(13,NULL,NULL,NULL,NULL),(14,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `tenant` ENABLE KEYS */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `fname` varchar(45) DEFAULT NULL,
  `lname` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `phone_number` varchar(45) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `role` varchar(45) DEFAULT NULL,
  `username` varchar(45) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Haso','Admin','haso@paragon.co.uk','07700100001','1985-03-15','Administrator','haso_admin','$2b$12$Fw2KirfAOByjONNCFcRleeaqN3tOHZyCcdeSc7BB2t3f3sxOOX4wC'),(2,'Sarah','Chen','sarah.chen@paragon.co.uk','07700100002','1980-07-22','Manager','sarah_mgr','$2b$12$kASMWwW/FgGmC6n0TQeb2.0xyrNwpbu4tUi2SyB7FXyJDjwddCeci'),(3,'James','Wilson','james.w@paragon.co.uk','07700100003','1992-11-08','Front Desk Staff','james_fd','$2b$12$B5PfbQVkHvN4qXD7SCMXyOF6Eee6K44B.YHeR.Vx887XmwDl9wKb6'),(4,'Nina','Patel','nina.p@paragon.co.uk','07700100004','1990-04-30','Finance Manager','nina_fin','$2b$12$QZ62jPy6yS3p8gXfaDiD5./qJI8CW5AAzEkXrhjmfoasdWgj9nRQO'),(5,'Marcus','Brown','marcus.b@paragon.co.uk','07700100005','1988-09-12','Maintenance Staff','marcus_maint','$2b$12$3Q0fHC60Dq5fDsyXUQ3LTuzc7BajKkHXVM0rJwB5G3xz/yDiZop6y'),(6,'Aisha','Osei','aisha.o@paragon.co.uk','07700100006','1994-02-18','Maintenance Staff','aisha_maint','$2b$12$Cl5tzDSN8R4BqZox4eBig.62UQCrEE.z/GWXLL7QlybjXzmdBM17y'),(7,'Oliver','Thompson','oliver.t@gmail.com','07800200001','1995-06-14','Tenant','oliver_t','$2b$12$G.qARhA1hHxzwR6.DIgoK.VrOXiJb9IXgQbQyCLbBmkZSZWGTNfTa'),(8,'Emma','Clarke','emma.c@gmail.com','07800200002','1998-01-25','Tenant','emma_c','$2b$12$w9509Gp9Jaa4K1ry1gFUIuSxXY1KuKKPmeyeR0ydHHFico4pdEWly'),(9,'Liam','Murphy','liam.m@gmail.com','07800200003','1993-08-03','Tenant','liam_m','$2b$12$ZQvhxuIZrlGv3roi8e/Wq.AM3NVGZqY/Bi8nS.GK6Y4PAcp6O5CqC'),(10,'Sophie','Williams','sophie.williams@gmail.com','07800200004','1997-12-11','Tenant','sophie_w','$2b$12$VKbYbjgPjHuyrnhgUzfjYOPhttyRuFElXI14XQ/KybV99QhJ17wCS'),(11,'Daniel','Khan','daniel.k@gmail.com','07800200005','1990-05-20','Tenant','daniel_k','$2b$12$qVK.aytR8vlUzrVj2SnYAerhtdRszfbFmvv6JcNISzmDPpqqeX8/.'),(12,'Zoe','Henderson','zoe.h@gmail.com','07800200006','1996-09-07','Tenant','zoe_h','$2b$12$2udACszFjljFVZs/zd5bkujVN80RKp6jX5BYlCW4Jnul.cP0zFyzS'),(13,'bob','jon','bob@gmail.com','+44 213456456','1991-01-10','Tenant','bobjon','$2b$12$hQRXG7eAWWRrArYNNyws2eYoOYshFCd.9uu/lfEHbwbYDwHAzugVu'),(14,'bro','bro','bro@bro','12345678','2000-01-01','Tenant','vroooo','$2b$12$YlwzhFEJEXmGSKuiwUFsJOaak0XtM0ils7uO1xEw/kc/p5k0NZqW6');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;

--
-- Dumping routines for database 'defaultdb'
--
-- SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-14 18:02:17
