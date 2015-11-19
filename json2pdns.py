# -*- coding: utf-8 -*-

import argparse
import json
import sqlite3
import sys

DB_SCHEMA = """
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

"""


def parse_args():
    """Parse commandline arguments and return them in parser object."""

    parser = argparse.ArgumentParser(
    description='JSON to PowerDNS SQLite DB converter')
    parser.add_argument('json_file', type=str, help='Path to input JSON file')
    parser.add_argument('-d',
                        dest='dest_file',
                        type=str,
                        help='Path to destination SQLite db file')
    return parser.parse_args()


def read_json(json_file):
    """Read text file with JSON and return parsed data in Python object."""

    try:
        with open(json_file, 'r') as f:
            json_data = json.loads(f.read())
    except EnvironmentError as e:
        print("ERROR reading json_file: {}").format(e)
        sys.exit(1)
    except ValueError as e:
        print("ERROR parsing json_file: {}").format(e)
        sys.exit(1)
    return json_data


def make_sql(json_data):
    """Make SQL data out of DB_SCHEMA and parsed JSON data."""

    sql_data = DB_SCHEMA
    domain_id = 1
    for domain in json_data:
        sql_data += "INSERT INTO domains (id,name,type) VALUES (%d,'%s','NATIVE');\n" % (domain_id, domain)
        for record in json_data[domain]:
            sql_data += "INSERT INTO records (content,ttl,type,domain_id,name) VALUES ('%s',%d,'%s',%d,'%s');\n" % (
                record["content"], record["ttl"], record["type"], domain_id,
                record["name"], )
        domain_id += 1
    return sql_data


def save_db(path, sql_data):
    """Save DB file on given path using created sql_data."""

    try:
        db = sqlite3.connect(path)
        c = db.cursor()
        c.executescript(sql_data)
        db.close()
    except sqlite3.OperationalError as e:
        print("ERROR creating sqlite DB file: {}").format(e)
        sys.exit(1)
    return


if __name__ == '__main__':
    args = parse_args()

    json_data = read_json(args.json_file)
    sql_data = make_sql(json_data)

    if args.dest_file:
        save_db(args.dest_file, sql_data)
    else:
        print(sql_data)
