# Setup

1. Create venv

```
python -m venv .venv
```

2. Activate

```
source .venv/bin/activate
``` 

3. Install Packages

```
pip install -r requirements.txt
```

4. Run with Uvicorn

```
uvicorn main:app --reload
```

# What to check

- Open http://127.0.0.1:8000/ in browser -> see {"message": "Hello World"}.
- Open http://127.0.0.1:8000/docs -> see FastAPI Swagger UI.

# Database Table structure

DB Name: asc_scheduler
List of relations
 Schema |     Name     | Type        
--------+--------------+-------
 public | passschedule | table
 public | satellite    | table 
 public | tle          | table 

Table "public.satellite"
   Column    |  Type   | Collation | Nullable |                Default                
-------------+---------+-----------+----------+---------------------------------------
 name        | text    |           | not null | 
 id          | integer |           | not null | nextval('satellite_id_seq'::regclass)
 description | text    |           | not null | 

Table "public.tle"
    Column    |           Type           | Collation | Nullable |               Default               
--------------+--------------------------+-----------+----------+-------------------------------------
 tle_id       | integer                  |           | not null | nextval('tle_tle_id_seq'::regclass)
 satellite_id | integer                  |           | not null | 
 line1        | character varying(80)    |           | not null | 
 line2        | character varying(80)    |           | not null | 
 timestamp    | timestamp with time zone |           | not null | CURRENT_TIMESTAMP

Table "public.passschedule"
     Column     |           Type           | Collation | Nullable |                Default                    
----------------+--------------------------+-----------+---------+-----------------------------------------------
 pass_id        | integer                  |           | not null | nextval('passschedule_pass_id_seq'::regclass)
 satellite_id   | integer                  |           | not null | 
 ground_station | character varying(100)   |           | not null | 
 start_time     | timestamp with time zone |           | not null | 
 end_time       | timestamp with time zone |           | not null | 
 status         | character varying(50)    |           | not null | 
