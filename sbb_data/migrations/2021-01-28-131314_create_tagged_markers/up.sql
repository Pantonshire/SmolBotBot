create table tagged_markers (
    robot_group_id  int8 primary key references robot_groups (id),
    tagged_at       timestamp with time zone not null default CURRENT_TIMESTAMP
);
