create table runner (
    runner_id integer primary key,
    name varchar(40) not null,
    birth_year integer,
    started_running_year integer
);

create table shoe (
    shoe_id integer primary key,
    runner_id integer not null,
    brand varchar(30) not null,
    model varchar(40) not null,
    purchase_date date not null,
    retired tinyint not null,           -- 1 = retired
    foreign key (runner_id) references runner (runner_id)
);

create table route (
    route_id integer primary key,
    name varchar(50) not null,
    distance_km real not null,
    surface varchar(10) not null,       -- road, trail, track
    elevation_gain_m integer not null
);

create table run (
    run_id integer primary key,
    runner_id integer not null,
    shoe_id integer not null,
    route_id integer not null,
    run_date date not null,
    duration_minutes real not null,
    avg_heart_rate integer,
    perceived_effort integer not null,  -- 1 (easy) to 10 (max)
    foreign key (runner_id) references runner (runner_id),
    foreign key (shoe_id) references shoe (shoe_id),
    foreign key (route_id) references route (route_id)
);

create table injury (
    injury_id integer primary key,
    runner_id integer not null,
    run_id integer,                     -- the run during which it started, if known
    body_part varchar(30) not null,
    start_date date not null,
    end_date date,                      -- null = still injured
    severity integer not null,          -- 1 (minor) to 5 (severe)
    foreign key (runner_id) references runner (runner_id),
    foreign key (run_id) references run (run_id)
);
