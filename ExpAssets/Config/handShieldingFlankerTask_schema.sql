CREATE TABLE participants (
    id integer primary key autoincrement not null,
    userhash text not null,
    gender text not null,
    age integer not null, 
    handedness text not null,
    created text not null
);

CREATE TABLE trials (
    id integer primary key autoincrement not null,
    participant_id integer not null references participants(id),
    practicing text not null,
    block_num integer not null,
    trial_num integer not null,
    hand_placed text not null,
    target_letter text not null,
    left_flanker_type text not null,
    right_flanker_type text not null,
    response_time text not null,
    response_made text not null
);
