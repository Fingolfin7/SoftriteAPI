# SoftriteAPI
API project to provide Adaski with updated payroll information over the internet including the latest RBZ Interbank Exchange rates and NEC rates and grades. 
The project also includes a scraper that downloads the latest exchange rate pdf from the RBZ website and extracts the latest USD-ZWL rate using the `tabula` and `tabulate` modules

## Admin/Support Pages

![image](https://user-images.githubusercontent.com/63872314/233022466-f06524ca-dc91-4339-992c-7487b6d9c571.png)

## API Endpoints
Here's a list of all the endpoints so far:

-	/interbank/get_latest_rate/: Returns the latest interbank exchange rate.
-	/interbank/get_rate_on/<str:date>/: Returns the interbank exchange rate for a specific date.
-	/interbank/get_all_rates/: Returns all interbank exchange rates.
-	/nec/get_necs/: Returns all National Employment Councils (NECs).
-	/nec/<int:pk>/get_latest_rate/: Returns the latest NEC exchange rate for a specific NEC.
-	/nec/<int:pk>/get_all_rates/: Returns all NEC exchange rates for a specific NEC.
- /nec/<int:pk>/get_rate_on/<str:date>/: Returns the NEC rate for a given date
- /nec/<int:pk>/get_all_grades/: Returns all the grades for a given NEC
- /nec/<int:pk>/get_grade/<str:grade>/: Returns the grade name and USD Minimum for a specific NEC and grade name.

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
