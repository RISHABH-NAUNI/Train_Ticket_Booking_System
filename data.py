# data.py

# Mock Database
TRAINS = [
    {'id': 'T101', 'name': 'Express A', 'source': 'City1', 'destination': 'City2', 'seats': 5},
    {'id': 'T102', 'name': 'Express B', 'source': 'City1', 'destination': 'City3', 'seats': 3},
    {'id': 'T103', 'name': 'Express C', 'source': 'City2', 'destination': 'City3', 'seats': 4},
]

# USERS: Mock users database
USERS = {}  # Example: {'username': 'password'}

# BOOKINGS: Mock bookings database
BOOKINGS = []  # Example: [{'user': 'username', 'train': 'T101', 'booking_id': 'BKG1001'}]

# Function to generate a unique booking ID
def generate_booking_id():
    return f"BKG{1000 + len(BOOKINGS)}"