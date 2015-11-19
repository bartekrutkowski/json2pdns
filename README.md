json2pdns
=======
**Create PowerDNS Authoritative Server SQLite database files from JSON zone data files.**

json2pdns is a Python software for creating PowerDNS (dubbed pdns) Authoritative Server SQLite databases using JSON files containing the DNS zone data.

## Requirements

To run json2pdns on a Unix/Mac/Linux system you need the following software installed:

- Python 2.7.x with following modules installed:
  - json (in Python's base lib)
  - sqlite3 (in Python's base lib)


## Usage

By default, json2pdns requires at least one argument, that's a path to valid JSON file containing zone data you want to serve with your PowerDNS auth servers:

```sh
$ python json2pdns.py
usage: json2pdns.py [-h] [-d DEST_FILE] json_file
json2pdns.py: error: too few arguments
$
```

In this mode, json2pdns will print out the SQL code to the console for you to review/amend/execute in SQLite3:

```sh
$ python json2pdns.py examples/proper_zone_file.json

PRAGMA foreign_keys = 1;

CREATE TABLE domains (
  id                    INTEGER PRIMARY KEY,
  name                  VARCHAR(255) NOT NULL COLLATE NOCASE,
  master                VARCHAR(128) DEFAULT NULL,
  last_check            INTEGER DEFAULT NULL,
  type                  VARCHAR(6) NOT NULL,
  notified_serial       INTEGER DEFAULT NULL,
  account               VARCHAR(40) DEFAULT NULL
);
CREATE UNIQUE INDEX name_index ON domains(name);

CREATE TABLE records (
  id                    INTEGER PRIMARY KEY,
  domain_id             INTEGER DEFAULT NULL,
  name                  VARCHAR(255) DEFAULT NULL,
  type                  VARCHAR(10) DEFAULT NULL,
  content               VARCHAR(65535) DEFAULT NULL,
  ttl                   INTEGER DEFAULT NULL,
  prio                  INTEGER DEFAULT NULL,
  change_date           INTEGER DEFAULT NULL,
  disabled              BOOLEAN DEFAULT 0,
  ordername             VARCHAR(255),
  auth                  BOOL DEFAULT 1,
  FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX rec_name_index ON records(name);
CREATE INDEX nametype_index ON records(name,type);
CREATE INDEX domain_id ON records(domain_id);
CREATE INDEX orderindex ON records(ordername);

CREATE TABLE supermasters (
  ip                    VARCHAR(64) NOT NULL,
  nameserver            VARCHAR(255) NOT NULL COLLATE NOCASE,
  account               VARCHAR(40) NOT NULL
);
CREATE UNIQUE INDEX ip_nameserver_pk ON supermasters(ip, nameserver);

CREATE TABLE comments (
  id                    INTEGER PRIMARY KEY,
  domain_id             INTEGER NOT NULL,
  name                  VARCHAR(255) NOT NULL,
  type                  VARCHAR(10) NOT NULL,
  modified_at           INT NOT NULL,
  account               VARCHAR(40) DEFAULT NULL,
  comment               VARCHAR(65535) NOT NULL,
  FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX comments_domain_id_index ON comments (domain_id);
CREATE INDEX comments_nametype_index ON comments (name, type);
CREATE INDEX comments_order_idx ON comments (domain_id, modified_at);

CREATE TABLE domainmetadata (
 id                     INTEGER PRIMARY KEY,
 domain_id              INT NOT NULL,
 kind                   VARCHAR(32) COLLATE NOCASE,
 content                TEXT,
 FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX domainmetaidindex ON domainmetadata(domain_id);

CREATE TABLE cryptokeys (
 id                     INTEGER PRIMARY KEY,
 domain_id              INT NOT NULL,
 flags                  INT NOT NULL,
 active                 BOOL,
 content                TEXT,
 FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX domainidindex ON cryptokeys(domain_id);

CREATE TABLE tsigkeys (
 id                     INTEGER PRIMARY KEY,
 name                   VARCHAR(255) COLLATE NOCASE,
 algorithm              VARCHAR(50) COLLATE NOCASE,
 secret                 VARCHAR(255)
);
CREATE UNIQUE INDEX namealgoindex ON tsigkeys(name, algorithm);

INSERT INTO domains (id,name,type) VALUES (1,'example.com','NATIVE');
INSERT INTO records (content,ttl,type,domain_id,name) VALUES ('ns1.example.com. hostmaster.example.com. 1299682996 300 1800 604800 300',300,'SOA',1,'example.com');
INSERT INTO records (content,ttl,type,domain_id,name) VALUES ('ns1.example.com',300,'NS',1,'example.com');
INSERT INTO records (content,ttl,type,domain_id,name) VALUES ('10.1.1.1',300,'A',1,'ns1.example.com');
INSERT INTO records (content,ttl,type,domain_id,name) VALUES ('web.example.com',300,'CNAME',1,'ldapass.example.com');
INSERT INTO records (content,ttl,type,domain_id,name) VALUES ('10.1.1.2',300,'A',1,'web.example.com');

$
```

If you want to use json2pdns in automated fashion (within Ansible task or Puppet module, for example) you may use optional `-d` argument with a path where you would like your SQLite database file to be created. When using this option, json2pdns wont provide any output to the console:

```sh
$ python json2pdns.py examples/proper_zone_file.json -d /var/db/pdns.sql
$ 
```
