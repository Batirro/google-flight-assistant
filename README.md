# Google Flight Scraper

A comprehensive flight monitoring and notification system built with Flask that helps users track flight prices and get notified when flights become available for their preferred dates.

## 🚀 Features

- **Flight Search**: Search for flights using Google Flights API through SerpAPI
- **Price Monitoring**: Track flight prices for specific routes and dates
- **Email Notifications**: Get notified when flights are available for your preferred dates
- **User Management**: Store user preferences and flight searches
- **Airport Search**: Intelligent airport search with IATA code validation
- **Scheduled Monitoring**: Background worker to continuously check for flight availability
- **Multi-class Support**: Support for different seat classes (Economy, Business, First)
- **Database Integration**: PostgreSQL database with SQLAlchemy ORM
- **Responsive UI**: Clean, responsive web interface

## 🛠 Tech Stack

- **Backend**: Flask, SQLAlchemy, Alembic
- **Database**: PostgreSQL
- **API**: SerpAPI (Google Flights)
- **Scheduling**: APScheduler
- **Email**: SMTP email notifications
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker
- **Environment Management**: Doppler (for production), python-dotenv (for development)

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL database
- SerpAPI key for Google Flights access
- Email server credentials (for notifications)

## 🔧 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/GoogleFlightScraper.git
   cd GoogleFlightScraper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   # Database Configuration
   DBUSER=your_db_user
   DBPASSWD=your_db_password
   HOSTIP=localhost
   DBPORT=5432
   DBNAME=flight_scraper

   # API Keys
   SERP_API=your_serpapi_key

   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password

   # Data Directory
   DATA_DIR=./data
   ```

5. **Database Setup**
   ```bash
   # Initialize database
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t flight-scraper .
   ```

2. **Run with environment variables**
   ```bash
   docker run -p 5000:5000 \
     -e DBUSER=your_db_user \
     -e DBPASSWD=your_db_password \
     -e HOSTIP=your_db_host \
     -e SERP_API=your_serpapi_key \
     flight-scraper
   ```

### Background Worker

To enable scheduled flight monitoring, run the background worker:

```bash
cd workers
python flight_checker_scheduled.py
```

## 📖 Usage

### Web Interface

1. **Search for Flights**
   - Navigate to the home page
   - Enter departure and arrival airports (with autocomplete)
   - Select departure and return dates
   - Choose seat class and currency
   - Submit the search

2. **Set Up Notifications**
   - Provide your email address
   - The system will monitor flights for your specified dates
   - Receive email notifications when flights become available

### API Endpoints

- `GET /` - Main flight search form
- `POST /` - Submit flight search
- `GET /api/airports` - Airport search endpoint for autocomplete

## 🗄 Database Schema

### Users Table
- `user_id` (Primary Key)
- `email` (Unique)

### Flight Preferences Table
- `preference_id` (Primary Key)
- `user_id` (Foreign Key)
- `target_departure`
- `return_date`
- `departure_airport`
- `arrival_airport`
- `currency`
- `seat_class`
- `max_price`
- `preferred_airline`

## 🔄 Database Migrations

The project uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🛡 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DBUSER` | Database username | Yes |
| `DBPASSWD` | Database password | Yes |
| `HOSTIP` | Database host | Yes |
| `DBPORT` | Database port | Yes |
| `DBNAME` | Database name | Yes |
| `SERP_API` | SerpAPI key for Google Flights | Yes |
| `EMAIL_HOST` | SMTP server host | Yes |
| `EMAIL_PORT` | SMTP server port | Yes |
| `EMAIL_USER` | Email username | Yes |
| `EMAIL_PASSWORD` | Email password/app password | Yes |
| `DATA_DIR` | Directory for data files | No |

## 📁 Project Structure

```
GoogleFlightScraper/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic configuration
├── flights_dates.json         # Flight data storage
├── alembic/                   # Database migrations
├── config/                    # Configuration files
│   └── config.py
├── logic/                     # Business logic
│   ├── airport_search.py      # Airport search functionality
│   ├── data_grabber.py        # Flight data retrieval
│   ├── date_parser.py         # Date parsing utilities
│   ├── email_sender.py        # Email notification system
│   └── flight_checker.py      # Flight availability checking
├── services/                  # Data services
│   ├── database.py            # Database operations
│   ├── db_instance.py         # Database instance
│   ├── models.py              # SQLAlchemy models
│   └── schemas.py             # Pydantic schemas
├── static/                    # Static assets
│   ├── css/
│   └── js/
├── templates/                 # HTML templates
└── workers/                   # Background workers
    └── flight_checker_scheduled.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Known Issues

- SerpAPI has rate limits that may affect frequent searches
- Email notifications require proper SMTP configuration
- Background worker needs to be run separately for scheduled monitoring

## 🔮 Future Enhancements

- [ ] Add targeting flights search for the whole month
- [ ] Enable more filters for flights preferences
- [ ] Make better airport search engine
- [ ] Make email notifications more readable

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please respect the terms of service of the APIs and websites being accessed. The authors are not responsible for any misuse of this software.
