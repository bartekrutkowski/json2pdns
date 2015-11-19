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

(... output stripped ...)

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
