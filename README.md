# bufit

A fitness web-application where users can create, share, and discover workouts.

# Concept
Admins can add available exercises to the website and designate coaches.

Coaches can confirm their accounts and create professional workouts for users.

Users are able to view a repository of exercises, create a workout from those given exercises, favorite exercises and workouts,
find regimes curated by a coach, and use BuFit as a hub for fitness.


# Deployment
Deployed through [AWS Elastic Beanstalk](https://docs.aws.amazon.com/elastic-beanstalk/index.html)

At: http://bufit.us-east-1.elasticbeanstalk.com/

# Local Run Guide
Follow these steps to run locally:
1. Set up your virtual environment (https://docs.python.org/3/library/venv.html)
2. Install requirements: `pip install -r requirements.txt`
3. Start local webserver: `python application.py`
4. Open your browser and navigate to: `http://127.0.0.1:5000/`

# References

## Data
To facilitate the web app's development, we utilized wger's API found [here](https://wger.de/en/software/api) to preload exercises and avoid manual data entry.
