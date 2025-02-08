import json
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Function to generate random activity metrics
def generate_activity_metrics(start_date, end_date):
    activities = []
    current_date = start_date

    while current_date <= end_date:
        # Generate random activity data
        activity = {
            "activityId": fake.uuid4(),
            "activityName": random.choice(["Morning Run", "Track Workout", "Sprint Session", "Long Run", "Interval Training"]),
            "startTimeLocal": current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "distance": random.randint(1000, 20000),  # in meters
            "duration": random.randint(1200, 7200),  # in seconds
            "averagePace": random.randint(240, 420),  # in seconds per kilometer
            "averageHeartRate": random.randint(120, 160),
            "maxHeartRate": random.randint(160, 190),
            "steps": random.randint(1000, 20000),
            "calories": random.randint(300, 1000),
            "vo2Max": round(random.uniform(40, 60), 1),
            "trainingEffect": round(random.uniform(3.0, 5.0), 1),
            "splits": generate_splits(),
            "maxSpeed": round(random.uniform(4.0, 6.0), 1),  # in meters per second
            "groundContactTime": random.randint(200, 300),  # in milliseconds
            "verticalOscillation": round(random.uniform(7.0, 9.0), 1),  # in centimeters
            "verticalRatio": round(random.uniform(7.0, 9.0), 1),  # in percentage
        }
        activities.append(activity)

        # Move to the next day (or skip some days for realism)
        current_date += timedelta(days=random.randint(1, 3))

    return activities

# Function to generate random splits for an activity
def generate_splits():
    splits = []
    for _ in range(random.randint(5, 20)):  # 5 to 20 splits
        split = {
            "distance": random.choice([400, 800, 1000, 1600]),  # in meters
            "time": random.randint(60, 300)  # in seconds
        }
        splits.append(split)
    return splits

# Function to save data to a JSON file
def save_to_json(data, filename="garmin_metrics.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Generated data saved to {filename}")

# Main function
def main():
    # Define date range (approximately 2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years ago

    # Generate activity metrics
    activity_metrics = generate_activity_metrics(start_date, end_date)

    # Save to JSON file
    save_to_json(activity_metrics)

if __name__ == "__main__":
    main()