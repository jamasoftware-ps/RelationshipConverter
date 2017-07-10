
# Jama Software
Jama Software is the definitive system of record and action for product development. The company’s modern requirements and test management solution helps enterprises accelerate development time, mitigate risk, slash complexity and verify regulatory compliance. More than 600 product-centric organizations, including NASA, Boeing and Caterpillar use Jama to modernize their process for bringing complex products to market. The venture-backed company is headquartered in Portland, Oregon. For more information, visit [jamasoftware.com](http://jamasoftware.com).

Please visit [dev.jamasoftware.com](http://dev.jamasoftware.com) for additional resources and join the discussion in our community [community.jamasoftware.com](http://community.jamasoftware.com).

## Relationship Converter
```relationship_converter.py``` is a script which can convert all relationships of a given type between two item types in Jama into another relationship type using the Jama REST API. Users can configure the project to convert multiple relationships types at a one time if needbe (see script comments). 

Please note that this script is distrubuted as-is as an example and will likely require modification to work for your specific use-case.  This example omits error checking. Jama Support will not assist with the use or modification of the script.

### Before you begin
- Install Python 2.7 or higher and the requests library.  [Python](https://www.python.org/) and [Requests](http://docs.python-requests.org/en/latest/)

### Setup
1. As always, set up a test environment and project to test the script.

2. Fill out the CONFIG section of the script.  The necessary fields are:
  - ```username```
  - ```password```
  - ```base_url```
3. Create an object and set it's key-value pairs as follows (see script for more examples): 

    ```
    object = {}
    
    object.__setitem__("from_item_type_id", "89025")
    
    object.__setitem__("to_item_type_id", "89008") 
    
    object.__setitem__("old_relationship_type", "Related to")  
    object.__setitem__("new_relationship_type", "Epic to Feature")
    
4. For each object you create, insert the following line into main:
    
        convert(object)
