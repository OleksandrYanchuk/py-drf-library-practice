# DRF-library-practice

Online management system for book borrowings

## Setup and Local Installation

### To set up and run the project locally, follow these steps:

#### 1.  Clone the repository:

```python
git clone https://github.com/OleksandrYanchuk/py-drf-library-practice.git
```
#### 2. Open the folder:
```python
cd py-drf-library-practice
```
#### 3. Create a virtual environment:
```python
python -m venv venv
```
#### 4. Activate the virtual environment:
   
##### - For Windows:
```python
venv\Scripts\activate
```
##### -	For macOS and Linux:
```python
source venv/bin/activate
```
#### 5. Setting up Environment Variables:

##### 1. Rename a file name `.env_sample` to `.env` in the project root directory.

##### 2. Make sure to replace all enviroment keys with your actual enviroment data.

#### 6. For run application manually make next steps:

```python
pip install -r requirements.txt
```
```python
python manage.py migrate
```
```python
python manage.py runserver
```
#### 7. Open your web browser and go to http://localhost:8000 to access the application.

#### 8. If necessary, it is possible to register a new user using the following link:
```python
http://localhost:8000/api/user/register/
```
##### You can get information about the available tokens for the user at the following link:
```python
http://localhost:8000/api/user/token/
```
##### also, for correct operation, you need to install an extension for working with request and response headers, for example ModHeader.
##### in expansion you need to enter "Authorize" in the name field, and "Bearer [your access tiken]" in the value field.

#### After all previous steps py-drf-library-practice will work correctly.
