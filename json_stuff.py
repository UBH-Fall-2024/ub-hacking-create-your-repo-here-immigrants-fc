import json
def clean_and_validate_json(json_string):
    """Clean and validate JSON string before parsing"""
    try:
        
        initial_data = json.loads(json_string)
        
 
        if isinstance(initial_data.get('User'), str) and len(initial_data.get('Timer_Items', {})) == 0:
            try:

                user_data = json.loads(initial_data['User'])
                if isinstance(user_data, dict) and 'Timer_Items' in user_data:
                    return {
                        'Action': 'New_Timer',
                        'Timer_Items': user_data['Timer_Items'],
                        'User': user_data.get('User', '')
                    }
            except json.JSONDecodeError:
                print("Failed to parse User field as JSON")
        
        return initial_data
            
    except Exception as e:
        print(f"Original JSON string: {json_string}")
        print(f"Error during JSON cleaning: {str(e)}")
        return {
            "Action": "New_Timer",
            "Timer_Items": {},
            "User": "Error occurred while processing the schedule."
        }