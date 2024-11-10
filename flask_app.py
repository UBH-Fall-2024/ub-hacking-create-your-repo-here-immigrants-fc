from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json
import threading
import time
import re
from Prompts import make_query 
from json_stuff import clean_and_validate_json



app = Flask(__name__)




def parse_timer_items(timer_items):
    """Parse timer items into a list of tasks"""
    tasks = []
    task_id = 1
    
    for item_key, item_data in timer_items.items():
        if isinstance(item_data, dict):
            for key, value in item_data.items():
                if isinstance(value, dict):
                    time_needed = next(iter(value))
                    description = value[time_needed]
                    
                    task = {
                        'id': task_id,
                        'text': f"{key}: {description}",
                        'time': time_needed,
                        'seconds': parse_time_to_seconds(time_needed),
                        'completed': False
                    }
                    tasks.append(task)
                    task_id += 1
    
    return tasks
class AppState:
    def __init__(self):
        self.tasks = []
        self.total_timer = 0  
        self.task_timer = 0   
        self.current_task_index = 0
        self.timer_running = False
        self.timer_thread = None
        self.current_schedule = None
        self.original_times = {}
        self.total_original_time = 0  


app_state = AppState()

def parse_time_to_seconds(time_str):
    """Convert time string (e.g., '25 minutes', '1 hour') to seconds"""
    time_str = time_str.lower().strip()

    total_seconds = 0
    

    if ' and ' in time_str:
        parts = time_str.split(' and ')
    else:
        parts = [time_str]
    
    for part in parts:
        if 'hour' in part:
            hours = float(part.split('hour')[0].strip())
            total_seconds += int(hours * 3600)
        elif 'minute' in part:
            minutes = float(part.split('minute')[0].strip())
            total_seconds += int(minutes * 60)
        elif 'second' in part:
            seconds = float(part.split('second')[0].strip())
            total_seconds += int(seconds)
            
    return total_seconds

def format_time(seconds):
    """Convert seconds to HH:MM:SS format"""
    if seconds < 0:
        seconds = 0
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@app.route('/')
def home():
    print("yes")
    return render_template('index.html')

def timer_thread_function():
    """Background thread for timer countdown"""
    print("Timer thread started")
    last_update_time = time.time()
    
    while app_state.timer_running and (app_state.total_timer > 0 or app_state.task_timer > 0):
        current_time = time.time()
        elapsed_time = int(current_time - last_update_time)
        
        if elapsed_time >= 1:  

            if app_state.total_timer > 0:
                app_state.total_timer -= elapsed_time
            if app_state.task_timer > 0:
                app_state.task_timer -= elapsed_time
                

            if app_state.task_timer <= 0 and app_state.current_task_index < len(app_state.tasks) - 1:
                print(f"Moving to next task from index {app_state.current_task_index}")
                app_state.tasks[app_state.current_task_index]['completed'] = True
                app_state.current_task_index += 1
                next_task = app_state.tasks[app_state.current_task_index]
                app_state.task_timer = app_state.original_times[next_task['id']]
                print(f"New task timer set to {app_state.task_timer}")
            
            last_update_time = current_time
            
        time.sleep(0.1)  
    

    app_state.timer_running = False
    if app_state.current_task_index < len(app_state.tasks):
        app_state.tasks[app_state.current_task_index]['completed'] = True
    print("Timer thread finished")

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400
            
        schedule_json = make_query(message)
        schedule_data = json.loads(schedule_json)
        
        if schedule_data['Action'] == 'New_Timer':
            app_state.tasks = []
            app_state.total_timer = 0
            app_state.task_timer = 0
            app_state.current_task_index = 0
            app_state.timer_running = False
            app_state.current_schedule = schedule_data
            app_state.original_times = {}
            app_state.total_original_time = 0
            

            timer_items = schedule_data.get('Timer_Items', {})
            for item_name, item_info in timer_items.items():
                time_needed = item_info.get('Time Needed', '0 minutes')
                description = item_info.get('Description', '')
                seconds = parse_time_to_seconds(time_needed)
                
                if seconds <= 0:
                    continue
                    
                task = {
                    'id': len(app_state.tasks) + 1,
                    'text': f"{description}",
                    'time': time_needed,
                    'seconds': seconds,
                    'completed': False
                }
                
                app_state.tasks.append(task)
                app_state.total_timer += seconds
                app_state.original_times[task['id']] = seconds
            
            app_state.total_original_time = app_state.total_timer
            
            
            if app_state.tasks:
                app_state.task_timer = app_state.tasks[0]['seconds']
                
                app_state.timer_running = True
                if app_state.timer_thread and app_state.timer_thread.is_alive():
                    app_state.timer_running = False
                    app_state.timer_thread.join(timeout=1.0)
                app_state.timer_thread = threading.Thread(target=timer_thread_function)
                app_state.timer_thread.daemon = True
                app_state.timer_thread.start()
        
        return jsonify({
            'status': 'success',
            'tasks': app_state.tasks,
            'total_timer': format_time(app_state.total_timer),
            'task_timer': format_time(app_state.task_timer),
            'current_task_index': app_state.current_task_index,
            'timer_running': app_state.timer_running,
            'total_original_time': format_time(app_state.total_original_time)
        })
            
    except Exception as e:
        print("Error in send_message:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
@app.route('/toggle-task', methods=['POST'])
def toggle_task():
    data = request.json
    task_id = data.get('taskId')
    
    for task in app_state.tasks:
        if str(task['id']) == str(task_id):
            task['completed'] = not task['completed']
            break
    
    return jsonify({
        'status': 'success',
        'tasks': app_state.tasks
    })

@app.route('/get-timers', methods=['GET'])
def get_timers():
    """Endpoint for polling timer values"""
    return jsonify({
        'total_timer': format_time(app_state.total_timer),
        'task_timer': format_time(app_state.task_timer),
        'current_task_index': app_state.current_task_index,
        'timer_running': app_state.timer_running
    })

@app.route('/reset', methods=['POST'])
def reset():
    """Reset all timers and tasks"""
    
    if app_state.timer_running:
        app_state.timer_running = False
        if app_state.timer_thread and app_state.timer_thread.is_alive():
            app_state.timer_thread.join(timeout=1.0)
    
    
    app_state.tasks = []
    app_state.total_timer = 0
    app_state.task_timer = 0
    app_state.current_task_index = 0
    app_state.current_schedule = None
    app_state.original_times = {}
    
    return jsonify({
        'status': 'success',
        'message': 'All timers and tasks reset',
        'tasks': [],
        'total_timer': '00:00:00',
        'task_timer': '00:00:00',
        'current_task_index': 0,
        'timer_running': False
    })

def cleanup_thread():
    """Cleanup function to stop timer thread when application stops"""
    if app_state.timer_running:
        app_state.timer_running = False
        if app_state.timer_thread and app_state.timer_thread.is_alive():
            app_state.timer_thread.join(timeout=1.0)


@app.before_request
def register_cleanup():
    import atexit
    atexit.register(cleanup_thread)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  