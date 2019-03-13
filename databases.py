

# database name is patentnlp

"""
create table applications(
   app_id INT NOT NULL AUTO_INCREMENT,
   app_number VARCHAR(40) NOT NULL,
   claimset_id INT NOT NULL,
   PRIMARY KEY ( app_id )
);

create table claimsets(
   claimset_id INT NOT NULL,
  claim_id INT NOT NULL,
   PRIMARY KEY ( claimset_id )
);

create table claims(
   claim_id INT NOT NULL AUTO_INCREMENT,
   claim_text VARCHAR(400) NOT NULL,
   PRIMARY KEY ( claim_id )
);

"""

appTableName = "applications"
claimTableName = "claims"