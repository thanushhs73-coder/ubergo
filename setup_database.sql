-- Create drivers table
CREATE TABLE drivers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    assigned_port INT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_port INT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ride_requests table
CREATE TABLE ride_requests (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    user_port INT NOT NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ASSIGNED', 'ACCEPTED', 'COMPLETED')),
    assigned_driver_id INT,
    assigned_driver_port INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_driver_id) REFERENCES drivers(id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_ride_requests_user_id ON ride_requests(user_id);
CREATE INDEX idx_ride_requests_driver_id ON ride_requests(assigned_driver_id);
CREATE INDEX idx_ride_requests_status ON ride_requests(status);
