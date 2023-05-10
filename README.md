# SoftriteAPI
API project to provide Adaski with updated payroll information over the internet including the latest RBZ Interbank Exchange rates and NEC rates and grades. 
The project also includes a scraper that downloads the latest exchange rate pdf from the RBZ website and extracts the latest USD-ZWL rate.

## Admin/Support Pages

![image](https://github.com/Fingolfin7/SoftriteAPI/assets/63872314/4897eddd-8f4a-4e07-ae6e-29c351166f04)

## API Endpoints
Here's a list of all the endpoints so far:

-	`/interbank/get_latest_rate/`: Returns the latest interbank exchange rate.
-	`/interbank/get_rate_on/<str:date>/`: Returns the interbank exchange rate for a specific date.
-	`/interbank/get_all_rates/`: Returns all interbank exchange rates.
-	`/nec/get_necs/`: Returns all National Employment Councils (NECs).
-	`/nec/<int:pk>/get_latest_rate/`: Returns the latest NEC exchange rate for a specific NEC.
-	`/nec/<int:pk>/get_all_rates/`: Returns all NEC exchange rates for a specific NEC.
-   `/nec/<int:pk>/get_rate_on/<str:date>/`: Returns the NEC rate for a given date
-   `/nec/<int:pk>/get_all_grades/`: Returns all the grades for a given NEC
-   `/nec/<int:pk>/get_grade/<str:grade>/`: Returns the grade name and USD Minimum for a specific NEC and grade name.

## Response Format
Data is returned in JSON format like so:

Request: 
```url
http://127.0.0.1:8000/interbank/get_latest_rate
```

Response:
```json
{
    "rate": 989.0679,
    "date": "04-19-2023"
}
```

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the requirements using `pip install -r requirements.txt`
4. Run the server using `python manage.py runserver`
5. Navigate to `http://127.0.0.1:8000/` to view the admin/support page
