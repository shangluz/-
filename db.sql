create database transportdb;
use transportdb;
show tables;

create table users (
    id int primary key auto_increment,
    username varchar(50) not null unique,
    password varchar(255) not null,
    name varchar(50),
    role varchar(20)
);

create table vehicles (
    id int primary key auto_increment,
    plate_number varchar(20) not null unique,
    type varchar(50) not null,
    status varchar(20) default '空闲'
);

create table drivers (
    id int primary key auto_increment,
    name varchar(50) not null,
    phone varchar(20)
);

create table transport_tasks (
    id int primary key auto_increment,
    client_name varchar(100),
    need_vehicle_type varchar(50),
    need_count int,
    plan_mileage decimal(10,2),
    plan_start_time datetime,
    plan_end_time datetime,
    vehicle_id int,
    driver_id int,
    real_start_time datetime,
    real_end_time datetime,
    real_mileage decimal(10,2),
    fuel_used decimal(10,2),
    status varchar(20) default '待安排',
    foreign key (vehicle_id) references vehicles(id),
    foreign key (driver_id) references drivers(id)
);

create table accidents (
    id int primary key auto_increment,
    vehicle_id int not null,
    driver_id int not null,
    accident_time datetime not null,
    location text,
    reason text,
    handle_method text,
    cost decimal(12,2),
    other_plate varchar(50),
    foreign key (vehicle_id) references vehicles(id),
    foreign key (driver_id) references drivers(id)
);

insert into users (username, password, name, role)
values
('root', '123', 'root', '管理员'),
('user1', '123', '张三', '司机');

insert into vehicles (plate_number, type, status)
values
('京A12345', '轿车', '空闲'),
('京B12345', '大货车', '任务中'),
('京C12345', '小货车', '空闲');

insert into drivers (name, phone)
values
('张三', '11111111111'),
('李四', '11111111112'),
('王五', '11111111113');

insert into transport_tasks (client_name, need_vehicle_type, need_count, plan_mileage, plan_start_time, plan_end_time, vehicle_id, driver_id, status)
value('北京食品公司', '大货车', 1, 120.50, '2025-12-02 08:00:00', '2025-12-02 18:00:00', 2, 1, '进行中');

insert into accidents (vehicle_id, driver_id, accident_time, location, reason, handle_method, cost, other_plate)
value(1, 2, '2025-12-01 14:30:00', '京沪高速入口', '追尾', '保险理赔', 5000.00, '京D12345');

select *
from users