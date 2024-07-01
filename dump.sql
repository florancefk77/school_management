-- Set SQL mode to allow zero values in auto-increment columns

-- Start a new transaction
START TRANSACTION;

-- Set the time zone to UTC
SET time_zone = "+00:00";

-- Create the 'classes' table
CREATE TABLE `classes` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `Capacity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Insert initial data into the 'classes' table
INSERT INTO `classes` (`id`, `name`, `Capacity`) VALUES
(50, 'first', 40);

-- Create the 'students' table
CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `class_id` int(11) NOT NULL,
  `Last_name` varchar(100) NOT NULL,
  `Phone` varchar(10) NOT NULL,
  `email` varchar(50) NOT NULL,
  `address` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Insert initial data into the 'students' table
INSERT INTO `students` (`id`, `first_name`, `class_id`, `Last_name`, `Phone`, `email`, `address`) VALUES
(20, 'John', 50, 'Doe', '1234567890', 'john.doe@example.com', '123 Main St');

-- Create the 'subjects' table
CREATE TABLE `subjects` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `class_id` int(11) DEFAULT NULL,
  `Teacher_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Insert initial data into the 'subjects' table
INSERT INTO `subjects` (`id`, `name`, `class_id`, `Teacher_id`) VALUES
(30, 'physics', 50, 60),
(31, 'chemistry', 50, 60);

-- Create the 'teachers' table
CREATE TABLE `teachers` (
  `id` int(11) NOT NULL,
  `First_name` varchar(50) NOT NULL,
  `Last_name` varchar(50) NOT NULL,
  `phone` varchar(10) NOT NULL,
  `Email` varchar(50) NOT NULL,
  `address` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Insert initial data into the 'teachers' table
INSERT INTO `teachers` (`id`, `First_name`, `Last_name`, `phone`, `Email`, `address`) VALUES
(60, 'max', 'mustermann', '0987654321', 'max.mustermann@example.com', '456 High St');

-- Create the 'users' table
CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Insert initial data into the 'users' table
INSERT INTO `users` (`id`, `username`, `password`, `email` , `role`) VALUES
(100, 'florance', 'florance', 'admin@example.com', 'admin' );

-- Add primary key to 'classes' table
ALTER TABLE `classes`
  ADD PRIMARY KEY (`id`);

-- Add primary key to 'students' table
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`);

-- Add primary key to 'subjects' table
ALTER TABLE `subjects`
  ADD PRIMARY KEY (`id`);

-- Add primary key to 'teachers' table
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`id`);

-- Add primary key to 'users' table
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

-- Modify 'id' column in 'classes' table to be auto-increment starting from 1
ALTER TABLE `classes`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

-- Modify 'id' column in 'students' table to be auto-increment starting from 1
ALTER TABLE `students`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

-- Modify 'id' column in 'subjects' table to be auto-increment starting from 6
ALTER TABLE `subjects`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

-- Modify 'id' column in 'teachers' table to be auto-increment starting from 24
ALTER TABLE `teachers`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;

-- Modify 'id' column in 'users' table to be auto-increment starting from 161
ALTER TABLE `users`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=100;

-- Add foreign key constraint to 'students' table on 'class_id' column referencing 'id' column in 'classes' table
-- This ensures referential integrity and cascades deletions and updates
-- ALTER TABLE `students`
    -- ADD CONSTRAINT `students_id` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add foreign key constraints to 'subjects' table
-- First, on 'class_id' column referencing 'id' column in 'classes' table
-- Second, on 'Teacher_id' column referencing 'id' column in 'teachers' table
-- Both constraints ensure referential integrity and cascade deletions and updates
-- ALTER TABLE `subjects`
    -- ADD CONSTRAINT `subjects_class_id` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    -- ADD CONSTRAINT `subjects_teacher_id` FOREIGN KEY (`Teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- Commit the transaction to make all the preceding changes permanent
COMMIT;
