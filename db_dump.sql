/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `properties` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `ref_num` varchar(20) NOT NULL,
  `last_update` date NOT NULL,
  `property_type` varchar(40) NOT NULL,
  `deal_type` varchar(20) NOT NULL,
  `price` int(10) NOT NULL,
  `address_detail_type` varchar(20) NOT NULL,
  `address_detail` varchar(40) DEFAULT NULL,
  `address` varchar(100) NOT NULL,
  `neighborhood` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(2) NOT NULL,
  `area_total` float NOT NULL,
  `area_usable` float DEFAULT NULL,
  `area_land` float NOT NULL,
  `total_rooms` int(2) NOT NULL DEFAULT '-1',
  `total_suites` int(2) NOT NULL DEFAULT '-1',
  `observations` text NOT NULL,
  `extra_info` text NOT NULL,
  `date_extracted` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ref_num` (`ref_num`,`last_update`)
) ENGINE=InnoDB AUTO_INCREMENT=2706 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sold` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `ref_num` varchar(20) NOT NULL,
  `selling_date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
